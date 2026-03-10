#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/15
@Author  : 
@File    : summary_buffer_memory.py
"""
import json
from pathlib import Path
from typing import Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class ConversationSummaryBufferMemory:
    """
    摘要缓冲记忆机制

    工作原理:
    1. 维护一个摘要(summary)和对话缓冲区(chat_histories)
    2. 当缓冲区的token数超过max_tokens时,将最早的对话合并到摘要中
    3. 返回记忆时,同时包含摘要和缓冲区中的对话
    """

    def __init__(
        self,
        session_id: str,
        storage_path: str = "storage/chat_history",
        max_tokens: int = 1000,
        model: str = "moonshot-v1-8k"
    ):
        """
        初始化摘要缓冲记忆

        Args:
            session_id: 会话ID
            storage_path: 存储路径
            max_tokens: 缓冲区最大token数,超过此值将触发摘要生成
            model: 用于生成摘要的模型
        """
        self.session_id = session_id
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.file_path = self.storage_path / f"{session_id}_summary_buffer.json"

        self.max_tokens = max_tokens
        self.client = ChatOpenAI(model=model)

        # 加载或初始化记忆
        self.summary = ""
        self.chat_histories: list[dict[str, str]] = []
        self._load_memory()

    def _load_memory(self) -> None:
        """从文件加载记忆"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.summary = data.get('summary', '')
                    self.chat_histories = data.get('chat_histories', [])
            except Exception as e:
                print(f"加载记忆失败: {e}")
                self.summary = ''
                self.chat_histories = []

    def _save_memory(self) -> None:
        """保存记忆到文件"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': self.summary,
                    'chat_histories': self.chat_histories
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆失败: {e}")

    @staticmethod
    def get_num_tokens(text: str) -> int:
        """
        计算文本的token数(简化估算)
        实际生产环境建议使用tiktoken等精确计算工具

        Args:
            text: 输入文本

        Returns:
            int: 估算的token数
        """
        # 简化估算: 中文约1字符=1token, 英文约4字符=1token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return chinese_chars + (other_chars // 4)

    def save_context(self, human_query: str, ai_response: str) -> None:
        """
        保存新的对话到缓冲区

        如果缓冲区超过max_tokens,会将最早的对话合并到摘要中

        Args:
            human_query: 用户输入
            ai_response: AI回复
        """
        # 添加新对话到缓冲区
        self.chat_histories.append({
            'human': human_query,
            'ai': ai_response,
        })

        # 检查是否需要生成新的摘要
        buffer_string = self._get_buffer_string()
        tokens = self.get_num_tokens(buffer_string)

        if tokens > self.max_tokens and len(self.chat_histories) > 0:
            # 移除最早的对话
            first_chat = self.chat_histories.pop(0)

            # 生成新的摘要
            new_chat_text = f"Human: {first_chat['human']}\nAI: {first_chat['ai']}"
            self.summary = self._summary_text(self.summary, new_chat_text)

        # 保存到文件
        self._save_memory()

    def _get_buffer_string(self) -> str:
        """
        将缓冲区对话转换为字符串

        Returns:
            str: 格式化的对话字符串
        """
        buffer_parts = []
        for chat in self.chat_histories:
            buffer_parts.append(f"Human: {chat['human']}")
            buffer_parts.append(f"AI: {chat['ai']}")
        return '\n'.join(buffer_parts)

    def load_memory_variables(self) -> dict[str, Any]:
        """
        加载记忆变量

        Returns:
            dict: 包含chat_history的字典,包含摘要和缓冲区对话
        """
        buffer_string = self._get_buffer_string()

        if self.summary and buffer_string:
            # 同时有摘要和缓冲区
            history_text = f"摘要:\n{self.summary}\n\n历史对话:\n{buffer_string}"
        elif self.summary:
            # 只有摘要
            history_text = f"摘要:\n{self.summary}"
        elif buffer_string:
            # 只有缓冲区
            history_text = f"历史对话:\n{buffer_string}"
        else:
            # 都没有
            history_text = ""

        return {
            "chat_history": history_text
        }

    def _summary_text(self, original_summary: str, new_chat: str) -> str:
        """
        将旧摘要和新对话生成新摘要

        Args:
            original_summary: 原始摘要
            new_chat: 新的对话内容

        Returns:
            str: 新的摘要
        """
        prompt = f"""你是一个强大的聊天机器人,请根据用户提供的谈话内容,总结摘要,并将其添加到先前提供的摘要中,返回一个新的摘要,除了新摘要其他任何数据都不要生成,如果用户的对话信息里有一些关键的信息,比方说姓名、爱好、性别、重要事件等等,这些全部都要包括在生成的摘要中,摘要尽可能要还原用户的对话记录。

请不要将<example>标签里的数据当成实际的数据,这里的数据只是一个示例数据,告诉你该如何生成新摘要。

<example>
当前摘要:人类会问人工智能对人工智能的看法,人工智能认为人工智能是一股向善的力量。

新的对话:
Human:为什么你认为人工智能是一股向善的力量?
AI:因为人工智能会帮助人类充分发挥潜力。

新摘要:人类会问人工智能对人工智能的看法,人工智能认为人工智能是一股向善的力量,因为它将帮助人类充分发挥潜力。
</example>

=====================以下的数据是实际需要处理的数据=====================

当前摘要:{original_summary}

新的对话:
{new_chat}

请帮用户将上面的信息生成新摘要。"""

        try:
            response = self.client.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"生成摘要失败: {e}")
            # 如果生成摘要失败,返回原始内容
            return original_summary

    def get_messages(self) -> list[BaseMessage]:
        """
        获取LangChain格式的消息列表

        Returns:
            list[BaseMessage]: LangChain消息列表
        """
        messages: list[BaseMessage] = []

        # 添加摘要作为系统消息(如果存在)
        if self.summary:
            messages.append(SystemMessage(content=f"[对话摘要]\n{self.summary}"))

        # 添加缓冲区对话
        for chat in self.chat_histories:
            messages.append(HumanMessage(content=chat['human']))
            messages.append(AIMessage(content=chat['ai']))

        return messages

    def clear_history(self) -> bool:
        """
        清空历史记录

        Returns:
            bool: 是否成功清空
        """
        try:
            self.summary = ''
            self.chat_histories = []
            if self.file_path.exists():
                self.file_path.unlink()
            return True
        except Exception as e:
            print(f"清空历史失败: {e}")
            return False

    def get_history_stats(self) -> dict[str, Any]:
        """
        获取历史统计信息

        Returns:
            dict: 包含统计信息的字典
        """
        buffer_string = self._get_buffer_string()
        return {
            'session_id': self.session_id,
            'summary_length': len(self.summary),
            'summary_tokens': self.get_num_tokens(self.summary),
            'chat_count': len(self.chat_histories),
            'buffer_tokens': self.get_num_tokens(buffer_string),
            'total_tokens': self.get_num_tokens(self.summary) + self.get_num_tokens(buffer_string)
        }
