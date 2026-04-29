from flask import Flask, request
from flask_cors import CORS
from routes.auth import auth_bp
from routes.ai import ai_bp
from routes.article import article_bp
from routes.upload import upload_bp
from routes.role import role_bp

app = Flask(__name__)
# 正确写法 ↓↓↓ 必须加 supports_credentials=True
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'your-very-secret-key-123!@#'

# ======================================
# 🔥 全局处理 OPTIONS（所有接口自动解决跨域）
# ======================================
@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 200

@app.route('/')
def home():
    return 'Flask started successfully.'

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(article_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(role_bp)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)