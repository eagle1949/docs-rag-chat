from typing import List

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from weaviate.auth import AuthApiKey
from langchain_classic.retrievers import MultiQueryRetriever
from langchain_core.load import dumps, loads

dotenv.load_dotenv()

class RAGFusionRetriever(MultiQueryRetriever):
    """RAG多查询结果融合策略检索器"""
    k: int = 4

    def retrieve_documents(
            self, queries: List[str], run_manager: CallbackManagerForRetrieverRun
    ) -> List[List]:
        """重写检索文档函数，返回值变成一个嵌套的列表"""
        documents = []
        for query in queries:
            docs = self.retriever.invoke(
                query, config={"callbacks": run_manager.get_child()}
            )
            documents.append(docs)
        return documents

    def unique_union(self, documents: List[List]) -> List[Document]:
        """使用RRF算法来去重合并对应的文档，参数为嵌套列表，返回值为文档列表"""
        # 1.定义一个变量存储每个文档的得分信息
        fused_result = {}

        # 2.循环两层获取每一个文档信息
        for docs in documents:
            for rank, doc in enumerate(docs):
                # 3.使用dumps函数将类示例转换成字符串
                doc_str = dumps(doc)
                # 4.判断下该文档的字符串是否已经计算过得分
                if doc_str not in fused_result:
                    fused_result[doc_str] = 0
                # 5.计算新的分
                fused_result[doc_str] += 1 / (rank + 60)

        # 6.执行排序操作，获取相应的数据，使用的是降序
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_result.items(), key=lambda x: x[1], reverse=True)
        ]

        return [item[0] for item in reranked_results[:self.k]]

# 1.构建向量数据库与检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="xsfb2okarbetu3miqefl7a.c0.asia-southeast1.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("NzRCREhtODhrZk9SeFZReF9PY2tya1Vpd2dDQ3hYc3ZxNW9tM09WN2VFMk9FREw4WHdwR1NGVmVka3FFPV92MjAw"),
    ),
    index_name="DatasetDemo",
    text_key="text",
    embedding= QianfanEmbeddingsEndpoint(model="embedding-v1"),
)
retriever = db.as_retriever(search_type="mmr")

rag_fusion_retriever = RAGFusionRetriever.from_llm(
    retriever=retriever,
    llm=ChatOpenAI(model="moonshot-v1-8k", temperature=0),
)

# 3.执行检索
docs = rag_fusion_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(docs)
print(len(docs))