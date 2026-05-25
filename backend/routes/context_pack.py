from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import text
import jwt

from database import engine
from db.schema import ensure_context_pack_tables, ensure_embedding_config_table
from services.context_pack_service import (
    add_article_sources,
    add_custom_sources,
    add_sources_to_pack,
    build_markdown,
    build_prompt,
    build_workspace_stats,
    create_context_pack_record,
    create_embedding,
    delete_context_pack_record,
    delete_context_pack_source_record,
    fetch_real_pack_rows,
    fetch_sources,
    get_embedding_config,
    get_pack_chunks,
    get_pack_index_stats,
    get_pack_or_404,
    is_legacy_demo_pack,
    json_dumps,
    json_loads,
    mask_secret,
    rebuild_pack_chunks,
    refresh_pack_embeddings,
    refresh_pack_metrics,
    row_to_pack,
    sync_pack_chunks,
    update_context_pack_fields,
)

__all__ = [
    "context_pack_bp",
    "ensure_context_pack_tables",
    "ensure_embedding_config_table",
    "get_embedding_config",
    "get_pack_chunks",
    "get_pack_or_404",
    "get_request_user",
    "can_view_pack",
    "can_manage_pack",
    "create_embedding",
    "mask_secret",
    "add_article_sources",
    "add_custom_sources",
    "is_legacy_demo_pack",
    "json_dumps",
    "json_loads",
]


context_pack_bp = Blueprint("context_pack", __name__)


def get_optional_user_id():
    user, _ = get_request_user(required=False)
    return user.get("id") if user else None


def get_request_user(required=False):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        if required:
            return None, (jsonify({"status": 1, "msg": "请先登录后再操作上下文包"}), 401)
        return None, None

    try:
        token = auth_header.split(" ", 1)[1] if auth_header.startswith("Bearer ") else auth_header
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("missing user_id")

        with engine.connect() as conn:
            user = conn.execute(
                text("SELECT id, username, role, role_id FROM users WHERE id = :id"),
                {"id": user_id},
            ).mappings().fetchone()
            if not user:
                raise ValueError("user not found")

            permissions = []
            if user.get("role_id"):
                permissions = list(conn.execute(text("""
                    SELECT p.code FROM permissions p
                    JOIN role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id = :rid
                """), {"rid": user["role_id"]}).scalars().all())

        user_data = dict(user)
        user_data["permissions"] = permissions
        return user_data, None
    except Exception as exc:
        if required:
            return None, (jsonify({"status": 1, "msg": "登录状态无效，请重新登录", "error": str(exc)}), 401)
        return None, None


def is_admin_user(user):
    if not user:
        return False
    permissions = set(user.get("permissions") or [])
    return user.get("role") == "admin" or "user:manage" in permissions or "context_pack:manage" in permissions


def can_view_pack(user, pack):
    if not pack:
        return False
    owner_id = pack.get("user_id")
    if owner_id is None:
        return True
    return bool(user and (is_admin_user(user) or int(owner_id) == int(user["id"])))


def can_manage_pack(user, pack):
    if not pack or not user:
        return False
    if is_admin_user(user):
        return True
    owner_id = pack.get("user_id")
    return owner_id is not None and int(owner_id) == int(user["id"])


def require_pack_access(pack, user, manage=False):
    allowed = can_manage_pack(user, pack) if manage else can_view_pack(user, pack)
    if allowed:
        return None
    return jsonify({"status": 1, "msg": "无权操作该上下文包"}), 403


def filter_visible_pack_rows(rows, user):
    return [row for row in rows if can_view_pack(user, row)]


def enrich_pack_access(pack, user):
    if not pack:
        return pack

    pack["visibility"] = "public" if pack.get("user_id") is None else "private"
    pack["canManage"] = can_manage_pack(user, pack)
    pack["canUseRag"] = can_view_pack(user, pack)
    return pack


@context_pack_bp.route("/api/context-packs", methods=["GET"])
def list_context_packs():
    pack_type = request.args.get("type")
    search = request.args.get("search", "")

    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)

            where_sql = ""
            params = {}
            if pack_type and pack_type != "all":
                where_sql += " AND type = :type"
                params["type"] = pack_type
            if search:
                where_sql += " AND (name LIKE :search OR description LIKE :search OR intent LIKE :search)"
                params["search"] = f"%{search}%"

            rows = fetch_real_pack_rows(conn, where_sql, params)
            rows = filter_visible_pack_rows(rows, user)
            packs = [
                enrich_pack_access(row_to_pack(row, fetch_sources(conn, row["id"])), user)
                for row in rows
            ]

        return jsonify({"status": 0, "data": packs})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/stats", methods=["GET"])
def context_pack_stats():
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            stats = build_workspace_stats(conn, user, can_view_pack=can_view_pack)
        return jsonify({"status": 0, "data": stats})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取上下文包统计失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs", methods=["POST"])
def create_context_pack():
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"status": 1, "msg": "上下文包名称不能为空"}), 400

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack_id = create_context_pack_record(conn, data, user["id"])
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "上下文包已创建", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "创建上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>", methods=["GET"])
def get_context_pack(pack_id):
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)
        if not pack:
            return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
        access_error = require_pack_access(pack, user, manage=False)
        if access_error:
            return access_error
        return jsonify({"status": 0, "data": enrich_pack_access(pack, user)})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>", methods=["PUT"])
