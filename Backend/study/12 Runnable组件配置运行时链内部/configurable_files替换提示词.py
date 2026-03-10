
from langchain_core.prompts import PromptTemplate, prompt
from langchain_core.runnables import ConfigurableField


prompt = PromptTemplate.from_template("请写一篇关于{subject}主题的冷笑话").configurable_fields(
    template=ConfigurableField(id="prompt_template")
)

content = prompt.invoke({"subject": "程序员"},
    config={"configurable": {"prompt_template": "请写一篇关于{subject}主题的藏头诗"}}
)

print(content)