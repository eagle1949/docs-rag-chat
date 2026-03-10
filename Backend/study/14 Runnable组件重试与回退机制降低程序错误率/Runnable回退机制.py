import dotenv
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(model='moonshot-v1-338k').with_fallbacks([QianfanChatEndpoint()])
chain = prompt | llm | StrOutputParser()
content = chain.invoke({"query": "你好，你是什么模型"})
print(content)


