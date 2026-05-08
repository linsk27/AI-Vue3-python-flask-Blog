# routes/ai.py
from flask import Blueprint, request, jsonify, Response, stream_with_context
import os
from openai import OpenAI
from typing import Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine
from routes.context_pack import (
    can_view_pack,
    cosine_similarity,
    create_embedding,
    ensure_embedding_config_table,
    ensure_context_pack_tables,
    get_embedding_config,
    get_pack_chunks,
    get_pack_or_404,
    get_request_user,
    mask_secret,
    normalize_source_content,
    parse_embedding,
)
from middleware import permission_required
import json
import math
import re
from urllib.parse import urlparse

ai_bp = Blueprint('ai', __name__)

# 简单的内存上下文管理，后续可扩展为数据库存储
context_store: Dict[str, List[Dict]] = {}
context_meta: Dict[str, Dict] = {}

# AI配置管理类 - 废弃旧的单例模式，改为直接数据库操作
# 但保留 models 字典供前端参考
SUPPORTED_MODELS = {
    'volcano': {
        'name': '火山方舟',
        'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
        'models': ['ep-20260125005850-g97x2', 'doubao-seed-1-6-251015']
    },
    'deepseek': {
        'name': 'DeepSeek',
        'base_url': 'https://api.deepseek.com',
        'models': ['deepseek-chat']
    }
}

def get_active_ai_config():
    active_config = None
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM ai_configs WHERE is_active = 1 LIMIT 1")).mappings().fetchone()
            if result:
                active_config = dict(result)
    except Exception as e:
        print(f"Error fetching active config: {e}")

    if not active_config:
        active_config = {
            'provider': 'volcano',
            'api_key': os.environ.get('ARK_API_KEY', ''),
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'ep-20260125005850-g97x2',
            'system_prompt': 'You are a helpful assistant.'
        }

    return active_config

def format_sse_event(payload):
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

DEFAULT_CONTEXT_TOKEN_BUDGET = 2600
MAX_CONTEXT_TOKEN_BUDGET = 6000
MIN_CONTEXT_TOKEN_BUDGET = 800
MAX_RAG_SNIPPETS = 6
QUERY_STOP_TERMS = {
    "的", "了", "和", "是", "我", "你", "它", "在", "有", "把", "这", "那",
    "这个", "那个", "一下", "什么", "怎么", "如何", "请问", "可以", "帮我",
}
PACK_OVERVIEW_TERMS = {"总结", "概括", "梳理", "归纳", "介绍", "上下文包", "资料", "内容", "整体"}


def estimate_tokens(text_value):
    if not text_value:
        return 0
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text_value))
    other_chars = max(len(text_value) - cjk_chars, 0)
    return max(1, math.ceil(cjk_chars / 1.6 + other_chars / 4))


def clamp_context_token_budget(value):
    try:
        budget = int(value)
    except (TypeError, ValueError):
        budget = DEFAULT_CONTEXT_TOKEN_BUDGET
    return max(MIN_CONTEXT_TOKEN_BUDGET, min(MAX_CONTEXT_TOKEN_BUDGET, budget))


def extract_query_terms(query):
    text_value = (query or "").lower()
    words = re.findall(r"[a-z0-9_+#.-]{2,}", text_value)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", text_value)
    cjk_bigrams = ["".join(cjk_chars[index:index + 2]) for index in range(max(len(cjk_chars) - 1, 0))]
    terms = words + cjk_bigrams
    if not terms:
        terms = cjk_chars
    return list(dict.fromkeys([
        term
        for term in terms
        if term.strip() and term not in QUERY_STOP_TERMS and term not in PACK_OVERVIEW_TERMS
    ]))


def is_pack_overview_query(query):
    return any(term in (query or "") for term in PACK_OVERVIEW_TERMS)


def split_text_into_chunks(content, max_chars=900, overlap=120):
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


def source_weight_score(weight):
    return {
        "高": 1.35,
        "中": 1.0,
        "低": 0.75,
    }.get(weight or "中", 1.0)


def score_chunk(query_terms, source, chunk):
    title = (source.get("title") or "").lower()
    chunk_lower = (chunk or "").lower()

    if not query_terms:
        return 0

    score = 0.0
    for term in query_terms:
        if term in title:
            score += 8
        score += min(chunk_lower.count(term), 5)

    return score * source_weight_score(source.get("weight"))


