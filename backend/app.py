import os

from flask import Flask, request
from flask_cors import CORS
from routes.auth import auth_bp
from routes.ai import ai_bp
from routes.article import article_bp
from routes.upload import upload_bp
from routes.role import role_bp

app = Flask(__name__)

def parse_env_list(name, defaults):
    value = os.environ.get(name, "")
    items = [item.strip().rstrip("/") for item in value.split(",") if item.strip()]
    return items or defaults


ALLOWED_ORIGINS = parse_env_list("CORS_ORIGINS", [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://ai-vue3-python-flask-blog.vercel.app",
    "https://ai-vue3-python-flask-blog-copy.vercel.app",
    "https://lindablog.xyz",
    "https://www.lindablog.xyz",
]) + parse_env_list("CORS_ORIGIN_REGEXES", [
    r"^https://ai-vue3-python-flask-blog-[a-z0-9-]+-linsk27s-projects\.vercel\.app$",
    r"^https://[a-z0-9-]+\.vercel\.app$",
    r"^https://[a-z0-9-]+-[a-z0-9-]+-linsk27s-projects\.vercel\.app$",
])

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "APP-ID"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

app.config['SECRET_KEY'] = 'your-very-secret-key-123!@#'

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 204

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
