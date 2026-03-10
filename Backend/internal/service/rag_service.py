#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : rag_service.py
@Description : RAG 业务逻辑服务
"""
import os
from pathlib import Path
from typing import Dict, List, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from internal.service.document_loader import DocumentLoader
from internal.service.document_splitter import DocumentSplitter
from internal.service.vector_store import VectorStoreManager


class RAGService:
    """RAG 业务逻辑服务"""

    def __init__(
        self,
        documents_dir: str = "./data/documents",
        index_path: str = "./data/faiss_index"
    ):
        """
        初始化 RAG 服务

        Args:
            documents_dir: 文档存储目录
            index_path: FAISS 索引存储路径
        """
        self.documents_dir = documents_dir
        self.index_path = index_path

        # 初始化各个服务
        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.vector_store = VectorStoreManager(index_path)

        # 确保文档目录存在
        Path(documents_dir).mkdir(parents=True, exist_ok=True)

    def upload_document(self, file_path: str) -> Dict[str, Any]:
        """
        上传文档并建立索引

        Args:
            file_path: 文件路径

        Returns:
            上传结果信息
        """
        try:
            # 1. 加载文档
            documents = self.loader.load_document(file_path)

            # 2. 切分文档
            split_docs = self.splitter.split_documents(documents)

            # 3. 添加到向量库
            self.vector_store.add_documents(split_docs)

            # 4. 保存索引
            self.vector_store.save_index()

            # 5. 返回结果
            filename = Path(file_path).name
            file_size = os.path.getsize(file_path)

            return {
                "filename": filename,
                "size": file_size,
                "chunks": len(split_docs),
                "message": "文档上传成功并建立索引"
            }
        except Exception as e:
            raise Exception(f"文档上传失败: {str(e)}")

    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        基于文档回答问题

        Args:
            question: 用户问题

        Returns:
            答案和引用信息
        """
        try:
            # 1. 检索相关文档
            retrieved_docs = self.vector_store.similarity_search(
                query=question,
                k=3,
                score_threshold=0.7
            )

            if not retrieved_docs:
                return {
                    "answer": "抱歉，没有找到相关的文档内容。请确保已上传相关文档。",
                    "sources": []
                }

            # 2. 生成答案
            answer = self._generate_answer(question, retrieved_docs)

            # 3. 准备引用信息
            sources = self._prepare_sources(retrieved_docs)

            return {
                "answer": answer,
                "sources": sources
            }
        except FileNotFoundError:
            return {
                "answer": "请先上传文档",
                "sources": []
            }
        except Exception as e:
            raise Exception(f"回答问题失败: {str(e)}")

    def _generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """
        使用 LLM 生成答案

        Args:
            question: 用户问题
            context_docs: 检索到的相关文档

        Returns:
            生成的答案
        """
        # 准备上下文
        context = "\n\n".join([
            f"【片段{i+1}】{doc.page_content}"
            for i, doc in enumerate(context_docs)
        ])

        # 创建 Prompt 模板
        prompt = ChatPromptTemplate.from_template("""
基于以下参考内容回答问题：

参考内容：
{context}

问题：{question}

如果参考内容中没有答案，请说"根据提供的文档内容，我无法回答这个问题。"
答案：""")

        # 使用月之暗面 LLM（通过 OpenAI 兼容接口）
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="moonshot-v1-8k",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )

        # 创建链
        chain = prompt | llm | StrOutputParser()

        # 生成答案
        answer = chain.invoke({
            "question": question,
            "context": context
        })

        return answer

    def _prepare_sources(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        准备引用信息

        Args:
            documents: 文档列表

        Returns:
            引用信息列表
        """
        sources = []
        for doc in documents:
            sources.append({
                "filename": doc.metadata.get("source", "unknown"),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "score": 0.8  # FAISS 暂时不返回具体分数，给一个默认值
            })
        return sources

    def clear_all(self):
        """清空所有文档和索引"""
        # 清空索引
        self.vector_store.clear_index()

        # 清空文档目录
        import shutil
        if Path(self.documents_dir).exists():
            shutil.rmtree(self.documents_dir)
            Path(self.documents_dir).mkdir(parents=True, exist_ok=True)
