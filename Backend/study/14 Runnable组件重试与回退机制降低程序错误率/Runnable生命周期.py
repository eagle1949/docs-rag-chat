from typing import Any


import time
from langchain_core import runnables
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableConfig

from langchain_core.tracers.schemas import Run



def on_start(run_obj: Run, config: RunnableConfig):
    print("start")
    print(run_obj)
    print(config)
    print("-----------")



def on_end(run_obj: Run, config: RunnableConfig):
    print("end")
    print(run_obj)
    print(config)
    print("-----------")



def on_error(run_obj: Run, config: RunnableConfig, error: Exception):
    print("error")
    print(run_obj)
    print(config)
    print(error)
    print("-----------")


runnables = RunnableLambda[Any, Any](lambda x: time.sleep(x)).with_listeners(
    on_start=on_start,
    on_end=on_end,
    on_error=on_error,
)

chain = runnables

chain.invoke(2, config={"configurable": {"name": "123"}})
