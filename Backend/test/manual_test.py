#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动测试脚本
"""
import requests
import tempfile
import os

BASE_URL = "http://localhost:5000"

def test_upload():
    """测试上传文档"""
    print("=" * 60)
    print("测试 1: 上传 Markdown 文档")
    print("=" * 60)

    # 创建测试文档
    content = """# LangChain 简介

LangChain 是一个用于开发由语言模型驱动的应用程序的框架。

## 核心概念

### Chain（链）
Chain 是 LangChain 的核心概念之一，它允许将多个组件串联在一起。

### Agent（智能体）
Agent 是一个使用 LLM 来决定行动的系统。
"""

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    try:
        with open(temp_path, 'rb') as f:
            files = {'file': ('langchain.md', f, 'text/markdown')}
            response = requests.post(f"{BASE_URL}/rag/documents/upload", files=files)

        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()

    finally:
        os.unlink(temp_path)

def test_ask():
    """测试提问"""
    print("=" * 60)
    print("测试 2: 提问")
    print("=" * 60)

    data = {"question": "什么是 LangChain？"}
    response = requests.post(f"{BASE_URL}/rag/ask", json=data)

    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {result}")

    if result['code'] == 'success':
        print(f"\n答案: {result['data']['answer']}")
        print(f"\n引用来源:")
        for i, source in enumerate(result['data']['sources'], 1):
            print(f"{i}. {source['filename']}")
            print(f"   {source['content']}")
    print()

if __name__ == "__main__":
    print("开始手动测试...")
    print("请确保 Flask 应用正在运行在 http://localhost:5000")
    print()

    # 测试上传
    test_upload()

    # 等待索引建立
    import time
    print("等待索引建立...")
    time.sleep(3)

    # 测试提问
    test_ask()

    print("测试完成！")
