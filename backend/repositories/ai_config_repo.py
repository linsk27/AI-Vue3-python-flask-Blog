from sqlalchemy import text


def fetch_active_config(conn):
    return conn.execute(
        text("SELECT * FROM ai_configs WHERE is_active = 1 LIMIT 1")
    ).mappings().fetchone()


def fetch_configs(conn, provider=None, model=None):
    sql = "SELECT * FROM ai_configs WHERE 1=1"
    params = {}

    if provider:
        sql += " AND provider = :provider"
        params["provider"] = provider
    if model:
        sql += " AND model LIKE :model"
        params["model"] = f"%{model}%"

    sql += " ORDER BY created_at DESC"
    return conn.execute(text(sql), params).mappings().fetchall()


def deactivate_all_configs(conn):
    conn.execute(text("UPDATE ai_configs SET is_active = 0"))


def insert_config(conn, payload):
    conn.execute(
        text("""
            INSERT INTO ai_configs (provider, api_key, base_url, model, system_prompt, is_active)
            VALUES (:provider, :api_key, :base_url, :model, :system_prompt, :is_active)
        """),
        {
            "provider": payload["provider"],
            "api_key": payload["api_key"],
            "base_url": payload["base_url"],
            "model": payload["model"],
            "system_prompt": payload.get("system_prompt", ""),
            "is_active": 1 if payload.get("is_active") else 0,
        },
    )


def update_config(conn, config_id, fields):
    update_parts = []
    params = {"id": config_id}
    allowed_columns = {
        "provider",
        "api_key",
        "base_url",
        "model",
        "system_prompt",
        "is_active",
    }

    for key, value in fields.items():
        if key not in allowed_columns:
            continue
        update_parts.append(f"{key} = :{key}")
        params[key] = value

    if not update_parts:
        return False

    conn.execute(text(f"UPDATE ai_configs SET {', '.join(update_parts)} WHERE id = :id"), params)
    return True


def delete_config(conn, config_id):
    conn.execute(text("DELETE FROM ai_configs WHERE id = :id"), {"id": config_id})


def activate_config(conn, config_id):
    deactivate_all_configs(conn)
    conn.execute(text("UPDATE ai_configs SET is_active = 1 WHERE id = :id"), {"id": config_id})


def fetch_active_embedding_config(conn):
    return conn.execute(
        text("SELECT * FROM ai_embedding_configs WHERE is_active = 1 ORDER BY updated_at DESC, id DESC LIMIT 1")
    ).mappings().fetchone()


def upsert_embedding_config(conn, existing, payload):
    if existing:
        conn.execute(
            text("""
                UPDATE ai_embedding_configs
                SET provider = :provider,
                    api_key = :api_key,
                    base_url = :base_url,
                    model = :model,
                    enabled = :enabled,
                    is_active = 1,
                    notes = :notes
                WHERE id = :id
            """),
            {
                "id": existing["id"],
                **payload,
            },
        )
        return

    conn.execute(text("UPDATE ai_embedding_configs SET is_active = 0"))
    conn.execute(
        text("""
            INSERT INTO ai_embedding_configs
                (provider, api_key, base_url, model, enabled, is_active, notes)
            VALUES
                (:provider, :api_key, :base_url, :model, :enabled, 1, :notes)
        """),
        payload,
    )
