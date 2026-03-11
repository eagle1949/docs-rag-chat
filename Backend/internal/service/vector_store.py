#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : vector_store.py
@Description : 向量库管理服务
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorStoreManager:
    """向量库管理器"""

    def __init__(self, index_path: str = "./data/faiss_index"):
        """
        初始化向量库管理器

        Args:
            index_path: FAISS 索引存储路径
        """
        self.index_path = index_path
        self.embeddings = QianfanEmbeddingsEndpoint()
        self.db: Optional[FAISS] = None

        # 确保索引目录存在
        Path(index_path).mkdir(parents=True, exist_ok=True)

    def create_index(self, documents: List[Document]) -> FAISS:
        """
        创建 FAISS 索引

        Args:
            documents: 文档列表

        Returns:
            FAISS 向量数据库
        """
        try:
            if not documents:
                raise ValueError("文档列表不能为空")

            # 创建新的索引
            self.db = FAISS.from_documents(documents, self.embeddings)
            return self.db
        except Exception as e:
            raise Exception(f"创建索引失败: {str(e)}")

    def save_index(self):
        """保存索引到本地"""
        if self.db is None:
            raise ValueError("没有可保存的索引")

        try:
            self.db.save_local(self.index_path)
        except Exception as e:
            raise Exception(f"保存索引失败: {str(e)}")

    def load_index(self) -> FAISS:
        """
        从本地加载索引

        Returns:
            FAISS 向量数据库

        Raises:
            FileNotFoundError: 索引文件不存在
        """
        if not self._index_exists():
            raise FileNotFoundError("索引文件不存在，请先上传文档")

        try:
            self.db = FAISS.load_local(
                self.index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return self.db
        except Exception as e:
            raise Exception(f"加载索引失败: {str(e)}")

    def add_documents(self, documents: List[Document]):
        """
        向现有索引添加文档

        Args:
            documents: 文档列表

        Raises:
            FileNotFoundError: 索引文件不存在
        """
        # 如果索引不存在，先加载
        if self.db is None:
            if self._index_exists():
                self.load_index()
            else:
                # 如果索引不存在，创建新索引
                self.create_index(documents)
                self.save_index()
                return

        try:
            ids = self.db.add_documents(documents)
            self.save_index()
            return ids
        except Exception as e:
            raise Exception(f"添加文档到索引失败: {str(e)}")

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        score_threshold: float = 0.7
    ) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度阈值（暂未使用，返回所有结果）

        Returns:
            相关文档列表

        Raises:
            FileNotFoundError: 索引文件不存在
        """
        if self.db is None:
            if not self._index_exists():
                raise FileNotFoundError("索引文件不存在，请先上传文档")
            self.load_index()

        try:
            # 使用简单的相似度搜索
            results = self.db.similarity_search(query, k=k)
            return results
        except Exception as e:
            raise Exception(f"相似度搜索失败: {str(e)}")

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3,
    ) -> List[Tuple[Document, float]]:
        """带分数的相似度搜索，返回 (Document, distance_score)。"""
        if self.db is None:
            if not self._index_exists():
                raise FileNotFoundError("索引文件不存在，请先上传文档。")
            self.load_index()

        try:
            return self.db.similarity_search_with_score(query, k=k)
        except Exception as e:
            raise Exception(f"相似度搜索失败: {str(e)}")

    def delete_documents(self, ids: List[str]) -> bool:
        """按向量 ID 删除文档向量。"""
        if not ids:
            return True

        if self.db is None:
            if not self._index_exists():
                return True
            self.load_index()

        try:
            deleted = self.db.delete(ids=ids)
            self.save_index()
            return bool(deleted)
        except Exception as e:
            raise Exception(f"删除向量失败: {str(e)}")

    def _index_exists(self) -> bool:
        """检查索引文件是否存在"""
        index_file = Path(self.index_path) / "index.faiss"
        return index_file.exists()

    def clear_index(self):
        """清空索引"""
        import shutil
        if Path(self.index_path).exists():
            shutil.rmtree(self.index_path)
            Path(self.index_path).mkdir(parents=True, exist_ok=True)
        self.db = None
