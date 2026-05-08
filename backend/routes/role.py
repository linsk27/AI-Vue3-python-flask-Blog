# routes/role.py
from flask import Blueprint, request, jsonify
from sqlalchemy import text

from database import engine
from middleware import permission_required

role_bp = Blueprint('role', __name__)

BUILTIN_ROLES = {'admin', 'user'}


def _normalize_permission_ids(value):
    if value is None:
        return None
    if not isinstance(value, list):
        return []

    permission_ids = []
    for raw_id in value:
        try:
            permission_id = int(raw_id)
        except (TypeError, ValueError):
            continue
        if permission_id not in permission_ids:
            permission_ids.append(permission_id)
    return permission_ids


def _ensure_valid_permission_ids(conn, permission_ids):
    if not permission_ids:
        return []

    rows = conn.execute(text("SELECT id FROM permissions")).scalars().all()
    existing_ids = set(rows)
    invalid_ids = [pid for pid in permission_ids if pid not in existing_ids]
    if invalid_ids:
        return None
    return permission_ids


def _serialize_role(conn, role):
    role_dict = dict(role)
    if role_dict.get('created_at'):
        role_dict['created_at'] = role_dict['created_at'].isoformat()

    permissions = conn.execute(text("""
        SELECT p.id, p.code, p.name
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = :role_id
        ORDER BY p.id
    """), {"role_id": role_dict['id']}).mappings().fetchall()

    role_dict['permissions'] = [permission['id'] for permission in permissions]
    role_dict['permissionNames'] = [permission['name'] for permission in permissions]
    role_dict['readonly'] = role_dict.get('name') in BUILTIN_ROLES
    return role_dict


@role_bp.route('/api/roles', methods=['GET'])
@permission_required('role:manage')
def get_roles(current_user_id):
    try:
        name = request.args.get('name')
        with engine.connect() as conn:
            sql = "SELECT * FROM roles WHERE 1=1"
            params = {}
            if name:
                sql += " AND name LIKE :name"
                params['name'] = f"%{name}%"

            sql += " ORDER BY id"
            roles = conn.execute(text(sql), params).mappings().fetchall()
            return jsonify({
                'status': 0,
                'data': [_serialize_role(conn, role) for role in roles]
            })
    except Exception as e:
        return jsonify({'status': 1, 'msg': 'Failed to get roles', 'error': str(e)}), 500


@role_bp.route('/api/roles', methods=['POST'])
@permission_required('role:manage')
def create_role(current_user_id):
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    description = data.get('description') or ''
    permission_ids = _normalize_permission_ids(data.get('permissions', []))

    if not name:
        return jsonify({'status': 1, 'msg': 'Role name is required'}), 400
    if name in BUILTIN_ROLES:
        return jsonify({'status': 1, 'msg': 'Built-in role names are reserved'}), 400

    try:
        with engine.begin() as conn:
            existing = conn.execute(
                text("SELECT id FROM roles WHERE name=:name"),
                {"name": name}
            ).scalar()
            if existing:
                return jsonify({'status': 1, 'msg': 'Role name already exists'}), 400

            valid_permission_ids = None
            if permission_ids is not None:
                valid_permission_ids = _ensure_valid_permission_ids(conn, permission_ids)
                if valid_permission_ids is None:
                    return jsonify({'status': 1, 'msg': 'Invalid permission id'}), 400

            result = conn.execute(
                text("INSERT INTO roles (name, description) VALUES (:name, :description)"),
                {"name": name, "description": description}
            )
            role_id = result.lastrowid

            for permission_id in valid_permission_ids:
                conn.execute(
                    text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"),
                    {"role_id": role_id, "permission_id": permission_id}
                )

            return jsonify({
                'status': 0,
                'msg': 'Role created',
                'data': {'id': role_id}
            })
    except Exception as e:
        return jsonify({'status': 1, 'msg': 'Failed to create role', 'error': str(e)}), 500


@role_bp.route('/api/roles/<int:role_id>', methods=['PUT'])
@permission_required('role:manage')
def update_role(current_user_id, role_id):
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    description = data.get('description') or ''
    permission_ids = _normalize_permission_ids(data.get('permissions')) if 'permissions' in data else None

    try:
        with engine.begin() as conn:
            existing_role = conn.execute(
                text("SELECT id, name FROM roles WHERE id=:id"),
                {"id": role_id}
            ).mappings().first()
            if not existing_role:
                return jsonify({'status': 1, 'msg': 'Role not found'}), 404

            current_name = existing_role['name']
            if current_name in BUILTIN_ROLES:
                return jsonify({'status': 1, 'msg': 'Built-in roles are read-only'}), 400
            if not name:
                return jsonify({'status': 1, 'msg': 'Role name is required'}), 400
            if name in BUILTIN_ROLES:
                return jsonify({'status': 1, 'msg': 'Built-in role names are reserved'}), 400

            duplicated = conn.execute(
                text("SELECT id FROM roles WHERE name=:name AND id != :id"),
                {"name": name, "id": role_id}
            ).scalar()
            if duplicated:
                return jsonify({'status': 1, 'msg': 'Role name already exists'}), 400

            valid_permission_ids = None
            if permission_ids is not None:
                valid_permission_ids = _ensure_valid_permission_ids(conn, permission_ids)
                if valid_permission_ids is None:
                    return jsonify({'status': 1, 'msg': 'Invalid permission id'}), 400

            conn.execute(
                text("UPDATE roles SET name=:name, description=:description WHERE id=:id"),
                {"name": name, "description": description, "id": role_id}
            )

            if valid_permission_ids is not None:
                conn.execute(text("DELETE FROM role_permissions WHERE role_id=:id"), {"id": role_id})
                for permission_id in valid_permission_ids:
                    conn.execute(
                        text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"),
                        {"role_id": role_id, "permission_id": permission_id}
                    )

            return jsonify({'status': 0, 'msg': 'Role updated', 'data': {'id': role_id}})
    except Exception as e:
        return jsonify({'status': 1, 'msg': 'Failed to update role', 'error': str(e)}), 500


@role_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@permission_required('role:manage')
def delete_role(current_user_id, role_id):
    try:
        with engine.begin() as conn:
            role_name = conn.execute(
                text("SELECT name FROM roles WHERE id=:id"),
                {"id": role_id}
            ).scalar()
            if not role_name:
                return jsonify({'status': 1, 'msg': 'Role not found'}), 404
            if role_name in BUILTIN_ROLES:
                return jsonify({'status': 1, 'msg': 'Built-in roles cannot be deleted'}), 400

            user_count = conn.execute(
                text("SELECT COUNT(*) FROM users WHERE role_id=:id"),
                {"id": role_id}
            ).scalar()
            if user_count > 0:
                return jsonify({'status': 1, 'msg': 'Role is still assigned to users'}), 400

            conn.execute(text("DELETE FROM role_permissions WHERE role_id=:id"), {"id": role_id})
            conn.execute(text("DELETE FROM roles WHERE id=:id"), {"id": role_id})
            return jsonify({'status': 0, 'msg': 'Role deleted'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': 'Failed to delete role', 'error': str(e)}), 500


@role_bp.route('/api/permissions', methods=['GET'])
@permission_required('role:manage')
def get_permissions(current_user_id):
    try:
        with engine.connect() as conn:
            permissions = conn.execute(text("SELECT * FROM permissions ORDER BY id")).mappings().fetchall()
            return jsonify({'status': 0, 'data': [dict(permission) for permission in permissions]})
    except Exception as e:
        return jsonify({'status': 1, 'msg': 'Failed to get permissions', 'error': str(e)}), 500
