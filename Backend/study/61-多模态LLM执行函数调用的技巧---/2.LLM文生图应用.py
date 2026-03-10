#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/13 12:34
@Author  : 
@File    : 2.LLM文生图应用.py - 千问版本
"""
import dotenv
import json
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import dashscope
from dashscope import ImageSynthesis
import requests
import os
from datetime import datetime

dotenv.load_dotenv()

# 千问API Key配置（需要在.env文件中设置 DASHSCOPE_API_KEY）
dashscope.api_key = dotenv.get_key(dotenv.find_dotenv(), "DASHSCOPE_API_KEY")

@tool
def generate_image(prompt: str) -> str:
    """
    使用通义万相生成图片

    Args:
        prompt: 图片描述提示词

    Returns:
        生成图片保存到当前目录
    """
    try:
        # 调用通义万相API生成图片
        response = ImageSynthesis.call(
            model='wanx-v1',
            prompt=prompt,
            n=1,  # 生成图片数量
            size='1024*1024'  # 图片尺寸
        )

        if response.status_code == 200:
            # 获取图片URL - 直接访问response.output
            image_url = response.output.results[0].url

            # 下载图片并保存到当前目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"

            # 下载图片
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                # 保存到当前目录
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                return f"图片生成成功！已保存到: {os.path.abspath(filename)}"
            else:
                return f"图片生成成功，但下载失败: {image_url}"
        else:
            return f"图片生成失败: {response.message}"

    except Exception as e:
        return f"图片生成异常: {str(e)}"

# 使用千问LLM（通过Ollama本地部署或使用dashscope SDK）
llm = ChatOpenAI(model="moonshot-v1-8k")  # 确保Ollama已下载qwen2.5模型
llm_with_tools = llm.bind_tools([generate_image])

# 构建链：LLM -> 工具调用 -> 执行工具
def extract_tool_args(msg):
    if msg.tool_calls:
        return msg.tool_calls[0]["args"]
    else:
        # 如果LLM没有调用工具，直接使用原始消息作为提示词
        return {"prompt": msg.content}

chain = llm_with_tools | extract_tool_args | generate_image

# 测试
print(chain.invoke("请生成一张图片：火影忍者鸣人和孙悟空打架"))
