#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试测试脚本
"""
import requests
import tempfile
import os
import json

BASE_URL = "http://localhost:5000"

def test_upload_and_ask():
    """测试上传和问答"""
    print("=" * 60)
    print("RAG API 调试测试")
    print("=" * 60)

    # 1. 上传文档
    print("\n1. 上传文档")
    content = """# LangChain 简介

LangChain 是一个用于开发由语言模型驱动的应用程序的框架。

## 核心概念

Chain（链）是 LangChain 的核心概念之一。
Agent（智能体）是使用 LLM 来决定行动的系统。
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    try:
        with open(temp_path, 'rb') as f:
            files = {'file': ('langchain.md', f, 'text/markdown')}
            response = requests.post(f"{BASE_URL}/rag/documents/upload", files=files)

        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

        if result['code'] != 'success':
            print("[FAIL] 文档上传失败")
            return

        print("[OK] 文档上传成功")

        # 2. 等待索引建立
        print("\n2. 等待索引建立...")
        import time
        time.sleep(5)

        # 3. 提问
        print("\n3. 提问测试")
        questions = [
            "什么是 LangChain？",
            "LangChain 的核心概念有哪些？",
            "什么是 Agent？"
        ]

        for question in questions:
            print(f"\n问题: {question}")
            data = {"question": question}
            response = requests.post(f"{BASE_URL}/rag/ask", json=data)

            print(f"状态码: {response.status_code}")
            result = response.json()
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

            if result['code'] == 'success':
                print(f"答案: {result['data']['answer'][:100]}...")
                print(f"引用数量: {len(result['data']['sources'])}")
            else:
                print("[FAIL] 请求失败")

    finally:
        os.unlink(temp_path)

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_upload_and_ask()
