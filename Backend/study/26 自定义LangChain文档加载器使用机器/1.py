from typing import Iterable, AsyncIterator

from langchain_core import document_loaders
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class CustomDocumentLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def lazy_load(self) -> Iterable[Document]:
        with open(self.file_path, "r", encoding="utf-8") as f:
             line_number = 0
             for line in f:
                 line_number += 1
                 yield Document(
                     page_content=line,
                     metadata={"score": self.file_path,"line_number": line_number}
                 )
                 line_number += 1
    
    async def alazy_load(self) -> AsyncIterator[Document]:
        import aiofiles
        async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
            line_number = 0
            async for line in f:
                line_number += 1
                yield Document(
                    page_content=line,
                    metadata={"score": self.file_path,"line_number": line_number}
                )
                line_number += 1

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./test.txt")
loader = CustomDocumentLoader(file_path)

documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
