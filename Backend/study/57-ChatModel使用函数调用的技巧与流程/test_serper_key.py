#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Serper API密钥是否有效
"""
import os
import requests
import dotenv

dotenv.load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
print(f"SERPER_API_KEY存在: {bool(serper_api_key)}")
print(f"SERPER_API_KEY前10位: {serper_api_key[:10] if serper_api_key else 'None'}...")

if serper_api_key:
    # 测试API调用
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "q": "test query",
        "gl": "us",
        "hl": "en"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            print("[OK] API密钥有效!")
            data = response.json()
            print(f"返回结果数量: {len(data.get('organic', []))}")
        elif response.status_code == 403:
            print("[ERROR] 403 Forbidden - API密钥无效或已过期")
            print("\n请按以下步骤获取新的API密钥:")
            print("1. 访问 https://serper.dev/")
            print("2. 注册或登录账户")
            print("3. 获取新的API密钥(免费版有2500次查询额度)")
            print("4. 将新密钥更新到 .env 文件的 SERPER_API_KEY")
        else:
            print(f"[ERROR] 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")
else:
    print("\n[ERROR] 未找到SERPER_API_KEY环境变量")
    print("请在 .env 文件中添加: SERPER_API_KEY=your_api_key_here")
