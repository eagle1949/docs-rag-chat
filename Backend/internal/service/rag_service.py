#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : rag_service.py
@Description : RAG 业务逻辑服务
"""
import json
import os
import re
import shutil
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Iterator, Tuple
from urllib.parse import urlparse

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from internal.service.document_loader import DocumentLoader
from internal.service.document_splitter import DocumentSplitter
from internal.service.summary_buffer_memory import ConversationSummaryBufferMemory
from internal.service.vector_store import VectorStoreManager


class RAGService:
    """RAG 业务逻辑服务"""

    def __init__(
        self,
        base_rag_dir: str = "./data/rag",
        memory_base_dir: str = "./storage/chat_history",
    ):
        self.base_rag_dir = Path(base_rag_dir)
        self.memory_base_dir = Path(memory_base_dir)

        # 保留原字段，兼容旧逻辑中的目录引用
        self.documents_dir = str(self.base_rag_dir / "default" / "documents")

        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter(chunk_size=500, chunk_overlap=50)

        self._vector_store_cache: dict[str, VectorStoreManager] = {}
        self._locks: dict[str, threading.Lock] = {}

        self.base_rag_dir.mkdir(parents=True, exist_ok=True)
        self.memory_base_dir.mkdir(parents=True, exist_ok=True)

    def get_documents_dir(self, app_id: str) -> str:
        return str(self._documents_dir(app_id))

    def list_documents(self, app_id: str) -> List[Dict[str, Any]]:
        app = self._normalize_app_id(app_id)
        meta = self._load_documents_meta(app)
        documents = meta.get("documents", [])
        items = []
        for doc in documents:
            items.append(
                {
                    "document_id": doc.get("document_id"),
                    "filename": doc.get("filename"),
                    "size": doc.get("size", 0),
                    "chunks": doc.get("chunks", 0),
                    "created_at": doc.get("created_at", ""),
                }
            )
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items

    def upload_document(self, app_id: str, file_path: str, original_filename: str) -> Dict[str, Any]:
        app = self._normalize_app_id(app_id)

        lock = self._lock_for(app)
        with lock:
            documents = self.loader.load_document(file_path)
            split_docs = self.splitter.split_documents(documents)

            document_id = f"doc_{uuid.uuid4().hex[:20]}"
            stored_filename = Path(file_path).name

            # 统一覆盖 metadata，确保删除与溯源可用
            for idx, doc in enumerate(split_docs):
                doc.metadata["app_id"] = app
                doc.metadata["document_id"] = document_id
                doc.metadata["source"] = original_filename
                doc.metadata["stored_source"] = stored_filename
                doc.metadata["chunk_id"] = idx

            vector_store = self._vector_store_for(app)
            vector_ids = vector_store.add_documents(split_docs)

            file_size = os.path.getsize(file_path)
            record = {
                "document_id": document_id,
                "filename": original_filename,
                "stored_filename": stored_filename,
                "size": file_size,
                "chunks": len(split_docs),
                "vector_ids": vector_ids,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            meta = self._load_documents_meta(app)
            meta.setdefault("documents", []).append(record)
            self._save_documents_meta(app, meta)

            return {
                "document_id": document_id,
                "filename": original_filename,
                "size": file_size,
                "chunks": len(split_docs),
                "message": "文档上传成功并建立索引",
            }

    def upload_url_document(self, app_id: str, url: str) -> Dict[str, Any]:
        app = self._normalize_app_id(app_id)
        lock = self._lock_for(app)
        with lock:
            documents = self.loader.load_url(url)
            split_docs = self.splitter.split_documents(documents)

            document_id = f"doc_{uuid.uuid4().hex[:20]}"
            parsed = urlparse(url)
            display_name = parsed.netloc + (parsed.path if parsed.path else "")
            display_name = display_name[:120] if display_name else url

            for idx, doc in enumerate(split_docs):
                doc.metadata["app_id"] = app
                doc.metadata["document_id"] = document_id
                doc.metadata["source"] = display_name
                doc.metadata["stored_source"] = ""
                doc.metadata["source_url"] = url
                doc.metadata["chunk_id"] = idx

            vector_store = self._vector_store_for(app)
            vector_ids = vector_store.add_documents(split_docs)

            approx_size = sum(len(doc.page_content or "") for doc in split_docs)
            record = {
                "document_id": document_id,
                "filename": display_name,
                "stored_filename": "",
                "source_url": url,
                "size": approx_size,
                "chunks": len(split_docs),
                "vector_ids": vector_ids,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            meta = self._load_documents_meta(app)
            meta.setdefault("documents", []).append(record)
            self._save_documents_meta(app, meta)

            return {
                "document_id": document_id,
                "filename": display_name,
                "size": approx_size,
                "chunks": len(split_docs),
                "message": "链接解析成功并建立索引",
            }

    def delete_document(self, app_id: str, document_id: str) -> Dict[str, Any]:
        app = self._normalize_app_id(app_id)

        lock = self._lock_for(app)
        with lock:
            meta = self._load_documents_meta(app)
            documents = meta.get("documents", [])
            target = next((x for x in documents if x.get("document_id") == document_id), None)
            if target is None:
                raise ValueError("文档不存在")

            vector_ids = target.get("vector_ids", [])
            if vector_ids:
                vector_store = self._vector_store_for(app)
                vector_store.delete_documents(vector_ids)

            stored_filename = target.get("stored_filename", "")
            if stored_filename:
                file_path = self._documents_dir(app) / stored_filename
                if file_path.exists():
                    file_path.unlink()

            meta["documents"] = [x for x in documents if x.get("document_id") != document_id]
            self._save_documents_meta(app, meta)

            return {
                "document_id": document_id,
                "message": "文档删除成功",
            }

    def ask_question(self, app_id: str, question: str, session_id: str) -> Dict[str, Any]:
        app = self._normalize_app_id(app_id)
        session = session_id.strip() or "default"
        memory = self._memory_for(app, session)
        chat_history = memory.load_memory_variables().get("chat_history", "")

        profile_ack = self._try_ack_profile_input(question)
        if profile_ack:
            memory.save_context(question, profile_ack)
            return {
                "answer": profile_ack,
                "session_id": session,
                "sources": [],
            }

        memory_answer = self._try_answer_from_memory(question, chat_history)
        if memory_answer:
            memory.save_context(question, memory_answer)
            return {
                "answer": memory_answer,
                "session_id": session,
                "sources": [],
            }

        try:
            vector_store = self._vector_store_for(app)
            results = vector_store.similarity_search_with_score(query=question, k=3)

            # FAISS 这里返回的是 distance，越小越相近，转换为 0~1 的 confidence
            scored_docs = []
            for doc, distance in results:
                confidence = 1.0 / (1.0 + float(distance))
                if confidence >= 0.2:
                    scored_docs.append((doc, confidence))

            if not scored_docs:
                # 没有检索到文档时，如果有会话记忆，仍尝试按历史回答。
                if chat_history:
                    answer = self._generate_answer(
                        question=question,
                        context_docs=[],
                        chat_history=chat_history,
                    )
                    memory.save_context(question, answer)
                    return {
                        "answer": answer,
                        "session_id": session,
                        "sources": [],
                    }

                return {
                    "answer": "抱歉，没有找到相关的文档内容。请确保已上传相关文档。",
                    "session_id": session,
                    "sources": [],
                }

            answer = self._generate_answer(
                question=question,
                context_docs=[doc for doc, _ in scored_docs],
                chat_history=chat_history,
            )
            memory.save_context(question, answer)

            sources = self._prepare_sources(scored_docs)
            return {
                "answer": answer,
                "session_id": session,
                "sources": sources,
            }
        except FileNotFoundError:
            return {
                "answer": "请先上传文档。",
                "session_id": session,
                "sources": [],
            }
        except Exception as e:
            raise Exception(self._friendly_llm_error(e))

    def ask_question_stream(self, app_id: str, question: str, session_id: str) -> Iterator[Dict[str, Any]]:
        """
        SSE 流式问答：逐 token 输出，最后输出 done 事件（带 sources）。
        """
        app = self._normalize_app_id(app_id)
        session = session_id.strip() or "default"
        memory = self._memory_for(app, session)
        chat_history = memory.load_memory_variables().get("chat_history", "")

        profile_ack = self._try_ack_profile_input(question)
        if profile_ack:
            memory.save_context(question, profile_ack)
            yield {"event": "token", "data": profile_ack}
            yield {"event": "done", "data": {"session_id": session, "sources": []}}
            return

        memory_answer = self._try_answer_from_memory(question, chat_history)
        if memory_answer:
            memory.save_context(question, memory_answer)
            yield {"event": "token", "data": memory_answer}
            yield {"event": "done", "data": {"session_id": session, "sources": []}}
            return

        try:
            scored_docs = self._retrieve_scored_docs(app, question)
            if not scored_docs and not chat_history:
                final_answer = "抱歉，没有找到相关的文档内容。请确保已上传相关文档。"
                memory.save_context(question, final_answer)
                yield {"event": "token", "data": final_answer}
                yield {"event": "done", "data": {"session_id": session, "sources": []}}
                return

            sources = self._prepare_sources(scored_docs)
            context_docs = [doc for doc, _ in scored_docs]
            full_answer = ""
            for chunk in self._generate_answer_stream(
                question=question,
                context_docs=context_docs,
                chat_history=chat_history,
            ):
                if not chunk:
                    continue
                full_answer += chunk
                yield {"event": "token", "data": chunk}

            if not full_answer.strip():
                full_answer = "根据当前会话记忆和文档内容，我无法回答这个问题。"
                yield {"event": "token", "data": full_answer}

            memory.save_context(question, full_answer)
            yield {"event": "done", "data": {"session_id": session, "sources": sources}}
        except Exception as e:
            yield {"event": "error", "data": {"message": self._friendly_llm_error(e)}}

    def _try_answer_from_memory(self, question: str, chat_history: str) -> str | None:
        """优先处理显式会话类问题，避免被文档检索噪音干扰。"""
        q = question.strip()
        if not q or not chat_history:
            return None

        if not self._is_name_query(q):
            return None

        name = self._extract_name_from_text(chat_history)
        if name:
            return f"根据历史对话，你的名字是{name}。"
        return "我暂时无法从历史对话中确认你的名字。"

    def _is_name_query(self, question: str) -> bool:
        q = question.strip().lower()
        if not q:
            return False
        zh_keywords = ("我叫什么", "我叫啥", "我的名字是什么", "我的名字叫啥", "你记得我叫", "我是谁")
        en_keywords = ("what is my name", "who am i", "do you remember my name")
        return any(k in question for k in zh_keywords) or any(k in q for k in en_keywords)

    def _extract_name_from_text(self, text: str) -> str | None:
        if not text:
            return None

        patterns = [
            r"(?:我叫|我的名字是|我的名字叫)([A-Za-z0-9_\u4e00-\u9fff]{1,20})",
            r"(?:my name is|i am)\s+([A-Za-z][A-Za-z0-9_\-]{0,29})",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                return str(matches[-1]).strip()
        return None

    def _try_ack_profile_input(self, question: str) -> str | None:
        q = question.strip()
        if not q or self._is_name_query(q):
            return None
        name = self._extract_name_from_text(q)
        if not name:
            return None
        return f"好的，我记住了，你叫{name}。"

    def clear_session_memory(self, app_id: str, session_id: str) -> Dict[str, Any]:
        app = self._normalize_app_id(app_id)
        session = session_id.strip() or "default"
        memory = self._memory_for(app, session)
        memory.clear_history()
        return {
            "session_id": session,
            "message": "会话记忆已清空",
        }

    def clear_all(self, app_id: str):
        """清空某个 app 的文档和索引。"""
        app = self._normalize_app_id(app_id)
        lock = self._lock_for(app)
        with lock:
            app_dir = self._app_dir(app)
            if app_dir.exists():
                shutil.rmtree(app_dir)
            app_dir.mkdir(parents=True, exist_ok=True)
            self._vector_store_cache.pop(app, None)

    def _generate_answer(self, question: str, context_docs: List[Document], chat_history: str) -> str:
        context = "\n\n".join([f"【片段{i + 1}】{doc.page_content}" for i, doc in enumerate(context_docs)])
        if not context:
            context = "（当前问题未检索到文档片段）"

        prompt = ChatPromptTemplate.from_template(
            """
