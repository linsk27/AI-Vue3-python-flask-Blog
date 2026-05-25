import hashlib
import json
import os

import httpx
from openai import OpenAI

from database import engine
from db.schema import ensure_embedding_config_table
from repositories import context_pack_repo as repo
from services.rag_utils import (
    estimate_tokens,
    normalize_source_content,
    serialize_embedding,
    split_source_into_chunks,
)


json_loads = repo.json_loads
row_to_source = repo.row_to_source
row_to_pack = repo.row_to_pack
fetch_sources = repo.fetch_sources
get_pack_or_404 = repo.get_pack_or_404
fetch_real_pack_rows = repo.fetch_real_pack_rows
is_legacy_demo_pack = repo.is_legacy_demo_pack


def json_dumps(value):
    return json.dumps(value or [], ensure_ascii=False)


def compute_pack_quality(source_count, has_intent, has_summary, tags_count):
    score = 34 + min(source_count, 6) * 9
    if has_intent:
        score += 10
    if has_summary:
        score += 8
    score += min(tags_count, 4) * 3
    return min(score, 98)


def estimate_token_budget(sources):
    total_chars = sum(len(source.get("content") or "") for source in sources)
    approx_tokens = max(800, round(total_chars / 1.6))
    return f"{approx_tokens / 1000:.1f}k"


def estimate_chunk_tokens(text_value):
    return estimate_tokens(text_value)


def normalize_tags(tags):
    if isinstance(tags, str):
        return [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]
    return tags or []


def mask_secret(value):
    if not value:
        return ""
    if len(value) <= 8:
        return "******"
    return f"{value[:4]}******{value[-4:]}"


def get_env_embedding_config():
    enabled = (os.getenv("RAG_EMBEDDING_ENABLED") or "").lower() in {"1", "true", "yes", "on"}
    model = os.getenv("RAG_EMBEDDING_MODEL", "").strip()
    api_key = os.getenv("RAG_EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ARK_API_KEY")
    base_url = os.getenv("RAG_EMBEDDING_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    provider = os.getenv("RAG_EMBEDDING_PROVIDER") or ("custom" if base_url else "openai")

    return {
        "enabled": enabled,
        "configured": bool(enabled and model and api_key),
        "provider": provider,
        "model": model,
        "api_key": api_key or "",
        "api_key_masked": mask_secret(api_key or ""),
        "base_url": base_url or "",
        "source": "environment",
    }


def get_database_embedding_config(conn):
    try:
        ensure_embedding_config_table(conn)
        row = repo.fetch_active_embedding_config(conn)
    except Exception:
        return None

    if not row:
        return None

    api_key = row.get("api_key") or ""
    enabled = bool(row.get("enabled") and row.get("is_active"))
    model = row.get("model") or ""
    return {
        "id": row.get("id"),
        "enabled": enabled,
        "configured": bool(enabled and model and api_key),
        "provider": row.get("provider") or "openai",
        "model": model,
        "api_key": api_key,
        "api_key_masked": mask_secret(api_key),
        "base_url": row.get("base_url") or "",
        "notes": row.get("notes") or "",
        "source": "database",
        "updated_at": row.get("updated_at").isoformat() if row.get("updated_at") else "",
    }


def get_embedding_config(conn=None):
    if conn is not None:
        db_config = get_database_embedding_config(conn)
        if db_config:
            return db_config
        return get_env_embedding_config()

    try:
        with engine.connect() as new_conn:
            db_config = get_database_embedding_config(new_conn)
            if db_config:
                return db_config
    except Exception:
        pass

    return get_env_embedding_config()


def extract_embedding_vector(response_payload):
    if not isinstance(response_payload, dict):
        return []

    data = response_payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("embedding"), list):
        return data["embedding"]
    if isinstance(data, list) and data and isinstance(data[0], dict) and isinstance(data[0].get("embedding"), list):
        return data[0]["embedding"]
    if isinstance(response_payload.get("embedding"), list):
        return response_payload["embedding"]
    return []


def create_volcano_multimodal_embedding(text_value, settings):
    base_url = (settings.get("base_url") or "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
    response = httpx.post(
        f"{base_url}/embeddings/multimodal",
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings["model"],
            "input": [{"type": "text", "text": (text_value or "")[:8000]}],
        },
        timeout=60,
    )
    response.raise_for_status()
    return extract_embedding_vector(response.json())


