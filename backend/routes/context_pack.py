from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import bindparam, text
from openai import OpenAI
import hashlib
import json
import jwt
import math
import os
import re
import html

from database import engine


context_pack_bp = Blueprint("context_pack", __name__)

LEGACY_DEMO_PACKS = {
    "Vercel + Railway 部署上下文包": "沉淀前端 Vercel",
    "毕业答辩 AI 表达包": "把项目需求",
}


def json_dumps(value):
    return json.dumps(value or [], ensure_ascii=False)


def json_loads(value, fallback=None):
    if fallback is None:
        fallback = []
    if not value:
        return fallback
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return fallback


def get_optional_user_id():
    user, _ = get_request_user(required=False)
    return user.get("id") if user else None


def get_request_user(required=False):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        if required:
            return None, (jsonify({"status": 1, "msg": "请先登录后再操作上下文包"}), 401)
        return None, None

    try:
        token = auth_header.split(" ", 1)[1] if auth_header.startswith("Bearer ") else auth_header
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("missing user_id")

        with engine.connect() as conn:
            user = conn.execute(
                text("SELECT id, username, role, role_id FROM users WHERE id = :id"),
                {"id": user_id},
            ).mappings().fetchone()
            if not user:
                raise ValueError("user not found")

            permissions = []
            if user.get("role_id"):
                permissions = list(conn.execute(text("""
                    SELECT p.code FROM permissions p
                    JOIN role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id = :rid
                """), {"rid": user["role_id"]}).scalars().all())

        user_data = dict(user)
        user_data["permissions"] = permissions
        return user_data, None
    except Exception as exc:
        if required:
            return None, (jsonify({"status": 1, "msg": "登录状态无效，请重新登录", "error": str(exc)}), 401)
        return None, None


def is_admin_user(user):
    if not user:
        return False
    permissions = set(user.get("permissions") or [])
    return user.get("role") == "admin" or "user:manage" in permissions or "context_pack:manage" in permissions


def can_view_pack(user, pack):
    if not pack:
        return False
    owner_id = pack.get("user_id")
    if owner_id is None:
        return True
    return bool(user and (is_admin_user(user) or int(owner_id) == int(user["id"])))


def can_manage_pack(user, pack):
    if not pack or not user:
        return False
    if is_admin_user(user):
        return True
    owner_id = pack.get("user_id")
    return owner_id is not None and int(owner_id) == int(user["id"])


def require_pack_access(pack, user, manage=False):
    allowed = can_manage_pack(user, pack) if manage else can_view_pack(user, pack)
    if allowed:
        return None
    return jsonify({"status": 1, "msg": "无权操作该上下文包"}), 403


