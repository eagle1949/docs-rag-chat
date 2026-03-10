from pydantic import BaseModel, Field
from langchain_core.tools import tool


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


@tool("multiply_tool", return_direct=True, args_schema=MultiplyInput)
def multiply(a: int, b: int) -> int:
    """将传递的两个数字相乘"""
    return a * b


# 打印下该工具的相关信息
print("名称: ", multiply.name)
print("描述: ", multiply.description)
print("参数: ", multiply.args)
print("直接返回: ", multiply.return_direct)

# 调用工具
print(multiply.invoke({"a": 2, "b": 8}))


# 名称:  multiply_tool
# 描述:  将传递的两个数字相乘
# 参数:  {'a': {'description': '第一个数字', 'title': 'A', 'type': 'integer'}, 'b': {'description': '第二个数字', 'title': 'B', 'type': 'integer'}}
# 直接返回:  True
# 16