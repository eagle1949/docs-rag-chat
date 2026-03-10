#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/14 21:31
@Author  : 
@File    : 1.基于工具调用的Agent.py
"""
import dotenv
import os
import requests
from datetime import datetime
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dashscope import ImageSynthesis
import dashscope

dotenv.load_dotenv()

# 设置通义万相API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class WanxiangArgsSchema(BaseModel):
    prompt: str = Field(description="输入应该是生成图像的文本提示(prompt)")


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


# 1.定义工具与工具列表
google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
tools = [google_serper, generate_image]

# 2.定义工具调用agent提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是由OpenAI开发的聊天机器人，善于帮助用户解决问题。"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 3.创建大语言模型
llm = ChatOpenAI(model="moonshot-v1-8k", temperature=0)

# 4.创建agent与agent执行者
agent = create_tool_calling_agent(
    prompt=prompt,
    llm=llm,
    tools=tools,
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print(agent_executor.invoke({"input": "帮我绘制一幅鲨鱼在天上游泳的场景"}))
