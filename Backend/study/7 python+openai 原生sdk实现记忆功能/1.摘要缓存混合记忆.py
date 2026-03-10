
from typing import Any;

import dotenv;
from openai import OpenAI;

dotenv.load_dotenv();

# 1.max_tokens用于判断是否需要生成新的摘要
# 2.summary用于存储摘要的信息
# 3.chat_histories用于存储历史对话
# 4.get_num_tokens用于计算传入文本的token数
# 5.save_context用于存储新的交流对话
# 6.get_buffer_string用于将历史对话转换成字符串
# 7.load_memory_variables用于加载记忆变量信息
# 8.summary_text用于将旧的摘要和传入的对话生成新摘要

class ConversationSummaryBufferMemory:

    def __init__(self, summary: str = '', chat_histories: list = None, max_tokens: int = 300):
        self.summary = summary;
        self.chat_histories = [] if chat_histories is None else chat_histories;
        self.max_tokens = max_tokens;
        self.client = OpenAI(base_url='https://api.moonshot.cn/v1');

    @classmethod
    def get_num_tokens(cls, query: str) -> int:
        return len(query);

    def save_content(self, human_query:str, ai_content: str) -> None:
        self.chat_histories.append({
            'human': human_query,
            'ai': ai_content,
        });

        buffer_string = self.get_buffer_string();
        tokens = self.get_num_tokens(buffer_string);
        if tokens > self.max_tokens:
            first_chat = self.chat_histories[0];
            # 生成新的摘要
            print(f"生成新的摘要中");
            self.summary = self.summary_text(self.summary, f"human: {human_query}\nai: {first_chat.get('ai')}");
            print(f"新的摘要: {self.summary}");
            # 移除第一个对话
            del self.chat_histories[0];

    def get_buffer_string(self) -> str:
        buffer_string = '';
        for chat in self.chat_histories:
            buffer_string += f"human: {chat.get('human')}\nai: {chat.get('ai')}\n";
        print(f"buffer_string: {buffer_string}");
        return buffer_string.strip();

        # 加载记忆变量信息
    def load_memory_variables(self) -> dict[str, Any]:
        buffer_string = self.get_buffer_string();
        return {
            "chat_history": f"摘要: {self.summary}\n历史信息:{buffer_string}",
        }

    def summary_text(self, original_summary: str, new_chat: str) -> str:
        """用于将旧摘要和传入的新对话生成一个新摘要"""
        prompt = f"""你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结摘要，并将其添加到先前提供的摘要中，返回一个新的摘要，除了新摘要其他任何数据都不要生成，如果用户的对话信息里有一些关键的信息，比方说姓名、爱好、性别、重要事件等等，这些全部都要包括在生成的摘要中，摘要尽可能要还原用户的对话记录。

请不要将<example>标签里的数据当成实际的数据，这里的数据只是一个示例数据，告诉你该如何生成新摘要。

<example>
当前摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量。

新的对话：
Human：为什么你认为人工智能是一股向善的力量？
AI：因为人工智能会帮助人类充分发挥潜力。

新摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥潜力。
</example>

=====================以下的数据是实际需要处理的数据=====================

当前摘要：{origin_summary}

新的对话：
{new_line}

请帮用户将上面的信息生成新摘要。"""
        completion = self._client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content


client = OpenAI(base_url='https://api.moonshot.cn/v1');
memory = ConversationSummaryBufferMemory("", [], 300);

while True:
    human_query = input("请输入: ");
    if human_query == 'q':
        break;
   
    memory_variables = memory.load_memory_variables();

    answer_prompt = ( 
        "你是一个强大的聊天机器人，请根据对应的上下文和用户提问解决问题。\n\n"
        f"{memory_variables.get('chat_history')}\n\n"
        f"用户的提问是: {human_query}"
    )

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": answer_prompt}],
        stream=True
    )

    print("AI: ", end="");
    ai_content = "";

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        ai_content += content
        print(content, end="")
    print("\n")

    memory.save_content(human_query, ai_content);
