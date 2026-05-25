from urllib.parse import urlparse

from database import engine
from db.schema import ensure_embedding_config_table
from repositories import ai_config_repo
from services.context_pack_service import get_embedding_config, mask_secret


def safe_embedding_config_payload(config):
    return {
        "id": config.get("id"),
        "enabled": bool(config.get("enabled")),
        "configured": bool(config.get("configured")),
        "provider": config.get("provider") or "openai",
        "model": config.get("model") or "",
        "base_url": config.get("base_url") or "",
        "api_key_masked": config.get("api_key_masked") or mask_secret(config.get("api_key") or ""),
        "notes": config.get("notes") or "",
        "source": config.get("source") or "environment",
        "updated_at": config.get("updated_at") or "",
    }


def get_embedding_config_payload():
    with engine.connect() as conn:
        ensure_embedding_config_table(conn)
        config = get_embedding_config(conn)
    return safe_embedding_config_payload(config)


def save_embedding_config_payload(data):
    data = data if isinstance(data, dict) else {}
    enabled = bool(data.get("enabled"))
    provider = (data.get("provider") or "openai").strip()
    model = (data.get("model") or "").strip()
    base_url = (data.get("base_url") or "").strip()
    api_key = (data.get("api_key") or "").strip()
    notes = (data.get("notes") or "").strip()

    with engine.connect() as conn:
        ensure_embedding_config_table(conn)
        existing = ai_config_repo.fetch_active_embedding_config(conn)

        model = model or (existing.get("model") if existing else "") or "unconfigured"
        api_key_to_save = api_key or (existing.get("api_key") if existing else "") or ""

        if enabled and (not model or model == "unconfigured" or not api_key_to_save):
            raise ValueError("启用 Embedding 前必须填写模型和 API Key")

        ai_config_repo.upsert_embedding_config(
            conn,
            existing,
            {
                "provider": provider,
                "api_key": api_key_to_save,
                "base_url": base_url,
                "model": model,
                "enabled": 1 if enabled else 0,
                "notes": notes,
            },
        )
        conn.commit()
        config = get_embedding_config(conn)

    return safe_embedding_config_payload(config)


def validate_embedding_config_draft(data):
    data = data if isinstance(data, dict) else {}
    with engine.connect() as conn:
        ensure_embedding_config_table(conn)
        config = get_embedding_config(conn)

    draft_config = dict(config)
    if isinstance(data, dict) and data:
        if "enabled" in data:
            draft_config["enabled"] = bool(data.get("enabled"))
        for key in ("provider", "model", "base_url", "notes"):
            if key in data:
                draft_config[key] = (data.get(key) or "").strip()
        if "api_key" in data and (data.get("api_key") or "").strip():
            draft_config["api_key"] = (data.get("api_key") or "").strip()
        draft_config["configured"] = bool(
            draft_config.get("enabled")
            and draft_config.get("model")
            and draft_config.get("model") != "unconfigured"
            and draft_config.get("api_key")
        )

    return validate_embedding_config_payload(draft_config)


def validate_embedding_config_payload(config):
    provider = (config.get("provider") or "").strip()
    model = (config.get("model") or "").strip()
    api_key = (config.get("api_key") or "").strip()
    base_url = (config.get("base_url") or "").strip()
    enabled = bool(config.get("enabled"))

    checks = [
        {
            "name": "enabled",
            "ok": enabled,
            "detail": "Embedding is enabled" if enabled else "Embedding is disabled",
        },
        {
            "name": "provider",
            "ok": bool(provider),
            "detail": provider or "Provider is empty",
        },
        {
            "name": "model",
            "ok": bool(model and model != "unconfigured"),
            "detail": model if model and model != "unconfigured" else "Model is empty",
        },
        {
            "name": "api_key",
            "ok": bool(api_key),
            "detail": "API key is present" if api_key else "API key is empty",
        },
    ]

    if base_url:
        parsed_url = urlparse(base_url)
        valid_url = parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)
        checks.append({
            "name": "base_url",
            "ok": valid_url,
            "detail": base_url if valid_url else "Base URL must start with http:// or https://",
        })
    else:
        checks.append({
            "name": "base_url",
            "ok": True,
            "detail": "Using provider default endpoint",
        })

    ok = all(item["ok"] for item in checks)
    return {
        "ok": ok,
        "network_call": False,
        "token_cost": False,
        "embedding_configured": bool(config.get("configured")),
        "source": config.get("source") or "environment",
        "model": model if model != "unconfigured" else "",
        "checks": checks,
        "next_action": (
            "Config is complete. You can build semantic indexes from a context pack."
            if ok
            else "Complete the failed checks before building semantic indexes."
        ),
    }
