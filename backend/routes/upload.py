from flask import Blueprint, request, jsonify, send_from_directory, current_app
import os
import uuid
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 1, 'msg': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'status': 1, 'msg': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # 生成安全的文件名，并加上 UUID 前缀防止冲突
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        
        # 返回文件访问 URL
        # 假设服务器地址是 http://localhost:5000
        # 这里返回相对路径，前端可以拼，或者返回完整路径
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
        return jsonify({'status': 1, 'msg': '不支持的文件类型'}), 400

@upload_bp.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
