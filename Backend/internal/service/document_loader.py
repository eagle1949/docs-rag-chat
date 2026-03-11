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
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document


class DocumentLoader:
    """文档加载器"""

    def load_document(self, file_path: str) -> List[Document]:
        """
        加载本地文档（md/txt/pdf）。
        """
        ext = Path(file_path).suffix.lower()

        if ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
        elif ext in [".txt", ".text"]:
            loader = TextLoader(file_path, encoding="utf-8")
        elif ext == ".pdf":
            loader = PyPDFLoader(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}，仅支持 .md/.txt/.pdf")

        try:
            documents = loader.load()
            for doc in documents:
                doc.metadata["source"] = Path(file_path).name
            return documents
        except Exception as e:
            raise Exception(f"文档加载失败: {str(e)}")

    def load_url(self, url: str) -> List[Document]:
        """
        解析网页链接为文档。
        """
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("仅支持 http/https 链接")

        try:
            loader = WebBaseLoader(
                web_paths=[url],
                requests_kwargs={"verify": False, "timeout": 20},
                header_template={"User-Agent": "docs-rag-chat/1.0"},
            )
            documents = loader.load()
            for doc in documents:
                doc.metadata["source"] = url
            return documents
        except Exception as e:
            raise Exception(f"链接解析失败: {str(e)}")
