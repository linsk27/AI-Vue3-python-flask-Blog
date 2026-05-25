"""Manual OpenAI-compatible provider smoke test.

Run explicitly with:
    AI_API_KEY=... AI_BASE_URL=... AI_MODEL=... python backend/test_openai.py

This file intentionally has no pytest test functions and never falls back to a
hard-coded key.
"""

import os

from openai import OpenAI


def main():
    api_key = os.environ.get("AI_API_KEY", "").strip()
    base_url = os.environ.get("AI_BASE_URL", "").strip()
    model = os.environ.get("AI_MODEL", "").strip()

    missing = [name for name, value in {
        "AI_API_KEY": api_key,
        "AI_BASE_URL": base_url,
        "AI_MODEL": model,
    }.items() if not value]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
