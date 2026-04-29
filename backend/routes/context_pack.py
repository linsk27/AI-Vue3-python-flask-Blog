from flask import Blueprint, request, jsonify
from sqlalchemy import text
from database import engine
from middleware import token_required
import json

context_pack_bp = Blueprint('context_pack', __name__)


def ensure_context_pack_tables(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_packs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(50) DEFAULT 'project',
            description TEXT,
            intent TEXT,
            summary TEXT,
            key_points JSON,
            tags JSON,
            owner_id INT,
            visibility VARCHAR(20) DEFAULT 'private',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_pack_documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pack_id INT NOT NULL,
            document_id INT NOT NULL,
            note VARCHAR(500),
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_pack_document (pack_id, document_id),
            FOREIGN KEY (pack_id) REFERENCES context_packs(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES articles(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))


def parse_json_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def pack_to_dict(row, documents=None):
    pack = dict(row)
    pack['tags'] = parse_json_list(pack.get('tags'))
    pack['keyPoints'] = parse_json_list(pack.get('key_points'))
    pack.pop('key_points', None)
    pack['documents'] = documents if documents is not None else []
    if pack.get('created_at'):
        pack['created_at'] = pack['created_at'].isoformat()
    if pack.get('updated_at'):
        pack['updated_at'] = pack['updated_at'].isoformat()
    return pack


def fetch_pack_documents(conn, pack_id):
    result = conn.execute(text("""
        SELECT a.id, a.title, cpd.note, cpd.sort_order
        FROM context_pack_documents cpd
        JOIN articles a ON a.id = cpd.document_id
        WHERE cpd.pack_id = :pack_id
        ORDER BY cpd.sort_order ASC, cpd.created_at ASC
    """), {"pack_id": pack_id}).mappings().fetchall()
    return [dict(row) for row in result]


@context_pack_bp.route('/api/context-packs', methods=['GET'])
def get_context_packs():
    try:
        pack_type = request.args.get('type', '')
        owner_id = request.args.get('owner_id', '')

        with engine.connect() as conn:
            ensure_context_pack_tables(conn)

            sql = """
                SELECT cp.*, COUNT(cpd.id) AS documents_count
                FROM context_packs cp
                LEFT JOIN context_pack_documents cpd ON cp.id = cpd.pack_id
                WHERE 1=1
            """
            params = {}

            if pack_type:
                sql += " AND cp.type = :type"
                params['type'] = pack_type
            if owner_id:
                sql += " AND cp.owner_id = :owner_id"
                params['owner_id'] = owner_id

            sql += " GROUP BY cp.id ORDER BY cp.updated_at DESC, cp.created_at DESC"
            rows = conn.execute(text(sql), params).mappings().fetchall()

            packs = []
            for row in rows:
                documents = fetch_pack_documents(conn, row['id'])
                pack = pack_to_dict(row, documents)
                pack['documents_count'] = row['documents_count']
                packs.append(pack)

            return jsonify({'status': 0, 'data': packs})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取上下文包失败', 'error': str(e)}), 500


@context_pack_bp.route('/api/context-packs/<int:pack_id>', methods=['GET'])
def get_context_pack(pack_id):
    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            row = conn.execute(
                text("SELECT * FROM context_packs WHERE id = :id"),
                {"id": pack_id}
            ).mappings().fetchone()

            if not row:
                return jsonify({'status': 1, 'msg': '上下文包不存在'}), 404

            documents = fetch_pack_documents(conn, pack_id)
            return jsonify({'status': 0, 'data': pack_to_dict(row, documents)})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取上下文包失败', 'error': str(e)}), 500


@context_pack_bp.route('/api/context-packs', methods=['POST'])
@token_required
def create_context_pack(current_user_id):
    data = request.get_json() or {}
    name = data.get('name')

    if not name:
        return jsonify({'status': 1, 'msg': '上下文包名称不能为空'}), 400

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            result = conn.execute(text("""
                INSERT INTO context_packs (
                    name, type, description, intent, summary, key_points, tags, owner_id, visibility
                )
                VALUES (
                    :name, :type, :description, :intent, :summary, :key_points, :tags, :owner_id, :visibility
                )
            """), {
                "name": name,
                "type": data.get('type', 'project'),
                "description": data.get('description', ''),
                "intent": data.get('intent', ''),
                "summary": data.get('summary', ''),
                "key_points": json.dumps(data.get('keyPoints') or data.get('key_points') or [], ensure_ascii=False),
                "tags": json.dumps(data.get('tags') or [], ensure_ascii=False),
                "owner_id": current_user_id,
                "visibility": data.get('visibility', 'private')
            })
            conn.commit()

            pack_id = result.lastrowid
            if not pack_id:
                pack_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            return jsonify({'status': 0, 'msg': '上下文包已创建', 'data': {'id': pack_id}})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '创建上下文包失败', 'error': str(e)}), 500


