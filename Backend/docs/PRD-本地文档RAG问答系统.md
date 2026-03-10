# 本地文档 RAG 问答系统 PRD

## 一、项目概述

### 1.1 项目背景
开发一个基于本地文档的 RAG（Retrieval-Augmented Generation）问答系统，允许用户上传文档并基于文档内容进行问答。

### 1.2 项目目标
- 支持用户上传本地文档（md/txt）
- 自动建立文档向量索引
- 基于文档内容回答用户问题
- 返回答案时附带引用来源

### 1.3 技术栈
- **后端框架**: Flask + LangChain
- **嵌入模型**: 百度千帆 Embedding API
- **LLM**: 月之暗面（Moonshot）API
- **向量数据库**: FAISS（本地存储）
- **前端**: Vue（已有项目，llmops-ui）

---

## 二、功能需求

### 2.1 核心功能（MVP）

#### 功能 1: 文档上传
- 支持格式：`.md`, `.txt`
- 文件大小限制：10MB
- 上传后自动建立向量索引
- 返回上传成功信息

#### 功能 2: 文档切分
- 使用 `RecursiveCharacterTextSplitter`
- Chunk 大小：500 字符
- Chunk 重叠：50 字符
- 分隔符：`\n\n`, `\n`, `。`, `！`, `？`, `.`, `!`, `?`, ` `

#### 功能 3: 向量索引
- 使用千帆 Embedding API 生成向量
- 存储到 FAISS 本地索引
- 支持增量添加文档

#### 功能 4: 语义检索
- 用户提问后检索相关文档片段
- 检索策略：相似度评分
- 返回 Top-K 个片段（K=3）
- 相似度阈值：0.7

#### 功能 5: 答案生成
- 使用月之暗面（Moonshot）LLM 生成答案
- Prompt 模板包含参考内容
- 如果文档中没有答案，明确告知用户

#### 功能 6: 引用展示
- 显示引用的文档片段
- 包含文件名、片段内容、相似度分数
- 按相关度排序

### 2.2 可选功能（后续迭代）
- [ ] PDF 文档支持
- [ ] 文档列表查看
- [ ] 文档删除
- [ ] 清空所有文档
- [ ] 流式答案返回
- [ ] 多文档批量上传

---

## 三、接口设计

### 3.1 API 接口列表

#### 3.1.1 上传文档
```
POST /rag/documents/upload
Content-Type: multipart/form-data
```

**请求参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 上传的文档文件 |

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "filename": "langchain.md",
    "size": 1024,
    "chunks": 10,
    "message": "文档上传成功并建立索引"
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "不支持的文件格式，仅支持 txt、md",
  "data": {}
}
```

#### 3.1.2 提问
```
POST /rag/ask
Content-Type: application/json
```

**请求参数：**
```json
{
  "question": "什么是 LangChain？"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| question | string | 是 | 用户问题，最大长度 500 字符 |

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "LangChain 是一个开源框架，用于开发由语言模型驱动的应用程序...",
    "sources": [
      {
        "filename": "langchain_intro.md",
        "chunk_id": 0,
        "content": "LangChain 是一个用于开发由语言模型驱动的应用程序的框架...",
        "score": 0.85
      },
      {
        "filename": "guide.md",
        "chunk_id": 2,
        "content": "LangChain 提供了 Chain、Agent、Memory 等核心组件...",
        "score": 0.78
      }
    ]
  }
}
```

**错误响应：**
```json
{
  "code": 404,
  "message": "请先上传文档",
  "data": {}
}
```

### 3.2 错误码定义

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在（如没有上传文档） |
| 500 | 服务器内部错误 |

---

## 四、数据结构

### 4.1 文件存储结构
```
llmops-api/
└── data/
    ├── documents/              # 原始文档存储
    │   ├── langchain.md
    │   └── guide.txt
    └── faiss_index/           # FAISS 向量索引
        ├── index.faiss
        └── index.pkl
```

### 4.2 文档 Metadata
```python
{
    "source": "langchain.md",      # 文件名
    "chunk_id": 0,                 # 片段序号
    "upload_time": "2024-03-07",   # 上传时间
}
```

### 4.3 引用数据结构
```python
{
    "filename": "langchain_intro.md",  # 来源文件
    "chunk_id": 0,                      # 片段序号
    "content": "LangChain 是...",       # 片段内容
    "score": 0.85                       # 相似度分数
}
```

---

## 五、技术架构

### 5.1 系统架构图
```
┌─────────────┐
│  Vue 前端   │  (llmops-ui)
└──────┬──────┘
       │ HTTP API
       ↓
┌─────────────┐
│ Flask 后端  │
└──────┬──────┘
       │
       ├──→ 文档上传 → 解析 → 切分 → 嵌入 → FAISS
       │
       └──→ 用户提问 → 检索 FAISS → LLM → 返回答案+引用
