from typing import List
from unittest import loader

import jieba.analyse

from langchain_community.document_loaders import UnstructuredFileLoader, docugami
from langchain_text_splitters import TextSplitter

class CustomTextSplitter(TextSplitter):
    
    def __init__(self, separator: str = "\n\n", top_k: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.separator = separator
        self.top_k = top_k


    def split_text(self, text: str) -> List[str]:
        split_texts = text.split(self.separator)
        
        text_keywords = []

        for split_text in split_texts:
            keywords = jieba.analyse.extract_tags(split_text, topK=self.top_k)
            text_keywords.append(keywords)
        
        return [' '.join(keywords) for keywords in text_keywords]

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "./科幻短篇.txt")
loader = UnstructuredFileLoader(file_path)

text_splitter = CustomTextSplitter("\n\n", 10)

documents = loader.load()
chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    print(chunk.page_content)

