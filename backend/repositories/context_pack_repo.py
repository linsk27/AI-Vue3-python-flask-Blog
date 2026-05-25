import json

from sqlalchemy import bindparam, text


LEGACY_DEMO_PACKS = {
    "Vercel + Railway 部署上下文包": "沉淀前端 Vercel",
    "毕业答辩 AI 表达包": "把项目需求",
}


def json_loads(value, fallback=None):
    if fallback is None:
        fallback = []
    if not value:
        return fallback
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return fallback


def last_insert_id(conn, result):
    return result.lastrowid or conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()


def row_to_source(row):
    source = dict(row)
    if source.get("created_at"):
        source["created_at"] = source["created_at"].isoformat()
    source["type"] = source.pop("source_type", "文档")
    return source


def row_to_pack(row, sources=None):
    pack = dict(row)
    pack["keyPoints"] = json_loads(pack.pop("key_points", "[]"))
    pack["tags"] = json_loads(pack.get("tags"), [])
    pack["sources"] = sources or []
    pack["documents"] = [source["title"] for source in pack["sources"]]
    pack["nextAction"] = pack.pop("next_action", "")
    pack["tokenBudget"] = pack.pop("token_budget", "0.8k")
    if pack.get("created_at"):
        pack["created_at"] = pack["created_at"].isoformat()
    if pack.get("updated_at"):
        pack["updated_at"] = pack["updated_at"].isoformat()
    return pack


def is_legacy_demo_pack(row):
    name = row.get("name")
    description = row.get("description") or ""
    return (
        row.get("user_id") is None
        and name in LEGACY_DEMO_PACKS
        and description.startswith(LEGACY_DEMO_PACKS[name])
    )


def fetch_active_embedding_config(conn):
    return conn.execute(
        text("SELECT * FROM ai_embedding_configs WHERE is_active = 1 ORDER BY updated_at DESC, id DESC LIMIT 1")
    ).mappings().fetchone()


def fetch_source_for_index(conn, source_id):
    return conn.execute(
        text("SELECT id, pack_id, title, content FROM context_pack_sources WHERE id = :id"),
        {"id": source_id},
    ).mappings().fetchone()


def delete_chunks_for_source(conn, source_id):
    conn.execute(text("DELETE FROM context_pack_source_chunks WHERE source_id = :source_id"), {"source_id": source_id})


def insert_source_chunk(conn, source_id, pack_id, chunk_index, content, tokens_estimate, content_hash):
    conn.execute(
        text("""
            INSERT INTO context_pack_source_chunks
                (source_id, pack_id, chunk_index, content, tokens_estimate, content_hash)
            VALUES
                (:source_id, :pack_id, :chunk_index, :content, :tokens_estimate, :content_hash)
        """),
        {
            "source_id": source_id,
            "pack_id": pack_id,
            "chunk_index": chunk_index,
            "content": content,
            "tokens_estimate": tokens_estimate,
            "content_hash": content_hash,
        },
    )


def fetch_source_ids_missing_chunks(conn, pack_id):
    return conn.execute(
        text("""
            SELECT s.id
            FROM context_pack_sources s
            LEFT JOIN context_pack_source_chunks c ON c.source_id = s.id
            WHERE s.pack_id = :pack_id
            GROUP BY s.id
            HAVING COUNT(c.id) = 0
        """),
        {"pack_id": pack_id},
    ).mappings().fetchall()


def delete_chunks_for_pack(conn, pack_id):
    conn.execute(text("DELETE FROM context_pack_source_chunks WHERE pack_id = :pack_id"), {"pack_id": pack_id})


def fetch_source_ids_for_pack(conn, pack_id):
    return conn.execute(
        text("SELECT id FROM context_pack_sources WHERE pack_id = :pack_id ORDER BY id"),
        {"pack_id": pack_id},
    ).mappings().fetchall()


