from database import engine
from db.schema import ensure_context_pack_tables
from services.context_pack_service import create_embedding, get_embedding_config, get_pack_chunks, get_pack_or_404
from services.rag_utils import (
    MAX_RAG_SNIPPETS,
    build_pack_profile,
    clamp_context_token_budget,
    cosine_similarity,
    estimate_tokens,
    extract_query_terms,
    is_pack_overview_query,
    parse_embedding,
    score_chunk,
    source_weight_score,
)


def retrieve_context_pack_snippets(
    context_pack_id,
    query,
    token_budget=None,
    max_snippets=MAX_RAG_SNIPPETS,
    allow_embedding=True,
    user=None,
    can_view_pack=None,
):
    if not context_pack_id:
        return "", None, None, None

    try:
        pack_id = int(context_pack_id)
    except (TypeError, ValueError):
        return "", None, None, "上下文包 ID 无效"

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            pack_chunks = get_pack_chunks(conn, pack_id) if pack else []
            embedding_config = get_embedding_config(conn)
    except Exception as exc:
        return "", None, None, f"读取上下文包失败：{exc}"

    if not pack:
        return "", None, None, "上下文包不存在"

    if can_view_pack and not can_view_pack(user, pack):
        return "", None, None, "无权访问该上下文包"

    budget = clamp_context_token_budget(token_budget)
    query_terms = extract_query_terms(query)
    candidates = []
    query_embedding = None
    retrieval_mode = "keyword"
    embedding_configured = bool(embedding_config.get("configured"))
    active_embedding_model = embedding_config.get("model") if embedding_configured else ""
    embedded_chunks = sum(1 for chunk_row in pack_chunks if chunk_row.get("embedding"))
    current_model_embedded_chunks = sum(
        1
        for chunk_row in pack_chunks
        if chunk_row.get("embedding") and active_embedding_model and chunk_row.get("embedding_model") == active_embedding_model
    )
    semantic_unavailable_reason = ""

    if allow_embedding and (query or "").strip():
        if not embedding_configured:
            semantic_unavailable_reason = "embedding_not_configured"
        elif not current_model_embedded_chunks:
            semantic_unavailable_reason = "no_current_model_embeddings"
        else:
            try:
                query_embedding = create_embedding(query or "", embedding_config)
                if query_embedding:
                    retrieval_mode = "semantic"
                else:
                    semantic_unavailable_reason = "query_embedding_not_created"
            except Exception as exc:
                semantic_unavailable_reason = "query_embedding_failed"
                print(f"Embedding retrieval fallback to keyword: {exc}")
    elif allow_embedding and not (query or "").strip():
        semantic_unavailable_reason = "empty_query"
    elif not allow_embedding:
        semantic_unavailable_reason = "semantic_not_requested"

    if query_embedding and not semantic_unavailable_reason:
        try:
            first_chunk_embedding = next(
                (
                    parse_embedding(chunk_row.get("embedding"))
                    for chunk_row in pack_chunks
                    if chunk_row.get("embedding") and chunk_row.get("embedding_model") == active_embedding_model
                ),
                None,
            )
            if first_chunk_embedding and len(first_chunk_embedding) != len(query_embedding):
                query_embedding = None
                retrieval_mode = "keyword"
                semantic_unavailable_reason = "embedding_dimension_mismatch"
        except Exception as exc:
            query_embedding = None
            retrieval_mode = "keyword"
            semantic_unavailable_reason = "embedding_validation_failed"
            print(f"Embedding retrieval fallback to keyword: {exc}")

    for chunk_row in pack_chunks:
        source = {
            "title": chunk_row.get("title"),
            "weight": chunk_row.get("weight"),
        }
        chunk = chunk_row.get("content") or ""
        score = score_chunk(query_terms, source, chunk)
        if query_embedding and chunk_row.get("embedding_model") == active_embedding_model:
            chunk_embedding = parse_embedding(chunk_row.get("embedding"))
            semantic_score = max(cosine_similarity(query_embedding, chunk_embedding), 0) * 100
            if semantic_score > 0:
                score += semantic_score * source_weight_score(source.get("weight"))
        if score <= 0:
            continue
        candidates.append({
            "source_id": chunk_row.get("source_id"),
            "source_ref_type": chunk_row.get("ref_type"),
            "source_ref_id": chunk_row.get("ref_id"),
            "title": chunk_row.get("title") or "未命名资料",
            "type": chunk_row.get("source_type") or "资料",
            "weight": chunk_row.get("weight") or "中",
            "chunk_index": chunk_row.get("chunk_index"),
            "content": chunk,
            "score": round(score, 2),
            "retrieval_mode": retrieval_mode,
            "tokens_estimate": chunk_row.get("tokens_estimate") or estimate_tokens(chunk),
        })

    if not candidates and is_pack_overview_query(query):
        seen_sources = set()
        for chunk_row in pack_chunks:
            if chunk_row.get("source_id") in seen_sources:
                continue
            seen_sources.add(chunk_row.get("source_id"))
            chunk = chunk_row.get("content") or ""
            candidates.append({
                "source_id": chunk_row.get("source_id"),
                "source_ref_type": chunk_row.get("ref_type"),
                "source_ref_id": chunk_row.get("ref_id"),
                "title": chunk_row.get("title") or "未命名资料",
                "type": chunk_row.get("source_type") or "资料",
                "weight": chunk_row.get("weight") or "中",
                "chunk_index": chunk_row.get("chunk_index"),
                "content": chunk,
                "score": round(0.1 * source_weight_score(chunk_row.get("weight")), 2),
                "retrieval_mode": retrieval_mode,
                "tokens_estimate": chunk_row.get("tokens_estimate") or estimate_tokens(chunk),
            })

    candidates.sort(key=lambda item: (item["score"], item["tokens_estimate"] * -1), reverse=True)

    selected = []
    used_tokens = estimate_tokens(build_pack_profile(pack))
    seen_source_ids = set()

    for candidate in candidates:
        if len(selected) >= max_snippets:
            break
        candidate_tokens = candidate["tokens_estimate"]
        if used_tokens + candidate_tokens > budget:
            continue
        if candidate["source_id"] in seen_source_ids and len(seen_source_ids) < min(len(pack.get("sources") or []), max_snippets):
            continue
        selected.append(candidate)
        used_tokens += candidate_tokens
        seen_source_ids.add(candidate["source_id"])

    if len(selected) < max_snippets:
        selected_keys = {(item["source_id"], item["chunk_index"]) for item in selected}
        for candidate in candidates:
            if len(selected) >= max_snippets:
                break
            key = (candidate["source_id"], candidate["chunk_index"])
            if key in selected_keys:
                continue
            candidate_tokens = candidate["tokens_estimate"]
            if used_tokens + candidate_tokens > budget:
                continue
            selected.append(candidate)
            selected_keys.add(key)
            used_tokens += candidate_tokens

    retrieval_label = "语义 RAG" if retrieval_mode == "semantic" else "关键词 RAG"
    context_lines = [
        "当前用户选择了上下文包，但本轮不会注入全量内容。",
        "你只能优先使用下面经过检索命中的片段回答；如果片段不足以支持结论，请明确说明缺口。",
        "回答中引用片段时使用 [S1]、[S2] 这样的编号，方便用户追溯来源。",
        "",
        "## 上下文包概况",
        build_pack_profile(pack),
        "",
        f"## 本轮检索结果（{retrieval_label}，预算约 {budget} tokens）",
    ]

    if selected:
        for index, item in enumerate(selected, start=1):
            item["id"] = f"S{index}"
            context_lines.extend([
                "",
                f"[S{index}] {item['title']}",
                f"- 类型：{item['type']}",
                f"- 权重：{item['weight']}",
                f"- 相关度：{item['score']}",
                "",
                item["content"],
            ])
    else:
        context_lines.extend([
            "",
            "没有检索到与用户问题明显相关的资料片段。",
            "请不要假装已经看到了上下文包全文；如果需要回答，只能说明资料缺口并建议用户补充或换一种问法。",
        ])

    retrieval = {
        "mode": retrieval_mode,
        "embedding_used": bool(query_embedding),
        "semantic_requested": bool(allow_embedding),
        "semantic_available": bool(query_embedding),
        "semantic_unavailable_reason": "" if query_embedding else semantic_unavailable_reason,
        "embedding_configured": embedding_configured,
        "embedding_model": active_embedding_model,
        "embedded_chunks": embedded_chunks,
        "current_model_embedded_chunks": current_model_embedded_chunks,
        "token_budget": budget,
        "used_tokens_estimate": used_tokens,
        "indexed_chunks": len(pack_chunks),
        "snippets": [
            {
                "id": item.get("id"),
                "source_id": item.get("source_id"),
                "source_ref_type": item.get("source_ref_type"),
                "source_ref_id": item.get("source_ref_id"),
                "title": item.get("title"),
                "type": item.get("type"),
                "score": item.get("score"),
                "retrieval_mode": item.get("retrieval_mode"),
                "tokens_estimate": item.get("tokens_estimate"),
                "content_preview": item.get("content", "")[:220],
            }
            for item in selected
        ],
        "query_terms": query_terms[:20],
        "truncated": len(candidates) > len(selected),
    }

    return "\n".join(context_lines), pack, retrieval, None


def build_effective_system_prompt(
    base_prompt,
    context_pack_id,
    query=None,
    token_budget=None,
    allow_embedding=True,
    user=None,
    can_view_pack=None,
):
    context_prompt, pack, retrieval, error = retrieve_context_pack_snippets(
        context_pack_id,
        query,
        token_budget,
        allow_embedding=allow_embedding,
        user=user,
        can_view_pack=can_view_pack,
    )
    if error:
        return None, None, None, error

    if context_prompt:
        return f"{base_prompt or 'You are a helpful assistant.'}\n\n{context_prompt}", pack, retrieval, None

    return base_prompt or "You are a helpful assistant.", None, None, None
