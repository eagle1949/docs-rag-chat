from langchain_community.document_loaders.generic import GenericLoader

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, ".")
loader = GenericLoader.from_filesystem(
    file_path,
    glob="*.txt", show_progress=True
)

for idx, doc in enumerate(loader.lazy_load()):
    print(f"当前正在加载第{idx}个文件,文件名:{doc.metadata['source']}")
