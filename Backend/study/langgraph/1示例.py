from typing import TypedDict, Annotated, Any

import dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

dotenv.load_dotenv()
llm = ChatOpenAI(model="moonshot-v1-32k")

# 创建状态图，并使用GraphState作为状态数据
class State(TypedDict):
    messages: Annotated[list, add_messages]
    username: str

def chatbot(state: State, config: dict = None) -> Any:
     """聊天机器人节点，使用大语言模型根据传递的消息列表生成内容"""
     ai_message = llm.invoke(state["messages"])
     return {"messages": [ai_message], "username": "chatbot"}

graph_builder = StateGraph(State)


graph_builder.add_node("llm", chatbot)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

# 4.编译图为Runnable可运行组件
graph = graph_builder.compile()


print(graph.invoke({"messages": [("human", "你好，你是谁，我叫慕小课，我喜欢打篮球游泳")], "username": "graph"}))


# 1. 状态定义 (State)


# class State(TypedDict):
#     messages: Annotated[list, add_messages]  # 消息列表
#     username: str                             # 用户名
# messages: 使用 add_messages 注解，表示消息会追加而不是覆盖
# username: 普通字符串字段
# 2. 节点函数 (chatbot)


# def chatbot(state: State, config: dict = None) -> Any:
#     ai_message = llm.invoke(state["messages"])
#     return {"messages": [ai_message], "username": "chatbot"}
# 接收当前状态，调用 LLM 生成回复
# 返回要更新的状态字段
# 3. 构建图 (graph_builder)


# graph_builder = StateGraph(State)
# graph_builder.add_node("llm", chatbot)     # 添加节点
# graph_builder.add_edge(START, "llm")       # 开始 → llm节点
# graph_builder.add_edge("llm", END)         # llm节点 → 结束
# 4. 编译并调用 (第29-32行)


# graph = graph_builder.compile()
# graph.invoke({"messages": [("human", "你好...")], "username": "graph"})
# 流程图

# START → llm节点 → END
#          ↓
#     调用大模型生成回复