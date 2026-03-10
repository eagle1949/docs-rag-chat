#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : document_loader.py
@Description : 文档加载服务
"""
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain_core.documents import Document


class DocumentLoader:
    """文档加载器"""

    def __init__(self):
        pass

    def load_document(self, file_path: str) -> List[Document]:
        """
        加载文档

        Args:
            file_path: 文档路径

        Returns:
            文档列表

        Raises:
            ValueError: 不支持的文件格式
        """
        ext = Path(file_path).suffix.lower()

        if ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
        elif ext in [".txt", ".text"]:
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件格式: {ext}，仅支持 .md 和 .txt")

        try:
            documents = loader.load()
            # 为每个文档添加源文件名到 metadata
            for doc in documents:
                doc.metadata["source"] = Path(file_path).name
            return documents
        except Exception as e:
            raise Exception(f"文档加载失败: {str(e)}")
