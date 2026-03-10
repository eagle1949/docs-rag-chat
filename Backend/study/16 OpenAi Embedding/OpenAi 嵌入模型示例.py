import dotenv

import numpy as np

from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from numpy import dot
from numpy.linalg import norm

dotenv.load_dotenv()

# 计算两个向量的余弦相似度
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    # 计算向量长度
    norm_vec1 = norm(vec1)
    norm_vec2 = norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)


# 创建文本嵌入模型
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings = QianfanEmbeddingsEndpoint(model="Embedding-V1")

query_vector = embeddings.embed_query("你好,我是一名学生")

print(query_vector)
print(len(query_vector))

documents_vectors = embeddings.embed_documents([
    "你好,我是一名学生",
    "你好,我是一名老师",
    "你好,我是一名学生",
])

print(documents_vectors)
print(len(documents_vectors))

# 计算查询向量与每个文档向量的相似度
print("向量1和向量2的相似度:", cosine_similarity(documents_vectors[0], documents_vectors[1]))
print("向量1和向量3的相似度:", cosine_similarity(documents_vectors[0], documents_vectors[2]))
