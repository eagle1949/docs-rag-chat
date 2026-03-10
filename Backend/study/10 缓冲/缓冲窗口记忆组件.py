import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

dotenv.load_dotenv()

# 1.创建提示模板&记忆
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请根据对应的上下文回复用户问题"),
    MessagesPlaceholder("history"),  # 需要的history其实是一个列表
    ("human", "{query}"),
])

# 使用简单的列表存储历史消息 (替代 ConversationTokenBufferMemory)
class SimpleMemory:
    def __init__(self, max_token_limit=2000):
        self.history = []
        self.max_token_limit = max_token_limit

    def add_user_message(self, message: str):
        self.history.append(HumanMessage(content=message))
        self._trim_history()

    def add_ai_message(self, message: str):
        self.history.append(AIMessage(content=message))
        self._trim_history()

    def _trim_history(self):
        """简单的token估算和修剪 (近似值: 1 token ≈ 4 字符)"""
        total_chars = sum(len(msg.content) for msg in self.history)
        max_chars = self.max_token_limit * 4

        while total_chars > max_chars and len(self.history) > 2:
            # 移除最旧的消息 (保留system消息后的对话)
            removed = self.history.pop(0)
            total_chars -= len(removed.content)

    def get_history(self):
        return self.history

memory = SimpleMemory(max_token_limit=2000)

# 2.创建大语言模型
llm = ChatOpenAI(model="moonshot-v1-8k")

# 3.构建链应用
chain = RunnablePassthrough.assign(
    history=lambda x: memory.get_history()
) | prompt | llm | StrOutputParser()

# 4.死循环构建对话命令行
while True:
    query = input("Human: ")

    if query == "q":
        exit(0)

    chain_input = {"query": query, "language": "中文"}

    response = chain.stream(chain_input)
    print("AI: ", flush=True, end="")
    output = ""
    for chunk in response:
        output += chunk
        print(chunk, flush=True, end="")

    # 保存对话到记忆
    memory.add_user_message(query)
    memory.add_ai_message(output)

    print("")
    print("history: ", memory.get_history())
