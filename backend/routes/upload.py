from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from middleware import token_required

upload_bp = Blueprint('upload', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGE_UPLOAD_BYTES = int(os.getenv('MAX_IMAGE_UPLOAD_MB', '5')) * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user_id):
    if request.content_length and request.content_length > MAX_IMAGE_UPLOAD_BYTES:
        return jsonify({'status': 1, 'msg': '图片不能超过 5MB'}), 413

    if 'file' not in request.files:
        return jsonify({'status': 1, 'msg': '请选择要上传的图片'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'status': 1, 'msg': '请选择要上传的图片'}), 400
        
    if file and allowed_file(file.filename):
        # 生成安全的文件名，并加上 UUID 前缀防止冲突
        filename = secure_filename(file.filename or '')
        if not filename:
            return jsonify({'status': 1, 'msg': '文件名无效'}), 400

        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(save_path)

        if os.path.getsize(save_path) > MAX_IMAGE_UPLOAD_BYTES:
            os.remove(save_path)
            return jsonify({'status': 1, 'msg': '图片不能超过 5MB'}), 413
        
        file_url = f"/api/uploads/{unique_filename}"
        
        return jsonify({
            'status': 0, 
            'msg': '上传成功', 
            'data': {
                'url': file_url,
                'name': filename
            }
        })
    else:
        return jsonify({'status': 1, 'msg': '仅支持 png、jpg、jpeg、gif、webp 图片'}), 400

@upload_bp.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
