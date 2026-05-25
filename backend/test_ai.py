"""Manual DeepSeek smoke test.

Run explicitly with:
    DEEPSEEK_API_KEY=... python backend/test_ai.py

This file intentionally has no pytest test functions and never falls back to a
hard-coded key.
"""

import os

from openai import OpenAI


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY is required for this manual smoke test.")

    client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )

    response = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
