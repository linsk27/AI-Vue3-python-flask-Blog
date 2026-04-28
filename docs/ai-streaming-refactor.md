# AI 流式输出改造方案

## 背景

当前项目的 AI 对话链路是同步阻塞式：

1. 前端通过 `aiChatService.sendMessage()` 调用 `/api/ai/chat`。
2. 后端在 `backend/routes/ai.py` 中读取启用的 `ai_configs` 配置。
3. 后端使用 OpenAI 兼容 SDK 调用 `client.chat.completions.create(..., stream=False)`。
4. 模型完整生成结束后，后端一次性返回 JSON。
5. 前端等完整响应返回后，再把 AI 回复插入消息列表。

这种方式实现简单，但用户要等待完整回复结束才能看到内容。后续改造目标是让 AI 回复逐字或分块显示。

## 改造目标

- 保留原有 `/api/ai/chat` 非流式接口，避免影响摘要生成、旧页面和测试脚本。
- 新增 `/api/ai/chat/stream` 流式接口，专门用于聊天 UI。
- 后端采用 SSE 格式输出，响应类型为 `text/event-stream`。
- 前端绕过当前 axios 响应拦截器，使用 `fetch + ReadableStream` 读取流。
- 前端 UI 先插入一条空 AI 消息，再持续追加模型增量内容。
- 流式完成后，后端仍然把完整 AI 回复写入 `context_store`，保持上下文能力。

## 非目标

- 本次不改造文章生成 `/api/ai/generate-article`。文章生成要求最终 JSON 结构，流式化需要单独设计结构化增量协议。
- 本次不把 `context_store` 持久化到数据库。它仍然是内存上下文。
- 本次不改变 AI 配置管理后台的数据结构。

## 后端设计

### 新增接口

`POST /api/ai/chat/stream`

请求体沿用 `/api/ai/chat`：

```json
{
  "message": "用户消息",
  "user_id": "123",
  "reset_context": false,
  "system_prompt": "可选系统提示词",
  "max_tokens": 500,
  "temperature": 0.3,
  "model_provider": "可选",
  "model_name": "可选"
}
```

响应类型：

```http
Content-Type: text/event-stream; charset=utf-8
Cache-Control: no-cache
X-Accel-Buffering: no
```

事件格式：

```text
data: {"type":"start","model_used":"xxx","provider_used":"volcano"}

data: {"type":"delta","content":"你"}

data: {"type":"delta","content":"好"}

data: {"type":"done","context_length":3,"model_used":"xxx","provider_used":"volcano"}
```

错误格式：

```text
data: {"type":"error","message":"错误信息"}
```

### 上下文处理

- 请求开始时读取启用 AI 配置。
- 如果 `reset_context=true`，先清空当前用户上下文。
- 如果没有 `message`，返回错误事件。
- 将用户消息加入 `context_store[user_id]`。
- 流式接收模型输出时累计 `assistant_reply`。
- 模型输出结束后，将完整 `assistant_reply` 追加到上下文。
- 最后继续保留系统消息和最近 18 条消息，避免上下文过长。

## 前端设计

### API 层

在 `front/src/api/modules/ai/index.ts` 中新增：

```ts
sendMessageStream(params, handlers)
```

它不走 `request.post()`，而是使用原生 `fetch`。原因是当前 `front/src/api/index.ts` 的 axios 拦截器默认把响应当作完整 JSON 处理，不适合流式读取。

处理器约定：

```ts
{
  onStart?: (payload) => void
  onDelta?: (content: string, payload) => void
  onDone?: (payload) => void
  onError?: (message: string, payload?) => void
}
```

### UI 层

聊天页面和浮动聊天框都改为：

1. 用户点击发送。
2. 立即插入用户消息。
3. 立即插入一条空的 AI 消息。
4. `onDelta` 中持续追加到这条 AI 消息的 `content`。
5. `onDone` 后结束 loading。
6. 错误时，如果 AI 消息为空，则显示错误或本地 fallback。

## 兼容性

- 原 `/api/ai/chat` 不删除，不改返回结构。
- 原摘要生成继续复用非流式 `/api/ai/chat`。
- 管理后台 AI 配置接口不变。
- 前端只改聊天中心和浮动聊天框，不影响文章生成。

## 验证清单

- 后端 Flask 能正常启动。
- `POST /api/ai/chat` 原接口仍返回完整 JSON。
- `POST /api/ai/chat/stream` 返回 SSE 数据。
- `front` 构建通过。
- AI 对话中心能看到回复逐步追加。
- 选中文本右键唤起的浮动聊天框也能流式追加回复。
