from langchain_community.document_loaders import TextLoader, docugami
import os

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "document.txt")

loader = TextLoader(file_path, encoding="utf-8")

documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
