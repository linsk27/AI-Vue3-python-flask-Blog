# ContextForge Requirements

## Product Direction

ContextForge is an open-source AI knowledge context workspace. It turns notes, articles, documents, conversations, and collected materials into a searchable, summarizable, and reusable personal knowledge base.

Chinese product name candidates:

- 语境工坊
- 知脉 AI
- 文脉 AI 工作台
- KnowFlow AI

Recommended positioning:

> Open-source AI knowledge workspace for documents, notes, context-aware chat, and personal knowledge management.

中文定位：

> 一个开源的 AI 知识上下文工作台，支持文档管理、智能摘要、上下文问答和个人知识沉淀。

## Rename Map

- 智汇博客 -> ContextForge
- 博客 -> 知识库 / 上下文库
- 文章 -> 文档 / 知识条目
- 写文章 -> 新建文档
- 我的作品 -> 我的知识库
- 我的喜欢 -> 我的收藏
- 评论 -> 讨论 / 批注
- AI 中心 -> AI 工作台
- AI 聊天 -> 上下文问答
- 智能摘要 -> 文档洞察
- 分类 -> 类型 / 场景
- 标签 -> 知识标签
- 后台文章管理 -> 文档管理

## Information Architecture

- 工作台
- 知识库
- 新建文档
- AI 工作台
- 我的空间
- 管理后台

## Frontend Requirements

### 1. Workspace Home

- [ ] Replace the current blog-style landing page with a product workspace.
- [ ] Show recent documents.
- [ ] Show recent favorites.
- [ ] Show document count, tag count, favorite count, and AI conversation count.
- [ ] Show quick actions: new document, summarize document, ask AI, import material.
- [ ] Show popular tags.
- [ ] Show recent AI conversations.
- [ ] Keep the layout useful as the first screen, not a marketing-only hero.

### 2. Knowledge Base

- [ ] Rename essays/article list to knowledge base.
- [ ] Support keyword search.
- [ ] Support tag filtering.
- [ ] Support document type filtering.
- [ ] Support document status filtering.
- [ ] Support grid and list view.
- [ ] Support sorting by created time, updated time, views, and favorites.
- [ ] Show title, summary, tags, type, author, views, favorites, and updated time.
- [ ] Keep local demo documents as seed examples, but rename them to knowledge entries.

Document types:

- [ ] Note
- [ ] Technical doc
- [ ] Paper
- [ ] Tutorial
- [ ] Project record
- [ ] Idea
- [ ] Q&A record
- [ ] Other

Document statuses:

- [ ] Draft
- [ ] Organized
- [ ] Reviewing
- [ ] Archived

### 3. Document Detail

- [ ] Rename article detail to document detail.
- [ ] Add AI insight panel.
- [ ] Show AI summary.
- [ ] Show extracted keywords.
- [ ] Show generated review questions.
- [ ] Show related documents placeholder.
- [ ] Add action: ask AI about this document.
- [ ] Add action: generate summary.
- [ ] Add action: generate keywords.
- [ ] Add action: generate questions.
- [ ] Convert like behavior into favorite behavior.
- [ ] Rename comments to discussion.

### 4. Document Editor

- [ ] Rename writing page to document editor.
- [ ] Keep Quill editor.
- [ ] Add document type.
- [ ] Add document status.
- [ ] Add source URL.
- [ ] Add visibility: private, public, team.
- [ ] Keep title, content, summary, tags.
- [ ] Replace AI article generation with AI document drafting.
- [ ] Add AI title generation.
- [ ] Add AI summary generation.
- [ ] Add AI tag extraction.
- [ ] Add AI structure optimization.
- [ ] Connect image upload to the backend instead of mock image URLs.

### 5. AI Workspace

- [ ] Rename AI center to AI workspace.
- [ ] Keep streaming chat.
- [ ] Support normal chat.
- [ ] Support current-document Q&A.
- [ ] Support selected-documents Q&A.
- [ ] Support summarize selected document.
- [ ] Support compare documents.
- [ ] Support generate review cards.
- [ ] Support save AI conversation as document.
- [ ] Persist chat history beyond localStorage in a later phase.

### 6. My Space

- [ ] Merge profile, my works, and my likes into a personal space.
- [ ] Show my documents.
- [ ] Show my favorites.
- [ ] Show my drafts.
- [ ] Show my tags.
- [ ] Show recent browsing history.
- [ ] Show saved AI conversations.

## Admin Requirements

### 1. Branding

- [ ] Rename admin system to ContextForge Admin.
- [ ] Replace blog wording with document/knowledge wording.
- [ ] Update login screen copy.
- [ ] Update dashboard metrics.
- [ ] Update menu labels.

### 2. Document Management

- [ ] Rename article management to document management.
- [ ] Add document type column.
- [ ] Add document status column.
- [ ] Add visibility column.
- [ ] Add favorite count column.
- [ ] Add AI summary status column.
- [ ] Keep title, author, tags, views, created time, updated time.
- [ ] Support filtering by type, status, author, and visibility.

### 3. AI Config Management

- [ ] Keep provider, base URL, API key, model, system prompt, active switch.
- [ ] Add connection test.
- [ ] Add default model flag.
- [ ] Add streaming enabled switch.
- [ ] Add OpenAI-compatible provider preset.
- [ ] Add Ollama preset in a later phase.

### 4. System Management

- [ ] Keep user management.
- [ ] Keep role management.
- [ ] Keep permission management.
- [ ] Add tag management if backend schema is split.
- [ ] Add discussion moderation.

