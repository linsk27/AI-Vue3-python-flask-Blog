
# AI-Vue3-python-flask-Blog

[https://ai-vue3-python-flask-blog.vercel.app/](体验地址）

> 一个现代化的 AI 增强型知识分享平台，基于 Vue3 + Python Flask 技术栈构建

[![Vue3](https://img.shields.io/badge/Vue-3.x-brightgreen)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 项目简介

**AI-Vue3-python-flask-Blog** 是一个面向开发者的智能知识创作与分享平台，集成了 AI 辅助写作、内容管理、用户权限控制等核心功能。项目采用前后端分离架构，提供现代化的用户体验和强大的内容管理能力。

## ✨ 核心特性

### 🎯 智能内容创作
- **AI 辅助写作**：基于 OpenAI API 的智能文章生成
- **多格式支持**：Markdown 编辑器 + 富文本编辑器
- **智能摘要**：自动生成文章摘要和标签
- **分类管理**：支持前端、后端、数据库、算法等专业分类

### 🔐 用户管理
- **多方式登录**：用户名密码、验证码、第三方登录
- **权限控制**：基于角色的访问控制 (RBAC)
- **个人中心**：个人信息管理、文章收藏、评论互动

### 📊 内容管理
- **文章管理**：创建、编辑、发布、删除文章
- **评论系统**：支持文章评论和互动
- **点赞收藏**：用户互动功能
- **数据统计**：阅读量、点赞数等数据追踪

### 🎨 现代化界面
- **响应式设计**：适配手机、平板、PC 全平台
- **多主题支持**：10+ 款精心设计的主题
- **暗色模式**：护眼暗色主题支持
- **流畅动画**：现代化交互动效

## 🏗️ 技术架构

### 前端技术栈
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全的 JavaScript
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Vite** - 构建工具
- **Sass** - CSS 预处理器

### 后端技术栈
- **Python Flask** - 轻量级 Web 框架
- **SQLAlchemy** - ORM 数据库工具
- **MySQL** - 关系型数据库
- **JWT** - 身份认证
- **OpenAI API** - AI 服务集成
- **CORS** - 跨域资源共享

### 项目结构
```
AI-Vue3-python-flask-Blog/
├── front/                    # 前端项目 (用户端)
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── api/            # API 接口
│   │   ├── store/          # 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json
├── avue-cli/               # 管理后台
│   ├── src/
│   │   ├── views/manager/  # 管理页面
│   │   ├── page/           # 页面布局
│   │   └── config/         # 配置管理
│   └── package.json
├── backend/                # 后端服务
│   ├── routes/            # 路由模块
│   │   ├── ai.py          # AI 相关接口
│   │   ├── article.py     # 文章接口
│   │   ├── auth.py        # 认证接口
│   │   └── upload.py      # 文件上传
│   ├── database.py        # 数据库配置
│   └── app.py             # 应用入口
└── README.md
```

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- MySQL 5.7+

### 后端部署

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **数据库配置**
```bash
# 创建数据库
python init_db.py
```

3. **启动服务**
```bash
python app.py
# 或使用生产环境
gunicorn app:app
```

### 前端部署

1. **安装依赖**
```bash
cd front
npm install
# 或使用 yarn
yarn
```

2. **开发环境**
```bash
npm run dev
```

3. **生产构建**
```bash
npm run build
```

### 管理后台部署

1. **安装依赖**
```bash
cd avue-cli
npm install
```

2. **启动服务**
```bash
npm run dev
```

## 📖 功能模块

### 用户端功能
- **首页展示**：文章列表、分类导航
- **文章阅读**：Markdown 渲染、代码高亮
- **AI 中心**：智能对话、内容摘要
- **个人中心**：个人信息、我的文章、收藏管理

### 管理后台功能
- **用户管理**：用户列表、权限分配
- **文章管理**：文章审核、分类管理
- **AI 配置**：模型密钥管理、服务配置
- **系统设置**：主题配置、权限管理

### API 接口
- **认证接口**：登录、注册、Token 验证
- **文章接口**：CRUD 操作、搜索、分类
- **AI 接口**：文章生成、内容摘要、智能对话
- **文件接口**：图片上传、文件管理

## 🔧 配置说明

### 环境变量配置
```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@host:port/database

# AI 服务配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_openai_base_url

# JWT 密钥
JWT_SECRET_KEY=your_secret_key
```

### 主题配置
项目支持多种主题切换，包括：
- 默认主题
- 暗色主题  
- Mac 风格主题
- 企业级主题

## 🤝 贡献指南

我们欢迎任何形式的贡献！请参考以下步骤：

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙏 致谢

感谢以下开源项目的支持：
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue3 UI 组件库
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [Avue](https://avuejs.com/) - 后台管理模板

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 项目 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！**
```

## 项目介绍说明

这个 README.md 文件包含了以下关键信息：

1. **项目概览** - 清晰的项目定位和技术栈介绍
2. **核心特性** - 突出项目的智能化和现代化特点
3. **技术架构** - 详细的技术栈说明和项目结构
4. **快速开始** - 完整的部署指南
5. **功能模块** - 用户端和管理后台的功能说明
6. **配置说明** - 环境变量和主题配置
7. **开源贡献** - 标准的开源项目规范
