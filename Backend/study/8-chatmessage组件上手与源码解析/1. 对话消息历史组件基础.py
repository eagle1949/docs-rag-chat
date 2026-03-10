from langchain_core.chat_history import InMemoryChatMessageHistory

chat_history = InMemoryChatMessageHistory()

chat_history.add_user_message("你好，我是cjw，你是谁")
chat_history.add_ai_message("你好，我是chatgpt，有什么可以帮到你？")

print(chat_history.messages)
# [HumanMessage(content='你好，我是cjw，你是谁', additional_kwargs={}, response_metadata={}), AIMessage(content='你好，我是chatgpt，有什么可以帮到你？', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[])]