def build_pack_profile(pack):
    profile_parts = [
        f"上下文包：{pack.get('name')}",
        f"类型：{pack.get('type') or '未设置'}",
        f"阶段：{pack.get('stage') or '未设置'}",
    ]
    if pack.get("intent"):
        profile_parts.append(f"目标：{pack.get('intent')}")
    if pack.get("summary"):
        profile_parts.append(f"摘要：{pack.get('summary')}")
    if pack.get("tags"):
        profile_parts.append("标签：" + "、".join(pack.get("tags") or []))
    return "\n".join(profile_parts)


def retrieve_context_pack_snippets(context_pack_id, query, token_budget=None, max_snippets=MAX_RAG_SNIPPETS, allow_embedding=True):
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

    user, auth_error = get_request_user(required=False)
    if not can_view_pack(user, pack):
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

    # 先让不同来源都有机会露出，再补充高分片段。
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


def build_effective_system_prompt(base_prompt, context_pack_id, query=None, token_budget=None):
    context_prompt, pack, retrieval, error = retrieve_context_pack_snippets(context_pack_id, query, token_budget)
    if error:
        return None, None, None, error

    if context_prompt:
        return f"{base_prompt or 'You are a helpful assistant.'}\n\n{context_prompt}", pack, retrieval, None

    return base_prompt or 'You are a helpful assistant.', None, None, None


def reset_user_context(user_id, context_key=""):
    context_store[user_id] = []
    context_meta[user_id] = {"context_pack_id": context_key}


def trim_context(user_id):
    if len(context_store[user_id]) > 18:
        context_store[user_id] = context_store[user_id][-18:]


@ai_bp.route('/api/ai/context-packs/<int:pack_id>/retrieve', methods=['POST'])
@permission_required('ai:access')
def preview_context_pack_retrieval(current_user_id, pack_id):
    data = request.get_json() or {}
    query = data.get('query') or ''
    context_prompt, pack, retrieval, error = retrieve_context_pack_snippets(
        pack_id,
        query,
        data.get('context_token_budget'),
        allow_embedding=bool(data.get('allow_embedding', False))
    )
    if error:
        status_code = 403 if '无权' in error or 'Permission' in error else 400
        return jsonify({'status': 1, 'msg': error}), status_code

    return jsonify({
        'status': 0,
        'msg': '检索成功',
        'data': {
            'pack': {
                'id': pack.get('id'),
                'name': pack.get('name')
            } if pack else None,
            'retrieval': retrieval,
            'prompt_tokens_estimate': estimate_tokens(context_prompt),
        }
    })

