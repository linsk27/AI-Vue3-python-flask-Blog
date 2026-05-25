import pytest

from services import ai_config_service


def test_default_ai_config_uses_env_key(monkeypatch):
    monkeypatch.setenv("ARK_API_KEY", "ark-test-key")

    config = ai_config_service.get_default_ai_config()

    assert config["provider"] == "volcano"
    assert config["api_key"] == "ark-test-key"
    assert config["model"]


def test_serialize_ai_config_masks_secret_and_dates():
    class FakeDate:
        def isoformat(self):
            return "2026-05-25T10:00:00"

    result = ai_config_service.serialize_ai_config({
        "id": 1,
        "provider": "deepseek",
        "api_key": "sk-1234567890",
        "base_url": "https://api.example.com",
        "model": "deepseek-chat",
        "system_prompt": "test",
        "created_at": FakeDate(),
        "updated_at": FakeDate(),
    })

    assert "api_key" not in result
    assert result["api_key_masked"] == "sk-1******7890"
    assert result["created_at"] == "2026-05-25T10:00:00"


def test_normalize_new_config_requires_core_fields():
    with pytest.raises(ValueError, match="缺少必要参数"):
        ai_config_service.normalize_new_config({
            "provider": "deepseek",
            "api_key": "",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
        })


def test_build_update_fields_keeps_false_active_flag():
    fields = ai_config_service.build_update_fields({
        "provider": " deepseek ",
        "api_key": "",
        "system_prompt": "",
        "is_active": False,
    })

    assert fields == {
        "provider": "deepseek",
        "system_prompt": "",
        "is_active": 0,
    }


def test_build_update_fields_ignores_non_object_payload():
    assert ai_config_service.build_update_fields(["bad"]) == {}
