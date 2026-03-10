#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : rag_handler.py
@Description : RAG 控制器
"""
import os
import uuid
from pathlib import Path
from dataclasses import dataclass
from werkzeug.utils import secure_filename
from flask import request, render_template
from injector import inject

from internal.service.rag_service import RAGService
from internal.schema.rag_schema import AskQuestionSchema
from pkg.response import success_json, fail_json, validate_error_json


@inject
@dataclass
class RAGHandler:
    """RAG 控制器"""
    rag_service: RAGService

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'md', 'txt'}
    # 最大文件大小 10MB
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    def rag_page(self):
        """RAG 前端页面"""
        return render_template('rag.html')

    def upload_document(self):
        """上传文档"""
        try:
            # 检查是否有文件
            if 'file' not in request.files:
                return fail_json({"message": "没有上传文件"})

            file = request.files['file']

            # 检查文件名是否为空
            if file.filename == '':
                return fail_json({"message": "文件名为空"})

            # 检查文件扩展名
            if not self._allowed_file(file.filename):
                # 获取文件扩展名用于错误提示
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else '无扩展名'
                return fail_json({
                    "message": f"不支持的文件格式: .{ext}，仅支持 {', '.join(self.ALLOWED_EXTENSIONS)}"
                })

            # 检查文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > self.MAX_CONTENT_LENGTH:
                return fail_json({"message": f"文件过大，最大支持 {self.MAX_CONTENT_LENGTH // (1024*1024)}MB"})

            # 确保目录存在
            Path(self.rag_service.documents_dir).mkdir(parents=True, exist_ok=True)

            # 保存文件
            original_filename = file.filename

            # 提取扩展名
            if '.' in original_filename:
                ext = original_filename.rsplit('.', 1)[1].lower()
            else:
                return fail_json({"message": "文件必须包含扩展名"})

            # 使用UUID作为文件名，保留扩展名（避免中文文件名问题）
            filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(self.rag_service.documents_dir, filename)

            file.save(file_path)

            # 上传到 RAG 服务
            result = self.rag_service.upload_document(file_path)

            return success_json(result)

        except Exception as e:
            return fail_json({"message": f"上传失败: {str(e)}"})

    def ask_question(self):
        """提问"""
        try:
            # 验证请求参数
            schema = AskQuestionSchema()
            if not schema.validate():
                return validate_error_json(schema.errors)

            question = schema.question.data

            # 调用 RAG 服务
            result = self.rag_service.ask_question(question)

            return success_json(result)

        except Exception as e:
            return fail_json({"message": f"提问失败: {str(e)}"})

    def _allowed_file(self, filename):
        """检查文件扩展名是否允许"""
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
            return ext in self.ALLOWED_EXTENSIONS
        return False
