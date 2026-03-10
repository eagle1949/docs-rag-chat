#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/4 8:06
@Author  : 
@File    : 3.最大边际相关性示例.py
"""
import dotenv
import weaviate
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./项目API文档.md")
# 1.构建加载器与分割器
loader = UnstructuredMarkdownLoader(file_path)
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", "", ],
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

# 2.加载文档并分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

# 3.将数据存储到向量数据库
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="r40kke3qtkmeqd518rdvw.c0.asia-southeast1.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("bVlLK3Y1OWhobTJud3k4bV9mZXk0bzErRTRMT2YvZlZRb2wrNGYwWGVGeDlsNjlpZW4xVEtLbnNSN3VvPV92MjAw"),
    ),
    index_name="DatasetDemo",
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
)
db.add_documents(chunks)

# 4.转换检索器（带阈值的相似性搜索，数据为10条，得分阈值为0.5）
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5},
)

# 5.检索结果
documents = retriever.invoke("关于配置接口的信息有哪些")

print(list(document.page_content[:50] for document in documents))
print(len(documents))
