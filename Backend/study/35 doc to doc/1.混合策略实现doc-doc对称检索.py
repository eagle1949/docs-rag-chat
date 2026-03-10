from typing import List

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

dotenv.load_dotenv()


class HyDERetriever(BaseRetriever):
    """HyDE混合策略检索器"""
    retriever: BaseRetriever
    llm: BaseLanguageModel

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """传递检索query实现HyDE混合策略检索"""
        # 1.构建生成假设性文档的prompt
        prompt = ChatPromptTemplate.from_template(
            "请用一段简洁的话（100字以内）来回答这个问题。\n"
            "问题: {question}\n"
            "回答: "
        )

        # 2.构建HyDE混合策略检索链
        chain = (
                {"question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
                | self.retriever
        )

        return chain.invoke(query)


# 1.构建向量数据库与检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
         cluster_url="r40kke3qtkmeqd518rdvw.c0.asia-southeast1.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("bVlLK3Y1OWhobTJud3k4bV9mZXk0bzErRTRMT2YvZlZRb2wrNGYwWGVGeDlsNjlpZW4xVEtLbnNSN3VvPV92MjAw"),
   ),
    index_name="DatasetDemo",
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
)
retriever = db.as_retriever(search_type="mmr")

# 2.创建HyDE检索器
hyde_retriever = HyDERetriever(
    retriever=retriever,
    llm=ChatOpenAI(model="moonshot-v1-8k", temperature=0),
)

# 3.检索文档
documents = hyde_retriever.invoke("关于LLMOps应用配置的文档有哪些？")
print(documents)
print(len(documents))
