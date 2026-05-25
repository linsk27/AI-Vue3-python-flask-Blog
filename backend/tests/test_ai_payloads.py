import pytest

from services.ai_article_service import normalize_article_payload
from services.ai_embedding_config_service import safe_embedding_config_payload, validate_embedding_config_payload


def test_validate_embedding_config_reports_disabled_without_network_cost():
    result = validate_embedding_config_payload(
        {
            "enabled": False,
            "provider": "openai",
            "model": "text-embedding-3-small",
            "api_key": "sk-test",
            "base_url": "",
            "configured": False,
        }
    )

    assert result["ok"] is False
    assert result["network_call"] is False
    assert result["token_cost"] is False
    assert any(item["name"] == "enabled" and not item["ok"] for item in result["checks"])


def test_validate_embedding_config_rejects_invalid_base_url():
    result = validate_embedding_config_payload(
        {
            "enabled": True,
            "provider": "custom",
            "model": "embedding-model",
            "api_key": "secret",
            "base_url": "not-a-url",
            "configured": True,
        }
    )

    assert result["ok"] is False
    assert any(item["name"] == "base_url" and not item["ok"] for item in result["checks"])


def test_validate_embedding_config_accepts_complete_payload():
    result = validate_embedding_config_payload(
        {
            "enabled": True,
            "provider": "custom",
            "model": "embedding-model",
            "api_key": "secret",
            "base_url": "https://api.example.com/v1",
            "configured": True,
        }
    )

    assert result["ok"] is True
    assert result["embedding_configured"] is True


def test_safe_embedding_config_payload_masks_raw_key():
    result = safe_embedding_config_payload(
        {
            "enabled": True,
            "configured": True,
            "provider": "custom",
            "model": "embedding-model",
            "base_url": "https://api.example.com/v1",
            "api_key": "sk-1234567890",
        }
    )

    assert result["api_key_masked"] == "sk-1******7890"
    assert "api_key" not in result


def test_normalize_article_payload_accepts_json_code_fence():
    raw = """```json
{"title":"RAG 入门","content":"正文内容","summary":"摘要","category":"ai","tags":["RAG"]}
```"""
    result = normalize_article_payload(raw, "默认标题")

    assert result["title"] == "RAG 入门"
    assert result["content"] == "正文内容"
    assert result["category"] == "ai"
    assert result["tags"] == ["RAG"]


def test_normalize_article_payload_rejects_unresolved_json_envelope():
    with pytest.raises(ValueError, match="content"):
        normalize_article_payload('{"content": {"nested": true}}', "默认标题")