@ai_bp.route('/api/ai/chat', methods=['POST'])
@permission_required('ai:access')
def chat(current_user_id):
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')  # 默认用户ID，后续可从JWT中获取
    user_id = str(current_user_id)
    message = data.get('message')
    reset_context = data.get('reset_context', False)
    context_pack_id = data.get('context_pack_id')

    if reset_context and not message:
        reset_user_context(user_id, str(context_pack_id or ''))
        return jsonify({
            'status': 0,
            'msg': '上下文已重置',
            'data': {
                'context_length': 0,
                'context_pack': None
            }
        })

    # 优先使用参数中的配置，如果没有则查询数据库中启用的配置
    
    # 获取当前启用的配置
    active_config = None
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM ai_configs WHERE is_active = 1 LIMIT 1")).mappings().fetchone()
            if result:
                active_config = dict(result)
    except Exception as e:
        print(f"Error fetching active config: {e}")

    # 如果没有启用的配置，使用默认值
    if not active_config:
        # Fallback default
        active_config = {
            'provider': 'volcano',
            'api_key': os.environ.get('ARK_API_KEY', ''),
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'ep-20260125005850-g97x2',
            'system_prompt': 'You are a helpful assistant.'
        }
    
    model_provider = data.get('model_provider', active_config.get('provider'))
    model_name = data.get('model_name', active_config.get('model'))
    system_prompt = data.get('system_prompt', active_config.get('system_prompt'))
    api_key = active_config.get('api_key')
    base_url = active_config.get('base_url')
    effective_system_prompt, context_pack, retrieval, context_error = build_effective_system_prompt(
        system_prompt,
        context_pack_id,
        message,
        data.get('context_token_budget')
    )
    if context_error:
        return jsonify({'status': 1, 'msg': context_error}), 400
    context_key = str(context_pack.get('id')) if context_pack else ''

    temperature = data.get('temperature', 0.3)  # 降低temperature，减少随机性，加快响应
    max_tokens = data.get('max_tokens', 500)  # 限制最大token数，减少回复长度
    
    # 重置上下文
    if reset_context:
        reset_user_context(user_id, context_key)
        # 如果只重置上下文，不发送消息，直接返回成功
        if not message:
            return jsonify({
                'status': 0,
                'msg': '上下文已重置',
                'data': {
                    'context_length': 0,
                    'context_pack': {
                        'id': context_pack.get('id'),
                        'name': context_pack.get('name')
                    } if context_pack else None
                }
            })
    
    # 检查消息是否为空（非重置上下文时）
    if not message:
        return jsonify({'status': 1, 'msg': '消息不能为空'}), 400
    
    # 初始化或获取现有上下文
    if (
        user_id not in context_store
        or reset_context
        or context_meta.get(user_id, {}).get('context_pack_id', '') != context_key
    ):
        reset_user_context(user_id, context_key)

    request_messages = [
        {"role": "system", "content": effective_system_prompt},
        *context_store[user_id][-18:],
        {"role": "user", "content": message}
    ]
    
    try:
        # 检查API密钥是否存在
        if not api_key:
            return jsonify({'status': 1, 'msg': '未配置有效的 API Key，请联系管理员配置 AI'}), 400
        
        # 初始化OpenAI客户端
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        # 调用API
        response = client.chat.completions.create(
            model=model_name,
            messages=request_messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 提取AI回复
        assistant_reply = response.choices[0].message.content
        
        # 添加本轮真实对话到上下文，system/RAG 片段每轮动态构造，不长期保存
        context_store[user_id].append({"role": "user", "content": message})
        context_store[user_id].append({"role": "assistant", "content": assistant_reply})
        trim_context(user_id)
        
        return jsonify({
            'status': 0,
            'msg': '成功',
            'data': {
                'reply': assistant_reply,
                'context_length': len(context_store[user_id]),
                'model_used': model_name,
                'provider_used': model_provider,
                'context_pack': {
                    'id': context_pack.get('id'),
                    'name': context_pack.get('name')
                } if context_pack else None,
                'retrieval': retrieval
            }
        })
        
    except Exception as e:
        return jsonify({'status': 1, 'msg': f'请求失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/chat/stream', methods=['POST'])
@permission_required('ai:access')
def chat_stream(current_user_id):
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    user_id = str(current_user_id)
    message = data.get('message')
    reset_context = data.get('reset_context', False)
    context_pack_id = data.get('context_pack_id')

    if reset_context and not message:
        reset_user_context(user_id, str(context_pack_id or ''))
        return Response(format_sse_event({
            'type': 'done',
            'message': '上下文已重置',
            'context_length': 0,
            'context_pack': None
        }), mimetype='text/event-stream')

    active_config = get_active_ai_config()

    model_provider = data.get('model_provider', active_config.get('provider'))
    model_name = data.get('model_name', active_config.get('model'))
    system_prompt = data.get('system_prompt', active_config.get('system_prompt'))
    api_key = active_config.get('api_key')
    base_url = active_config.get('base_url')
    effective_system_prompt, context_pack, retrieval, context_error = build_effective_system_prompt(
        system_prompt,
        context_pack_id,
        message,
        data.get('context_token_budget')
    )
    context_key = str(context_pack.get('id')) if context_pack else ''
    temperature = data.get('temperature', 0.3)
    max_tokens = data.get('max_tokens', 500)

    def generate():
        if context_error:
            yield format_sse_event({'type': 'error', 'message': context_error})
            return

        if reset_context:
            reset_user_context(user_id, context_key)

        if reset_context and not message:
            yield format_sse_event({
                'type': 'done',
                'message': '上下文已重置',
                'context_length': 0,
                'model_used': model_name,
                'provider_used': model_provider,
                'context_pack': {
                    'id': context_pack.get('id'),
                    'name': context_pack.get('name')
                } if context_pack else None
            })
            return

        if not message:
            yield format_sse_event({'type': 'error', 'message': '消息不能为空'})
            return

        if not api_key:
            yield format_sse_event({'type': 'error', 'message': '未配置有效的 API Key，请联系管理员配置 AI'})
            return

        if (
            user_id not in context_store
            or reset_context
            or context_meta.get(user_id, {}).get('context_pack_id', '') != context_key
        ):
            reset_user_context(user_id, context_key)

        request_messages = [
            {"role": "system", "content": effective_system_prompt},
            *context_store[user_id][-18:],
            {"role": "user", "content": message}
        ]
        assistant_reply = ''

        try:
            client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )

            yield format_sse_event({
                'type': 'start',
                'model_used': model_name,
                'provider_used': model_provider,
                'context_pack': {
                    'id': context_pack.get('id'),
                    'name': context_pack.get('name')
                } if context_pack else None,
                'retrieval': retrieval
            })

            response = client.chat.completions.create(
                model=model_name,
                messages=request_messages,
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens
            )

            for chunk in response:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta.content
                if not delta:
                    continue

                assistant_reply += delta
                yield format_sse_event({
                    'type': 'delta',
                    'content': delta
                })

            context_store[user_id].append({"role": "user", "content": message})
            context_store[user_id].append({"role": "assistant", "content": assistant_reply})
            trim_context(user_id)

            yield format_sse_event({
                'type': 'done',
                'context_length': len(context_store[user_id]),
                'model_used': model_name,
                'provider_used': model_provider,
                'context_pack': {
                    'id': context_pack.get('id'),
                    'name': context_pack.get('name')
                } if context_pack else None,
                'retrieval': retrieval
            })
        except Exception as e:
            yield format_sse_event({'type': 'error', 'message': f'请求失败: {str(e)}'})

    headers = {
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    }
    return Response(stream_with_context(generate()), mimetype='text/event-stream', headers=headers)

def extract_json_text(value):
    text_value = (value or "").strip()
    fenced = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", text_value, re.IGNORECASE)
    candidate = fenced.group(1).strip() if fenced else text_value
    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate
    match = re.search(r"\{[\s\S]*\}", candidate)
    return match.group(0) if match else ""


def decode_jsonish_string(value):
    try:
        return json.loads(f'"{value}"')
    except Exception:
        return (
            value
            .replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace("\\r", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )


def read_jsonish_string_field(source, field):
    for key in [f'"{field}"', f"'{field}'"]:
        key_index = source.find(key)
        if key_index < 0:
            continue

        colon_index = source.find(":", key_index + len(key))
        if colon_index < 0:
            continue

        cursor = colon_index + 1
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1

        if cursor >= len(source) or source[cursor] not in ('"', "'"):
            continue

        quote = source[cursor]
        cursor += 1
        chars = []
        escaped = False

        while cursor < len(source):
            char = source[cursor]

            if escaped:
                chars.append(f"\\{char}")
                escaped = False
                cursor += 1
                continue

            if char == "\\":
                escaped = True
                cursor += 1
                continue

            if char == quote:
                rest = source[cursor + 1:]
                if re.match(r"\s*(,|\})", rest):
                    return decode_jsonish_string("".join(chars)).strip()

            chars.append(char)
            cursor += 1

    return ""


def read_jsonish_tags(source):
    match = re.search(r'["\']tags["\']\s*:\s*\[([\s\S]*?)\]', source)
    if not match:
        return []

    body = match.group(1)
    try:
        parsed = json.loads(f"[{body}]")
        if isinstance(parsed, list):
            return [str(tag).strip() for tag in parsed if str(tag).strip()]
    except Exception:
        pass

    return [tag.strip() for tag in re.findall(r'["\']([^"\']+)["\']', body) if tag.strip()]


def repair_article_payload(value):
    if not isinstance(value, str):
        return None

    candidate = extract_json_text(value) or value.strip()
    if not re.search(r'["\'](?:title|content|summary|category|tags)["\']\s*:', candidate):
        return None

    content = read_jsonish_string_field(candidate, "content")
    if not content:
        return None

    return {
        "title": read_jsonish_string_field(candidate, "title"),
        "content": content,
        "summary": read_jsonish_string_field(candidate, "summary"),
        "category": read_jsonish_string_field(candidate, "category"),
        "tags": read_jsonish_tags(candidate),
    }


def looks_like_article_json_envelope(value):
    return bool(isinstance(value, str) and value.strip().startswith("{") and re.search(r'["\']content["\']\s*:', value))


def normalize_article_payload(raw_content, topic):
    article_data = None

    for candidate in [extract_json_text(raw_content), raw_content]:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate.strip())
            if isinstance(parsed, dict):
                article_data = parsed
                break
        except Exception:
            continue

    if article_data is None:
        article_data = repair_article_payload(raw_content)

    if article_data is None:
        if looks_like_article_json_envelope(raw_content):
            raise ValueError("AI 返回了无法解析的 JSON 外壳")
        article_data = {
            "title": topic[:28],
            "content": raw_content.strip(),
            "summary": "",
            "category": "other",
            "tags": ["AI生成"],
        }

    nested_content = article_data.get("content")
    if isinstance(nested_content, str):
        nested_data = None
        for candidate in [extract_json_text(nested_content), nested_content]:
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate.strip())
                if isinstance(parsed, dict) and (parsed.get("content") or parsed.get("title")):
                    nested_data = parsed
                    break
            except Exception:
                continue
        if nested_data is None:
            nested_data = repair_article_payload(nested_content)
        if nested_data:
            article_data.update({key: value for key, value in nested_data.items() if value})

    content = article_data.get("content")
    if not isinstance(content, str):
        raise ValueError("AI 返回的 content 不是文本")

    content = decode_jsonish_string(content).strip()
    repaired_content = repair_article_payload(content)
    if repaired_content:
        article_data.update({key: value for key, value in repaired_content.items() if value})
        content = repaired_content["content"].strip()

    if not content or looks_like_article_json_envelope(content):
        raise ValueError("AI 返回的正文仍是 JSON 外壳")

    allowed_categories = {"frontend", "backend", "database", "algorithm", "devops", "architecture", "ai", "other"}
    title = article_data.get("title") if isinstance(article_data.get("title"), str) else ""
    summary = article_data.get("summary") if isinstance(article_data.get("summary"), str) else ""
    category = article_data.get("category") if article_data.get("category") in allowed_categories else "other"
    tags = article_data.get("tags") if isinstance(article_data.get("tags"), list) else []
    tags = [str(tag).strip() for tag in tags if str(tag).strip()][:6]

    return {
        "title": title.strip() or topic[:28],
        "content": content,
        "summary": summary.strip() or content[:150].replace("\n", " ") + "...",
        "category": category,
        "tags": tags or ["AI生成"],
    }


