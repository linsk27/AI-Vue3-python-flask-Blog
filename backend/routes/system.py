from datetime import datetime, timezone
from time import perf_counter

from flask import Blueprint, jsonify
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from database import engine
from routes.context_pack import ensure_context_pack_tables, get_embedding_config
from middleware import permission_required


system_bp = Blueprint("system", __name__)

REQUIRED_TABLES = [
    "users",
    "articles",
    "ai_configs",
    "context_packs",
    "context_pack_sources",
    "context_pack_source_chunks",
    "ai_embedding_configs",
]
SELF_CHECK_HISTORY = []


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def build_check(name, ok, detail, severity="normal"):
    return {
        "name": name,
        "ok": bool(ok),
        "detail": detail,
        "severity": severity if ok else "high",
    }


def ensure_system_tables(conn):
    ensure_context_pack_tables(conn)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_packs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            type VARCHAR(50) DEFAULT 'project',
            stage VARCHAR(50) DEFAULT 'Draft',
            description TEXT,
            intent TEXT,
            summary TEXT,
            next_action TEXT,
            key_points LONGTEXT,
            tags LONGTEXT,
            quality INT DEFAULT 40,
            token_budget VARCHAR(40) DEFAULT '0.8k',
            freshness VARCHAR(40) DEFAULT '刚刚',
            user_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_pack_sources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pack_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            source_type VARCHAR(80) DEFAULT '文档',
            ref_type VARCHAR(80) DEFAULT 'custom',
            ref_id INT NULL,
            content LONGTEXT,
            weight VARCHAR(20) DEFAULT '中',
            status VARCHAR(40) DEFAULT '已收集',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pack_id) REFERENCES context_packs(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))
    conn.commit()


def run_system_checks():
    started = perf_counter()
    checks = []
    active_config = None

    try:
        with engine.connect() as conn:
            ensure_system_tables(conn)
            conn.execute(text("SELECT 1"))
        checks.append(build_check("database_connection", True, "数据库连接正常"))
    except SQLAlchemyError as exc:
        checks.append(build_check("database_connection", False, f"数据库连接失败：{exc}"))

    try:
        inspector = inspect(engine)
        missing_tables = [table for table in REQUIRED_TABLES if not inspector.has_table(table)]
        checks.append(
            build_check(
                "schema_integrity",
                not missing_tables,
                "核心数据表完整" if not missing_tables else f"缺少数据表：{', '.join(missing_tables)}",
            )
        )
    except SQLAlchemyError as exc:
        checks.append(build_check("schema_integrity", False, f"数据表检查失败：{exc}"))

    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT provider, model, api_key, is_active FROM ai_configs WHERE is_active = 1 LIMIT 1")
            ).mappings().fetchone()
            active_config = dict(row) if row else None

        has_key = bool(active_config and active_config.get("api_key"))
        checks.append(
            build_check(
                "ai_config",
                bool(active_config),
                f"当前模型：{active_config.get('provider')} / {active_config.get('model')}"
                if active_config
                else "未找到已启用的 AI 配置",
                "medium",
            )
        )
        checks.append(
            build_check(
                "ai_key",
                has_key,
                "AI Key 已配置" if has_key else "AI Key 为空，聊天和生成能力会降级",
                "medium",
            )
        )
    except SQLAlchemyError as exc:
        checks.append(build_check("ai_config", False, f"AI 配置检查失败：{exc}"))

    try:
        with engine.connect() as conn:
            embedding_config = get_embedding_config(conn)

        embedding_ok = (not embedding_config.get("enabled")) or embedding_config.get("configured")
        if not embedding_config.get("enabled"):
            embedding_detail = "Embedding 未启用，RAG 将使用关键词检索"
        elif embedding_config.get("configured"):
            embedding_detail = f"Embedding 已启用：{embedding_config.get('provider')} / {embedding_config.get('model')}"
        else:
            embedding_detail = "Embedding 已启用但模型或 API Key 不完整"
        checks.append(build_check("embedding_config", embedding_ok, embedding_detail, "medium"))
    except SQLAlchemyError as exc:
        checks.append(build_check("embedding_config", False, f"Embedding 配置检查失败：{exc}"))

    ok_count = sum(1 for item in checks if item["ok"])
    score = round(ok_count / len(checks) * 100) if checks else 0
    status = "healthy" if score >= 90 else "attention" if score >= 60 else "critical"

    return {
        "status": status,
        "score": score,
        "ok_count": ok_count,
        "total": len(checks),
        "checks": checks,
        "checked_at": utc_now_iso(),
        "duration_ms": round((perf_counter() - started) * 1000, 2),
    }

def record_self_check(report, source="manual"):
    stored_report = {**report, "source": source}
    SELF_CHECK_HISTORY.insert(0, stored_report)
    del SELF_CHECK_HISTORY[12:]
    return stored_report


@system_bp.route("/api/health", methods=["GET"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({
            "status": 0,
            "msg": "ok",
            "data": {
                "status": "healthy",
                "checked_at": utc_now_iso(),
            },
        })
    except SQLAlchemyError:
        return jsonify({
            "status": 1,
            "msg": "unhealthy",
            "data": {
                "status": "critical",
                "checked_at": utc_now_iso(),
            },
        }), 503


@system_bp.route("/api/system/self-check", methods=["GET", "POST"])
@permission_required("system:observe")
def self_check(current_user_id):
    report = run_system_checks()
    return jsonify({"status": 0, "msg": "系统自检完成", "data": record_self_check(report)})


@system_bp.route("/api/system/self-check/history", methods=["GET"])
@permission_required("system:observe")
def self_check_history(current_user_id):
    return jsonify({
        "status": 0,
        "msg": "ok",
        "data": {
            "reports": SELF_CHECK_HISTORY,
        },
    })
