# routes/ai.py

from flask import Blueprint, request, jsonify
import os
from openai import OpenAI
from typing import Dict, List, Optional

ai_bp = Blueprint('ai', **name**)

# 简单的内存上下文管理，后续可扩展为数据库存储

context_store: Dict[str, List[Dict]] = {}

# 获取API密钥（火山方舟）

# api_key = os.environ.get('ARK_API_KEY', '450530a8-5088-431d-b482-f2c0611b49b7')

api_key = '450530a8-5088-431d-b482-f2c0611b49b7'

@ai_bp.route('/api/ai/chat', methods=['POST'])
def chat():
data = request.get_json()
user_id = data.get('user_id', 'default') # 默认用户ID，后续可从JWT中获取
message = data.get('message')
reset_context = data.get('reset_context', False)

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
    if user_id not in context_store:
        context_store[user_id] = [
            {"role": "system", "content": "You are a helpful assistant"}
        ]

    # 添加用户消息到上下文
    context_store[user_id].append({"role": "user", "content": message})

    try:
        # 检查API密钥是否存在
        if not api_key:
            return jsonify({'status': 1, 'msg': '请设置ARK_API_KEY环境变量'}), 400

        # 初始化OpenAI客户端（火山方舟）
        client = OpenAI(
            base_url='https://ark.cn-beijing.volces.com/api/v3',
            api_key=api_key
        )

        # 调用火山方舟API（使用chat.completions.create方法）
        response = client.chat.completions.create(
            model="ep-20260125005850-g97x2",
            messages=context_store[user_id],
            stream=False
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
                'context_length': len(context_store[user_id])
            }
        })

    except Exception as e:
        return jsonify({'status': 1, 'msg': f'请求失败: {str(e)}'}), 500

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
