# app.py
from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.ai import ai_bp
from routes.article import article_bp
from routes.upload import upload_bp
from routes.role import role_bp

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your-very-secret-key-123!@#'  # 必须是字符串

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
    app.run(host='0.0.0.0', port=5000)
