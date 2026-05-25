import os

from database import engine
from db.schema import ensure_ai_config_table
from repositories import ai_config_repo
from services.context_pack_service import mask_secret


DEFAULT_ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_ARK_MODEL = "ep-20260125005850-g97x2"


def get_env_value(*keys):
    for key in keys:
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return ""


def get_default_ai_config():
    return {
        "provider": get_env_value("AI_PROVIDER") or "volcano",
        "api_key": get_env_value("AI_API_KEY", "ARK_API_KEY"),
        "base_url": get_env_value("AI_BASE_URL", "ARK_BASE_URL") or DEFAULT_ARK_BASE_URL,
        "model": get_env_value("AI_MODEL", "ARK_MODEL") or DEFAULT_ARK_MODEL,
        "system_prompt": get_env_value("AI_SYSTEM_PROMPT") or "You are a helpful assistant.",
    }


def merge_ai_config_with_env_fallback(config):
    config = config or {}
    default_config = get_default_ai_config()
    merged = dict(config)

    if not merged.get("api_key"):
        merged["api_key"] = default_config["api_key"]
    if not merged.get("base_url"):
        merged["base_url"] = default_config["base_url"]
    if not merged.get("provider"):
        merged["provider"] = default_config["provider"]
    if not merged.get("system_prompt"):
        merged["system_prompt"] = default_config["system_prompt"]

    env_model = get_env_value("AI_MODEL", "ARK_MODEL")
    if env_model and (not merged.get("model") or merged.get("model") == DEFAULT_ARK_MODEL):
        merged["model"] = env_model
    elif not merged.get("model"):
        merged["model"] = default_config["model"]

    env_base_url = get_env_value("AI_BASE_URL", "ARK_BASE_URL")
    if env_base_url and merged.get("base_url") == DEFAULT_ARK_BASE_URL and not config.get("api_key"):
        merged["base_url"] = env_base_url

    return merged


def get_active_ai_config():
    try:
        with engine.connect() as conn:
            ensure_ai_config_table(conn)
            result = ai_config_repo.fetch_active_config(conn)
            if result:
                return merge_ai_config_with_env_fallback(dict(result))
    except Exception as e:
        print(f"Error fetching active config: {e}")

    return get_default_ai_config()


def serialize_ai_config(row):
    config = dict(row)
    config["api_key_masked"] = mask_secret(config.get("api_key") or "")
    config.pop("api_key", None)

    for key in ("created_at", "updated_at"):
        value = config.get(key)
        if hasattr(value, "isoformat"):
            config[key] = value.isoformat()

    return config


def list_ai_configs(provider=None, model=None):
    with engine.connect() as conn:
        ensure_ai_config_table(conn)
        rows = ai_config_repo.fetch_configs(conn, provider=provider, model=model)
    return [serialize_ai_config(row) for row in rows]


def normalize_new_config(data):
    data = data if isinstance(data, dict) else {}
    payload = {
        "provider": (data.get("provider") or "").strip(),
        "api_key": (data.get("api_key") or "").strip(),
        "base_url": (data.get("base_url") or "").strip(),
        "model": (data.get("model") or "").strip(),
        "system_prompt": data.get("system_prompt", ""),
        "is_active": bool(data.get("is_active", False)),
    }
    if not all([payload["provider"], payload["api_key"], payload["base_url"], payload["model"]]):
        raise ValueError("缺少必要参数")
    return payload


def create_ai_config(data):
    payload = normalize_new_config(data)
    with engine.connect() as conn:
        ensure_ai_config_table(conn)
        if payload["is_active"]:
            ai_config_repo.deactivate_all_configs(conn)
        ai_config_repo.insert_config(conn, payload)
        conn.commit()


def build_update_fields(data):
    data = data if isinstance(data, dict) else {}
    fields = {}

    for key in ("provider", "api_key", "base_url", "model"):
        value = (data.get(key) or "").strip()
        if value:
            fields[key] = value

    if "system_prompt" in data and data.get("system_prompt") is not None:
        fields["system_prompt"] = data.get("system_prompt")

    if "is_active" in data and data.get("is_active") is not None:
        fields["is_active"] = 1 if data.get("is_active") else 0

    return fields


def update_ai_config(config_id, data):
    fields = build_update_fields(data)
    if not fields:
        return False

    with engine.connect() as conn:
        ensure_ai_config_table(conn)
        if fields.get("is_active"):
            ai_config_repo.deactivate_all_configs(conn)
        changed = ai_config_repo.update_config(conn, config_id, fields)
        conn.commit()

    return changed


def delete_ai_config(config_id):
    with engine.connect() as conn:
        ensure_ai_config_table(conn)
        ai_config_repo.delete_config(conn, config_id)
        conn.commit()


def activate_ai_config(config_id):
    with engine.connect() as conn:
        ensure_ai_config_table(conn)
        ai_config_repo.activate_config(conn, config_id)
        conn.commit()