@ai_bp.route('/api/ai/generate-article', methods=['POST'])
@permission_required('ai:access')
def generate_article(current_user_id):
    data = request.get_json() or {}
    topic = (data.get('topic') or '').strip()
    context_pack_id = data.get('context_pack_id')
    context_token_budget = data.get('context_token_budget')
    allow_embedding = bool(data.get('allow_embedding', False))

    if not topic:
        return jsonify({'status': 1, 'msg': '请输入文章概要或主题'}), 400

    active_config = get_active_ai_config()
    if not active_config:
        return jsonify({'status': 1, 'msg': 'AI 服务未配置，请先在 AI 中心启用模型配置'}), 500

    api_key = active_config.get('api_key')
    base_url = active_config.get('base_url')
    model_name = active_config.get('model')
    if not api_key or not model_name:
        return jsonify({'status': 1, 'msg': 'AI 配置缺少 API Key 或模型名称'}), 500

    system_prompt = """你是一个专业的知识文档起草助手。请根据用户提供的主题、资料或要求，生成一份可以直接进入编辑器继续修改的文档草稿。

要求：
1. 内容要结构清晰，适合加入知识库和上下文包复用。
2. content 字段必须使用 Markdown。
3. title 要简洁，summary 控制在 120 字以内。
4. category 只能从 frontend、backend、database、algorithm、devops、architecture、ai、other 中选择一个。
5. tags 返回 3 到 6 个短标签。
6. 只返回 JSON，不要包裹 ```json，也不要输出额外解释。

返回 JSON 格式：
{
  "title": "文档标题",
  "content": "Markdown 正文",
  "summary": "文档摘要",
  "category": "other",
  "tags": ["标签1", "标签2"]
}
"""

    user_prompt = f"请根据下面的起草要求生成文档草稿：\n\n{topic}"
    context_pack = None
    retrieval = None
    if context_pack_id:
        context_prompt, context_pack, retrieval, context_error = retrieve_context_pack_snippets(
            context_pack_id,
            topic,
            context_token_budget,
            allow_embedding=allow_embedding,
        )
        if context_error:
            status_code = 403 if '无权' in context_error or 'Permission' in context_error else 400
            return jsonify({'status': 1, 'msg': context_error}), status_code

        if context_prompt:
            system_prompt = "\n\n".join([
                system_prompt,
                "下面是用户为本次起草选择的上下文包检索结果。只使用命中的片段补充事实依据；如果片段不足，请在正文中保持谨慎，不要编造来源。",
                context_prompt,
            ])

    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            temperature=0.45,
            max_tokens=2600
        )

        content = response.choices[0].message.content or ""
        article_data = normalize_article_payload(content, topic)
        article_data["retrieval"] = retrieval
        article_data["context_pack"] = {
            "id": context_pack.get("id"),
            "name": context_pack.get("name"),
        } if context_pack else None

        return jsonify({
            'status': 0,
            'msg': '生成成功',
            'data': article_data
        })

    except Exception as e:
        return jsonify({'status': 1, 'msg': f'AI 起草失败：{str(e)}'}), 500

