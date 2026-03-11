# Local Document RAG Q&A System / 本地文档 RAG 问答系统

[English](#english) | [中文](#中文)

---

## English

### Overview

A local RAG Q&A system built with Flask + Vue 3 + LangChain + FAISS.  
It supports multi-knowledge-base isolation, file/URL ingestion, and streaming multi-turn chat.

### Core Features

- Multi-tenant knowledge base isolation by `app_id`
- Document upload and parsing (`.md / .txt / .pdf`)
- URL ingestion (`http/https`) and indexing
- Document management (list / delete by `document_id`)
- RAG question answering with source snippets
- Multi-turn memory by `session_id` + clear memory API
- SSE token streaming (backend + frontend)

### Tech Stack

- Backend: Python 3.13, Flask, LangChain, FAISS, uv
- Frontend: Vue 3, TypeScript, Vite, Arco Design, markdown-it

### Project Structure

```text
.
├─ Backend
│  ├─ app
│  ├─ internal
│  │  ├─ handler
│  │  ├─ router
│  │  └─ service
│  ├─ docs
│  └─ run_backend.bat
└─ frontend
   └─ src
```

### Quick Start

#### 1. Start Backend

```powershell
cd Backend
uv sync
run_backend.bat
```

Backend default: `http://127.0.0.1:5000`

#### 2. Start Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend default: `http://127.0.0.1:5173`

#### 3. Entry

- RAG page: `/rag`

### Key RAG APIs

- `POST /apps/{app_id}/rag/documents/upload`
- `POST /apps/{app_id}/rag/url/upload`
- `GET /apps/{app_id}/rag/documents`
- `DELETE /apps/{app_id}/rag/documents/{document_id}`
- `POST /apps/{app_id}/rag/ask`
- `POST /apps/{app_id}/rag/ask/stream`
- `DELETE /apps/{app_id}/rag/sessions/{session_id}/memory`

### Environment Variables (`Backend/.env`)

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.moonshot.cn/v1
QIANFAN_ACCESS_KEY=your_access_key
QIANFAN_SECRET_KEY=your_secret_key
FLASK_DEBUG=1
WTF_CSRF_ENABLED=False
```

---

## 中文

### 项目简介

基于 Flask + Vue 3 + LangChain + FAISS 的本地文档问答系统。  
支持多知识库隔离、文件/链接入库与流式多轮对话。

### 核心功能

- 按 `app_id` 隔离知识库数据
- 文档上传与解析（`md / txt / pdf`）
- URL 入库（`http/https`）
- 文档管理（列表 / 按 `document_id` 删除）
- RAG 问答并返回来源片段
- 基于 `session_id` 的多轮记忆与清理
- SSE 流式输出（前后端）

### 技术栈

- 后端：Python 3.13、Flask、LangChain、FAISS、uv
- 前端：Vue 3、TypeScript、Vite、Arco Design、markdown-it

### 目录结构

```text
.
├─ Backend
│  ├─ app
│  ├─ internal
│  │  ├─ handler
│  │  ├─ router
│  │  └─ service
│  ├─ docs
│  └─ run_backend.bat
└─ frontend
   └─ src
```

### 快速开始

#### 1. 启动后端

```powershell
cd Backend
uv sync
run_backend.bat
```

后端默认地址：`http://127.0.0.1:5000`

#### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端默认地址：`http://127.0.0.1:5173`

#### 3. 页面入口

- RAG 页面：`/rag`

### 关键 RAG API

- `POST /apps/{app_id}/rag/documents/upload`
- `POST /apps/{app_id}/rag/url/upload`
- `GET /apps/{app_id}/rag/documents`
- `DELETE /apps/{app_id}/rag/documents/{document_id}`
- `POST /apps/{app_id}/rag/ask`
- `POST /apps/{app_id}/rag/ask/stream`
- `DELETE /apps/{app_id}/rag/sessions/{session_id}/memory`

### 环境变量（`Backend/.env`）

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.moonshot.cn/v1
QIANFAN_ACCESS_KEY=your_access_key
QIANFAN_SECRET_KEY=your_secret_key
FLASK_DEBUG=1
WTF_CSRF_ENABLED=False
```

### 说明

- `__pycache__` 和 `*.pyc` 已加入 Git 忽略。
- 详细迭代记录：`Backend/docs/今日功能更新-2026-03-11.md`
