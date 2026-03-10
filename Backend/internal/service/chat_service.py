#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/15
@Author  : 
@File    : chat_service.py
"""
import json
from pathlib import Path
from typing import Iterator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from internal.service.summary_buffer_memory import ConversationSummaryBufferMemory


class ChatService:
    """聊天服务，支持摘要缓冲记忆功能"""

    def __init__(
        self,
        model: str = "moonshot-v1-8k",
        storage_path: str = "storage/chat_history",
        max_tokens: int = 1000
    ):
        """
        初始化聊天服务

        Args:
            model: 使用的模型名称
            storage_path: 聊天历史存储路径
            max_tokens: 缓冲区最大token数,超过此值将触发摘要生成
        """
        self.model = model
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.max_tokens = max_tokens

        # 初始化LLM
        self.llm = ChatOpenAI(model=model)

    def _get_memory(self, session_id: str) -> ConversationSummaryBufferMemory:
        """
        获取指定会话的记忆对象

        Args:
            session_id: 会话ID

        Returns:
            ConversationSummaryBufferMemory: 摘要缓冲记忆对象
        """
        return ConversationSummaryBufferMemory(
            session_id=session_id,
            storage_path=str(self.storage_path),
            max_tokens=self.max_tokens,
            model=self.model
        )

    def chat_stream(self, query: str, session_id: str) -> Iterator[str]:
        """
        流式聊天，支持摘要缓冲记忆功能

        Args:
            query: 用户查询
            session_id: 会话ID，用于区分不同的聊天会话

        Yields:
            str: SSE格式的流式响应
        """
        try:
            # 获取记忆对象
            memory = self._get_memory(session_id)

            # 获取历史消息
            history_messages = memory.get_messages()

            # 构建消息列表
            messages = [SystemMessage(content="你是一个有用的AI助手。")]
            messages.extend(history_messages)
            messages.append(HumanMessage(content=query))

            # 流式调用LLM
            full_response = ""
            for chunk in self.llm.stream(messages):
                content = chunk.content
                if content:
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            # 保存对话到记忆中(会自动处理摘要生成)
            memory.save_context(query, full_response)

            # 发送结束标记
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    def clear_history(self, session_id: str) -> bool:
        """
        清空指定会话的聊天历史

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功清空
        """
        memory = self._get_memory(session_id)
        return memory.clear_history()

    def get_history(self, session_id: str) -> list[BaseMessage]:
        """
        获取指定会话的聊天历史

        Args:
            session_id: 会话ID

        Returns:
            list[BaseMessage]: 聊天历史消息列表
        """
        memory = self._get_memory(session_id)
        return memory.get_messages()

    def get_history_stats(self, session_id: str) -> dict:
        """
        获取指定会话的历史统计信息

        Args:
            session_id: 会话ID

        Returns:
            dict: 包含统计信息的字典
        """
        memory = self._get_memory(session_id)
        return memory.get_history_stats()