import dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.baidu_qianfan_endpoint import QianfanEmbeddingsEndpoint

dotenv.load_dotenv()

embedding = QianfanEmbeddingsEndpoint()

db = FAISS.load_local("./vector-store/", embedding, allow_dangerous_deserialization=True)

print(db.similarity_search_with_score("我养了一只猫，叫笨笨"))
