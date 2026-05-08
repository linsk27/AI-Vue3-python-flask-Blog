# app.py
import os

from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.ai import ai_bp
from routes.article import article_bp
from routes.upload import upload_bp
from routes.role import role_bp
from routes.system import system_bp
from routes.context_pack import context_pack_bp
from config import SECRET_KEY

app = Flask(__name__)

allowed_origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ai-vue3-python-flask-blog.vercel.app",
]

extra_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": allowed_origins
            + extra_origins
            + [
                r"^https://[a-z0-9-]+\.vercel\.app$",
                r"^https://[a-z0-9-]+-[a-z0-9-]+-linsk27s-projects\.vercel\.app$",
            ],
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization", "APP-ID"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    },
)

app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def home():
    return 'ContextForge backend started successfully.'

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(article_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(role_bp)
app.register_blueprint(system_bp)
app.register_blueprint(context_pack_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
