#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : rag_handler.py
@Description : RAG 控制器
"""
import os
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from flask import Response, render_template, request, stream_with_context
from injector import inject

from internal.service.rag_service import RAGService
from pkg.response import fail_json, success_json


@inject
@dataclass
class RAGHandler:
    """RAG 控制器"""

    rag_service: RAGService

    ALLOWED_EXTENSIONS = {"md", "txt", "pdf"}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    def rag_page(self):
        return render_template("rag.html")

    def upload_document(self, app_id: str = "default"):
        try:
            if "file" not in request.files:
                return fail_json({"message": "没有上传文件"})

            file = request.files["file"]
            if file.filename == "":
                return fail_json({"message": "文件名为空"})

            if not self._allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "无扩展名"
                return fail_json({"message": f"不支持的文件格式: .{ext}，仅支持 {', '.join(self.ALLOWED_EXTENSIONS)}"})

            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if file_size > self.MAX_CONTENT_LENGTH:
                return fail_json({"message": f"文件过大，最大支持 {self.MAX_CONTENT_LENGTH // (1024 * 1024)}MB"})

            original_filename = file.filename
            if "." not in original_filename:
                return fail_json({"message": "文件必须包含扩展名"})

            ext = original_filename.rsplit(".", 1)[1].lower()
            stored_filename = f"{uuid.uuid4().hex}.{ext}"

            documents_dir = self.rag_service.get_documents_dir(app_id)
            Path(documents_dir).mkdir(parents=True, exist_ok=True)
            file_path = os.path.join(documents_dir, stored_filename)
            file.save(file_path)

            result = self.rag_service.upload_document(
                app_id=app_id,
                file_path=file_path,
                original_filename=original_filename,
            )
            return success_json(result)
        except Exception as e:
            return fail_json({"message": f"上传失败: {str(e)}"})

    def list_documents(self, app_id: str = "default"):
        try:
            documents = self.rag_service.list_documents(app_id)
            return success_json({"documents": documents})
        except Exception as e:
            return fail_json({"message": f"获取文档列表失败: {str(e)}"})

    def upload_url(self, app_id: str = "default"):
        try:
            payload = request.get_json(silent=True) or {}
            url = str(payload.get("url", "")).strip()
            if not url:
                return fail_json({"message": "url 不能为空"})
            if not (url.startswith("http://") or url.startswith("https://")):
                return fail_json({"message": "仅支持 http/https 链接"})

            result = self.rag_service.upload_url_document(app_id=app_id, url=url)
            return success_json(result)
        except Exception as e:
            return fail_json({"message": f"链接解析失败: {str(e)}"})

    def delete_document(self, app_id: str = "default", document_id: str = ""):
        try:
            if not document_id:
                return fail_json({"message": "document_id 不能为空"})
            result = self.rag_service.delete_document(app_id=app_id, document_id=document_id)
            return success_json(result)
        except ValueError as e:
            return fail_json({"message": str(e)})
        except Exception as e:
            return fail_json({"message": f"删除文档失败: {str(e)}"})

    def ask_question(self, app_id: str = "default"):
        try:
            payload = request.get_json(silent=True) or {}
            question = str(payload.get("question", "")).strip()
            session_id = str(payload.get("session_id", "default")).strip() or "default"

            if not question:
                return fail_json({"message": "问题不能为空"})
            if len(question) > 500:
                return fail_json({"message": "问题最大长度为500字符"})
            if len(session_id) > 128:
                return fail_json({"message": "session_id 最大长度为128字符"})

            result = self.rag_service.ask_question(app_id=app_id, question=question, session_id=session_id)
            return success_json(result)
        except Exception as e:
            return fail_json({"message": f"提问失败: {str(e)}"})

    def ask_question_stream(self, app_id: str = "default"):
        payload = request.get_json(silent=True) or {}
        question = str(payload.get("question", "")).strip()
        session_id = str(payload.get("session_id", "default")).strip() or "default"

        if not question:
            return fail_json({"message": "问题不能为空"})
        if len(question) > 500:
            return fail_json({"message": "问题最大长度为500字符"})
        if len(session_id) > 128:
            return fail_json({"message": "session_id 最大长度为128字符"})

        def event_stream():
            try:
                for item in self.rag_service.ask_question_stream(
                    app_id=app_id,
                    question=question,
                    session_id=session_id,
                ):
                    event = item.get("event", "message")
                    data = item.get("data", "")
                    payload_text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
                    yield f"event: {event}\n"
                    yield f"data: {payload_text}\n\n"
            except Exception as e:
                err = json.dumps({"message": f"流式提问失败: {str(e)}"}, ensure_ascii=False)
                yield "event: error\n"
                yield f"data: {err}\n\n"

        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    def clear_session_memory(self, app_id: str = "default", session_id: str = "default"):
        try:
            result = self.rag_service.clear_session_memory(app_id=app_id, session_id=session_id)
            return success_json(result)
        except Exception as e:
            return fail_json({"message": f"清空会话记忆失败: {str(e)}"})

    def _allowed_file(self, filename: str) -> bool:
        if "." in filename:
            ext = filename.rsplit(".", 1)[1].lower()
            return ext in self.ALLOWED_EXTENSIONS
        return False
