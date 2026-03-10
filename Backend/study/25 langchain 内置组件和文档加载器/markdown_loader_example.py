from langchain_community.document_loaders import UnstructuredMarkdownLoader
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./项目API资料.md")


loader = UnstructuredMarkdownLoader(file_path)

documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
