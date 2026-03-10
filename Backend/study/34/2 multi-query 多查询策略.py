#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/3 9:25
@Author  : 
@File    : 1.Multi-Query多查询策略.py
"""
import dotenv
import weaviate
from langchain_classic.retrievers import MultiQueryRetriever

from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1.构建向量数据库与检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="xsfb2okarbetu3miqefl7a.c0.asia-southeast1.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("NzRCREhtODhrZk9SeFZReF9PY2tya1Vpd2dDQ3hYc3ZxNW9tM09WN2VFMk9FREw4WHdwR1NGVmVka3FFPV92MjAw"),
    ),
    index_name="DatasetDemo",
    text_key="text",
    embedding= QianfanEmbeddingsEndpoint(model="embedding-v1"),
)
retriever = db.as_retriever(search_type="mmr")

# 2.创建多查询检索器
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=ChatOpenAI(model="moonshot-v1-8k", temperature=0),
    include_original=True,
)

# 3.执行检索
docs = multi_query_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(docs)
print(len(docs))
