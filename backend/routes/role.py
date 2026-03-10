# routes/role.py
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from database import engine
from middleware import token_required

role_bp = Blueprint('role', __name__)

@role_bp.route('/api/roles', methods=['GET'])
@token_required
def get_roles(current_user_id):
    try:
        name = request.args.get('name')
        with engine.connect() as conn:
            # Check permissions (optional, for now just allow logged in users or add a check)
            # Fetch roles
            sql = "SELECT * FROM roles WHERE 1=1"
            params = {}
            if name:
                sql += " AND name LIKE :name"
                params['name'] = f"%{name}%"
            
            sql += " ORDER BY id"
            roles = conn.execute(text(sql), params).mappings().fetchall()
            
            roles_data = []
            for role in roles:
                role_dict = dict(role)
                if role_dict.get('created_at'):
                    role_dict['created_at'] = role_dict['created_at'].isoformat()
                    
                # Fetch permissions for this role
                perms = conn.execute(text("""
                    SELECT p.id, p.code, p.name 
                    FROM permissions p 
                    JOIN role_permissions rp ON p.id = rp.permission_id 
                    WHERE rp.role_id = :rid
                """), {"rid": role_dict['id']}).mappings().fetchall()
                
                role_dict['permissions'] = [dict(p)['id'] for p in perms] # Just IDs for the select box
                role_dict['permissionNames'] = [dict(p)['name'] for p in perms] # Names for display
                
                roles_data.append(role_dict)
                
            return jsonify({'status': 0, 'data': roles_data})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取角色列表失败', 'error': str(e)}), 500

@role_bp.route('/api/roles', methods=['POST'])
@token_required
def create_role(current_user_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    permission_ids = data.get('permissions', [])
    
    if not name:
        return jsonify({'status': 1, 'msg': '角色名称不能为空'}), 400
        
    try:
        with engine.connect() as conn:
            # Check if exists
            existing = conn.execute(text("SELECT id FROM roles WHERE name=:name"), {"name": name}).scalar()
            if existing:
                return jsonify({'status': 1, 'msg': '角色名称已存在'}), 400
                
            # Insert role
            result = conn.execute(text("INSERT INTO roles (name, description) VALUES (:name, :description)"), 
                                  {"name": name, "description": description})
            role_id = result.lastrowid
            
            # Insert permissions
            for pid in permission_ids:
                conn.execute(text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:rid, :pid)"), 
                             {"rid": role_id, "pid": pid})
            
            conn.commit()
            return jsonify({'status': 0, 'msg': '创建角色成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '创建角色失败', 'error': str(e)}), 500

@role_bp.route('/api/roles/<int:role_id>', methods=['PUT'])
@token_required
def update_role(current_user_id, role_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    permission_ids = data.get('permissions') # If None, don't update perms? Or empty list means clear? Assume list.
    
    try:
        with engine.connect() as conn:
            # Update role info
            if name:
                conn.execute(text("UPDATE roles SET name=:name, description=:description WHERE id=:id"), 
                             {"name": name, "description": description, "id": role_id})
            
            # Update permissions if provided
            if permission_ids is not None:
                # Delete old
                conn.execute(text("DELETE FROM role_permissions WHERE role_id=:id"), {"id": role_id})
                # Insert new
                for pid in permission_ids:
                    conn.execute(text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:rid, :pid)"), 
                                 {"rid": role_id, "pid": pid})
            
            conn.commit()
            return jsonify({'status': 0, 'msg': '更新角色成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '更新角色失败', 'error': str(e)}), 500

@role_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@token_required
def delete_role(current_user_id, role_id):
    try:
        with engine.connect() as conn:
            # Check if any user is using this role
            count = conn.execute(text("SELECT COUNT(*) FROM users WHERE role_id=:id"), {"id": role_id}).scalar()
            if count > 0:
                return jsonify({'status': 1, 'msg': '该角色下还有用户，无法删除'}), 400
                
            conn.execute(text("DELETE FROM roles WHERE id=:id"), {"id": role_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '删除角色成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除角色失败', 'error': str(e)}), 500

@role_bp.route('/api/permissions', methods=['GET'])
@token_required
def get_permissions(current_user_id):
    try:
        with engine.connect() as conn:
            perms = conn.execute(text("SELECT * FROM permissions")).mappings().fetchall()
            return jsonify({'status': 0, 'data': [dict(p) for p in perms]})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取权限列表失败', 'error': str(e)}), 500
