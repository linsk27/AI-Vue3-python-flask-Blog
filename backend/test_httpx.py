import os
import httpx

api_key = os.environ.get('DEEPSEEK_API_KEY', 'sk-9cc34a9c38e14d1f918f7649e9789c3a')

# 直接使用httpx调用DeepSeek API
url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    "stream": False
}

# 创建httpx客户端
with httpx.Client() as client:
    response = client.post(url, headers=headers, json=payload, timeout=30.0)

# 检查响应状态
if response.status_code == 200:
    # 解析响应
    response_data = response.json()
    assistant_reply = response_data['choices'][0]['message']['content']
    print(f"AI回复: {assistant_reply}")
else:
    print(f"API请求失败: {response.status_code} - {response.text}")