def update_context_pack(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    if not data:
        return jsonify({"status": 0, "msg": "无变更"})

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            changed = update_context_pack_fields(conn, pack_id, data)
            if not changed:
                return jsonify({"status": 0, "msg": "无变更"})
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "上下文包已更新", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "更新上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>", methods=["DELETE"])
def delete_context_pack(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            delete_context_pack_record(conn, pack_id)
            conn.commit()
        return jsonify({"status": 0, "msg": "上下文包已删除"})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "删除上下文包失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/rag-index", methods=["GET"])
def get_context_pack_rag_index(pack_id):
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404

            access_error = require_pack_access(pack, user, manage=False)
            if access_error:
                return access_error

            index_stats = get_pack_index_stats(conn, pack_id)

        return jsonify({"status": 0, "data": index_stats})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "获取 RAG 索引状态失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/rag-index/rebuild", methods=["POST"])
def rebuild_context_pack_rag_index(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404

            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error

            index_stats = rebuild_pack_chunks(conn, pack_id)
            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({
            "status": 0,
            "msg": "RAG 索引已重建",
            "data": {
                "pack": pack,
                "index": index_stats,
            },
        })
    except Exception as exc:
        return jsonify({"status": 1, "msg": "重建 RAG 索引失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/rag-index/embeddings", methods=["POST"])
def build_context_pack_embeddings(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    force = bool(data.get("force"))
    dry_run = bool(data.get("dry_run"))

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404

            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error

            sync_pack_chunks(conn, pack_id)
            index_stats, error = refresh_pack_embeddings(conn, pack_id, force=force, dry_run=dry_run)
            if error:
                conn.rollback()
                return jsonify({"status": 1, "msg": error}), 400

            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({
            "status": 0,
            "msg": "语义索引预估完成" if dry_run else "语义索引已生成",
            "data": {
                "pack": pack,
                "index": index_stats,
            },
        })
    except Exception as exc:
        return jsonify({"status": 1, "msg": "生成语义索引失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/sources", methods=["POST"])
@context_pack_bp.route("/api/context-packs/<int:pack_id>/articles", methods=["POST"])
def add_context_pack_sources(pack_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    article_ids = data.get("article_ids") or []
    sources = data.get("sources") or []

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            article_result, custom_added, total_added = add_sources_to_pack(conn, pack_id, article_ids, sources)

            if (article_ids or sources) and total_added == 0:
                conn.rollback()
                if article_ids and article_result["found"] == 0:
                    return jsonify({"status": 1, "msg": "选中的文章不存在或已被删除"}), 400
                if article_ids and article_result["duplicates"] > 0:
                    return jsonify({"status": 1, "msg": "选中的文章已经在上下文包中"}), 409
                return jsonify({"status": 1, "msg": "没有找到可加入的真实资料"}), 400

            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "资料已加入上下文包", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "加入资料失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-pack-sources", methods=["POST"])
def add_context_pack_sources_flat():
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    pack_id = data.get("pack_id")
    if not pack_id:
        return jsonify({"status": 1, "msg": "缺少上下文包 ID"}), 400

    try:
        pack_id = int(pack_id)
    except (TypeError, ValueError):
        return jsonify({"status": 1, "msg": "上下文包 ID 无效"}), 400

    request_data = {
        "article_ids": data.get("article_ids") or [],
        "sources": data.get("sources") or [],
    }

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            article_result, custom_added, total_added = add_sources_to_pack(
                conn,
                pack_id,
                request_data["article_ids"],
                request_data["sources"],
            )

            if (request_data["article_ids"] or request_data["sources"]) and total_added == 0:
                conn.rollback()
                if request_data["article_ids"] and article_result["found"] == 0:
                    return jsonify({"status": 1, "msg": "选中的文章不存在或已被删除"}), 400
                if request_data["article_ids"] and article_result["duplicates"] > 0:
                    return jsonify({"status": 1, "msg": "选中的文章已经在上下文包中"}), 409
                return jsonify({"status": 1, "msg": "没有找到可加入的真实资料"}), 400

            refresh_pack_metrics(conn, pack_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "资料已加入上下文包", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "加入资料失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/sources/<int:source_id>", methods=["DELETE"])
def delete_context_pack_source(pack_id, source_id):
    user, auth_error = get_request_user(required=True)
    if auth_error:
        return auth_error

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
            if not pack:
                return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
            access_error = require_pack_access(pack, user, manage=True)
            if access_error:
                return access_error
            delete_context_pack_source_record(conn, pack_id, source_id)
            conn.commit()
            pack = enrich_pack_access(get_pack_or_404(conn, pack_id), user)

        return jsonify({"status": 0, "msg": "资料已移除", "data": pack})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "移除资料失败", "error": str(exc)}), 500


@context_pack_bp.route("/api/context-packs/<int:pack_id>/markdown", methods=["GET"])
def export_context_pack_markdown(pack_id):
    try:
        user, auth_error = get_request_user(required=False)
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = get_pack_or_404(conn, pack_id)
        if not pack:
            return jsonify({"status": 1, "msg": "上下文包不存在"}), 404
        access_error = require_pack_access(pack, user, manage=False)
        if access_error:
            return access_error

        markdown = build_markdown(pack)
        prompt = build_prompt(markdown)
        return jsonify({"status": 0, "data": {"markdown": markdown, "prompt": prompt}})
    except Exception as exc:
        return jsonify({"status": 1, "msg": "导出上下文包失败", "error": str(exc)}), 500
