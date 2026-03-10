#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : rag_schema.py
@Description : RAG 请求验证 Schema
"""
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired, Length, Optional


class UploadDocumentSchema(FlaskForm):
    """文档上传请求验证"""
    file = FileField("file", validators=[
        DataRequired(message="请选择要上传的文件")
    ])


class AskQuestionSchema(FlaskForm):
    """提问请求验证"""
    question = StringField("question", validators=[
        DataRequired(message="问题是必填项"),
        Length(max=500, message="问题最大长度为500字符")
    ])
