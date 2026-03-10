import json
from typing import TypedDict, Annotated, Any, Literal

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dashscope import ImageSynthesis
import dashscope
import requests
import os
from datetime import datetime

# 设置通义万相API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


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

class State(TypedDict):
    """图状态数据结构，类型为字典"""
    messages: Annotated[list, add_messages]


tools = [google_serper, generate_image]
llm = ChatOpenAI(model="moonshot-v1-8k")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State) -> Any:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表数据并传递给LLM
    ai_message = llm_with_tools.invoke(state["messages"])
    # 2.返回更新/生成的状态
    return {"messages": [ai_message]}

def tool_executor(state: State) -> Any:
    """工具执行函数"""
    tool_calls = state["messages"][-1].tool_calls

    # 2.根据找到的tool_calls去获取需要执行什么工具
    tools_by_name = {tool.name: tool for tool in tools}

    # 3.执行工具得到对应的结果
    messages = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        messages.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=json.dumps(tool.invoke(tool_call["args"])),
            name=tool_call["name"]
        ))

    # 4.将工具的执行结果作为工具消息更新到数据状态机中
    return {"messages": messages}

def route(state: State) -> Literal["tool_executor", "__end__"]:
    """通过路由来取检测下后续的返回节点是什么，返回的节点有2个，一个是工具执行，一个是结束节点"""
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tool_executor"
    return END


# 1. 创建状态图
graph = StateGraph(State)
# 2. 添加节点
graph.add_node("llm", chatbot)
graph.add_node("tool_executor", tool_executor)


# 4. 设置入口点
graph.set_entry_point("llm")
graph.add_conditional_edges( "llm", route) # 添加条件边
graph.add_edge("tool_executor", "llm")  # 固定边，工具执行后返回LLM


# 5. 编译状态图
app = graph.compile()

# 5.调用图架构应用
state = app.invoke({"messages": [("human", "生成一张小鸟走路图片")]})

for message in state["messages"]:
    print("消息类型: ", message.type)
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        print("工具调用参数: ", message.tool_calls)
    print("消息内容: ", message.content)
    print("=====================================")


# 入口 → chatbot节点 ──┬──→ route函数(条件边) ──→ tool_executor节点 ─┐
#                     │                                      │
#                     └──────────────────────────────────────┘
#                          (有tool调用则执行工具，否则结束)
# 关键组件
# 1. 工具定义
# google_serper: 谷歌搜索工具，用于时事查询
# generate_image: 使用通义万相 API 生成图片并保存到本地
# 2. 状态类 (State)

# class State(TypedDict):
#     messages: Annotated[list, add_messages]
# 使用 add_messages 注解自动合并消息列表，避免覆盖。

# 3. 两个节点
# chatbot: 调用 LLM，生成回复或工具调用
# tool_executor: 执行 LLM 返回的工具调用
# 4. 条件边 (route) - 核心重点

# def route(state: State) -> Literal["tool_executor", "__end__"]:
#     ai_message = state["messages"][-1]
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tool_executor"  # 有工具调用 → 执行工具
#     return END                   # 无工具调用 → 结束
# 这是条件边的关键：根据消息内容动态决定下一个节点。

# 5. 图构建 (关键代码)

# graph.add_conditional_edges("llm", route)  # 从llm节点出发，根据route函数决定去向
# graph.add_edge("tool_executor", "llm")     # 工具执行完返回llm继续处理
# 执行结果示例
# 对于请求 "生成一张小鸟走路图片"：

# LLM 识别需要调用 generate_image 工具
# route 返回 "tool_executor"
# 执行图片生成并保存
# 回到 chatbot 节点
# LLM 根据工具结果生成最终回复
# route 返回 END，流程结束