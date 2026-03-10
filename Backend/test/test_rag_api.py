#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/7
@Author  : Claude
@File    : test_rag_api.py
@Description : RAG API 测试用例
"""
import unittest
import os
import sys
import tempfile
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.http.app import app


class TestRAGAPI(unittest.TestCase):
    """RAG API 测试类"""

    def setUp(self):
        """测试前准备"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # 创建测试文档
        self.test_docs = {
            'langchain.md': '''# LangChain 简介

LangChain 是一个用于开发由语言模型驱动的应用程序的框架。

## 核心概念

### Chain（链）
Chain 是 LangChain 的核心概念之一，它允许将多个组件串联在一起。

### Agent（智能体）
Agent 是一个使用 LLM 来决定行动的系统，它可以访问工具并决定使用哪些工具。

### Memory（记忆）
Memory 允许系统在多次交互中记住信息。

## 使用场景

LangChain 可以用于构建各种应用，包括：
- 问答系统
- 聊天机器人
- 文档分析
- 数据生成
''',
            'python.txt': '''Python 是一种高级编程语言。

Python 的特点：
1. 简单易学
2. 功能强大
3. 应用广泛

Python 常用于：
- Web 开发
- 数据科学
- 人工智能
- 自动化脚本
'''
        }

    def tearDown(self):
        """测试后清理"""
        # 清理测试数据
        import shutil
        if os.path.exists('./data/faiss_index'):
            shutil.rmtree('./data/faiss_index')
        if os.path.exists('./data/documents'):
            shutil.rmtree('./data/documents')

    def test_01_upload_markdown_document(self):
        """测试上传 Markdown 文档"""
        print("\n测试 1: 上传 Markdown 文档")

        # 准备测试数据
        doc_content = self.test_docs['langchain.md']
        data = {
            'file': (tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.md',
                delete=False,
                encoding='utf-8'
            ), doc_content)
        }

        # 写入临时文件
        with open(data['file'][0].name, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        # 重新准备数据（因为文件需要先关闭）
        with open(data['file'][0].name, 'rb') as f:
            response = self.client.post(
                '/rag/documents/upload',
                data={'file': (f, 'langchain.md')},
                content_type='multipart/form-data'
            )

        # 清理临时文件
        os.unlink(data['file'][0].name)

        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.get_json()}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['code'], 200)
        self.assertIn('filename', data['data'])
        self.assertIn('chunks', data['data'])
        print("[OK] Markdown 文档上传成功")

    def test_02_upload_txt_document(self):
        """测试上传 TXT 文档"""
        print("\n测试 2: 上传 TXT 文档")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.test_docs['python.txt'])
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    '/rag/documents/upload',
                    data={'file': (f, 'python.txt')},
                    content_type='multipart/form-data'
                )

            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.get_json()}")

            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['code'], 'success')
            print("[OK] TXT 文档上传成功")
        finally:
            os.unlink(temp_path)

    def test_03_upload_unsupported_format(self):
        """测试上传不支持的文件格式"""
        print("\n测试 3: 上传不支持的文件格式")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    '/rag/documents/upload',
                    data={'file': (f, 'test.pdf')},
                    content_type='multipart/form-data'
                )

            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.get_json()}")

            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['code'], 'fail')  # 应该返回错误码
            print("[OK] 正确拒绝不支持的文件格式")
        finally:
            os.unlink(temp_path)

    def test_04_upload_without_file(self):
        """测试没有上传文件"""
        print("\n测试 4: 没有上传文件")

        response = self.client.post(
            '/rag/documents/upload',
            data={},
            content_type='multipart/form-data'
        )

        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.get_json()}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['code'], 'fail')
        print("[OK] 正确处理未上传文件的情况")

    def test_05_ask_question(self):
        """测试提问功能"""
        print("\n测试 5: 提问功能")

        # 先上传一个文档
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.test_docs['langchain.md'])
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                upload_response = self.client.post(
                    '/rag/documents/upload',
                    data={'file': (f, 'langchain.md')},
                    content_type='multipart/form-data'
                )

            print(f"文档上传响应: {upload_response.get_json()}")

            # 等待索引建立完成
            import time
            time.sleep(2)

            # 提问
            question_response = self.client.post(
                '/rag/ask',
                data=json.dumps({'question': '什么是 LangChain？'}),
                content_type='application/json'
            )

            print(f"响应状态码: {question_response.status_code}")
            print(f"响应内容: {question_response.get_json()}")

            self.assertEqual(question_response.status_code, 200)
            data = question_response.get_json()
            self.assertEqual(data['code'], 'success')
            self.assertIn('answer', data['data'])
            self.assertIn('sources', data['data'])
            print("[OK] 提问功能正常")
        finally:
            os.unlink(temp_path)

    def test_06_ask_without_documents(self):
        """测试没有上传文档时提问"""
        print("\n测试 6: 没有上传文档时提问")

        response = self.client.post(
            '/rag/ask',
            data=json.dumps({'question': '测试问题'}),
            content_type='application/json'
        )

        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.get_json()}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # 应该返回提示上传文档的消息
        self.assertIn('没有找到相关', data['data']['answer'])
        print("[OK] 正确处理未上传文档的情况")

    def test_07_ask_empty_question(self):
        """测试空问题"""
        print("\n测试 7: 空问题")

        response = self.client.post(
            '/rag/ask',
            data=json.dumps({'question': ''}),
            content_type='application/json'
        )

        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.get_json()}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['code'], 'validate_error')  # 应该返回验证错误
        print("[OK] 正确处理空问题")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("RAG API 测试开始")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRAGAPI)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 60)
    print(f"测试完成！运行: {result.testsRun}, 成功: {result.testsRun - len(result.failures) - len(result.errors)}, 失败: {len(result.failures)}, 错误: {len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