@ai_bp.route('/api/ai/context', methods=['GET'])
@permission_required('ai:access')
def get_context(current_user_id):
    user_id = str(current_user_id)
    
    if user_id not in context_store:
        return jsonify({'status': 0, 'data': {'context': []}})
    
    return jsonify({
        'status': 0,
        'data': {
            'context': context_store[user_id],
            'length': len(context_store[user_id])
        }
    })

@ai_bp.route('/api/ai/context', methods=['DELETE'])
@permission_required('ai:access')
def clear_context(current_user_id):
    user_id = str(current_user_id)
    
    if user_id in context_store:
        del context_store[user_id]
    
    return jsonify({'status': 0, 'msg': '上下文已清除'})

# 后台管理接口
@ai_bp.route('/api/ai/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    return jsonify({
        'status': 0,
        'data': {
            'models': SUPPORTED_MODELS
        }
    })


def safe_embedding_config_payload(config):
    return {
        "id": config.get("id"),
        "enabled": bool(config.get("enabled")),
        "configured": bool(config.get("configured")),
        "provider": config.get("provider") or "openai",
        "model": config.get("model") or "",
        "base_url": config.get("base_url") or "",
        "api_key_masked": config.get("api_key_masked") or mask_secret(config.get("api_key") or ""),
        "notes": config.get("notes") or "",
        "source": config.get("source") or "environment",
        "updated_at": config.get("updated_at") or "",
    }