def should_try_volcano_multimodal(settings, error):
    if (settings.get("provider") or "").lower() != "volcano":
        return False

    error_text = str(error)
    return (
        "does not support this api" in error_text
        or "InvalidEndpointOrModel.NotFound" in error_text
        or "doubao-embedding-vision" in error_text
    )


def create_embedding(text_value, config=None):
    settings = config or get_embedding_config()
    if not settings["configured"]:
        return None

    client_kwargs = {"api_key": settings["api_key"]}
    if settings["base_url"]:
        client_kwargs["base_url"] = settings["base_url"]

    client = OpenAI(**client_kwargs)
    try:
        response = client.embeddings.create(
            model=settings["model"],
            input=(text_value or "")[:8000],
        )
        return response.data[0].embedding
    except Exception as error:
        if should_try_volcano_multimodal(settings, error):
            return create_volcano_multimodal_embedding(text_value, settings)
        raise


def refresh_source_chunks(conn, source_id):
    source = repo.fetch_source_for_index(conn, source_id)
    if not source:
        return 0

    chunks = split_source_into_chunks(source.get("content") or "")
    if not chunks and source.get("title"):
        chunks = [source.get("title")]

    repo.delete_chunks_for_source(conn, source_id)
    for chunk_index, chunk in enumerate(chunks):
        repo.insert_source_chunk(
            conn,
            source_id=source["id"],
            pack_id=source["pack_id"],
            chunk_index=chunk_index,
            content=chunk,
            tokens_estimate=estimate_chunk_tokens(chunk),
            content_hash=hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
        )

    return len(chunks)


def sync_pack_chunks(conn, pack_id):
    created = 0
    for row in repo.fetch_source_ids_missing_chunks(conn, pack_id):
        created += refresh_source_chunks(conn, row["id"])
    return created


def rebuild_pack_chunks(conn, pack_id):
    repo.delete_chunks_for_pack(conn, pack_id)
    for row in repo.fetch_source_ids_for_pack(conn, pack_id):
        refresh_source_chunks(conn, row["id"])
    return get_pack_index_stats(conn, pack_id)


def get_pack_index_stats(conn, pack_id):
    embedding_config = get_embedding_config(conn)
    active_model = embedding_config["model"] if embedding_config["configured"] else ""
    row = repo.fetch_pack_index_row(conn, pack_id, active_model)

    sources = int(row.get("sources") or 0) if row else 0
    indexed_sources = int(row.get("indexed_sources") or 0) if row else 0
    latest_updated_at = row.get("latest_updated_at") if row else None
    chunks = int(row.get("chunks") or 0) if row else 0
    embedded_chunks = int(row.get("embedded_chunks") or 0) if row else 0
    current_model_embedded_chunks = int(row.get("current_model_embedded_chunks") or 0) if row else 0
    stale_embedding_chunks = int(row.get("stale_embedding_chunks") or 0) if row else 0
    pending_embedding_chunks = int(row.get("pending_embedding_chunks") or 0) if row else 0
    pending_embedding_tokens_estimate = int(row.get("pending_embedding_tokens_estimate") or 0) if row else 0

    return {
        "sources": sources,
        "indexed_sources": indexed_sources,
        "chunks": chunks,
        "embedded_chunks": embedded_chunks,
        "current_model_embedded_chunks": current_model_embedded_chunks,
        "stale_embedding_chunks": stale_embedding_chunks,
        "pending_embedding_chunks": pending_embedding_chunks,
        "embedding_configured": embedding_config["configured"],
        "embedding_model": embedding_config["model"] if embedding_config["enabled"] else "",
        "tokens_estimate": int(row.get("tokens_estimate") or 0) if row else 0,
        "pending_embedding_tokens_estimate": pending_embedding_tokens_estimate,
        "embedding_target_chunks": pending_embedding_chunks,
        "embedding_target_tokens_estimate": pending_embedding_tokens_estimate,
        "embedding_skip_current_model_chunks": current_model_embedded_chunks,
        "pending_sources": max(sources - indexed_sources, 0),
        "latest_updated_at": latest_updated_at.isoformat() if latest_updated_at else "",
    }


