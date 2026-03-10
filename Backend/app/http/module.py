#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/5 19:03
@Author  : 
@File    : module.py
"""
from flask_migrate import Migrate
from injector import Module, Binder, singleton

from internal.extension.database_extension import db
from internal.extension.migrate_extension import migrate
from internal.service.chat_service import ChatService
from internal.service.rag_service import RAGService
from internal.handler.rag_handler import RAGHandler
from pkg.sqlalchemy import SQLAlchemy


class ExtensionModule(Module):
    """扩展模块的依赖注入"""

    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
        # 绑定ChatService为单例
        binder.bind(ChatService, to=ChatService, scope=singleton)
        # 绑定RAGService为单例
        binder.bind(RAGService, to=RAGService, scope=singleton)
        # 绑定RAGHandler
        binder.bind(RAGHandler, to=RAGHandler, scope=singleton)
