import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, prompt
from langchain_openai import ChatOpenAI


dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}")
])

llm = ChatOpenAI(model="moonshot-v1-8k")

chain = prompt | llm.bind(model="moonshot-v1-32k") | StrOutputParser()

content = chain.invoke({"query": "你好，你是什么模型,版本号是多少"})
print(content)
