from typing import Iterator

from langchain_core.document_loaders import Blob
from langchain_core.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document

class CustomParser(BaseBlobParser):
    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        line_number = 0
        with blob.as_bytes_io() as f:
           for line in f:     
                yield Document(
                    page_content=line,
                    metadata={"score": blob.source,"line_number": line_number}
                )
                line_number += 1

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./test.txt")
blob = Blob.from_path(file_path)
parser = CustomParser()

documents = list(parser.lazy_parse(blob))

print(documents)
print(len(documents))
print(documents[0].metadata)
