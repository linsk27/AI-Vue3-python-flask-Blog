# routes/auth.py
from flask import Blueprint, current_app, request, jsonify
#数据库
from sqlalchemy import text
from database import engine
# 加密库
from werkzeug.security import generate_password_hash,check_password_hash
# jwt
import datetime
import jwt
from middleware import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    avatar = data.get('avatar')
    email = data.get('email')

    # 简单校验
    if not username or not password:
        return {"status": 1, "msg": "用户名和密码不能为空"}, 400
    
    # 获取角色，默认为 user
    # role = data.get('role', 'user') # Old logic
    role_id = data.get('role_id') # New logic, if passed
    
    with engine.connect() as conn:
        # 如果没有指定role_id，默认使用 'user' 角色的ID
        if not role_id:
            role_id = conn.execute(text("SELECT id FROM roles WHERE name='user'")).scalar()
            
        # 判断用户名是否存在
        existing_user = conn.execute(
            text("SELECT * FROM users WHERE username=:username"), {"username": username}
        ).fetchone()

        if existing_user:
            return {"status": 1, "msg": "用户名已存在","data":{
        'success': False,
    }}, 400

        # 密码加密
        hashed_password = generate_password_hash(password)

        # 插入新用户 (Insert role_id instead of role string, though we might still have role string column? 
        # I kept the column in migration, but let's see. 
        # Actually I didn't drop 'role' column in migration script, I just added role_id.
        # So I should populate both for compatibility or just role_id.
        # Let's populate role_id. The 'role' column might be deprecated.
        # But wait, 'role' column is NOT NULL? Need to check schema. 
        # Assuming 'role' column allows null or default, or we update it too.
        # To be safe, let's fetch role name for 'role' column.
        role_name = conn.execute(text("SELECT name FROM roles WHERE id=:id"), {"id": role_id}).scalar()
        
        conn.execute(
            text("INSERT INTO users (username, password, avatar, role, role_id, email) VALUES (:username, :password, :avatar, :role, :role_id, :email)"),
            {"username": username, "password": hashed_password, "avatar": avatar or '', "role": role_name, "role_id": role_id, "email": email}
        )
        conn.commit()

    return {'status': 0, "msg": "注册成功","data":{
        'success': True,
    }}

@auth_bp.route('/api/user/info', methods=['GET'])
@token_required
def get_user_info(current_user_id):
    with engine.connect() as conn:
        user = conn.execute(
            text("SELECT id, username, avatar, role, role_id, email, created_at FROM users WHERE id=:id"),
            {"id": current_user_id}
        ).mappings().fetchone()
        
    if user:
        user_data = dict(user)
        if user_data.get('created_at'):
            user_data['created_at'] = user_data['created_at'].strftime('%Y-%m-%d')
        # Avue 需要 roles 数组
        # Avue 需要 roles 数组
        user_data['roles'] = [user_data.get('role', 'user')]
        
        # 权限列表，根据角色ID查询 permissions 表
        permissions = []
        if user_data.get('role_id'):
            with engine.connect() as conn:
                perms = conn.execute(text("""
                    SELECT p.code FROM permissions p
                    JOIN role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id = :rid
                """), {"rid": user_data['role_id']}).scalars().all()
                permissions = list(perms)
        
        user_data['permissions'] = permissions
        return jsonify({'status': 0, 'data': user_data})
    
    return jsonify({'status': 1, 'msg': '用户不存在'}), 404

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # 验证输入
    if not username or not password:
        return jsonify({'status': 1, 'msg': '用户名和密码不能为空'}), 400

    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM users WHERE username=:username "
            ), {"username": username}
        ).mappings().fetchone()

    if result and check_password_hash(result['password'], password):
        # 获取权限列表
        permissions = []
        if result.get('role_id'):
            with engine.connect() as conn:
                perms = conn.execute(text("""
                    SELECT p.code FROM permissions p
                    JOIN role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id = :rid
                """), {"rid": result['role_id']}).scalars().all()
                permissions = list(perms)

        # 生成JWT token
        token = jwt.encode({
            'user_id': result['id'],
            'username': result['username'],
            'role': result.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'status': 0, 'msg': '登录成功','data':{
            'id':result['id'],
            'username':result['username'],
            'role': result.get('role', 'user'),
            'email': result.get('email'),
            'permissions': permissions,
            'token':token,
        }})
    return jsonify({'status': 1, 'msg': '用户名或密码错误'}), 401

@auth_bp.route('/api/users', methods=['GET'])
def get_users():
    try:
        username = request.args.get('username')
        email = request.args.get('email')
        
        with engine.connect() as conn:
            sql = "SELECT id, username, avatar, created_at, role, role_id, email FROM users WHERE 1=1"
            params = {}
            
            if username:
                sql += " AND username LIKE :username"
                params['username'] = f"%{username}%"
            
            if email:
                sql += " AND email LIKE :email"
                params['email'] = f"%{email}%"
                
            sql += " ORDER BY created_at DESC"
            
            result = conn.execute(text(sql), params).mappings().fetchall()
            users = []
            for row in result:
                user = dict(row)
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat()
                users.append(user)
            return jsonify({'status': 0, 'data': users})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取用户列表失败', 'error': str(e)}), 500

@auth_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    avatar = data.get('avatar')
    password = data.get('password')
    role_id = data.get('role_id') # Accept role_id
    email = data.get('email')
    
    try:
        with engine.connect() as conn:
            # 检查用户是否存在
            existing = conn.execute(text("SELECT * FROM users WHERE id=:id"), {"id": user_id}).fetchone()
            if not existing:
                return jsonify({'status': 1, 'msg': '用户不存在'}), 404
            
            update_sql = "UPDATE users SET username=:username, avatar=:avatar, email=:email"
            params = {"username": username, "avatar": avatar, "id": user_id, "email": email}
            
            if password:
                update_sql += ", password=:password"
                params["password"] = generate_password_hash(password)
            
            if role_id:
                # Update role string too
                role_name = conn.execute(text("SELECT name FROM roles WHERE id=:id"), {"id": role_id}).scalar()
                update_sql += ", role=:role, role_id=:role_id"
                params["role"] = role_name
                params["role_id"] = role_id
                
            update_sql += " WHERE id=:id"
            
            conn.execute(text(update_sql), params)
            conn.commit()
            
            return jsonify({'status': 0, 'msg': '更新成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '更新失败', 'error': str(e)}), 500

@auth_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM users WHERE id=:id"), {"id": user_id})
            conn.commit()
            return jsonify({'status': 0, 'msg': '删除成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除失败', 'error': str(e)}), 500
