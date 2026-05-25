# 火山方舟多模态向量适配记录

知镜的 RAG 文本语义检索现在支持火山方舟多模态向量 Endpoint。

已验证配置：

```text
Provider: volcano
Base URL: https://ark.cn-beijing.volces.com/api/v3
Model: ep-20260525145645-vzjp6
Endpoint model: doubao-embedding-vision-251215
Embedding dimension: 2048
```

适配原因：

- 该 Endpoint 不能走普通 OpenAI `/embeddings` 接口。
- 火山返回 `does not support this api` 时，后端会自动切换到 `/embeddings/multimodal`。
- 文本资料分块按 `[{ "type": "text", "text": "..." }]` 提交。

验证链路：

```text
创建临时文章 -> 创建上下文包 -> 加入资料 -> 重建 RAG 分块
-> 生成 Embedding -> allow_embedding=true 语义检索
-> AI 起草携带检索片段 -> 清理临时数据
```
