"""
先创建 FAISS 向量数据库
"""
import dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.baidu_qianfan_endpoint import QianfanEmbeddingsEndpoint
from langchain_core.documents import Document

dotenv.load_dotenv()

# 初始化嵌入模型 - 使用千帆
embedding = QianfanEmbeddingsEndpoint()

# 准备文档数据
documents = [
    Document(page_content="我养了一只猫，叫笨笨", metadata={"id": 1}),
    Document(page_content="我养了一只狗，叫旺财", metadata={"id": 2}),
    Document(page_content="我养了一只鸟，叫小飞", metadata={"id": 3}),
    Document(page_content="我喜欢吃苹果", metadata={"id": 4}),
    Document(page_content="我喜欢吃香蕉", metadata={"id": 5}),
]

# 创建 FAISS 向量数据库
db = FAISS.from_documents(documents, embedding)

# 保存到本地
db.save_local("./vector-store/")

print("向量数据库创建成功！已保存到 ./vector-store/")
