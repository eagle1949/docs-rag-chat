#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/7 19:28
@Author  : 
@File    : 1.Cohere重排序示例.py
"""
import dotenv
import weaviate
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

dotenv.load_dotenv()

# 1.创建向量数据库与重排组件
embedding = QianfanEmbeddingsEndpoint()
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="r40kke3qtkmeqd518rdvw.c0.asia-southeast1.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("bVlLK3Y1OWhobTJud3k4bV9mZXk0bzErRTRMT2YvZlZRb2wrNGYwWGVGeDlsNjlpZW4xVEtLbnNSN3VvPV92MjAw"),
        skip_init_checks=True,  # Skip gRPC health check
    ),
    index_name="ParentDocument",
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
)
rerank = CohereRerank(model="rerank-multilingual-v3.0")

# 2.构建压缩检索器
retriever = ContextualCompressionRetriever(
    base_retriever=db.as_retriever(search_type="mmr"),
    base_compressor=rerank,
)

# 3.执行搜索并排序
search_docs = retriever.invoke("关于LLMOps应用配置的信息有哪些呢？")
print(search_docs)
print(len(search_docs))
