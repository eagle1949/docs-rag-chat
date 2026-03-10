import random

from langchain_core.runnables import RunnableLambda

def get_weather(location: str, unit:str, name: str) -> str:
    print('location', location);
    print('unit', unit);
    print('name', name);
    return f"{name}你好，查询到{location}的天气是{random.randint(24, 40)}度{unit}"

get_weather_runnable = RunnableLambda(get_weather).bind(unit="摄氏度", name="muxiaoke")

res = get_weather_runnable.invoke("广州")
print(res)