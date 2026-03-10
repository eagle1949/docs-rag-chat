# 本地文档 RAG 问答系统 / Local Document RAG Q&A System

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## English

### Project Overview

A modern Document Q&A System built with **RAG (Retrieval-Augmented Generation)** technology. This application allows users to upload documents (.md, .txt files) and ask questions about their content, receiving accurate AI-generated answers with source references.

### Key Features

- **Document Upload**: Support for Markdown (.md) and Text (.txt) files up to 10MB
- **AI-Powered Q&A**: Intelligent question answering using LangChain and OpenAI
- **Source References**: View relevant document chunks used to generate answers
- **Modern UI**: Clean and responsive interface built with Vue 3 and Arco Design
- **Vector Search**: Fast similarity search using FAISS vector database
- **Chunk Management**: Documents are automatically split into searchable chunks

### Architecture

#### Frontend

- **Framework**: Vue 3 + TypeScript + Vite
- **UI Library**: Arco Design
- **State Management**: Pinia
- **Routing**: Vue Router
- **Styling**: Tailwind CSS

#### Backend

- **Framework**: Flask (Python)
- **AI/ML**: LangChain, OpenAI API
- **Vector Database**: FAISS
- **Document Processing**: LangChain Document Loaders & Splitters
- **Database**: PostgreSQL with SQLAlchemy

### Quick Start

#### Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL 13+
- OpenAI API Key (or compatible API)

#### Backend Setup

1. **Navigate to backend directory**:

```bash
cd Backend
```

2. **Install dependencies** (using uv):

```bash
# Install uv if you haven't already
pip install uv

# Install dependencies
uv sync
```

3. **Configure environment variables**:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure your API keys
# Required: OPENAI_API_KEY, OPENAI_API_BASE
```

4. **Initialize database**:

```bash
# Run database migrations
flask db upgrade
```

5. **Start the backend server**:

```bash
python app/http/app.py
```

The backend will run on `http://localhost:5000`

#### Frontend Setup

1. **Navigate to frontend directory**:

```bash
cd frontend
```

2. **Install dependencies**:

```bash
# Using yarn (recommended)
yarn install

# Or using npm
npm install
```

3. **Start the development server**:

```bash
# Using yarn
yarn dev

# Or using npm
npm run dev
```

The frontend will run on `http://localhost:5173`

### Usage

1. **Open the application** in your browser at `http://localhost:5173/rag`

2. **Upload documents**:
   - Click "Upload Files" button
   - Select .md or .txt files (max 10MB)
   - Files will be automatically processed and indexed

3. **Ask questions**:
   - Type your question in the input field
   - Click "Send" or press Enter
   - View the AI-generated answer with source references

4. **Manage documents**:
   - View all uploaded documents in the left panel
   - See document size and chunk count
   - Clear all documents when needed

### Configuration

#### Backend Environment Variables (.env)

```env
# Flask Configuration
FLASK_DEBUG=1
FLASK_ENV=development

# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/dbname
SQLALCHEMY_POOL_SIZE=30
SQLALCHEMY_POOL_RECYCLE=3600

# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Optional: LangSmith for tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=your_project_name
```

### Project Structure

