# 火山方舟模型配置

知镜的聊天、AI 起草和 RAG 问答使用 OpenAI 兼容接口。火山方舟可以按下面方式接入。

## 推荐配置

在后台管理端新增或启用一条模型配置：

```text
供应商：volcano
Base URL：https://ark.cn-beijing.volces.com/api/v3
模型：火山方舟控制台里的 Endpoint ID，通常形如 ep-xxxxxxxx
API Key：火山方舟 API Key
```

注意：你打开的控制台页面不是 API 地址。真正的接口地址通常是上面的 `Base URL`，模型字段填 Endpoint ID。

## 环境变量配置

也可以在后端环境变量里配置：

```bash
ARK_API_KEY=你的火山方舟APIKey
ARK_MODEL=你的EndpointID
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

如果数据库里存在一条默认模型配置但 API Key 为空，系统会自动回退读取 `ARK_API_KEY` 和 `ARK_MODEL`。

## Embedding 说明

RAG 的语义检索是独立的 Embedding 配置，不等于聊天模型配置。只有你配置了支持向量的模型，并手动生成语义索引后，语义检索才会真正调用模型并产生费用。

## 安全要求

- 不要把 API Key 写进前端代码、Markdown 示例或迁移脚本。
- 不要把 `.env` 提交到 Git。
- 如果 Key 曾经出现在 GitHub 提交记录里，应在火山方舟控制台立即轮换。