def ensure_context_pack_tables(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_packs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            type VARCHAR(50) DEFAULT 'project',
            stage VARCHAR(50) DEFAULT 'Draft',
            description TEXT,
            intent TEXT,
            summary TEXT,
            next_action TEXT,
            key_points LONGTEXT,
            tags LONGTEXT,
            quality INT DEFAULT 40,
            token_budget VARCHAR(40) DEFAULT '0.8k',
            freshness VARCHAR(40) DEFAULT '刚刚',
            user_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_pack_sources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pack_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            source_type VARCHAR(80) DEFAULT '文档',
            ref_type VARCHAR(80) DEFAULT 'custom',
            ref_id INT NULL,
            content LONGTEXT,
            weight VARCHAR(20) DEFAULT '中',
            status VARCHAR(40) DEFAULT '已收集',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pack_id) REFERENCES context_packs(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_pack_source_chunks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            source_id INT NOT NULL,
            pack_id INT NOT NULL,
            chunk_index INT NOT NULL,
            content LONGTEXT NOT NULL,
            tokens_estimate INT DEFAULT 0,
            content_hash CHAR(64) NOT NULL,
            embedding LONGTEXT NULL,
            embedding_provider VARCHAR(80) NULL,
            embedding_model VARCHAR(160) NULL,
            embedding_dimension INT DEFAULT 0,
            embedded_at TIMESTAMP NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uniq_source_chunk (source_id, chunk_index),
            INDEX idx_pack_chunks (pack_id),
            FOREIGN KEY (source_id) REFERENCES context_pack_sources(id) ON DELETE CASCADE,
            FOREIGN KEY (pack_id) REFERENCES context_packs(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    ensure_chunk_embedding_columns(conn)
    ensure_embedding_config_table(conn)


def ensure_chunk_embedding_columns(conn):
    rows = conn.execute(
        text("""
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'context_pack_source_chunks'
        """)
    ).mappings().fetchall()
    columns = {row["COLUMN_NAME"] for row in rows}
    column_sql = {
        "embedding": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding LONGTEXT NULL",
        "embedding_provider": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding_provider VARCHAR(80) NULL",
        "embedding_model": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding_model VARCHAR(160) NULL",
        "embedding_dimension": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding_dimension INT DEFAULT 0",
        "embedded_at": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedded_at TIMESTAMP NULL",
    }

    for column, sql in column_sql.items():
        if column not in columns:
            conn.execute(text(sql))


def ensure_embedding_config_table(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ai_embedding_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provider VARCHAR(80) DEFAULT 'openai',
            api_key TEXT,
            base_url VARCHAR(255),
            model VARCHAR(160) NOT NULL,
            enabled TINYINT DEFAULT 0,
            is_active TINYINT DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))


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
    if not text_value:
        return 0
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text_value))
    other_chars = max(len(text_value) - cjk_chars, 0)
    return max(1, math.ceil(cjk_chars / 1.6 + other_chars / 4))


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
        row = conn.execute(
            text("SELECT * FROM ai_embedding_configs WHERE is_active = 1 ORDER BY updated_at DESC, id DESC LIMIT 1")
        ).mappings().fetchone()
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


def create_embedding(text_value, config=None):
    settings = config or get_embedding_config()
    if not settings["configured"]:
        return None

    client_kwargs = {"api_key": settings["api_key"]}
    if settings["base_url"]:
        client_kwargs["base_url"] = settings["base_url"]

    client = OpenAI(**client_kwargs)
    response = client.embeddings.create(
        model=settings["model"],
        input=(text_value or "")[:8000],
    )
    return response.data[0].embedding


def serialize_embedding(vector):
    return json.dumps(vector or [], ensure_ascii=False, separators=(",", ":"))


def parse_embedding(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        vector = json.loads(value)
    except Exception:
        return []
    return vector if isinstance(vector, list) else []


def cosine_similarity(left, right):
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for left_value, right_value in zip(left, right):
        dot += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value

    if not left_norm or not right_norm:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)


def split_source_into_chunks(content, max_chars=900, overlap=120):
    content = normalize_source_content(content)
    if not content:
        return []

    paragraphs = [item.strip() for item in re.split(r"\n{2,}", content) if item.strip()]
    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                chunk = paragraph[start:start + max_chars].strip()
                if chunk:
                    chunks.append(chunk)
                start += max_chars - overlap
            continue

        next_text = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(next_text) > max_chars and current:
            chunks.append(current.strip())
            current = paragraph
        else:
            current = next_text

    if current:
        chunks.append(current.strip())

    return chunks


def refresh_source_chunks(conn, source_id):
    source = conn.execute(
        text("SELECT id, pack_id, title, content FROM context_pack_sources WHERE id = :id"),
        {"id": source_id},
    ).mappings().fetchone()
    if not source:
        return 0

    chunks = split_source_into_chunks(source.get("content") or "")
    if not chunks and source.get("title"):
        chunks = [source.get("title")]

    conn.execute(text("DELETE FROM context_pack_source_chunks WHERE source_id = :source_id"), {"source_id": source_id})
    for chunk_index, chunk in enumerate(chunks):
        conn.execute(
            text("""
                INSERT INTO context_pack_source_chunks
                    (source_id, pack_id, chunk_index, content, tokens_estimate, content_hash)
                VALUES
                    (:source_id, :pack_id, :chunk_index, :content, :tokens_estimate, :content_hash)
            """),
            {
                "source_id": source["id"],
                "pack_id": source["pack_id"],
                "chunk_index": chunk_index,
                "content": chunk,
                "tokens_estimate": estimate_chunk_tokens(chunk),
                "content_hash": hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
            },
        )

    return len(chunks)


