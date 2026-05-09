# 知境 ContextForge

知境 ContextForge 是一个从 Vue3 + Flask 博客升级来的 AI 知识工作台。当前核心目标不是普通博客，而是把文章、资料、上下文包、AI 对话和 RAG 检索组织成可复用的知识系统。

产品边界已经拆清楚：

- `front/`：普通用户使用的知识工作台，负责写作、知识库、上下文包和 AI 对话。
- `avue-cli/`：管理员使用的独立管理台，负责用户、角色、内容运营、AI 配置、Embedding 和系统自检。
- `backend/`：统一 API、鉴权、权限、AI、RAG 和数据持久化。

交付版架构、群体和使用说明见 [docs/contextforge-architecture-usage.md](docs/contextforge-architecture-usage.md)。
历史项目解析见 [docs/project-analysis-and-usage.md](docs/project-analysis-and-usage.md)。

## 技术栈

- 前台：Vue 3、Vite、TypeScript、Pinia、Vue Router、Element Plus、Quill、Marked、Mammoth
- 管理台：Avue、Vue 3、Vite、Element Plus
- 后端：Python Flask、SQLAlchemy、PyMySQL、JWT、Flask-CORS
- 数据库：MySQL
- AI：OpenAI-compatible Chat API，可配置多模型；Embedding 需要单独配置

## 快速启动

### 1. 准备数据库

先创建 MySQL 数据库：

```sql
CREATE DATABASE lsk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 启动后端

```powershell
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
python app.py
```

后端默认运行在 `http://127.0.0.1:5000`。

`backend/.env` 里最重要的是：

- `DATABASE_URL`：MySQL 连接地址
- `SECRET_KEY`：JWT 密钥，正式环境必须换成随机长字符串
- `CORS_ALLOWED_ORIGINS`：允许访问后端的前端地址

初始化后默认管理员账号：

```text
admin / admin123
```

### 3. 启动前端

```powershell
cd front
copy .env.example .env.local
npm install
npm run dev -- --host 0.0.0.0 --port 8080
```

前端默认访问 `http://127.0.0.1:8080`。

`front/.env.local` 中：

```text
VITE_API_BASE_URL=http://127.0.0.1:5000/api
VITE_ADMIN_APP_URL=http://127.0.0.1:5001
```

### 4. 启动管理台

```powershell
cd avue-cli
npm install
npm run dev -- --host 0.0.0.0
```

管理台默认访问 `http://127.0.0.1:5001`。前台管理员导航里的“管理后台”会跳到这里。

## 主要页面

前台：

- `/essays`：知识库列表，展示公开且已发布的真实文档
- `/essays/write`：新建文档，支持 AI 起草和图片上传
- `/essays/my-works`：当前用户自己的文档
- `/essays/my-likes`：当前用户收藏的文档
- `/context-packs`：上下文包管理、RAG 索引、Markdown 导出
- `/ai-center`：用户侧 AI 工作台入口
- `/ai-center/chat`：携带上下文包的 AI 对话
- `/profile`：个人中心和真实内容洞察

管理台：

- `/wel/index`：真实数据运营概览
- `/manager/access/user`：账号管理
- `/manager/access/role`：角色权限
- `/manager/access/system`：系统自检
- `/manager/content/article`：文章管理
- `/manager/content/context`：上下文包与 RAG 运营
- `/manager/ai-center/model`：聊天模型配置
- `/manager/ai-center/embedding`：Embedding 配置

## AI 和 RAG 使用顺序

1. 登录管理员账号。
2. 进入管理台，先在 AI 与 RAG 中配置一个可用的聊天模型。
3. 在知识库中新建真实文档。
4. 进入上下文包，新建一个包，并把文档加入资料来源。
5. 点击重建 RAG 索引，系统会把资料来源切成可检索的片段。
6. 未配置 Embedding 时，可以使用关键词检索，不消耗 embedding token。
7. 在管理台配置 Embedding 后，再对指定上下文包生成向量，语义检索才会真正启用。
8. 在 AI 对话中选择上下文包，系统只会把命中的少量片段传给 AI，不会把整个包塞进提示词。

## 权限模型

- 访客：只能浏览公开且已发布的文档。
- 普通用户：管理自己的文档、收藏、评论、上下文包和 AI 使用。
- 管理员：进入 Avue 管理台，管理用户、角色、内容、AI 配置、Embedding、RAG 索引和系统自检。
- AI 生成接口需要 `ai:access`，AI/Embedding 配置需要 `ai:manage`，系统自检需要 `system:observe`。

## 当前开发重点

- 继续消除演示数据和无效展示。
- 继续收紧后台、AI、上下文包权限。
- 让页面只展示数据库中的真实数据。
- 把 RAG 从关键词检索逐步升级到可维护的向量检索。
- 改善后台信息架构，让管理员和普通用户的入口更清晰。