def fetch_pack_index_row(conn, pack_id, active_model):
    return conn.execute(
        text("""
            SELECT
                COUNT(DISTINCT s.id) AS sources,
                COUNT(DISTINCT c.source_id) AS indexed_sources,
                COUNT(c.id) AS chunks,
                SUM(CASE WHEN c.embedding IS NOT NULL AND c.embedding != '' THEN 1 ELSE 0 END) AS embedded_chunks,
                SUM(CASE WHEN :active_model != '' AND c.embedding IS NOT NULL AND c.embedding != '' AND c.embedding_model = :active_model THEN 1 ELSE 0 END) AS current_model_embedded_chunks,
                SUM(CASE WHEN :active_model != '' AND c.embedding IS NOT NULL AND c.embedding != '' AND COALESCE(c.embedding_model, '') != :active_model THEN 1 ELSE 0 END) AS stale_embedding_chunks,
                SUM(CASE
                    WHEN c.id IS NOT NULL AND (
                        (:active_model != '' AND (c.embedding IS NULL OR c.embedding = '' OR COALESCE(c.embedding_model, '') != :active_model))
                        OR (:active_model = '' AND (c.embedding IS NULL OR c.embedding = ''))
                    )
                    THEN 1 ELSE 0
                END) AS pending_embedding_chunks,
                COALESCE(SUM(c.tokens_estimate), 0) AS tokens_estimate,
                COALESCE(SUM(CASE
                    WHEN c.id IS NOT NULL AND (
                        (:active_model != '' AND (c.embedding IS NULL OR c.embedding = '' OR COALESCE(c.embedding_model, '') != :active_model))
                        OR (:active_model = '' AND (c.embedding IS NULL OR c.embedding = ''))
                    )
                    THEN c.tokens_estimate ELSE 0
                END), 0) AS pending_embedding_tokens_estimate,
                MAX(c.updated_at) AS latest_updated_at
            FROM context_pack_sources s
            LEFT JOIN context_pack_source_chunks c ON c.source_id = s.id
            WHERE s.pack_id = :pack_id
        """),
        {"pack_id": pack_id, "active_model": active_model},
    ).mappings().fetchone()


def fetch_chunks_for_embedding(conn, pack_id):
    return conn.execute(
        text("""
            SELECT id, content, tokens_estimate, embedding, embedding_model
            FROM context_pack_source_chunks
            WHERE pack_id = :pack_id
            ORDER BY id
        """),
        {"pack_id": pack_id},
    ).mappings().fetchall()


def update_chunk_embedding(conn, row_id, embedding, provider, model, dimension):
    conn.execute(
        text("""
            UPDATE context_pack_source_chunks
            SET embedding = :embedding,
                embedding_provider = :provider,
                embedding_model = :model,
                embedding_dimension = :dimension,
                embedded_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """),
        {
            "id": row_id,
            "embedding": embedding,
            "provider": provider,
            "model": model,
            "dimension": dimension,
        },
    )


def fetch_pack_chunks(conn, pack_id):
    rows = conn.execute(
        text("""
            SELECT
                c.id,
                c.source_id,
                c.chunk_index,
                c.content,
                c.tokens_estimate,
                c.embedding,
                c.embedding_provider,
                c.embedding_model,
                c.embedding_dimension,
                c.embedded_at,
                s.title,
                s.source_type,
                s.ref_type,
                s.ref_id,
                s.weight,
                s.status
            FROM context_pack_source_chunks c
            JOIN context_pack_sources s ON s.id = c.source_id
            WHERE c.pack_id = :pack_id
            ORDER BY c.source_id, c.chunk_index
        """),
        {"pack_id": pack_id},
    ).mappings().fetchall()
    return [dict(row) for row in rows]


def fetch_sources(conn, pack_id):
    rows = conn.execute(
        text("SELECT * FROM context_pack_sources WHERE pack_id = :pack_id ORDER BY created_at DESC, id DESC"),
        {"pack_id": pack_id},
    ).mappings().fetchall()
    return [row_to_source(row) for row in rows]