```

### 5.2 代码结构
```
llmops-api/
├── internal/
│   ├── handler/
│   │   └── rag_handler.py          # RAG 控制器（处理 HTTP 请求）
│   ├── service/
│   │   ├── rag_service.py          # RAG 业务逻辑服务
│   │   ├── document_loader.py      # 文档加载服务
│   │   ├── document_splitter.py    # 文档切分服务
│   │   └── vector_store.py         # 向量库管理服务
│   └── schema/
│       └── rag_schema.py           # 请求参数验证
├── data/                           # 数据目录
│   ├── documents/                  # 上传的文档
│   └── faiss_index/                # FAISS 索引
├── config/
│   └── rag_config.py               # RAG 配置（可选）
└── internal/router/router.py       # 路由注册
```

### 5.3 核心组件

#### 5.3.1 RAGHandler（控制器）
- 处理 HTTP 请求
- 参数验证
- 调用 RAGService
- 返回响应

#### 5.3.2 RAGService（业务逻辑）
- 协调各个服务
- 处理上传文档流程
- 处理问答流程

#### 5.3.3 DocumentLoader（文档加载）
- 根据文件类型选择加载器
- TextLoader（.txt）
- UnstructuredMarkdownLoader（.md）

#### 5.3.4 DocumentSplitter（文档切分）
- RecursiveCharacterTextSplitter
- chunk_size=500, chunk_overlap=50

#### 5.3.5 VectorStore（向量库）
- 使用千帆 Embedding API
- FAISS 存储
- 相似度检索（threshold=0.7, k=3）

---

## 六、技术实现细节

### 6.1 API 配置
```python
# .env 文件
# 千帆 Embedding API
QIANFAN_API_KEY=your_qianfan_api_key
QIANFAN_SECRET_KEY=your_qianfan_secret_key

# 月之暗面（Moonshot）LLM API
MOONSHOT_API_KEY=your_moonshot_api_key
```

### 6.2 文档加载器选择
```python
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader
)

def load_document(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".md":
        return UnstructuredMarkdownLoader(file_path).load()
    elif ext in [".txt", ".text"]:
        return TextLoader(file_path, encoding="utf-8").load()
    else:
        raise ValueError(f"不支持的文件格式: {ext}")
```

### 6.3 文档切分配置
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
)
```

### 6.4 检索配置
```python
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 3,
        "score_threshold": 0.7
    }
)
```

### 6.5 LLM Prompt 模板
```
基于以下参考内容回答问题：

参考内容：
{context}

问题：{question}

如果参考内容中没有答案，请说"根据提供的文档内容，我无法回答这个问题。"

答案：
```

---

## 七、依赖项

### 7.1 Python 依赖（已安装）
```toml
langchain>=1.2.2
langchain-core>=0.1.0
langchain-community>=0.4.1
langchain-openai>=0.1.0
qianfan>=0.4.12.3
faiss-cpu>=1.13.2
flask>=3.0.2
injector==0.21.0
python-dotenv>=1.2.1
```

### 7.2 需要确认的依赖
```toml
# 如果支持 PDF
pypdf>=3.0.0  # 或 PyPDF2
```

---

## 八、实现计划

### 8.1 Phase 1: MVP（最小可用版本）
- [ ] 创建基础代码结构
- [ ] 实现文档上传接口（支持 md/txt）
- [ ] 实现文档加载和切分
- [ ] 实现向量索引建立
- [ ] 实现问答接口
- [ ] 实现检索和答案生成
- [ ] 错误处理

### 8.2 Phase 2: 功能增强
- [ ] PDF 文档支持
- [ ] 文档列表接口
- [ ] 文档删除接口
- [ ] 前端对接和联调

### 8.3 Phase 3: 优化提升
- [ ] 流式答案返回
- [ ] 批量文档上传
- [ ] 缓存优化
- [ ] 性能监控

---

## 九、非功能需求

### 9.1 性能要求
- 文档上传和索引建立：< 30 秒（1MB 文件）
- 问答响应：< 5 秒

### 9.2 安全要求
- 文件大小限制：10MB
- 文件类型校验
- 路径遍历防护

### 9.3 可用性要求
- 友好的错误提示
- API 接口幂等性

---

## 十、风险和限制

### 10.1 已知限制
- MVP 版本仅支持 md/txt 格式
- 使用同步处理，大文件可能超时
- FAISS 索引存储在本地，不支持分布式

### 10.2 风险点
- 千帆 Embedding API 调用可能失败或限流
- 月之暗面 API 调用可能失败或限流
- 大文件处理可能超时
- 并发上传可能导致索引冲突

### 10.3 缓解措施
- 添加 API 重试机制
- 设置合理的超时时间
- 考虑添加文件上传锁

---

## 十一、测试场景

### 11.1 功能测试
1. 上传 md 文件，验证索引建立
2. 上传 txt 文件，验证索引建立
3. 上传不支持的格式，验证错误提示
4. 上传超大文件，验证错误提示
5. 基于文档提问，验证答案准确性
6. 提问文档中没有的内容，验证提示

### 11.2 边界测试
1. 空文件上传
2. 特殊字符文件名
3. 超长问题（>500 字符）
4. 连续多次提问

---

## 十二、待确认事项

### 12.1 技术选型
- [ ] 是否需要支持 PDF（MVP 阶段）
- [ ] 是否需要流式返回答案
- [ ] 是否需要文档删除功能

### 12.2 业务逻辑
- [ ] 上传后立即建立索引还是异步处理
- [ ] 是否允许并发上传
- [ ] 索引建立期间是否允许提问

### 12.3 配置参数
- [ ] Chunk 大小（建议 500）
- [ ] Chunk 重叠（建议 50）
- [ ] 检索 Top-K（建议 3）
- [ ] 相似度阈值（建议 0.7）
- [ ] 文件大小限制（建议 10MB）

---

## 十三、附录

### 13.1 参考资源
- LangChain 文档：https://python.langchain.com/
- 千帆 Embedding 文档：https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html
- 月之暗面文档：https://platform.moonshot.cn/docs/intro
- FAISS 文档：https://faiss.ai/

### 13.2 项目现有可参考代码
- `study/18 huggingFace/百度千帆文本嵌入模型.py`
- `study/19 Faiss 向量数据库的配置与使用/`
- `study/28 文档转换器与文本分割器组件的使用/`
- `study/33 VectorStore/`

---

**文档版本**: v1.0
**创建时间**: 2024-03-07
**最后更新**: 2024-03-07
