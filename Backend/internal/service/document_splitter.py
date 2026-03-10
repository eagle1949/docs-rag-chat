#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : document_splitter.py
@Description : 文档切分服务
"""
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentSplitter:
    """文档切分器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文档切分器

        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        切分文档

        Args:
            documents: 文档列表

        Returns:
            切分后的文档列表
        """
        try:
            split_docs = self.splitter.split_documents(documents)
            # 为每个切分后的文档添加 chunk_id
            for i, doc in enumerate(split_docs):
                doc.metadata["chunk_id"] = i
            return split_docs
        except Exception as e:
            raise Exception(f"文档切分失败: {str(e)}")
