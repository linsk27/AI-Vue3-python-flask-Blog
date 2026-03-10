# routes/ai.py
from flask import Blueprint, request, jsonify
import os
from openai import OpenAI
from typing import Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine
import json

ai_bp = Blueprint('ai', __name__)

# 简单的内存上下文管理，后续可扩展为数据库存储
context_store: Dict[str, List[Dict]] = {}

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

@ai_bp.route('/api/ai/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id', 'default')  # 默认用户ID，后续可从JWT中获取
    message = data.get('message')
    reset_context = data.get('reset_context', False)
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

    temperature = data.get('temperature', 0.3)  # 降低temperature，减少随机性，加快响应
    max_tokens = data.get('max_tokens', 500)  # 限制最大token数，减少回复长度
    
    # 重置上下文
    if reset_context:
        context_store[user_id] = []
        # 如果只重置上下文，不发送消息，直接返回成功
        if not message:
            return jsonify({
                'status': 0,
                'msg': '上下文已重置',
                'data': {
                    'context_length': 0
                }
            })
    
    # 检查消息是否为空（非重置上下文时）
    if not message:
        return jsonify({'status': 1, 'msg': '消息不能为空'}), 400
    
    # 初始化或获取现有上下文
    if user_id not in context_store or reset_context:
        context_store[user_id] = [
            {"role": "system", "content": system_prompt}
        ]
    
    # 添加用户消息到上下文
    context_store[user_id].append({"role": "user", "content": message})
    
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
            messages=context_store[user_id],
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 提取AI回复
        assistant_reply = response.choices[0].message.content
        
        # 添加AI回复到上下文
        context_store[user_id].append({"role": "assistant", "content": assistant_reply})
        
        # 限制上下文长度，避免token超限
        if len(context_store[user_id]) > 20:  # 保留系统消息 + 最近的18条消息
            context_store[user_id] = context_store[user_id][0:1] + context_store[user_id][-18:]
        
        return jsonify({
            'status': 0,
            'msg': '成功',
            'data': {
                'reply': assistant_reply,
                'context_length': len(context_store[user_id]),
                'model_used': model_name,
                'provider_used': model_provider
            }
        })
        
    except Exception as e:
        return jsonify({'status': 1, 'msg': f'请求失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/generate-article', methods=['POST'])
def generate_article():
    data = request.get_json()
    topic = data.get('topic')
    print(f"Generating article for topic: {topic}")
    
    if not topic:
        return jsonify({'status': 1, 'msg': '请输入文章概要或主题'}), 400
        
    # 获取AI配置
    active_config = None
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM ai_configs WHERE is_active = 1 LIMIT 1")).mappings().fetchone()
            if result:
                active_config = dict(result)
    except Exception as e:
        print(f"Error fetching active config: {e}")

    if not active_config:
        print("AI config not found or not active")
        return jsonify({'status': 1, 'msg': 'AI服务未配置'}), 500
        
    api_key = active_config.get('api_key')
    base_url = active_config.get('base_url')
    model_name = active_config.get('model')
    print(f"Using AI config: {active_config.get('provider')}, model: {model_name}")
    
    # 构造提示词
    system_prompt = """
    你是一个专业的文章创作者。请根据用户提供的主题或概要，创作一篇完整的文章。
    
    ### 任务要求：
    1. 文章内容必须丰富、充实，字数建议在 1000 字以上（如有必要可分章节）。
    2. 使用 Markdown 语法编写 `content` 字段。
    3. 严禁在 JSON 字符串外部包含任何解释性文字或 Markdown 代码块标记（如 ```json）。
    
    ### 返回格式（必须是纯 JSON）：
    {
        "title": "文章标题",
        "content": "文章正文内容（支持 Markdown 格式，内容要丰富充实）",
        "summary": "文章摘要（100字以内）",
        "category": "文章分类（从以下选项中选择一个：frontend, backend, database, algorithm, devops, architecture, ai, other）",
        "tags": ["标签1", "标签2", "标签3"]
    }
    """
    
    user_prompt = f"请直接输出符合格式的 JSON 字符串，文章主题关于：{topic}"
    
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        print("Calling OpenAI API...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            temperature=0.7, 
            max_tokens=2500  # 增加 token 限制以支持长文章
        )
        
        content = response.choices[0].message.content
        print(f"AI response received, length: {len(content)}")
        
        # 尝试解析JSON
        try:
            # 更加健壮的 JSON 提取逻辑
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
                
            article_data = json.loads(content.strip())
            print("JSON parsed successfully")
            
            return jsonify({
                'status': 0,
                'msg': '生成成功',
                'data': article_data
            })
        except Exception as json_err:
            print(f"JSON parse failed: {str(json_err)}, returning raw content")
            # 如果解析失败，尝试简单清洗内容并返回
            return jsonify({
                'status': 0,
                'msg': '生成成功（非标准格式）',
                'data': {
                    "title": topic[:20],
                    "content": content,
                    "summary": content[:150].replace('\n', ' ') + '...',
                    "category": "other",
                    "tags": ["AI生成"]
                }
            })
            
    except Exception as e:
        print(f"AI generation failed: {str(e)}")
        return jsonify({'status': 1, 'msg': f'生成失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/context', methods=['GET'])
def get_context():
    user_id = request.args.get('user_id', 'default')
    
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
def clear_context():
    user_id = request.args.get('user_id', 'default')
    
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

@ai_bp.route('/api/ai/configs', methods=['GET'])
def get_configs():
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
                
                if config.get('created_at'):
                    config['created_at'] = config['created_at'].isoformat()
                if config.get('updated_at'):
                    config['updated_at'] = config['updated_at'].isoformat()
                    
                configs.append(config)
            return jsonify({'status': 0, 'data': configs})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取配置列表失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs', methods=['POST'])
def create_config():
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
def update_config_item(config_id):
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
def delete_config(config_id):
    """删除配置"""
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM ai_configs WHERE id = :id"), {"id": config_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '删除成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除失败', 'error': str(e)}), 500

@ai_bp.route('/api/ai/configs/<int:config_id>/activate', methods=['POST'])
def activate_config(config_id):
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