你是一个“文档问答 + 多轮会话”助手。你有两类信息源：
1) 会话记忆（chat_history）：历史摘要与最近对话
2) 参考文档（context）：本轮检索到的文档片段

历史对话：
{chat_history}

参考内容：
{context}

问题：{question}

要求：
1. 若问题是会话相关（例如“我叫什么名字”“你刚才说了什么”），优先根据历史对话回答。
2. 若问题是文档知识相关，优先依据参考文档回答，可结合历史对话做指代消解。
3. 若用户是在补充个人信息（如“我叫xx”），先确认“已记住”，不要转为文档总结。
4. 若两类信息都不足，再回答：“根据当前会话记忆和文档内容，我无法回答这个问题。”
5. 禁止编造不存在的信息，回答简洁直接。

答案：
"""
        )

        chain_input = {
            "question": question,
            "context": context,
            "chat_history": chat_history,
        }

        for attempt in range(3):
            try:
                llm = ChatOpenAI(
                    model=self._llm_model(),
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    openai_api_base=os.getenv("OPENAI_API_BASE"),
                )
                chain = prompt | llm | StrOutputParser()
                return chain.invoke(chain_input)
            except Exception as e:
                if not self._is_overloaded_error(e) or attempt >= 2:
                    raise
                time.sleep(1.2 * (attempt + 1))
        raise RuntimeError("LLM 调用失败")

    def _generate_answer_stream(self, question: str, context_docs: List[Document], chat_history: str) -> Iterator[str]:
        context = "\n\n".join([f"【片段{i + 1}】{doc.page_content}" for i, doc in enumerate(context_docs)])
        if not context:
            context = "（当前问题未检索到文档片段）"

        prompt = ChatPromptTemplate.from_template(
            """
