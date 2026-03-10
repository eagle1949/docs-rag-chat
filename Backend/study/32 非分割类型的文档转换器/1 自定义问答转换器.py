"""
自定义问答转换器 - 使用 LangChain 原生功能替代 doctran
从文档中提取问答对，生成相关问题以增强检索效果

环境配置说明：
- 如果使用 SiliconFlow API: 模型名称应该是 "Qwen/Qwen2.5-7B-Instruct" 或其他 SiliconFlow 支持的模型
- 如果使用 Moonshot API: 模型名称应该是 "moonshot-v1-8k"
- 如果使用 OpenAI API: 模型名称应该是 "gpt-3.5-turbo" 或 "gpt-4"
"""
import os
import dotenv
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser

# 加载环境变量
dotenv.load_dotenv()

# 根据 API BASE 自动选择合适的模型
API_BASE = os.getenv("OPENAI_API_BASE", "")
if "siliconflow" in API_BASE.lower():
    DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"  # SiliconFlow 支持的模型
elif "moonshot" in API_BASE.lower():
    DEFAULT_MODEL = "moonshot-v1-8k"  # Moonshot 的模型
else:
    DEFAULT_MODEL = "gpt-3.5-turbo"  # 默认使用 OpenAI 模型

# 1. 构建文档列表
page_content = """机密文件 - 仅供内部使用
日期：2023年7月1日
主题：各种话题的更新和讨论
亲爱的团队，
希望这封邮件能找到你们一切安好。在这份文件中，我想向你们提供一些重要的更新，并讨论需要我们关注的各种话题。请将此处包含的信息视为高度机密。
安全和隐私措施
作为我们不断致力于确保客户数据安全和隐私的一部分，我们已在所有系统中实施了强有力的措施。我们要赞扬IT部门的John Doe（电子邮件：john.doe@example.com）在增强我们网络安全方面的勤奋工作。未来，我们提醒每个人严格遵守我们的数据保护政策和准则。此外，如果您发现任何潜在的安全风险或事件，请立即向我们专门的团队报告，联系邮箱为security@example.com。
人力资源更新和员工福利
最近，我们迎来了几位为各自部门做出重大贡献的新团队成员。我要表扬Jane Smith（社保号：049-45-5928）在客户服务方面的出色表现。Jane一直受到客户的积极反馈。此外，请记住我们的员工福利计划的开放报名期即将到来。如果您有任何问题或需要帮助，请联系我们的人力资源代表Michael Johnson（电话：418-492-3850，电子邮件：michael.johnson@example.com）。
营销倡议和活动
我们的营销团队一直在积极制定新策略，以提高品牌知名度并推动客户参与。我们要感谢Sarah Thompson（电话：415-555-1234）在管理我们的社交媒体平台方面的杰出努力。Sarah在过去一个月内成功将我们的关注者基数增加了20%。此外，请记住7月15日即将举行的产品发布活动。我们鼓励所有团队成员参加并支持我们公司的这一重要里程碑。
研发项目
在追求创新的过程中，我们的研发部门一直在为各种项目不懈努力。我要赞扬David Rodriguez（电子邮件：david.rodriguez@example.com）在项目负责人角色中的杰出工作。David对我们尖端技术的发展做出了重要贡献。此外，我们希望每个人在7月10日定期举行的研发头脑风暴会议上分享他们的想法和建议，以开展潜在的新项目。
请将此文档中的信息视为最机密，并确保不与未经授权的人员分享。如果您对讨论的话题有任何疑问或顾虑，请随时直接联系我。
感谢您的关注，让我们继续共同努力实现我们的目标。
此致，
Jason Fan
联合创始人兼首席执行官
Psychic
jason@psychic.dev"""

documents = [Document(page_content=page_content)]

