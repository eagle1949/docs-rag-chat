# 本地文档 RAG 问答系统 PRD（v2.0）

## 1. 项目概述

### 1.1 背景
当前版本已具备基础 RAG 上传与问答能力，但仍是“全局单知识库、无会话记忆、无文档生命周期管理”。
本次迭代聚焦把系统升级为可用于真实业务场景的多知识库问答系统。

### 1.2 本期目标
1. 支持按 `app_id` 隔离文档与向量索引。
2. 支持文档列表与按 `document_id` 删除。
3. 支持多轮对话（按 `session_id`）并接入摘要缓存记忆。
4. 前后端联动支持以上能力。

### 1.3 技术栈
- Backend: Flask + LangChain + FAISS
- Embedding: Qianfan Embedding API
- LLM: Moonshot(OpenAI Compatible)
- Frontend: Vue3 + TypeScript + Vite

---

## 2. 功能需求

### 2.1 核心能力（必须）

#### 功能 A：按 app_id 的知识库隔离
- 同一服务可承载多个知识库。
- 每个 `app_id` 具备独立的：
  - 文档目录
  - FAISS 索引目录
  - 文档元数据文件
- 检索和问答仅在当前 `app_id` 范围内执行。

#### 功能 B：文档上传与管理
- 支持上传 `.md` / `.txt`。
- 上传后自动：加载 -> 切分 -> 向量化 -> 入库。
- 返回 `document_id`。
- 支持文档列表查询。
- 支持删除指定文档（同步删除原文、向量数据、元数据）。

#### 功能 C：多轮问答与记忆
- 问答接口必须接收 `session_id`。
- 每次回答基于：
  - 当前问题
  - 检索到的文档上下文
  - 对话记忆（摘要 + 近期对话）
- 每轮问答后写入记忆。
- 支持清空某会话记忆。

#### 功能 D：可解释性输出
- 回答需返回引用来源列表 `sources`。
- 每条来源包含：`document_id`、`filename`、`chunk_id`、`score`、`content`。

### 2.2 非目标（本期不做）
- PDF/Docx/PPT 解析增强。
- 流式 SSE 输出。
- 权限鉴权（默认内部环境）。

---

## 3. 接口设计

### 3.1 上传文档
`POST /apps/{app_id}/rag/documents/upload`

- Content-Type: `multipart/form-data`
- FormData:
  - `file`: 文件（必填）

响应示例：
```json
{
  "code": "success",
  "message": "",
  "data": {
    "document_id": "doc_7e55f3d7f6f649c4b8a9",
    "filename": "产品手册.md",
    "size": 20480,
    "chunks": 18,
    "message": "文档上传成功并建立索引"
  }
}
```

### 3.2 文档列表
`GET /apps/{app_id}/rag/documents`

响应示例：
```json
{
  "code": "success",
  "message": "",
  "data": {
    "documents": [
      {
        "document_id": "doc_7e55f3d7f6f649c4b8a9",
        "filename": "产品手册.md",
        "size": 20480,
        "chunks": 18,
        "created_at": "2026-03-11T13:05:00Z"
      }
    ]
  }
}
```

### 3.3 删除文档
`DELETE /apps/{app_id}/rag/documents/{document_id}`

响应示例：
```json
{
  "code": "success",
  "message": "",
  "data": {
    "document_id": "doc_7e55f3d7f6f649c4b8a9",
    "message": "文档删除成功"
  }
}
```

### 3.4 问答（多轮）
`POST /apps/{app_id}/rag/ask`

请求示例：
```json
{
  "question": "这个产品的保修期多久？",
  "session_id": "user_1001_chat_a"
}
```

响应示例：
```json
{
  "code": "success",
  "message": "",
  "data": {
    "answer": "根据文档，标准保修期为 12 个月。",
    "session_id": "user_1001_chat_a",
    "sources": [
      {
        "document_id": "doc_7e55f3d7f6f649c4b8a9",
        "filename": "产品手册.md",
        "chunk_id": 4,
        "score": 0.89,
        "content": "...保修政策说明..."
      }
    ]
  }
}
```

### 3.5 清空会话记忆
`DELETE /apps/{app_id}/rag/sessions/{session_id}/memory`

---

## 4. 数据模型

### 4.1 文档元数据（每个 app_id 独立）
```json
{
  "app_id": "default",
  "documents": [
    {
      "document_id": "doc_xxx",
      "filename": "产品手册.md",
      "stored_filename": "a3f5....md",
      "size": 20480,
      "chunks": 18,
      "vector_ids": ["..."],
      "created_at": "2026-03-11T13:05:00Z"
    }
  ]
}
```

### 4.2 向量 metadata（chunk 级）
```python
{
  "app_id": "default",
  "document_id": "doc_xxx",
  "source": "产品手册.md",
  "stored_source": "a3f5....md",
  "chunk_id": 4
}
```

### 4.3 存储目录
```text
data/
  rag/
    {app_id}/
      documents/
      faiss_index/
      documents_meta.json
storage/
  chat_history/
    {app_id}/
      {session_id}_summary_buffer.json
```

---

## 5. 技术方案

### 5.1 检索策略
- 默认 `top_k = 3`
- 使用 `similarity_search_with_score`
- 输出 `score`，并在业务层进行阈值过滤（默认 0.7，按归一化后分值）

### 5.2 对话记忆策略
- 采用摘要缓存记忆（Summary + Recent Buffer）。
- 输入 Prompt 包含：
  - 历史摘要
  - 近期对话
  - 本轮检索上下文
- 每轮结束后调用 `save_context(question, answer)`。

### 5.3 并发与一致性
- 对同一 `app_id` 的索引写操作加锁（上传/删除）。
- 删除文档时必须保证“文件、索引、元数据”三者一致更新。

---

## 6. 前端需求

1. 新增 `app_id` 输入（默认 `default`）。
2. 新增 `session_id` 输入（默认自动生成，可编辑）。
3. 文档面板支持：
   - 拉取当前 app 的文档列表
   - 删除单个文档
4. 问答面板支持多轮会话记录展示。
5. 每次提问都携带 `app_id + session_id`。

---

## 7. 验收标准

1. 不同 `app_id` 的文档互不可见，问答互不串库。
2. 删除文档后无法再被检索到。
3. 同一 `session_id` 连续提问可利用历史语境。
4. 不同 `session_id` 间记忆隔离。
5. 前端可完整完成“上传 -> 列表 -> 删除 -> 多轮问答”。

---

## 8. 版本信息
- 文档版本：v2.0
- 更新时间：2026-03-11
- 负责人：Codex
