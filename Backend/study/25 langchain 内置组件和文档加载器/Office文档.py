from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./章节介绍.pptx")


# excel_loader = UnstructuredExcelLoader(file_path, mode="elements")
# excel_document = excel_loader.load()

# word_loader = UnstructuredWordDocumentLoader(file_path, mode="elements")
# word_document = word_loader.load()

ppt_loader = UnstructuredPowerPointLoader(file_path, mode="elements")
ppt_document = ppt_loader.load()


print(ppt_document)
print(len(ppt_document))
print(ppt_document[0].metadata)
