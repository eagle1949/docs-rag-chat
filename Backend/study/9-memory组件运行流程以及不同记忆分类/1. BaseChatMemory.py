from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

# 新版方案1：使用 BaseChatMessageHistory（推荐）
chat_history: BaseChatMessageHistory = InMemoryChatMessageHistory()

# 添加消息
chat_history.add_user_message("你好")
chat_history.add_ai_message("你好！有什么可以帮助你的？")

# 获取历史消息
messages = chat_history.messages
print(messages)