## Backend Requirements

### 1. API Compatibility

- [ ] Keep existing `/api/articles` routes during transition.
- [ ] Add document aliases or new document routes.
- [ ] Avoid breaking the current frontend until the new frontend is ready.

### 2. Document APIs

- [ ] `GET /api/documents`
- [ ] `POST /api/documents`
- [ ] `GET /api/documents/<id>`
- [ ] `PUT /api/documents/<id>`
- [ ] `DELETE /api/documents/<id>`
- [ ] `POST /api/documents/<id>/favorite`
- [ ] `POST /api/documents/<id>/view`
- [ ] `GET /api/documents/<id>/comments`
- [ ] `POST /api/documents/<id>/comments`

### 3. AI APIs

- [ ] `POST /api/ai/chat`
- [ ] `POST /api/ai/chat/stream`
- [ ] `POST /api/ai/generate-document`
- [ ] `POST /api/ai/summarize`
- [ ] `POST /api/ai/extract-tags`
- [ ] `POST /api/ai/generate-questions`
- [ ] `POST /api/ai/ask-documents`
- [ ] `GET /api/ai/configs`
- [ ] `POST /api/ai/configs`
- [ ] `PUT /api/ai/configs/<id>`
- [ ] `DELETE /api/ai/configs/<id>`
- [ ] `POST /api/ai/configs/<id>/activate`

### 4. Upload APIs

- [ ] `POST /api/upload/image`
- [ ] Return stable uploaded file URLs.
- [ ] Validate file type.
- [ ] Validate file size.
- [ ] Store uploads under a predictable public path.

### 5. Security

- [ ] Move `SECRET_KEY` to environment variables.
- [ ] Add `.env.example`.
- [ ] Protect admin APIs with token and permissions.
- [ ] Protect user update/delete APIs.
- [ ] Keep public document read routes open only for public documents.
- [ ] Hide full API keys in all responses.
- [ ] Replace default admin password guidance with setup instructions.

## Database Requirements

### Minimum Transitional Fields

Add these to the existing `articles` table or migrate to a new `documents` table:

- [ ] `resource_type VARCHAR(50)`
- [ ] `visibility VARCHAR(20) DEFAULT 'private'`
- [ ] `source_url VARCHAR(500)`
- [ ] `ai_summary TEXT`
- [ ] `ai_keywords JSON`
- [ ] `ai_questions JSON`
- [ ] `favorite_count INT DEFAULT 0`

### Ideal Tables

- [ ] `documents`
- [ ] `document_favorites`
- [ ] `document_comments`
- [ ] `document_tags`
- [ ] `ai_conversations`
- [ ] `ai_messages`
- [ ] `ai_configs`
- [ ] `workspaces`
- [ ] `workspace_members`

MVP can skip team workspaces and keep a personal workspace model.

## Open Source Requirements

- [ ] Root `README.md`
- [ ] Screenshots
- [ ] Architecture diagram
- [ ] Quick start guide
- [ ] `.env.example`
- [ ] `.gitignore`
- [ ] Docker Compose
- [ ] Database initialization guide
- [ ] Demo account instructions
- [ ] Roadmap
- [ ] License
- [ ] Contributing guide
- [ ] Issue templates
- [ ] Pull request template

## Visual Direction

Preferred UI direction:

- [ ] AI console/workspace feel.
- [ ] Left knowledge-space navigation.
- [ ] Center document list or document body.
- [ ] Right AI context assistant.
- [ ] Dense but clean surfaces.
- [ ] Less blog-like hero design.
- [ ] Avoid a one-note warm blog palette.
- [ ] Use icons for actions.
- [ ] Keep cards for documents, modals, and framed tools only.

Potential design references from `design-md`:

- [ ] Linear-style engineering workspace.
- [ ] Mintlify-style documentation clarity.
- [ ] Open WebUI-style AI console flow.
- [ ] Notion-style personal knowledge calmness.

## MVP Scope

### Version 0.1.0

- [ ] Product rename to ContextForge.
- [ ] Frontend copy rename.
- [ ] Admin copy rename.
- [ ] Knowledge base page.
- [ ] Document editor page.
- [ ] Document detail page with AI insight panel.
- [ ] AI workspace streaming chat.
- [ ] AI document generation.
- [ ] AI document summary.
- [ ] Favorite behavior.
- [ ] Backend document-compatible fields.
- [ ] README and setup documentation.

### Version 0.2.0

- [ ] Document type and status filtering.
- [ ] AI tag extraction.
- [ ] AI review question generation.
- [ ] My Space redesign.
- [ ] Real image upload.
- [ ] Admin document filters.

### Version 0.3.0

- [ ] Multi-document Q&A.
- [ ] Save AI conversation as document.
- [ ] Related document recommendation.
- [ ] Persistent AI conversation history.

### Version 0.4.0

- [ ] OpenAI-compatible model presets.
- [ ] Ollama local model support.
- [ ] Model connection test.
- [ ] Better AI config validation.

### Version 0.5.0

- [ ] File upload and parsing.
- [ ] Markdown import.
- [ ] Word document import.
- [ ] Basic RAG retrieval.
- [ ] Vector database research and optional integration.

### Version 1.0.0

- [ ] Workspace/team model.
- [ ] Team permissions.
- [ ] Production Docker deployment.
- [ ] Full documentation.
- [ ] Stable API naming.
- [ ] Public demo environment.