```
.
├── Backend/                 # Python Flask backend
│   ├── app/                # Application entry point
│   ├── config/             # Configuration files
│   ├── internal/           # Business logic
│   │   ├── handler/        # Request handlers
│   │   ├── service/        # Business services
│   │   ├── router/         # API routes
│   │   └── model/          # Data models
│   ├── templates/          # HTML templates
│   └── storage/            # Data storage
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── api/           # API clients
│   │   ├── components/    # Vue components
│   │   ├── composables/   # Composables
│   │   ├── views/         # Page views
│   │   └── stores/        # Pinia stores
│   └── public/            # Static assets
└── README.md              # This file
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is open source and available under the MIT License.

---

<a name="chinese"></a>

## 中文

### 项目简介

基于 **RAG（检索增强生成）** 技术构建的现代化文档问答系统。该应用允许用户上传文档（.md、.txt 文件）并针对文档内容提问，获取带有来源引用的准确 AI 生成答案。

### 核心功能

- **文档上传**: 支持 Markdown (.md) 和文本 (.txt) 文件，最大 10MB
- **AI 智能问答**: 使用 LangChain 和 OpenAI 实现智能问答
- **来源引用**: 查看生成答案时使用的相关文档片段
- **现代界面**: 使用 Vue 3 和 Arco Design 构建的简洁响应式界面
- **向量搜索**: 使用 FAISS 向量数据库实现快速相似度搜索
- **分块管理**: 文档自动分割为可搜索的文本块

### 技术架构

#### 前端技术栈

- **框架**: Vue 3 + TypeScript + Vite
- **UI 库**: Arco Design
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: Tailwind CSS

#### 后端技术栈

- **框架**: Flask (Python)
- **AI/ML**: LangChain、OpenAI API
- **向量数据库**: FAISS
- **文档处理**: LangChain 文档加载器和分割器
- **数据库**: PostgreSQL + SQLAlchemy

### 快速开始

#### 环境要求

- Node.js 18+
- Python 3.13+
- PostgreSQL 13+
- OpenAI API Key（或兼容的 API）

#### 后端设置

1. **进入后端目录**:

```bash
cd Backend
```

2. **安装依赖**（使用 uv）:

```bash
# 如果尚未安装 uv
pip install uv

# 安装依赖
uv sync
```

3. **配置环境变量**:

```bash
# 复制示例环境文件
cp .env.example .env

# 编辑 .env 文件并配置您的 API 密钥
# 必需配置: OPENAI_API_KEY, OPENAI_API_BASE
```

4. **初始化数据库**:

```bash
# 运行数据库迁移
flask db upgrade
```

5. **启动后端服务**:

```bash
python app/http/app.py
```

后端服务将运行在 `http://localhost:5000`

#### 前端设置

1. **进入前端目录**:

```bash
cd frontend
```

2. **安装依赖**:

```bash
# 使用 yarn（推荐）
yarn install

# 或使用 npm
npm install
```

3. **启动开发服务器**:

```bash
# 使用 yarn
yarn dev

# 或使用 npm
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 使用说明

1. **在浏览器中打开应用**: `http://localhost:5173/rag`

2. **上传文档**:
   - 点击"Upload Files"按钮
   - 选择 .md 或 .txt 文件（最大 10MB）
   - 文件将自动处理并建立索引

3. **提问**:
   - 在输入框中输入您的问题
   - 点击"Send"按钮或按 Enter 键
   - 查看 AI 生成的答案和来源引用

4. **管理文档**:
   - 在左侧面板查看所有已上传的文档
   - 显示文档大小和分块数量
   - 需要时可清除所有文档

### 配置说明

#### 后端环境变量 (.env)

```env
# Flask 配置
FLASK_DEBUG=1
FLASK_ENV=development

# 数据库配置
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/dbname
SQLALCHEMY_POOL_SIZE=30
SQLALCHEMY_POOL_RECYCLE=3600

# OpenAI 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 可选配置: LangSmith 追踪
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=your_project_name
```

### 项目结构

```
.
├── Backend/                 # Python Flask 后端
│   ├── app/                # 应用入口
│   ├── config/             # 配置文件
│   ├── internal/           # 业务逻辑
│   │   ├── handler/        # 请求处理器
│   │   ├── service/        # 业务服务
│   │   ├── router/         # API 路由
│   │   └── model/          # 数据模型
│   ├── templates/          # HTML 模板
│   └── storage/            # 数据存储
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── components/    # Vue 组件
│   │   ├── composables/   # 组合式函数
│   │   ├── views/         # 页面视图
│   │   └── stores/        # Pinia 状态管理
│   └── public/            # 静态资源
└── README.md              # 本文件
```

### 贡献

欢迎贡献！请随时提交 Pull Request。

### 许可证

本项目是开源项目，采用 MIT 许可证。
