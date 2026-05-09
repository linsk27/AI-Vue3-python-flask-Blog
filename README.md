# AI-Vue3-python-flask-Blog

一个基于 **Vue 3 + Python Flask + MySQL** 的 AI 增强型博客与知识分享系统。

当前 `main` 分支是线上稳定版本，已经用于 Vercel 和 Railway 部署。为了避免影响线上环境，`main` 主要保留博客、文章、用户、后台管理和基础 AI 能力。

体验地址：[https://ai-vue3-python-flask-blog.vercel.app/](https://ai-vue3-python-flask-blog.vercel.app/)

## 适合人群

`main` 分支适合大学生、前后端初学者和正在准备课程设计/毕业设计的同学二次开发。它已经包含前台、后台、后端 API、数据库、登录鉴权、文章管理和基础 AI 能力，可以作为一个完整的全栈项目基础继续扩展。

如果这个项目对你的学习、毕设选题或二开有帮助，欢迎 Star、Fork 和使用。

## 页面截图

以下截图来自 `main` 稳定分支，展示当前博客系统的主要页面效果。

### 前台首页

![前台首页](docs/screenshots/main-home.png)

### 文章库

![文章库](docs/screenshots/main-articles.png)

### 管理后台登录

![管理后台登录](docs/screenshots/main-admin-login.png)

## 分支说明

| 分支 | 状态 | 说明 |
| --- | --- | --- |
| `main` | 稳定部署分支 | 当前线上博客系统，适合查看已部署版本、基础架构和生产配置 |
| `feat/contextforge-workspace` | 开发中 | 正在升级为 **知境 ContextForge AI 知识工作台**，包含上下文包、RAG、Embedding、独立管理台等新能力 |

想了解正在开发的 **知境 ContextForge**，请切换到开发分支：

```bash
git fetch origin
git checkout feat/contextforge-workspace
```

开发分支上的项目说明文档：

- [知境 ContextForge 架构、群体与使用说明](https://github.com/linsk27/AI-Vue3-python-flask-Blog/blob/feat/contextforge-workspace/docs/contextforge-architecture-usage.md)
- [开发分支代码](https://github.com/linsk27/AI-Vue3-python-flask-Blog/tree/feat/contextforge-workspace)

## main 分支项目定位

`main` 分支当前是一个前后端分离的 AI 博客系统，核心能力包括：

- 用户注册、登录、JWT 鉴权
- 文章创建、编辑、发布、删除
- 文章列表、详情、评论、点赞和收藏
- AI 辅助写作、AI 对话和模型配置
- Avue 管理后台，用于用户、文章和 AI 配置管理
- Vercel 前端部署和 Railway 后端部署适配

它适合作为一个完整的 Vue3 + Flask 全栈项目基础版本，也适合继续扩展为内容管理系统、个人知识库或 AI 写作平台。

## 技术栈

### 用户端 `front/`

- Vue 3
- Vite
- TypeScript
- Pinia
- Vue Router
- Element Plus
- Markdown / 富文本编辑能力

### 管理后台 `avue-cli/`

- Vue 3
- Vite
- Avue
- Element Plus
- Axios

### 后端 `backend/`

- Python Flask
- SQLAlchemy
- PyMySQL
- MySQL
- JWT
- Flask-CORS
- OpenAI-compatible API

## 项目结构

```text
AI-Vue3-python-flask-Blog/
├── front/        # 用户端前台
├── avue-cli/     # Avue 管理后台
├── backend/      # Flask 后端 API
└── README.md
```

## 本地启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python init_db.py
python app.py
```

默认后端地址：

```text
http://127.0.0.1:5000
```

### 2. 用户端前台

```bash
cd front
npm install
npm run dev
```

### 3. 管理后台

```bash
cd avue-cli
npm install
npm run dev
```

## 开发中的知境 ContextForge

`feat/contextforge-workspace` 分支正在把项目从“AI 博客”升级为“AI 知识工作台”。

开发分支的重点包括：

- 将文章、笔记、链接、AI 对话组织成上下文包
- 使用 RAG 检索，避免把整包资料直接塞进提示词
- 支持关键词检索和可配置 Embedding 语义检索
- 将普通用户前台和 Avue 管理台边界拆清楚
- 让页面展示真实数据，减少演示数据和无效按钮
- 支持 AI 起草时携带上下文包命中片段

这个方向的产品名是：

```text
知境 ContextForge
```

如果你是开发者，建议先看 `main` 了解当前线上版本，再切换到 `feat/contextforge-workspace` 理解下一阶段的产品演进。