@context_pack_bp.route('/api/context-packs/<int:pack_id>', methods=['PUT'])
@token_required
def update_context_pack(current_user_id, pack_id):
    data = request.get_json() or {}

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            existing = conn.execute(
                text("SELECT owner_id FROM context_packs WHERE id = :id"),
                {"id": pack_id}
            ).fetchone()
            if not existing:
                return jsonify({'status': 1, 'msg': '上下文包不存在'}), 404
            if existing.owner_id and existing.owner_id != current_user_id:
                return jsonify({'status': 1, 'msg': '无权修改该上下文包'}), 403

            update_parts = []
            params = {"id": pack_id}
            field_map = {
                "name": "name",
                "type": "type",
                "description": "description",
                "intent": "intent",
                "summary": "summary",
                "visibility": "visibility"
            }

            for body_field, column in field_map.items():
                if body_field in data:
                    update_parts.append(f"{column} = :{column}")
                    params[column] = data.get(body_field)

            if 'tags' in data:
                update_parts.append("tags = :tags")
                params['tags'] = json.dumps(data.get('tags') or [], ensure_ascii=False)
            if 'keyPoints' in data or 'key_points' in data:
                update_parts.append("key_points = :key_points")
                params['key_points'] = json.dumps(data.get('keyPoints') or data.get('key_points') or [], ensure_ascii=False)

            if not update_parts:
                return jsonify({'status': 0, 'msg': '无变更'})

            conn.execute(text(f"UPDATE context_packs SET {', '.join(update_parts)} WHERE id = :id"), params)
            conn.commit()
            return jsonify({'status': 0, 'msg': '上下文包已更新'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '更新上下文包失败', 'error': str(e)}), 500


@context_pack_bp.route('/api/context-packs/<int:pack_id>', methods=['DELETE'])
@token_required
def delete_context_pack(current_user_id, pack_id):
    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            existing = conn.execute(
                text("SELECT owner_id FROM context_packs WHERE id = :id"),
                {"id": pack_id}
            ).fetchone()
            if not existing:
                return jsonify({'status': 1, 'msg': '上下文包不存在'}), 404
            if existing.owner_id and existing.owner_id != current_user_id:
                return jsonify({'status': 1, 'msg': '无权删除该上下文包'}), 403

            conn.execute(text("DELETE FROM context_packs WHERE id = :id"), {"id": pack_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '上下文包已删除'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除上下文包失败', 'error': str(e)}), 500


@context_pack_bp.route('/api/context-packs/<int:pack_id>/documents', methods=['POST'])
@token_required
def add_context_pack_document(current_user_id, pack_id):
    data = request.get_json() or {}
    document_id = data.get('document_id')
    if not document_id:
        return jsonify({'status': 1, 'msg': '缺少文档 ID'}), 400

    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = conn.execute(text("SELECT owner_id FROM context_packs WHERE id = :id"), {"id": pack_id}).fetchone()
            if not pack:
                return jsonify({'status': 1, 'msg': '上下文包不存在'}), 404
            if pack.owner_id and pack.owner_id != current_user_id:
                return jsonify({'status': 1, 'msg': '无权修改该上下文包'}), 403

            conn.execute(text("""
                INSERT INTO context_pack_documents (pack_id, document_id, note, sort_order)
                VALUES (:pack_id, :document_id, :note, :sort_order)
                ON DUPLICATE KEY UPDATE note = VALUES(note), sort_order = VALUES(sort_order)
            """), {
                "pack_id": pack_id,
                "document_id": document_id,
                "note": data.get('note', ''),
                "sort_order": data.get('sort_order', 0)
            })
            conn.commit()
            return jsonify({'status': 0, 'msg': '文档已加入上下文包'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '添加文档失败', 'error': str(e)}), 500


@context_pack_bp.route('/api/context-packs/<int:pack_id>/documents/<int:document_id>', methods=['DELETE'])
@token_required
def remove_context_pack_document(current_user_id, pack_id, document_id):
    try:
        with engine.connect() as conn:
            ensure_context_pack_tables(conn)
            pack = conn.execute(text("SELECT owner_id FROM context_packs WHERE id = :id"), {"id": pack_id}).fetchone()
            if not pack:
                return jsonify({'status': 1, 'msg': '上下文包不存在'}), 404
            if pack.owner_id and pack.owner_id != current_user_id:
                return jsonify({'status': 1, 'msg': '无权修改该上下文包'}), 403

            conn.execute(text("""
                DELETE FROM context_pack_documents
                WHERE pack_id = :pack_id AND document_id = :document_id
            """), {"pack_id": pack_id, "document_id": document_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '文档已移出上下文包'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '移除文档失败', 'error': str(e)}), 500
