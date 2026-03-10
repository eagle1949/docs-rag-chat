#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/29 14:59
@Author  : 
@File    : app_handler.py
"""
import uuid
from dataclasses import dataclass
from uuid import UUID

from flask import Response
from injector import inject

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from internal.service.chat_service import ChatService
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService
    chat_service: ChatService

    def create_app(self):
        """调用服务创建新的APP记录"""
        app = self.app_service.create_app()
        return success_message(f"应用已经成功创建，id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名字是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改，修改的名字是:{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除，id为:{app.id}")

    def debug(self, app_id: UUID):
        """聊天接口，支持记忆功能"""
        # 1.提取从接口中获取的输入，POST
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.获取会话ID，如果没有提供则使用app_id作为默认会话ID
        session_id = req.session_id.data if req.session_id.data else str(app_id)

        # 3.使用ChatService进行流式聊天
        return Response(
            self.chat_service.chat_stream(req.query.data, session_id),
            mimetype="text/event-stream"
        )
        

    def ping(self):
        raise FailException("数据未找到")