def refresh_pack_embeddings(conn, pack_id, force=False, dry_run=False):
    embedding_config = get_embedding_config(conn)
    if not embedding_config["configured"]:
        return None, "Embedding 未配置：请先设置 RAG_EMBEDDING_ENABLED=1、RAG_EMBEDDING_MODEL 和 API Key"

    generated = 0
    skipped = 0
    failed = 0
    planned = 0
    planned_tokens = 0

    for row in repo.fetch_chunks_for_embedding(conn, pack_id):
        if (
            not force
            and row.get("embedding")
            and row.get("embedding_model") == embedding_config["model"]
        ):
            skipped += 1
            continue

        planned += 1
        planned_tokens += int(row.get("tokens_estimate") or estimate_chunk_tokens(row.get("content") or ""))
        if dry_run:
            continue

        try:
            vector = create_embedding(row.get("content") or "", embedding_config)
            if not vector:
                failed += 1
                continue
            repo.update_chunk_embedding(
                conn,
                row_id=row["id"],
                embedding=serialize_embedding(vector),
                provider=embedding_config["provider"],
                model=embedding_config["model"],
                dimension=len(vector),
            )
            generated += 1
        except Exception:
            failed += 1

    stats = get_pack_index_stats(conn, pack_id)
    stats.update({
        "generated_embeddings": generated,
        "skipped_embeddings": skipped,
        "failed_embeddings": failed,
        "planned_embeddings": planned,
        "planned_embedding_tokens_estimate": planned_tokens,
        "dry_run": dry_run,
        "force": force,
    })
    return stats, None


def get_pack_chunks(conn, pack_id):
    created = sync_pack_chunks(conn, pack_id)
    if created:
        conn.commit()
    return repo.fetch_pack_chunks(conn, pack_id)


def add_article_sources(conn, pack_id, article_ids):
    if not article_ids:
        return {"added": 0, "found": 0, "duplicates": 0}

    normalized_ids = []
    for article_id in article_ids:
        try:
            normalized_ids.append(int(article_id))
        except (TypeError, ValueError):
            continue

    normalized_ids = list(dict.fromkeys(normalized_ids))
    if not normalized_ids:
        return {"added": 0, "found": 0, "duplicates": 0}

    rows = repo.fetch_articles_by_ids(conn, normalized_ids)
    existing_ids = repo.fetch_existing_article_ref_ids(conn, pack_id, normalized_ids)
    added = 0

    for row in rows:
        if row["id"] in existing_ids:
            continue

        article_content = row.get("content") or ""
        content_parts = []
        if row.get("summary"):
            content_parts.append(f"摘要：{row.get('summary')}")
        if article_content:
            content_parts.append(article_content[:4200])
        content = "\n\n".join(content_parts)
        source_id = repo.insert_context_pack_source(
            conn,
            {
                "pack_id": pack_id,
                "title": row["title"],
                "source_type": row.get("category") or "知识库文章",
                "ref_type": "article",
                "ref_id": row["id"],
                "content": content,
                "weight": "高",
                "status": "已接入",
            },
        )
        if source_id:
            refresh_source_chunks(conn, source_id)
        added += 1

    return {"added": added, "found": len(rows), "duplicates": len(rows) - added}


def add_custom_sources(conn, pack_id, sources):
    added = 0
    for source in sources or []:
        title = (source.get("title") or "").strip()
        if not title:
            continue

        source_id = repo.insert_context_pack_source(
            conn,
            {
                "pack_id": pack_id,
                "title": title,
                "source_type": source.get("type") or source.get("source_type") or "自定义资料",
                "ref_type": source.get("ref_type") or "custom",
                "ref_id": source.get("ref_id"),
                "content": source.get("content") or "",
                "weight": source.get("weight") or "中",
                "status": source.get("status") or "已收集",
            },
        )
        if source_id:
            refresh_source_chunks(conn, source_id)
        added += 1

    return added


def add_sources_to_pack(conn, pack_id, article_ids, sources):
    article_result = add_article_sources(conn, pack_id, article_ids)
    custom_added = add_custom_sources(conn, pack_id, sources)
    return article_result, custom_added, article_result["added"] + custom_added


def refresh_pack_metrics(conn, pack_id):
    sources = repo.fetch_sources(conn, pack_id)
    pack_row = repo.fetch_pack_metric_row(conn, pack_id)
    if not pack_row:
        return

    quality = compute_pack_quality(
        len(sources),
        bool(pack_row.get("intent")),
        bool(pack_row.get("summary")),
        len(json_loads(pack_row.get("tags"), [])),
    )
    token_budget = estimate_token_budget(sources)
    freshness = "刚刚" if sources else "待补充"
    repo.update_pack_metrics(conn, pack_id, quality, token_budget, freshness)


