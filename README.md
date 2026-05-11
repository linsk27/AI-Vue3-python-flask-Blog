# 知境 ContextForge

`feat/contextforge-workspace` 是本项目的开发分支，用来把原来的 Vue3 + Flask AI 博客升级成一个面向学习者、写作者和小团队的 AI 知识工作台。

`main` 分支仍然保留更适合大学生课程设计、毕业设计和二次开发的稳定 AI 博客基础版；当前分支更适合想继续学习 RAG、上下文包、Embedding、后台权限和 AI 产品化的开发者。

> 使用声明：本项目仅供学习交流、课程设计、毕业设计和个人非商业二次开发参考使用，禁止商业用途。

## 页面预览

### 工作台首页

![知境工作台首页](docs/screenshots/contextforge/home.png)

### 知识库列表

![知识库列表](docs/screenshots/contextforge/knowledge-list.png)

### 前台登录与 AI 工作台入口

![前台登录页](docs/screenshots/contextforge/login-workspace.png)

### 独立管理后台

![知境管理后台登录](docs/screenshots/contextforge/admin-login.png)

## 项目定位

知境 ContextForge 不是单纯“给博客加一个 AI 按钮”。它的核心目标是把零散内容沉淀成可检索、可复用、可继续生成的上下文资产。

核心链路：

```text
真实文档
  -> 加入上下文包
  -> 构建 RAG 分块索引
  -> 检索命中少量相关片段
  -> AI 对话或 AI 起草只携带必要上下文
  -> 新内容继续沉淀回知识库
```

这样可以避免把整份资料塞进提示词，降低 token 消耗，也让 AI 回答更容易追溯来源。

## 面向用户

- 访客：浏览公开且已发布的知识文档。
- 普通用户：写文档、维护自己的上下文包、收藏内容、使用 AI 对话和 AI 起草。
- 知识维护者：维护上下文包、资料来源、RAG 索引和 Markdown 导出。
- 管理员：进入独立 Avue 管理后台，维护用户、角色、权限、内容、AI 模型、Embedding 配置和系统自检。

产品边界已经拆清楚：

- `front/`：普通用户的知识工作台，不再混入后台治理功能。
- `avue-cli/`：管理员使用的独立后台。
- `backend/`：统一 API、鉴权、权限、AI、RAG 和数据持久化。

## 技术栈

- 前台：Vue 3、Vite、TypeScript、Pinia、Vue Router、Element Plus、Quill、Marked、Mammoth
- 管理台：Avue、Vue 3、Vite、Element Plus
- 后端：Python Flask、SQLAlchemy、PyMySQL、JWT、Flask-CORS
- 数据库：MySQL
- AI：OpenAI-compatible Chat API，可配置多模型；Embedding 需要单独配置

## 快速启动

### 1. 准备数据库

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

初始化后默认管理员账号：

```text
admin / admin123
```

正式环境必须修改默认密码和 `SECRET_KEY`。

### 3. 启动前台

```powershell
cd front
copy .env.example .env.local
npm install
npm run dev -- --host 0.0.0.0 --port 8080
```

前台默认访问 `http://127.0.0.1:8080`。

### 4. 启动管理台

```powershell
cd avue-cli
npm install
npm run dev -- --host 0.0.0.0
```

管理台默认访问 `http://127.0.0.1:5001`。

## 主要页面

前台：

- `/`：知境工作台首页
- `/essays`：知识库公开文档列表
- `/essays/write`：新建文档，支持 AI 起草和上下文包引用
- `/essays/my-works`：我的文档
- `/essays/my-likes`：我的收藏
- `/context-packs`：上下文包、RAG 索引、检索预览、Markdown 导出
- `/ai-center`：用户侧 AI 工作台入口
- `/ai-center/chat`：携带上下文包的 AI 对话
- `/profile`：个人中心

管理台：

- `/wel/index`：真实数据运营概览
- `/manager/access/user`：账号管理
- `/manager/access/role`：角色权限
- `/manager/access/system`：手动系统自检
- `/manager/content/article`：全站文章管理
- `/manager/content/context`：上下文包与 RAG 运营
- `/manager/ai-center/model`：AI 聊天模型配置
- `/manager/ai-center/embedding`：Embedding 配置

## RAG 和 Embedding

系统默认先走关键词检索，不会偷偷产生 Embedding 成本。

只有同时满足下面条件时，语义检索才会真正启用：

1. 后台已经配置可用的 Embedding 模型。
2. 当前上下文包已经用该模型生成向量索引。
3. 用户在检索或 AI 使用时允许语义检索。

未满足条件时，系统会回退到关键词检索。这样既能先把 RAG 工作流跑通，也能避免不必要的 token 和接口费用。

## 文档

- [ContextForge 架构、用户边界与使用说明](docs/contextforge-architecture-usage.md)
- [ContextForge 需求说明](docs/contextforge-requirements.md)
- [项目解析和使用方式](docs/project-analysis-and-usage.md)
- [AI 流式响应重构记录](docs/ai-streaming-refactor.md)

## 当前完成度

已经完成开发分支的核心 MVP 闭环：

- 前台和管理后台边界拆分
- 真实文档写作和展示
- 上下文包维护
- RAG 分块索引和检索预览
- AI 对话携带上下文包
- AI 起草写入结构化文档
- 关键词检索默认可用
- Embedding 配置、校验和语义索引基础能力
- 管理后台承接账号、角色、内容、上下文包、AI、Embedding 和系统自检

仍建议继续增强：

- 自动化测试覆盖
- 文件上传解析 PDF、Word、Markdown
- 后台审计日志和成本统计
- 生产环境安全加固
- 更多真实数据场景和端到端验证
