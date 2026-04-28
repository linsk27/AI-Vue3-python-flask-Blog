# ContextForge Development Blueprint

## 1. Product Thesis

ContextForge is an open-source AI context workspace. It helps users collect notes, documents, webpages, repositories, and AI conversations, then turn them into reusable AI-ready context.

Tagline:

> Stop losing context. Forge reusable AI context packs from docs, notes, webpages, repos, and conversations.

The project should not feel like a blog with AI attached. It should feel like a practical AI-native workspace for people who constantly gather, summarize, reuse, and ship knowledge.

## 2. Differentiated Core Features

### 2.1 Context Packs

Context Pack is the signature feature. It is more than a folder or favorite list.

A context pack groups documents, links, notes, and AI conversations into one reusable bundle.

Examples:

- Vue 3 Interview Pack
- Graduation Defense Pack
- Flask Backend Refactor Pack
- Product Requirement Pack
- Paper Reading Pack

MVP requirements:

- Create a context pack.
- Add documents to a pack.
- Remove documents from a pack.
- Generate pack summary.
- Generate pack key points.
- Ask AI with pack context.
- Export pack as Markdown.

Later requirements:

- Share public pack link.
- Clone public pack.
- Version pack snapshots.
- Add repo/webpage import results to a pack.

### 2.2 AI Reading Assistant

Document detail should have an AI assistant built around the current document, not a detached chatbot.

MVP actions:

- Explain selected text.
- Summarize selected text.
- Generate examples.
- Generate review questions.
- Extract keywords.
- Add selection to a context pack.

Later actions:

- Challenge this claim.
- Convert selection to prompt.
- Convert selection to flashcards.
- Translate and simplify.

### 2.3 Prompt Factory

Prompt Factory turns documents and context packs into reusable prompts.

Prompt types:

- Summary prompt
- Teaching prompt
- Q&A prompt
- Code review prompt
- Paper analysis prompt
- Requirement analysis prompt
- Project resume prompt

MVP requirements:

- Generate prompt from document.
- Generate prompt from context pack.
- Copy prompt.
- Save prompt template.
- Run prompt with selected model.

### 2.4 Project Debrief Generator

This feature makes the project useful for students, developers, resumes, reports, and software copyright materials.

Input:

- Project name
- Tech stack
- Feature list
- Source documents
- Optional repo link

Generated outputs:

- Project introduction
- Architecture summary
- Feature modules
- Database design summary
- Technical highlights
- Challenges and solutions
- Resume bullet points
- Software copyright description draft

### 2.5 Webpage and GitHub Import

MVP import:

- Paste URL.
- Save source URL.
- Let user paste extracted text manually if crawler fails.
- AI generates title, summary, tags, and document type.

Later import:

- Fetch webpage title and body.
- Import GitHub README and docs.
- Generate repository summary.
- Generate learning route from repository.
- Save import as context pack.

### 2.6 Model Routing

AI config should evolve from "one active model" to a model routing center.

Task routes:

- chat
- summary
- extraction
- coding
- long-context
- private-local

Supported providers:

- OpenAI-compatible API
- DeepSeek
- Volcano Ark
- Ollama, later

## 3. Rename Map

- Blog -> Knowledge Base
- Article -> Document
- Write Article -> New Document
- My Works -> My Documents
- My Likes -> Favorites
- Comment -> Discussion
- AI Center -> AI Workspace
- AI Chat -> Context Chat
- Smart Summary -> Document Insight
- Category -> Type
- Tags -> Knowledge Tags
- Article Management -> Document Management

## 4. Frontend Development Plan

### Phase F1: Product Shell

- [x] Add development blueprint.
- [ ] Rename global brand to ContextForge.
- [ ] Replace blog navigation with Workspace, Knowledge Base, Context Packs, AI Workspace.
- [ ] Replace footer copy.
- [ ] Replace home page with AI workspace dashboard.
- [ ] Keep existing routes stable during transition.

### Phase F2: Knowledge Base

- [ ] Rename essays page UI to Knowledge Base.
- [ ] Add document type filter.
- [ ] Add document status filter.
- [ ] Replace likes wording with favorites.
- [ ] Add card fields for type, status, source URL, and updated time.
- [ ] Add empty-state actions for import and new document.

### Phase F3: Document Detail

- [ ] Rename article detail to document detail.
- [ ] Add right-side AI insight panel.
- [ ] Add summary, keywords, and questions sections.
- [ ] Add "Ask with this document" action.
- [ ] Add "Add to Context Pack" placeholder action.
- [ ] Rename comment area to discussion.

### Phase F4: Document Editor

