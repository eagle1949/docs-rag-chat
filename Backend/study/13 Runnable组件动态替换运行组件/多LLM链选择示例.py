import dotenv
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()



prompt = ChatPromptTemplate.from_template("{query}")

llm = ChatOpenAI(model="moonshot-v1-8k").configurable_alternatives(
    ConfigurableField(id="llm", name="大语言模型提供者", description="选择使用的大语言模型提供者"),
    default_key="moonshot-v1-8k",
    wenxin=QianfanChatEndpoint()
)

chain = prompt | llm | StrOutputParser()

content = chain.invoke({"query": "你好，你是什么模型"}, config={"configurable": {"llm": "wenxin"}})

print(content)
