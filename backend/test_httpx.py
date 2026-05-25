"""Manual DeepSeek HTTP smoke test.

Run explicitly with:
    DEEPSEEK_API_KEY=... python backend/test_httpx.py

This file intentionally has no pytest test functions and never falls back to a
hard-coded key.
"""

import os

import httpx


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY is required for this manual smoke test.")

    url = os.environ.get("DEEPSEEK_CHAT_URL", "https://api.deepseek.com/v1/chat/completions")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        "stream": False,
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=30.0)

    if response.status_code == 200:
        response_data = response.json()
        assistant_reply = response_data["choices"][0]["message"]["content"]
        print(f"AI reply: {assistant_reply}")
    else:
        print(f"API request failed: {response.status_code} - {response.text}")


if __name__ == "__main__":
    main()
