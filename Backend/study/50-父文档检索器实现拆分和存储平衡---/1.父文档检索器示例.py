#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/6 12:53
@Author  : 
@File    : 1.父文档检索器示例.py
"""
import dotenv
import weaviate
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import LocalFileStore
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from weaviate.auth import AuthApiKey

import os

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./电商产品数据.txt")
file_path1 = os.path.join(script_dir, "./项目API文档.md")

dotenv.load_dotenv()

# 1.创建加载器与文档列表，并加载文档
loaders = [
    UnstructuredFileLoader(file_path),
    UnstructuredFileLoader(file_path1),
]
docs = []
for loader in loaders:
    docs.extend(loader.load())

# 2.创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

vector_store = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="r40kke3qtkmeqd518rdvw.c0.asia-southeast1.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("bVlLK3Y1OWhobTJud3k4bV9mZXk0bzErRTRMT2YvZlZRb2wrNGYwWGVGeDlsNjlpZW4xVEtLbnNSN3VvPV92MjAw"),
   ),
    index_name="ParentDocument",
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
)

byte_store = LocalFileStore("./parent-document")

# 4.创建父文档检索器
retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    byte_store=byte_store,
    child_splitter=text_splitter,
)

# 5.添加文档
# retriever.add_documents(docs, ids=None)

# 6.检索并返回内容
search_docs = retriever.vectorstore.similarity_search("分享关于LLMOps的一些应用配置")
# search_docs = retriever.invoke("分享关于LLMOps的一些应用配置")
print(search_docs)
print(len(search_docs))