你是一个“文档问答 + 多轮会话”助手。你有两类信息源：
1) 会话记忆（chat_history）：历史摘要与最近对话
2) 参考文档（context）：本轮检索到的文档片段

历史对话：
{chat_history}

参考内容：
{context}

问题：{question}

要求：
1. 若问题是会话相关（例如“我叫什么名字”“你刚才说了什么”），优先根据历史对话回答。
2. 若问题是文档知识相关，优先依据参考文档回答，可结合历史对话做指代消解。
3. 若用户是在补充个人信息（如“我叫xx”），先确认“已记住”，不要转为文档总结。
4. 若两类信息都不足，再回答：“根据当前会话记忆和文档内容，我无法回答这个问题。”
5. 禁止编造不存在的信息，回答简洁直接。

答案：
"""
        )

        chain_input = {
            "question": question,
            "context": context,
            "chat_history": chat_history,
        }
        for attempt in range(3):
            try:
                llm = ChatOpenAI(
                    model=self._llm_model(),
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    openai_api_base=os.getenv("OPENAI_API_BASE"),
                )
                chain = prompt | llm | StrOutputParser()
                for chunk in chain.stream(chain_input):
                    yield chunk
                return
            except Exception as e:
                if not self._is_overloaded_error(e) or attempt >= 2:
                    raise
                time.sleep(1.2 * (attempt + 1))

    def _retrieve_scored_docs(self, app_id: str, question: str) -> List[Tuple[Document, float]]:
        vector_store = self._vector_store_for(app_id)
        results = vector_store.similarity_search_with_score(query=question, k=3)
        scored_docs: List[Tuple[Document, float]] = []
        for doc, distance in results:
            confidence = 1.0 / (1.0 + float(distance))
            if confidence >= 0.2:
                scored_docs.append((doc, confidence))
        return scored_docs

    def _prepare_sources(self, documents_with_scores: List[tuple[Document, float]]) -> List[Dict[str, Any]]:
        sources: List[Dict[str, Any]] = []
        for doc, score in documents_with_scores:
            sources.append(
                {
                    "document_id": doc.metadata.get("document_id", ""),
                    "filename": doc.metadata.get("source", "unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", 0),
                    "content": doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content,
                    "score": round(float(score), 4),
                }
            )
        return sources

    def _normalize_app_id(self, app_id: str) -> str:
        app = (app_id or "default").strip()
        if not app:
            return "default"
        safe = "".join(c for c in app if c.isalnum() or c in ("-", "_"))
        return safe or "default"

    def _app_dir(self, app_id: str) -> Path:
        return self.base_rag_dir / app_id

    def _documents_dir(self, app_id: str) -> Path:
        path = self._app_dir(app_id) / "documents"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _index_dir(self, app_id: str) -> Path:
        path = self._app_dir(app_id) / "faiss_index"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _documents_meta_path(self, app_id: str) -> Path:
        return self._app_dir(app_id) / "documents_meta.json"

    def _load_documents_meta(self, app_id: str) -> Dict[str, Any]:
        self._app_dir(app_id).mkdir(parents=True, exist_ok=True)
        meta_path = self._documents_meta_path(app_id)
        if not meta_path.exists():
            return {"app_id": app_id, "documents": []}

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("app_id", app_id)
                    data.setdefault("documents", [])
                    return data
        except Exception:
            pass
        return {"app_id": app_id, "documents": []}

    def _save_documents_meta(self, app_id: str, data: Dict[str, Any]) -> None:
        meta_path = self._documents_meta_path(app_id)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _lock_for(self, app_id: str) -> threading.Lock:
        if app_id not in self._locks:
            self._locks[app_id] = threading.Lock()
        return self._locks[app_id]

    def _vector_store_for(self, app_id: str) -> VectorStoreManager:
        if app_id not in self._vector_store_cache:
            self._vector_store_cache[app_id] = VectorStoreManager(str(self._index_dir(app_id)))
        return self._vector_store_cache[app_id]

    def _memory_for(self, app_id: str, session_id: str) -> ConversationSummaryBufferMemory:
        memory_dir = self.memory_base_dir / app_id
        memory_dir.mkdir(parents=True, exist_ok=True)
        return ConversationSummaryBufferMemory(
            session_id=session_id,
            storage_path=str(memory_dir),
            max_tokens=1000,
            model=self._llm_model(),
        )

    @staticmethod
    def _is_overloaded_error(error: Exception) -> bool:
        text = str(error).lower()
        return "429" in text or "engine_overloaded_error" in text or "overloaded" in text

    @staticmethod
    def _friendly_llm_error(error: Exception) -> str:
        if RAGService._is_overloaded_error(error):
            return "模型服务当前繁忙（429），已自动重试。请稍后再试，或切换到更轻量模型。"
        return f"回答问题失败: {str(error)}"

    @staticmethod
    def _llm_model() -> str:
        return os.getenv("RAG_LLM_MODEL", "moonshot-v1-8k")
