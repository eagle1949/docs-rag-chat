import dotenv

from langchain_community.chat_message_histories import FileChatMessageHistory

from openai import OpenAI

dotenv.load_dotenv()


client = OpenAI(base_url='https://api.moonshot.cn/v1')

chat_history = FileChatMessageHistory('./memory.txt')


while True:
    query = input("Human:")

    if query == "q":
        exit(0)

    print("AI", flush=True, end="")

    system_prompt = (
        "你是OpenAi开发的ChatGpt聊天机器人，可以根据相对应的上下文回复用户消息，上下文存放的是人类和你的对话信息列表"
        f"<context>{chat_history}</context>\n\n"
    )
    print(chat_history, 'chat_history')

    response = client.chat.completions.create(
        model='moonshot-v1-8k',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        stream=True,
    )

    ai_content = ""

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        ai_content += content
        print(content, flush=True, end="")

    chat_history.add_user_message(query)
    chat_history.add_ai_message(ai_content)
    print("")