def create_context_pack_record(conn, data, user_id):
    tags = normalize_tags(data.get("tags") or [])
    pack_id = repo.insert_context_pack(
        conn,
        {
            "name": (data.get("name") or "").strip(),
            "type": data.get("type") or "project",
            "stage": data.get("stage") or "Draft",
            "description": data.get("description") or "",
            "intent": data.get("intent") or "",
            "summary": data.get("summary") or "",
            "next_action": data.get("nextAction") or data.get("next_action") or "",
            "key_points": json_dumps(data.get("keyPoints") or []),
            "tags": json_dumps(tags),
            "user_id": user_id,
        },
    )
    add_article_sources(conn, pack_id, data.get("article_ids") or [])
    add_custom_sources(conn, pack_id, data.get("sources") or [])
    refresh_pack_metrics(conn, pack_id)
    return pack_id


def update_context_pack_fields(conn, pack_id, data):
    allowed_fields = {
        "name": "name",
        "type": "type",
        "stage": "stage",
        "description": "description",
        "intent": "intent",
        "summary": "summary",
        "nextAction": "next_action",
        "next_action": "next_action",
    }

    fields = {}
    for incoming, column in allowed_fields.items():
        if incoming in data:
            fields[column] = data[incoming]

    if "keyPoints" in data:
        fields["key_points"] = json_dumps(data["keyPoints"])
    if "tags" in data:
        fields["tags"] = json_dumps(normalize_tags(data["tags"]))

    if not fields:
        return False

    repo.update_context_pack(conn, pack_id, fields)
    refresh_pack_metrics(conn, pack_id)
    return True


def delete_context_pack_record(conn, pack_id):
    repo.delete_context_pack(conn, pack_id)


def delete_context_pack_source_record(conn, pack_id, source_id):
    repo.delete_context_pack_source(conn, pack_id, source_id)
    refresh_pack_metrics(conn, pack_id)


def build_markdown(pack):
    lines = [
        f"# {pack['name']}",
        "",
        f"类型：{pack.get('type')}",
        f"阶段：{pack.get('stage')}",
        f"质量：{pack.get('quality')}%",
        f"Token 预算：{pack.get('tokenBudget')}",
    ]

    if pack.get("intent"):
        lines.extend(["", "## 目标", pack["intent"]])

    if pack.get("summary"):
        lines.extend(["", "## AI 洞察摘要", pack["summary"]])

    if pack.get("keyPoints"):
        lines.extend(["", "## 关键线索"])
        lines.extend([f"- {point}" for point in pack["keyPoints"]])

    if pack.get("sources"):
        lines.extend(["", "## 来源"])
        for index, source in enumerate(pack["sources"], start=1):
            lines.extend([
                "",
                f"### {index}. {source['title']}",
                "",
                f"- 类型：{source.get('type')}",
                f"- 权重：{source.get('weight')}",
                f"- 状态：{source.get('status')}",
            ])
            source_content = normalize_source_content(source.get("content"))
            if source_content:
                lines.extend(["", source_content])

    if pack.get("tags"):
        lines.extend(["", "## 标签", " ".join([f"#{tag}" for tag in pack["tags"]])])

    return "\n".join(lines)


def build_prompt(markdown):
    return "\n".join([
        "你是一个严谨的 AI 协作助手。请只基于下面的上下文包回答用户问题。",
        "如果上下文里没有足够依据，请先说明缺口，再给出需要补充的资料清单。",
        "回答时保留关键来源，不要编造不存在的事实。",
        "",
        "用户问题：",
        "（在这里补充你的具体问题）",
        "",
        "上下文包：",
        markdown,
    ])


def build_workspace_stats(conn, user=None, can_view_pack=None):
    pack_rows = repo.fetch_real_pack_rows(conn)
    if can_view_pack:
        pack_rows = [row for row in pack_rows if can_view_pack(user, row)]
    pack_ids = [row["id"] for row in pack_rows]

    latest_updated_at = None
    for row in pack_rows:
        updated_at = row.get("updated_at")
        if updated_at and (latest_updated_at is None or updated_at > latest_updated_at):
            latest_updated_at = updated_at

    return {
        "packs": len(pack_rows),
        "sources": repo.count_sources_for_pack_ids(conn, pack_ids),
        "articles": repo.count_articles(conn),
        "latest_updated_at": latest_updated_at.isoformat() if latest_updated_at else "",
    }
