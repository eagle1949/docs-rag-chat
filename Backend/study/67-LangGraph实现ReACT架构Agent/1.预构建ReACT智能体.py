import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import dashscope
import requests
import os
from datetime import datetime
from dashscope import ImageSynthesis
# 设置通义万相API Key
dashscope.api_key = dotenv.get_key(dotenv.find_dotenv(), "DASHSCOPE_API_KEY")



dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


# 1.定义工具与工具列表
google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
class WanxiangArgsSchema(BaseModel):
    prompt: str = Field(description="输入应该是生成图像的文本提示(prompt)")


@tool
def generate_image(prompt: str) -> str:
    """
    当用户要求生成图片、绘制图像、创作视觉内容或需要将文字描述转换为图片时，使用此工具。
    该工具可以根据文本描述生成高质量的艺术图片。

    Args:
        prompt: 图片描述提示词，详细描述你想要生成的图片内容

    Returns:
        生成图片保存到当前目录
    """
    generate_image.args_schema = WanxiangArgsSchema
    try:
        # 调用通义万相API生成图片
        response = ImageSynthesis.call(
            model='wanx-v1',
            prompt=prompt,
            n=1,  # 生成图片数量
            size='1024*1024'  # 图片尺寸
        )

        if response.status_code == 200:
            # 获取图片URL - 直接访问response.output
            image_url = response.output.results[0].url

            # 下载图片并保存到当前目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"

            # 下载图片
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                # 保存到当前目录
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                return f"图片生成成功！已保存到: {os.path.abspath(filename)}"
            else:
                return f"图片生成成功，但下载失败: {image_url}"
        else:
            return f"图片生成失败: {response.message}"

    except Exception as e:
        return f"图片生成异常: {str(e)}"


tools = [google_serper, generate_image]

# 2.创建大语言模型
model = ChatOpenAI(model="moonshot-v1-8k", temperature=0)
# 3.使用预构建的函数创建ReACT智能体
agent = create_react_agent(model=model, tools=tools)

# 4.调用智能体并输出内容
print(agent.invoke({"messages": [("human", "请帮我绘制一幅鲨鱼在天上飞的图片")]}))