def fetch_pack_row(conn, pack_id):
    return conn.execute(
        text("SELECT * FROM context_packs WHERE id = :id"),
        {"id": pack_id},
    ).mappings().fetchone()


def get_pack_or_404(conn, pack_id):
    row = fetch_pack_row(conn, pack_id)
    if row and is_legacy_demo_pack(row):
        return None
    return row_to_pack(row, fetch_sources(conn, pack_id)) if row else None


def fetch_articles_by_ids(conn, article_ids):
    query = text("""
        SELECT id, title, content, summary, category
        FROM articles
        WHERE id IN :ids
    """).bindparams(bindparam("ids", expanding=True))
    return conn.execute(query, {"ids": article_ids}).mappings().fetchall()


def fetch_existing_article_ref_ids(conn, pack_id, article_ids):
    query = text("""
        SELECT ref_id
        FROM context_pack_sources
        WHERE pack_id = :pack_id AND ref_type = 'article' AND ref_id IN :ids
    """).bindparams(bindparam("ids", expanding=True))
    rows = conn.execute(query, {"pack_id": pack_id, "ids": article_ids}).mappings().fetchall()
    return {row["ref_id"] for row in rows}


def insert_context_pack_source(conn, values):
    result = conn.execute(
        text("""
            INSERT INTO context_pack_sources
                (pack_id, title, source_type, ref_type, ref_id, content, weight, status)
            VALUES
                (:pack_id, :title, :source_type, :ref_type, :ref_id, :content, :weight, :status)
        """),
        values,
    )
    return last_insert_id(conn, result)


def fetch_pack_metric_row(conn, pack_id):
    return conn.execute(
        text("SELECT intent, summary, tags FROM context_packs WHERE id = :id"),
        {"id": pack_id},
    ).mappings().fetchone()


def update_pack_metrics(conn, pack_id, quality, token_budget, freshness):
    conn.execute(
        text("""
            UPDATE context_packs
            SET quality = :quality, token_budget = :token_budget, freshness = :freshness
            WHERE id = :id
        """),
        {"quality": quality, "token_budget": token_budget, "freshness": freshness, "id": pack_id},
    )


def fetch_real_pack_rows(conn, where_sql="", params=None):
    sql = f"SELECT * FROM context_packs WHERE 1=1 {where_sql} ORDER BY updated_at DESC, id DESC"
    rows = conn.execute(text(sql), params or {}).mappings().fetchall()
    return [row for row in rows if not is_legacy_demo_pack(row)]


def count_sources_for_pack_ids(conn, pack_ids):
    if not pack_ids:
        return 0
    query = text("""
        SELECT COUNT(*)
        FROM context_pack_sources
        WHERE pack_id IN :ids
    """).bindparams(bindparam("ids", expanding=True))
    return conn.execute(query, {"ids": pack_ids}).scalar() or 0


def count_articles(conn):
    try:
        return conn.execute(text("SELECT COUNT(*) FROM articles")).scalar() or 0
    except Exception:
        return 0


def insert_context_pack(conn, values):
    result = conn.execute(
        text("""
            INSERT INTO context_packs
                (name, type, stage, description, intent, summary, next_action, key_points, tags, user_id)
            VALUES
                (:name, :type, :stage, :description, :intent, :summary, :next_action, :key_points, :tags, :user_id)
        """),
        values,
    )
    return last_insert_id(conn, result)


def update_context_pack(conn, pack_id, fields):
    params = {"id": pack_id, **fields}
    update_parts = [f"{column} = :{column}" for column in fields]
    conn.execute(text(f"UPDATE context_packs SET {', '.join(update_parts)} WHERE id = :id"), params)


def delete_context_pack(conn, pack_id):
    conn.execute(text("DELETE FROM context_packs WHERE id = :id"), {"id": pack_id})


def delete_context_pack_source(conn, pack_id, source_id):
    conn.execute(
        text("DELETE FROM context_pack_sources WHERE id = :source_id AND pack_id = :pack_id"),
        {"source_id": source_id, "pack_id": pack_id},
    )
