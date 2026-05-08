from functools import wraps
from flask import request, jsonify, current_app
import jwt
from sqlalchemy import text
from database import engine


def _extract_bearer_token():
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token.split(" ", 1)[1]
    return token


def load_user_permissions(role_id):
    if not role_id:
        return []

    with engine.connect() as conn:
        permissions = conn.execute(text("""
            SELECT p.code FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = :rid
        """), {"rid": role_id}).scalars().all()
        return list(permissions)


def load_current_user():
    token = _extract_bearer_token()
    if not token:
        return None, (jsonify({'status': 1, 'msg': 'Token is missing!'}), 401)

    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = data['user_id']
    except Exception as e:
        return None, (jsonify({'status': 1, 'msg': 'Token is invalid!', 'error': str(e)}), 401)

    with engine.connect() as conn:
        user = conn.execute(
            text("SELECT id, username, avatar, role, role_id, email FROM users WHERE id=:id"),
            {"id": user_id}
        ).mappings().fetchone()

    if not user:
        return None, (jsonify({'status': 1, 'msg': 'User does not exist!'}), 401)

    user_data = dict(user)
    user_data['permissions'] = load_user_permissions(user_data.get('role_id'))
    return user_data, None


def load_optional_user():
    token = _extract_bearer_token()
    if not token:
        return None

    current_user, error = load_current_user()
    if error:
        return None
    return current_user


def user_has_permission(user, *permission_codes):
    if not user:
        return False
    if user.get('role') == 'admin':
        return True
    permissions = set(user.get('permissions') or [])
    return any(code in permissions for code in permission_codes)


def permission_required(*permission_codes):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user, error = load_current_user()
            if error:
                return error

            if not user_has_permission(current_user, *permission_codes):
                return jsonify({'status': 1, 'msg': 'Permission denied!'}), 403

            return f(current_user['id'], *args, **kwargs)

        return decorated

    return decorator

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user, error = load_current_user()
        if error:
            return error

        return f(current_user['id'], *args, **kwargs)
    
    return decorated
