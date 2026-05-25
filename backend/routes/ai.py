# routes/ai.py
from flask import Blueprint, request, jsonify, Response, stream_with_context
from openai import OpenAI
from routes.context_pack import (
    can_view_pack,
    get_request_user,
)
from services.rag_utils import (
    estimate_tokens,
)
from services import ai_rag_service
from services.ai_context_service import (
    append_exchange,
    clear_user_context,
    get_user_context,
    needs_context_reset,
    reset_user_context,
)
from services.ai_article_service import normalize_article_payload
from services.ai_config_service import (
    activate_ai_config,
    create_ai_config,
    delete_ai_config,
    get_active_ai_config,
    list_ai_configs,
    update_ai_config,
)
from services.ai_embedding_config_service import (
    get_embedding_config_payload,
    save_embedding_config_payload,
    validate_embedding_config_draft,
)
from middleware import permission_required
import json

ai_bp = Blueprint('ai', __name__)

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

def format_sse_event(payload):
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

def retrieve_context_pack_snippets(context_pack_id, query, token_budget=None, max_snippets=ai_rag_service.MAX_RAG_SNIPPETS, allow_embedding=True):
    user, _ = get_request_user(required=False)
    return ai_rag_service.retrieve_context_pack_snippets(
        context_pack_id,
        query,
        token_budget,
        max_snippets=max_snippets,
        allow_embedding=allow_embedding,
        user=user,
        can_view_pack=can_view_pack,
    )


def build_effective_system_prompt(base_prompt, context_pack_id, query=None, token_budget=None):
    user, _ = get_request_user(required=False)
    return ai_rag_service.build_effective_system_prompt(
        base_prompt,
        context_pack_id,
        query,
        token_budget,
        user=user,
        can_view_pack=can_view_pack,
    )


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

    # 优先使用参数中的模型名，服务端仍统一从启用配置读取 API Key 与默认端点。
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
    if needs_context_reset(user_id, context_key, reset_context=reset_context):
        reset_user_context(user_id, context_key)

    request_messages = [
        {"role": "system", "content": effective_system_prompt},
        *get_user_context(user_id)[-18:],
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
        append_exchange(user_id, message, assistant_reply)
        
        return jsonify({
            'status': 0,
            'msg': '成功',
            'data': {
                'reply': assistant_reply,
                'context_length': len(get_user_context(user_id)),
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

        if needs_context_reset(user_id, context_key, reset_context=reset_context):
            reset_user_context(user_id, context_key)

        request_messages = [
            {"role": "system", "content": effective_system_prompt},
            *get_user_context(user_id)[-18:],
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

            append_exchange(user_id, message, assistant_reply)

            yield format_sse_event({
                'type': 'done',
                'context_length': len(get_user_context(user_id)),
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
    
    if not get_user_context(user_id):
        return jsonify({'status': 0, 'data': {'context': []}})
    
    return jsonify({
        'status': 0,
        'data': {
            'context': get_user_context(user_id),
            'length': len(get_user_context(user_id))
        }
    })

@ai_bp.route('/api/ai/context', methods=['DELETE'])
@permission_required('ai:access')
def clear_context(current_user_id):
    user_id = str(current_user_id)
    
    clear_user_context(user_id)
    
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


@ai_bp.route('/api/ai/embedding-config', methods=['GET'])
@permission_required('ai:manage')
def get_embedding_config_item(current_user_id):
    try:
        return jsonify({'status': 0, 'data': get_embedding_config_payload()})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取 Embedding 配置失败', 'error': str(e)}), 500


@ai_bp.route('/api/ai/embedding-config', methods=['POST'])
@permission_required('ai:manage')
def save_embedding_config_item(current_user_id):
    data = request.get_json() or {}
    try:
        return jsonify({
            'status': 0,
            'msg': 'Embedding 配置已保存',
            'data': save_embedding_config_payload(data)
        })
    except ValueError as e:
        return jsonify({'status': 1, 'msg': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 1, 'msg': '保存 Embedding 配置失败', 'error': str(e)}), 500


@ai_bp.route('/api/ai/embedding-config/validate', methods=['POST'])
@permission_required('ai:manage')
def validate_embedding_config_item(current_user_id):
    try:
        data = request.get_json(silent=True) or {}
        return jsonify({
            'status': 0,
            'msg': 'Embedding config validated without network call',
            'data': validate_embedding_config_draft(data)
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
        return jsonify({'status': 0, 'data': list_ai_configs(provider=provider, model=model)})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取配置列表失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs', methods=['POST'])
@permission_required('ai:manage')
def create_config(current_user_id):
    """创建新配置"""
    data = request.get_json() or {}
    try:
        create_ai_config(data)
        return jsonify({'status': 0, 'msg': '配置创建成功'})
    except ValueError as e:
        return jsonify({'status': 1, 'msg': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 1, 'msg': '创建失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>', methods=['PUT'])
@permission_required('ai:manage')
def update_config_item(current_user_id, config_id):
    """更新配置"""
    data = request.get_json() or {}
    try:
        if not update_ai_config(config_id, data):
            return jsonify({'status': 0, 'msg': '无变更'})
        return jsonify({'status': 0, 'msg': '更新成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '更新失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>', methods=['DELETE'])
@permission_required('ai:manage')
def delete_config(current_user_id, config_id):
    """删除配置"""
    try:
        delete_ai_config(config_id)
        return jsonify({'status': 0, 'msg': '删除成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>/activate', methods=['POST'])
@permission_required('ai:manage')
def activate_config(current_user_id, config_id):
    """启用指定配置"""
    try:
        activate_ai_config(config_id)
        return jsonify({'status': 0, 'msg': '已启用该配置'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '操作失败', 'error': str(e)}), 500