def validate_embedding_config_payload(config):
    provider = (config.get("provider") or "").strip()
    model = (config.get("model") or "").strip()
    api_key = (config.get("api_key") or "").strip()
    base_url = (config.get("base_url") or "").strip()
    enabled = bool(config.get("enabled"))

    checks = [
        {
            "name": "enabled",
            "ok": enabled,
            "detail": "Embedding is enabled" if enabled else "Embedding is disabled",
        },
        {
            "name": "provider",
            "ok": bool(provider),
            "detail": provider or "Provider is empty",
        },
        {
            "name": "model",
            "ok": bool(model and model != "unconfigured"),
            "detail": model if model and model != "unconfigured" else "Model is empty",
        },
        {
            "name": "api_key",
            "ok": bool(api_key),
            "detail": "API key is present" if api_key else "API key is empty",
        },
    ]

    if base_url:
        parsed_url = urlparse(base_url)
        valid_url = parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)
        checks.append({
            "name": "base_url",
            "ok": valid_url,
            "detail": base_url if valid_url else "Base URL must start with http:// or https://",
        })
    else:
        checks.append({
            "name": "base_url",
            "ok": True,
            "detail": "Using provider default endpoint",
        })

    ok = all(item["ok"] for item in checks)
    return {
        "ok": ok,
        "network_call": False,
        "token_cost": False,
        "embedding_configured": bool(config.get("configured")),
        "source": config.get("source") or "environment",
        "model": model if model != "unconfigured" else "",
        "checks": checks,
        "next_action": (
            "Config is complete. You can build semantic indexes from a context pack."
            if ok
            else "Complete the failed checks before building semantic indexes."
        ),
    }


@ai_bp.route('/api/ai/embedding-config', methods=['GET'])
@permission_required('ai:manage')
def get_embedding_config_item(current_user_id):
    try:
        with engine.connect() as conn:
            ensure_embedding_config_table(conn)
            config = get_embedding_config(conn)
        return jsonify({'status': 0, 'data': safe_embedding_config_payload(config)})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取 Embedding 配置失败', 'error': str(e)}), 500


