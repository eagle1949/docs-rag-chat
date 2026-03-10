#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/10 17:30
@Author  : 
@File    : 1.RunnableParallel使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.编排prompt
joke_prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话，尽可能短一些")
poem_prompt = ChatPromptTemplate.from_template("请写一篇关于{subject}的诗，尽可能短一些")

# 2.创建大语言模型
llm = ChatOpenAI(model="moonshot-v1-8k")

# 3.创建输出解析器
parser = StrOutputParser()

# 4.编排链
joke_chain = joke_prompt | llm | parser
poem_chain = poem_prompt | llm | parser

# 5.并行链
map_chain = RunnableParallel(joke=joke_chain, poem=poem_chain)
# map_chain = RunnableParallel({
#     "joke": joke_chain,
#     "poem": poem_chain,
# })

res = map_chain.invoke({"subject": "程序员"})

print(res)

# 输出
# {'joke': '好的，这里有一个简短的程序员冷笑话：\n\n问：为什么程序员总是混淆圣诞节和万圣节？\n答：因为他们喜欢 Oct 31（十月三十一日）胜过 Dec 25（十二月二十五日）。', 'poem': '在数字世界里，代码编织梦，\n程序员，夜以继日，键盘敲击声。\n逻辑的海洋，算法的风，\n创造奇迹，于无形。\n\n代码如诗行，逻辑如旋律，\n在虚拟空间，构建真实界。\n他们是数字世界的建筑师，\n在0和1之间，寻找真理。\n\n程序员，梦想家，创造者，\n在代码的海洋，航行无垠。\n他们是现代的魔法师，\n在数字的宇宙，绘制星辰。'}