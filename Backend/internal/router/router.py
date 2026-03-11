#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/29 15:01
@Author  : 
@File    : router.py
"""
from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler
from internal.handler.rag_handler import RAGHandler


@inject
@dataclass
class Router:
    """路由"""
    app_handler: AppHandler
    rag_handler: RAGHandler

    def register_router(self, app: Flask):
        """注册路由"""
        # 1.创建一个蓝图
        bp = Blueprint("llmops", __name__, url_prefix="")

        # 2.将url与对应的控制器方法做绑定
        # bp.add_url_rule("/ping", view_func=self.app_handler.ping)
        bp.add_url_rule("/apps/<uuid:app_id>/debug", methods=["POST"], view_func=self.app_handler.debug)
        # bp.add_url_rule("/app", methods=["POST"], view_func=self.app_handler.create_app)
        # bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.get_app)
        # bp.add_url_rule("/app/<uuid:id>", methods=["POST"], view_func=self.app_handler.update_app)
        # bp.add_url_rule("/app/<uuid:id>/delete", methods=["POST"], view_func=self.app_handler.delete_app)

        # RAG 相关路由
        bp.add_url_rule("/rag", methods=["GET"], view_func=self.rag_handler.rag_page)
        bp.add_url_rule("/rag/documents/upload", methods=["POST"], view_func=self.rag_handler.upload_document)
        bp.add_url_rule("/rag/url/upload", methods=["POST"], view_func=self.rag_handler.upload_url)
        bp.add_url_rule("/rag/ask", methods=["POST"], view_func=self.rag_handler.ask_question)
        bp.add_url_rule("/rag/ask/stream", methods=["POST"], view_func=self.rag_handler.ask_question_stream)
        bp.add_url_rule("/rag/documents", methods=["GET"], view_func=self.rag_handler.list_documents)

        # 按 app_id 隔离的 RAG 路由
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/documents/upload",
            methods=["POST"],
            view_func=self.rag_handler.upload_document,
        )
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/url/upload",
            methods=["POST"],
            view_func=self.rag_handler.upload_url,
        )
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/documents",
            methods=["GET"],
            view_func=self.rag_handler.list_documents,
        )
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/documents/<string:document_id>",
            methods=["DELETE"],
            view_func=self.rag_handler.delete_document,
        )
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/ask",
            methods=["POST"],
            view_func=self.rag_handler.ask_question,
        )
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/ask/stream",
            methods=["POST"],
            view_func=self.rag_handler.ask_question_stream,
        )
        bp.add_url_rule(
            "/apps/<string:app_id>/rag/sessions/<string:session_id>/memory",
            methods=["DELETE"],
            view_func=self.rag_handler.clear_session_memory,
        )

        # 3.在应用上去注册蓝图
        app.register_blueprint(bp)