@ai_bp.route('/api/ai/embedding-config', methods=['POST'])
@permission_required('ai:manage')
def save_embedding_config_item(current_user_id):
    data = request.get_json() or {}
    enabled = bool(data.get('enabled'))
    provider = (data.get('provider') or 'openai').strip()
    model = (data.get('model') or '').strip()
    base_url = (data.get('base_url') or '').strip()
    api_key = (data.get('api_key') or '').strip()
    notes = (data.get('notes') or '').strip()

    try:
        with engine.connect() as conn:
            ensure_embedding_config_table(conn)
            existing = conn.execute(
                text("SELECT * FROM ai_embedding_configs WHERE is_active = 1 ORDER BY updated_at DESC, id DESC LIMIT 1")
            ).mappings().fetchone()

            model = model or (existing.get('model') if existing else '') or 'unconfigured'
            api_key_to_save = api_key or (existing.get('api_key') if existing else '') or ''

            if enabled and (not model or model == 'unconfigured' or not api_key_to_save):
                return jsonify({'status': 1, 'msg': '启用 Embedding 前必须填写模型和 API Key'}), 400

            if existing:
                conn.execute(
                    text("""
                        UPDATE ai_embedding_configs
                        SET provider = :provider,
                            api_key = :api_key,
                            base_url = :base_url,
                            model = :model,
                            enabled = :enabled,
                            is_active = 1,
                            notes = :notes
                        WHERE id = :id
                    """),
                    {
                        "id": existing["id"],
                        "provider": provider,
                        "api_key": api_key_to_save,
                        "base_url": base_url,
                        "model": model,
                        "enabled": 1 if enabled else 0,
                        "notes": notes,
                    }
                )
            else:
                conn.execute(text("UPDATE ai_embedding_configs SET is_active = 0"))
                conn.execute(
                    text("""
                        INSERT INTO ai_embedding_configs
                            (provider, api_key, base_url, model, enabled, is_active, notes)
                        VALUES
                            (:provider, :api_key, :base_url, :model, :enabled, 1, :notes)
                    """),
                    {
                        "provider": provider,
                        "api_key": api_key_to_save,
                        "base_url": base_url,
                        "model": model,
                        "enabled": 1 if enabled else 0,
                        "notes": notes,
                    }
                )
            conn.commit()
            config = get_embedding_config(conn)

        return jsonify({'status': 0, 'msg': 'Embedding 配置已保存', 'data': safe_embedding_config_payload(config)})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '保存 Embedding 配置失败', 'error': str(e)}), 500


@ai_bp.route('/api/ai/embedding-config/validate', methods=['POST'])
@permission_required('ai:manage')
def validate_embedding_config_item(current_user_id):
    try:
        data = request.get_json(silent=True) or {}
        with engine.connect() as conn:
            ensure_embedding_config_table(conn)
            config = get_embedding_config(conn)
        draft_config = dict(config)
        if isinstance(data, dict) and data:
            if 'enabled' in data:
                draft_config['enabled'] = bool(data.get('enabled'))
            for key in ('provider', 'model', 'base_url', 'notes'):
                if key in data:
                    draft_config[key] = (data.get(key) or '').strip()
            if 'api_key' in data and (data.get('api_key') or '').strip():
                draft_config['api_key'] = (data.get('api_key') or '').strip()
            draft_config['configured'] = bool(
                draft_config.get('enabled')
                and draft_config.get('model')
                and draft_config.get('model') != 'unconfigured'
                and draft_config.get('api_key')
            )

        return jsonify({
            'status': 0,
            'msg': 'Embedding config validated without network call',
            'data': validate_embedding_config_payload(draft_config)
        })
    except Exception as e:
        return jsonify({'status': 1, 'msg': 'Failed to validate Embedding config', 'error': str(e)}), 500