def sync_pack_chunks(conn, pack_id):
    source_rows = conn.execute(
        text("""
            SELECT s.id
            FROM context_pack_sources s
            LEFT JOIN context_pack_source_chunks c ON c.source_id = s.id
            WHERE s.pack_id = :pack_id
            GROUP BY s.id
            HAVING COUNT(c.id) = 0
        """),
        {"pack_id": pack_id},
    ).mappings().fetchall()

    created = 0
    for row in source_rows:
        created += refresh_source_chunks(conn, row["id"])
    return created


def rebuild_pack_chunks(conn, pack_id):
    conn.execute(
        text("DELETE FROM context_pack_source_chunks WHERE pack_id = :pack_id"),
        {"pack_id": pack_id},
    )
    source_rows = conn.execute(
        text("SELECT id FROM context_pack_sources WHERE pack_id = :pack_id ORDER BY id"),
        {"pack_id": pack_id},
    ).mappings().fetchall()

    chunk_count = 0
    for row in source_rows:
        chunk_count += refresh_source_chunks(conn, row["id"])

    return get_pack_index_stats(conn, pack_id)


def get_pack_index_stats(conn, pack_id):
    embedding_config = get_embedding_config(conn)
    active_model = embedding_config["model"] if embedding_config["configured"] else ""
    row = conn.execute(
        text("""
            SELECT
                COUNT(DISTINCT s.id) AS sources,
                COUNT(DISTINCT c.source_id) AS indexed_sources,
                COUNT(c.id) AS chunks,
                SUM(CASE WHEN c.embedding IS NOT NULL AND c.embedding != '' THEN 1 ELSE 0 END) AS embedded_chunks,
                SUM(CASE WHEN :active_model != '' AND c.embedding IS NOT NULL AND c.embedding != '' AND c.embedding_model = :active_model THEN 1 ELSE 0 END) AS current_model_embedded_chunks,
                SUM(CASE WHEN :active_model != '' AND c.embedding IS NOT NULL AND c.embedding != '' AND COALESCE(c.embedding_model, '') != :active_model THEN 1 ELSE 0 END) AS stale_embedding_chunks,
                SUM(CASE
                    WHEN c.id IS NOT NULL AND (
                        (:active_model != '' AND (c.embedding IS NULL OR c.embedding = '' OR COALESCE(c.embedding_model, '') != :active_model))
                        OR (:active_model = '' AND (c.embedding IS NULL OR c.embedding = ''))
                    )
                    THEN 1 ELSE 0
                END) AS pending_embedding_chunks,
                COALESCE(SUM(c.tokens_estimate), 0) AS tokens_estimate,
                COALESCE(SUM(CASE
                    WHEN c.id IS NOT NULL AND (
                        (:active_model != '' AND (c.embedding IS NULL OR c.embedding = '' OR COALESCE(c.embedding_model, '') != :active_model))
                        OR (:active_model = '' AND (c.embedding IS NULL OR c.embedding = ''))
                    )
                    THEN c.tokens_estimate ELSE 0
                END), 0) AS pending_embedding_tokens_estimate,
                MAX(c.updated_at) AS latest_updated_at
            FROM context_pack_sources s
            LEFT JOIN context_pack_source_chunks c ON c.source_id = s.id
            WHERE s.pack_id = :pack_id
        """),
        {"pack_id": pack_id, "active_model": active_model},
    ).mappings().fetchone()

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

    rows = conn.execute(
        text("""
            SELECT id, content, tokens_estimate, embedding, embedding_model
            FROM context_pack_source_chunks
            WHERE pack_id = :pack_id
            ORDER BY id
        """),
        {"pack_id": pack_id},
    ).mappings().fetchall()

    generated = 0
    skipped = 0
    failed = 0
    planned = 0
    planned_tokens = 0

    for row in rows:
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
            conn.execute(
                text("""
                    UPDATE context_pack_source_chunks
                    SET embedding = :embedding,
                        embedding_provider = :provider,
                        embedding_model = :model,
                        embedding_dimension = :dimension,
                        embedded_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {
                    "id": row["id"],
                    "embedding": serialize_embedding(vector),
                    "provider": embedding_config["provider"],
                    "model": embedding_config["model"],
                    "dimension": len(vector),
                },
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
    rows = conn.execute(
        text("""
            SELECT
                c.id,
                c.source_id,
                c.chunk_index,
                c.content,
                c.tokens_estimate,
                c.embedding,
                c.embedding_provider,
                c.embedding_model,
                c.embedding_dimension,
                c.embedded_at,
                s.title,
                s.source_type,
                s.ref_type,
                s.ref_id,
                s.weight,
                s.status
            FROM context_pack_source_chunks c
            JOIN context_pack_sources s ON s.id = c.source_id
            WHERE c.pack_id = :pack_id
            ORDER BY c.source_id, c.chunk_index
        """),
        {"pack_id": pack_id},
    ).mappings().fetchall()
    return [dict(row) for row in rows]


def row_to_source(row):
    source = dict(row)
    if source.get("created_at"):
        source["created_at"] = source["created_at"].isoformat()
    source["type"] = source.pop("source_type", "文档")
    return source


def row_to_pack(row, sources=None):
    pack = dict(row)
    pack["keyPoints"] = json_loads(pack.pop("key_points", "[]"))
    pack["tags"] = json_loads(pack.get("tags"), [])
    pack["sources"] = sources or []
    pack["documents"] = [source["title"] for source in pack["sources"]]
    pack["nextAction"] = pack.pop("next_action", "")
    pack["tokenBudget"] = pack.pop("token_budget", "0.8k")
    if pack.get("created_at"):
        pack["created_at"] = pack["created_at"].isoformat()
    if pack.get("updated_at"):
        pack["updated_at"] = pack["updated_at"].isoformat()
    return pack


def fetch_sources(conn, pack_id):
    rows = conn.execute(
        text("SELECT * FROM context_pack_sources WHERE pack_id = :pack_id ORDER BY created_at DESC, id DESC"),
        {"pack_id": pack_id},
    ).mappings().fetchall()
    return [row_to_source(row) for row in rows]


def get_pack_or_404(conn, pack_id):
    row = conn.execute(
        text("SELECT * FROM context_packs WHERE id = :id"),
        {"id": pack_id},
    ).mappings().fetchone()
    if row and is_legacy_demo_pack(row):
        return None
    return row_to_pack(row, fetch_sources(conn, pack_id)) if row else None


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

    article_query = text("""
            SELECT id, title, content, summary, category
            FROM articles
            WHERE id IN :ids
        """).bindparams(bindparam("ids", expanding=True))
    rows = conn.execute(article_query, {"ids": normalized_ids}).mappings().fetchall()

    existing_query = text("""
            SELECT ref_id
            FROM context_pack_sources
            WHERE pack_id = :pack_id AND ref_type = 'article' AND ref_id IN :ids
        """).bindparams(bindparam("ids", expanding=True))
    existing_ids = {
        row["ref_id"]
        for row in conn.execute(existing_query, {"pack_id": pack_id, "ids": normalized_ids}).mappings().fetchall()
    }

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
        result = conn.execute(
            text("""
                INSERT INTO context_pack_sources
                    (pack_id, title, source_type, ref_type, ref_id, content, weight, status)
                VALUES
                    (:pack_id, :title, :source_type, 'article', :ref_id, :content, '高', '已接入')
            """),
            {
                "pack_id": pack_id,
                "title": row["title"],
                "source_type": row.get("category") or "知识库文章",
                "ref_id": row["id"],
                "content": content,
            },
        )
        source_id = result.lastrowid or conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
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

        result = conn.execute(
            text("""
                INSERT INTO context_pack_sources
                    (pack_id, title, source_type, ref_type, ref_id, content, weight, status)
                VALUES
                    (:pack_id, :title, :source_type, :ref_type, :ref_id, :content, :weight, :status)
            """),
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
        source_id = result.lastrowid or conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        if source_id:
            refresh_source_chunks(conn, source_id)
        added += 1

    return added


def refresh_pack_metrics(conn, pack_id):
    sources = fetch_sources(conn, pack_id)
    pack_row = conn.execute(
        text("SELECT intent, summary, tags FROM context_packs WHERE id = :id"),
        {"id": pack_id},
    ).mappings().fetchone()
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

    conn.execute(
        text("""
            UPDATE context_packs
            SET quality = :quality, token_budget = :token_budget, freshness = :freshness
            WHERE id = :id
        """),
        {"quality": quality, "token_budget": token_budget, "freshness": freshness, "id": pack_id},
    )


def normalize_source_content(content):
    if not content:
        return ""

    text_content = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.I | re.S)
    text_content = re.sub(r"<br\s*/?>", "\n", text_content, flags=re.I)
    text_content = re.sub(r"</p\s*>", "\n", text_content, flags=re.I)
    text_content = re.sub(r"<[^>]+>", "", text_content)
    return html.unescape(re.sub(r"\n{3,}", "\n\n", text_content).strip())


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


def is_legacy_demo_pack(row):
    name = row.get("name")
    description = row.get("description") or ""
    return (
        row.get("user_id") is None
        and name in LEGACY_DEMO_PACKS
        and description.startswith(LEGACY_DEMO_PACKS[name])
    )


def fetch_real_pack_rows(conn, where_sql="", params=None):
    sql = f"SELECT * FROM context_packs WHERE 1=1 {where_sql} ORDER BY updated_at DESC, id DESC"
    rows = conn.execute(text(sql), params or {}).mappings().fetchall()
    return [row for row in rows if not is_legacy_demo_pack(row)]


def filter_visible_pack_rows(rows, user):
    return [row for row in rows if can_view_pack(user, row)]


def enrich_pack_access(pack, user):
    if not pack:
        return pack

    pack["visibility"] = "public" if pack.get("user_id") is None else "private"
    pack["canManage"] = can_manage_pack(user, pack)
    pack["canUseRag"] = can_view_pack(user, pack)
    return pack


def build_workspace_stats(conn, user=None):
    pack_rows = fetch_real_pack_rows(conn)
    pack_rows = filter_visible_pack_rows(pack_rows, user)
    pack_ids = [row["id"] for row in pack_rows]

    source_count = 0
    if pack_ids:
        source_query = text("""
            SELECT COUNT(*)
            FROM context_pack_sources
            WHERE pack_id IN :ids
        """).bindparams(bindparam("ids", expanding=True))
        source_count = conn.execute(source_query, {"ids": pack_ids}).scalar() or 0

    try:
        article_count = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar() or 0
    except Exception:
        article_count = 0

    latest_updated_at = None
    for row in pack_rows:
        updated_at = row.get("updated_at")
        if updated_at and (latest_updated_at is None or updated_at > latest_updated_at):
            latest_updated_at = updated_at

    return {
        "packs": len(pack_rows),
        "sources": source_count,
        "articles": article_count,
        "latest_updated_at": latest_updated_at.isoformat() if latest_updated_at else "",
    }


@context_pack_bp.route("/api/context-packs", methods=["GET"])
def list_context_packs():
    pack_type = request.args.get("type")
    search = request.args.get("search", "")

    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)

            where_sql = ""
            params = {}
            if pack_type and pack_type != "all":
                where_sql += " AND type = :type"
                params["type"] = pack_type
            if search:
                where_sql += " AND (name LIKE :search OR description LIKE :search OR intent LIKE :search)"
                params["search"] = f"%{search}%"

            rows = fetch_real_pack_rows(conn, where_sql, params)
            rows = filter_visible_pack_rows(rows, user)
            packs = [
                enrich_pack_access(row_to_pack(row, fetch_sources(conn, row["id"])), user)
                for row in rows
            ]

        return jsonify({"status": 0, "data": packs})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/stats", methods=["GET"])
def context_pack_stats():
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            stats = build_workspace_stats(conn, user)
        return jsonify({"status": 0, "data": stats})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取上下文包统计失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs", methods=["POST"])
def create_context_pack():
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"status": 1, "msg": "上下文包名称不能为空"}), 400

    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            result = conn.execute(
                text("""
                    INSERT INTO context_packs
                        (name, type, stage, description, intent, summary, next_action, key_points, tags, user_id)
                    VALUES
                        (:name, :type, :stage, :description, :intent, :summary, :next_action, :key_points, :tags, :user_id)
                """),
                {
                    "name": name,
                    "type": data.get("type") or "project",
                    "stage": data.get("stage") or "Draft",
                    "description": data.get("description") or "",
                    "intent": data.get("intent") or "",
                    "summary": data.get("summary") or "",
                    "next_action": data.get("nextAction") or data.get("next_action") or "",
                    "key_points": json_dumps(data.get("keyPoints") or []),
                    "tags": json_dumps(tags),
                    "user_id": user["id"],
                },
            )
            pack_id = result.lastrowid or conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            add_article_sources(conn, pack_id, data.get("article_ids") or [])
            add_custom_sources(conn, pack_id, data.get("sources") or [])
            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "上下文包已创建", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "创建上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>", methods=["GET"])
def get_context_pack(pack_id):
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)
        if not pack:
            return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
        access_error = require_pack_access(pack, user, manage=False)
        if access_error:
            return access_error
        return jsonify({"status": 0, "data": enrich_pack_access(pack, user)})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>", methods=["PUT"])
def update_context_pack(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
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

    update_parts = []
    params = {"id": pack_id}
    for incoming, column in allowed_fields.items():
        if incoming in data:
            update_parts.append(f"{column} = :{column}")
            params[column] = data[incoming]

    if "keyPoints" in data:
        update_parts.append("key_points = :key_points")
        params["key_points"] = json_dumps(data["keyPoints"])
    if "tags" in data:
        update_parts.append("tags = :tags")
        params["tags"] = json_dumps(data["tags"])

    if not update_parts:
        return jsonify({"status": 0, "msg": "无变更"})

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            conn.execute(text(f"UPDATE context_packs SET {', '.join(update_parts)} WHERE id = :id"), params)
            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "上下文包已更新", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "更新上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>", methods=["DELETE"])
def delete_context_pack(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            conn.execute(text("DELETE FROM context_packs WHERE id = :id"), {"id": pack_id})
            conn.commit()
        return jsonify({"status": 0, "msg": "上下文包已删除"})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "删除上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/rag-index", methods=["GET"])
def get_context_pack_rag_index(pack_id):
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404

            access_error = require_pack_access(pack, user, manage=False)
            if access_error:
                return access_error

            index_stats = get_pack_index_stats(conn, pack_id)

        return jsonify({"status": 0, "data": index_stats})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取 RAG 索引状态失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/rag-index/rebuild", methods=["POST"])
def rebuild_context_pack_rag_index(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404

            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error

            index_stats = rebuild_pack_chunks(conn, pack_id)
            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({
            "status": 0,
            "msg": "RAG 索引已重建",
            "data": {
                "pack": pack,
                "index": index_stats,
            },
        })
    except Exception as exc:
        return jsonify({"status": 1, "msg": "重建 RAG 索引失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/rag-index/embeddings", methods=["POST"])
def build_context_pack_embeddings(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    force = bool(data.get("force"))
    dry_run = bool(data.get("dry_run"))

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404

            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error

            sync_pack_chunks(conn, pack_id)
            index_stats, error = refresh_pack_embeddings(conn, pack_id, force=force, dry_run=dry_run)
            if error:
                conn.rollback()
                return jsonify({"status": 1, "msg": error}), 400

            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({
            "status": 0,
            "msg": "语义索引预估完成" if dry_run else "语义索引已生成",
            "data": {
                "pack": pack,
                "index": index_stats,
            },
        })
    except Exception as exc:
        return jsonify({"status": 1, "msg": "生成语义索引失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/sources", methods=["POST"])
@context_pack_bp.route("/api/context-packs/<int:pack_id>/articles", methods=["POST"])
def add_context_pack_sources(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    article_ids = data.get("article_ids") or []
    sources = data.get("sources") or []

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            article_result = add_article_sources(conn, pack_id, article_ids)
            custom_added = add_custom_sources(conn, pack_id, sources)
            total_added = article_result["added"] + custom_added

            if (article_ids or sources) and total_added == 0:
                conn.rollback()
                if article_ids and article_result["found"] == 0:
                    return jsonify({"status": 1, "msg": "选中的文章不存在或已被删除"}), 400
                if article_ids and article_result["duplicates"] > 0:
                    return jsonify({"status": 1, "msg": "选中的文章已经在上下文包中"}), 409
                return jsonify({"status": 1, "msg": "没有找到可加入的真实资料"}), 400

            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "资料已加入上下文包", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "加入资料失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-pack-sources", methods=["POST"])
def add_context_pack_sources_flat():
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    pack_id = data.get("pack_id")
    if not pack_id:
        return jsonify({"status": 1, "msg": "缺少上下文包 ID"}), 400

    try:
        pack_id = int(pack_id)
    except (TypeError, ValueError):
        return jsonify({"status": 1, "msg": "上下文包 ID 无效"}), 400

    request_data = {
        "article_ids": data.get("article_ids") or [],
        "sources": data.get("sources") or [],
    }

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            article_result = add_article_sources(conn, pack_id, request_data["article_ids"])
            custom_added = add_custom_sources(conn, pack_id, request_data["sources"])
            total_added = article_result["added"] + custom_added

            if (request_data["article_ids"] or request_data["sources"]) and total_added == 0:
                conn.rollback()
                if request_data["article_ids"] and article_result["found"] == 0:
                    return jsonify({"status": 1, "msg": "选中的文章不存在或已被删除"}), 400
                if request_data["article_ids"] and article_result["duplicates"] > 0:
                    return jsonify({"status": 1, "msg": "选中的文章已经在上下文包中"}), 409
                return jsonify({"status": 1, "msg": "没有找到可加入的真实资料"}), 400

            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "资料已加入上下文包", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "加入资料失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/sources/<int:source_id>", methods=["DELETE"])
def delete_context_pack_source(pack_id, source_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            conn.execute(
                text("DELETE FROM context_pack_sources WHERE id = :source_id AND pack_id = :pack_id"),
                {"source_id": source_id, "pack_id": pack_id},
            )
            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "资料已移除", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "移除资料失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/markdown", methods=["GET"])
def export_context_pack_markdown(pack_id):
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
        if not pack:
            return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
        access_error = require_pack_access(pack, user, manage=False)
        if access_error:
            return access_error

        markdown = build_markdown(pack)
        prompt = build_prompt(markdown)
        return jsonify({"status": 0, "data": {"markdown": markdown, "prompt": prompt}})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "导出上下文包失败", "error": str(exc)}), 500
