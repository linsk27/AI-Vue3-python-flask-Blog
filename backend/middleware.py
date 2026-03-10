from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return jsonify({'status': 1, 'msg': 'Token is missing!'}), 401
        
        try:
            # Check if token starts with Bearer
            if token.startswith('Bearer '):
                token = token.split(" ")[1]
                
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
            # Pass full token data if possible or just user_id. 
            # To support admin check, we might want to pass role info too.
            # But the signature is f(current_user_id, ...).
            # Let's keep it simple and fetch user role inside the route if needed, OR
            # modify this to pass a user object/dict.
            # For minimal impact, let's just stick to user_id and fetch role in the route.
        except Exception as e:
            return jsonify({'status': 1, 'msg': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(current_user_id, *args, **kwargs)
    
    return decorated