@ai_bp.route('/api/ai/configs', methods=['GET'])
@permission_required('ai:manage')
def get_configs(current_user_id):
    """获取配置列表"""
    try:
        provider = request.args.get('provider')
        model = request.args.get('model')
        
        with engine.connect() as conn:
            sql = "SELECT * FROM ai_configs WHERE 1=1"
            params = {}
            
            if provider:
                sql += " AND provider = :provider"
                params['provider'] = provider
            if model:
                sql += " AND model LIKE :model"
                params['model'] = f"%{model}%"
                
            sql += " ORDER BY created_at DESC"
            result = conn.execute(text(sql), params).mappings().fetchall()
            configs = []
            for row in result:
                config = dict(row)
                # Hide sensitive info partially
                if config.get('api_key') and len(config['api_key']) > 8:
                    config['api_key_masked'] = config['api_key'][:4] + '******' + config['api_key'][-4:]
                else:
                    config['api_key_masked'] = '******'
                config.pop('api_key', None)
                
                if config.get('created_at'):
                    config['created_at'] = config['created_at'].isoformat()
                if config.get('updated_at'):
                    config['updated_at'] = config['updated_at'].isoformat()
                    
                configs.append(config)
            return jsonify({'status': 0, 'data': configs})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取配置列表失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs', methods=['POST'])
@permission_required('ai:manage')
def create_config(current_user_id):
    """创建新配置"""
    data = request.get_json()
    provider = data.get('provider')
    api_key = data.get('api_key')
    base_url = data.get('base_url')
    model = data.get('model')
    system_prompt = data.get('system_prompt', '')
    is_active = data.get('is_active', False)
    
    if not all([provider, api_key, base_url, model]):
        return jsonify({'status': 1, 'msg': '缺少必要参数'}), 400
        
    try:
        with engine.connect() as conn:
            # 如果设置为启用，先禁用其他所有配置
            if is_active:
                conn.execute(text("UPDATE ai_configs SET is_active = 0"))
                
            conn.execute(
                text("""
                    INSERT INTO ai_configs (provider, api_key, base_url, model, system_prompt, is_active)
                    VALUES (:provider, :api_key, :base_url, :model, :system_prompt, :is_active)
                """),
                {
                    "provider": provider,
                    "api_key": api_key,
                    "base_url": base_url,
                    "model": model,
                    "system_prompt": system_prompt,
                    "is_active": 1 if is_active else 0
                }
            )
            conn.commit()
            return jsonify({'status': 0, 'msg': '配置创建成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '创建失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>', methods=['PUT'])
@permission_required('ai:manage')
def update_config_item(current_user_id, config_id):
    """更新配置"""
    data = request.get_json()
    provider = data.get('provider')
    api_key = data.get('api_key')
    base_url = data.get('base_url')
    model = data.get('model')
    system_prompt = data.get('system_prompt')
    is_active = data.get('is_active')
    
    try:
        with engine.connect() as conn:
            # 如果设置为启用，先禁用其他所有配置
            if is_active:
                conn.execute(text("UPDATE ai_configs SET is_active = 0"))
            
            # 构建更新语句
            update_parts = []
            params = {"id": config_id}
            
            if provider:
                update_parts.append("provider = :provider")
                params["provider"] = provider
            if api_key:
                update_parts.append("api_key = :api_key")
                params["api_key"] = api_key
            if base_url:
                update_parts.append("base_url = :base_url")
                params["base_url"] = base_url
            if model:
                update_parts.append("model = :model")
                params["model"] = model
            if system_prompt is not None:
                update_parts.append("system_prompt = :system_prompt")
                params["system_prompt"] = system_prompt
            if is_active is not None:
                update_parts.append("is_active = :is_active")
                params["is_active"] = 1 if is_active else 0
                
            if not update_parts:
                return jsonify({'status': 0, 'msg': '无变更'})
                
            sql = f"UPDATE ai_configs SET {', '.join(update_parts)} WHERE id = :id"
            conn.execute(text(sql), params)
            conn.commit()
            
            return jsonify({'status': 0, 'msg': '更新成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '更新失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>', methods=['DELETE'])
@permission_required('ai:manage')
def delete_config(current_user_id, config_id):
    """删除配置"""
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM ai_configs WHERE id = :id"), {"id": config_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '删除成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>/activate', methods=['POST'])
@permission_required('ai:manage')
def activate_config(current_user_id, config_id):
    """启用指定配置"""
    try:
        with engine.connect() as conn:
            # 开启事务：禁用所有 -> 启用指定
            conn.execute(text("UPDATE ai_configs SET is_active = 0"))
            conn.execute(text("UPDATE ai_configs SET is_active = 1 WHERE id = :id"), {"id": config_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '已启用该配置'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '操作失败', 'error': str(e)}), 500