# 2. 定义问答提取的提示模板
qa_extraction_prompt = ChatPromptTemplate.from_template("""
你是一个专业的文档分析师。请从以下文档中提取3-5个最重要的问答对。

要求：
1. 的问题应该基于文档内容，能够帮助读者理解文档的核心信息
2. 答案应该简洁明了，直接来自文档内容
3. 问答对应该涵盖文档的主要话题

文档内容：
{document}

请以JSON格式返回，格式如下：
{{
    "questions_and_answers": [
        {{"question": "问题1", "answer": "答案1"}},
        {{"question": "问题2", "answer": "答案2"}},
        {{"question": "问题3", "answer": "答案3"}}
    ]
}}

只返回JSON，不要包含其他内容：
""")

# 3. 构建问答转换器
class CustomQATransformer:
    """自定义问答转换器，使用LLM从文档中提取问答对"""

    def __init__(self, openai_api_model: str = "gpt-3.5-turbo", temperature: float = 0):
        """
        初始化问答转换器

        Args:
            openai_api_model: 使用的模型名称
            temperature: 温度参数，控制随机性
        """
        self.llm = ChatOpenAI(model=openai_api_model, temperature=temperature)
        self.chain = qa_extraction_prompt | self.llm

    def transform_documents(self, documents: list[Document]) -> list[Document]:
        """
        转换文档列表，为每个文档提取问答对

        Args:
            documents: 文档列表

        Returns:
            包含问答对的文档列表（问答对存储在metadata中）
        """
        transformed_docs = []

        for doc in documents:
            # 调用LLM提取问答对
            result = self.chain.invoke({"document": doc.page_content})

            # 解析JSON结果
            try:
                # 尝试从返回内容中提取JSON
                content = result.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                qa_data = json.loads(content)

                # 将问答对添加到文档的metadata中
                new_doc = Document(
                    page_content=doc.page_content,
                    metadata={
                        **doc.metadata,
                        "questions_and_answers": qa_data.get("questions_and_answers", [])
                    }
                )
                transformed_docs.append(new_doc)

            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始内容: {result.content}")
                # 如果解析失败，返回原始文档
                transformed_docs.append(doc)
            except Exception as e:
                print(f"处理文档时出错: {e}")
                transformed_docs.append(doc)

        return transformed_docs


# 4. 使用自定义问答转换器并转换
print("=" * 60)
print("自定义问答转换器示例")
print("=" * 60)
print(f"当前 API Base: {API_BASE}")
print(f"使用模型: {DEFAULT_MODEL}")
print()

# 创建转换器实例
qa_transformer = CustomQATransformer(openai_api_model=DEFAULT_MODEL)

# 执行转换
print("正在从文档中提取问答对...\n")
transformer_documents = qa_transformer.transform_documents(documents)

# 5. 输出内容
print("提取的问答对：")
print("-" * 60)
for idx, qa in enumerate(transformer_documents[0].metadata.get("questions_and_answers", []), 1):
    print(f"\n问答对 {idx}:")
    print(f"问题: {qa.get('question', 'N/A')}")
    print(f"答案: {qa.get('answer', 'N/A')}")

print("\n" + "=" * 60)
print("转换完成！")
print("=" * 60)

# 额外示例：展示如何批量处理多个文档
print("\n\n" + "=" * 60)
print("批量处理示例")
print("=" * 60)

# 创建多个测试文档
test_documents = [
    Document(page_content="Python是一种高级编程语言，由Guido van Rossum于1991年创建。它以简洁易读的语法而闻名，广泛应用于Web开发、数据科学、人工智能等领域。"),
    Document(page_content="LangChain是一个用于开发由语言模型驱动的应用程序的框架。它提供了丰富的工具和集成，帮助开发者构建复杂的AI应用。")
]

print(f"\n待处理文档数量: {len(test_documents)}")
transformed_docs = qa_transformer.transform_documents(test_documents)

for idx, doc in enumerate(transformed_docs, 1):
    print(f"\n文档 {idx}:")
    print(f"原文内容: {doc.page_content[:50]}...")
    print(f"提取的问答对数量: {len(doc.metadata.get('questions_and_answers', []))}")
    for qa in doc.metadata.get("questions_and_answers", []):
        print(f"  - {qa.get('question', 'N/A')}")
