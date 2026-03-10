import dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 使用 ChatPromptTemplate.from_messages 创建消息提示模板
prompt = PromptTemplate.from_template("请生成一个小于{x}的随机整数,直接给我数字即可")

# 使用 configurable_fields 方法配置可运行字段
llm = ChatOpenAI(model="moonshot-v1-8k").configurable_fields(
    temperature=ConfigurableField(id="llm_temperature", name="大语言模型的温度", description="温度越低，大语言模型生成的内容越确定，温度越高，生成内容越随机")
)

chain = prompt | llm | StrOutputParser()

# 示例：调用链并传入配置
# content = chain.invoke({"x": 1000}, config={"configurable": {"llm_temperature": 0.9}})

with_config_chain = chain.with_config(configurable={"llm_temperature": 0.9})
content = with_config_chain.invoke({"x": 1000})

print(content)