- [ ] Rename write article page to document editor.
- [ ] Add type field.
- [ ] Add status field.
- [ ] Add visibility field.
- [ ] Add source URL field.
- [ ] Replace AI writing modal with AI document drafting.
- [ ] Replace mock image upload with backend upload.

### Phase F5: Context Packs

- [ ] Add context pack list page.
- [ ] Add context pack detail page.
- [ ] Add create/edit pack modal.
- [ ] Add document-to-pack action.
- [ ] Add pack summary placeholder.
- [ ] Add pack AI chat placeholder.

### Phase F6: Prompt Factory

- [ ] Add prompt factory page.
- [ ] Add prompt templates.
- [ ] Add generate-from-document action.
- [ ] Add generate-from-pack action.
- [ ] Add copy/run/save actions.

## 5. Backend Development Plan

### Phase B1: Transitional Document Layer

- [ ] Keep `/api/articles` working.
- [ ] Add document-compatible fields to existing table.
- [ ] Add `/api/documents` aliases or routes.
- [ ] Normalize response field names.

Suggested transitional fields:

- `resource_type`
- `visibility`
- `source_url`
- `ai_summary`
- `ai_keywords`
- `ai_questions`
- `favorite_count`

### Phase B2: AI Insight APIs

- [ ] `POST /api/ai/generate-document`
- [ ] `POST /api/ai/summarize`
- [ ] `POST /api/ai/extract-tags`
- [ ] `POST /api/ai/generate-questions`
- [ ] `POST /api/ai/generate-prompt`
- [ ] `POST /api/ai/project-debrief`

### Phase B3: Context Pack APIs

- [ ] `GET /api/context-packs`
- [ ] `POST /api/context-packs`
- [ ] `GET /api/context-packs/<id>`
- [ ] `PUT /api/context-packs/<id>`
- [ ] `DELETE /api/context-packs/<id>`
- [ ] `POST /api/context-packs/<id>/documents`
- [ ] `DELETE /api/context-packs/<id>/documents/<document_id>`
- [ ] `POST /api/context-packs/<id>/summary`
- [ ] `POST /api/context-packs/<id>/ask`

### Phase B4: Security and Open Source Readiness

- [ ] Move Flask secret key to environment variables.
- [ ] Add `.env.example`.
- [ ] Add `.gitignore`.
- [ ] Protect management APIs.
- [ ] Mask API keys.
- [ ] Add Docker Compose.

## 6. Admin Development Plan

### Phase A1: Branding

- [ ] Rename admin title to ContextForge Admin.
- [ ] Replace blog wording.
- [ ] Update dashboard metrics around documents, packs, AI calls, users.
- [ ] Update login copy.

### Phase A2: Document Management

- [ ] Rename article management to document management.
- [ ] Add document type.
- [ ] Add document status.
- [ ] Add visibility.
- [ ] Add source URL.
- [ ] Add AI summary status.

### Phase A3: AI Operations

- [ ] Add provider presets.
- [ ] Add connection test.
- [ ] Add task routing.
- [ ] Add streaming switch.
- [ ] Add Ollama roadmap slot.

## 7. Database Roadmap

MVP can use the existing `articles` table as `documents` to reduce risk.

Ideal schema:

- `documents`
- `document_favorites`
- `document_comments`
- `context_packs`
- `context_pack_documents`
- `prompt_templates`
- `ai_conversations`
- `ai_messages`
- `ai_configs`
- `workspaces`
- `workspace_members`

## 8. Open Source Checklist

- [ ] Root README
- [ ] Screenshots
- [ ] Architecture diagram
- [ ] Quick start
- [ ] Environment variable guide
- [ ] Database setup guide
- [ ] Docker Compose
- [ ] Demo account guide
- [ ] Roadmap
- [ ] Contributing guide
- [ ] Issue template
- [ ] Pull request template
- [ ] License confirmation

## 9. MVP Release Scope

### v0.1.0

- Product shell rename.
- Knowledge Base rename.
- AI Workspace rename.
- Document detail AI insight panel.
- Document editor rename.
- Backend fields for document metadata.
- README and setup docs.

### v0.2.0

- Context Packs MVP.
- Prompt Factory MVP.
- AI project debrief generator.
- Webpage manual import.

### v0.3.0

- Multi-document Q&A.
- Saved AI conversations.
- GitHub repository import.
- Export context pack as Markdown.

### v0.4.0

- Model routing.
- Ollama provider.
- Local-first mode.
- AI config connection test.

### v1.0.0

- Team workspace.
- Stable document API.
- Docker production deployment.
- Full open-source documentation.
