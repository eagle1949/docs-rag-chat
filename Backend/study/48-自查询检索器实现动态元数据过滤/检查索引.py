"""
检查 Pinecone 索引状态
"""
import dotenv
from pinecone import Pinecone

dotenv.load_dotenv()

pc = Pinecone()

# 列出所有索引
indexes = pc.list_indexes()
print("当前所有索引：")
for idx in indexes:
    print(f"  - {idx.name}")

# 检查 llmops 索引详情
if "llmops" in [idx.name for idx in indexes]:
    index = pc.Index("llmops")
    stats = index.describe_index_stats()
    print(f"\nllmops 索引详情：")
    print(f"  维度: {stats.dimension}")
    print(f"  总向量数: {stats.total_vector_count}")
    print(f"  命名空间: {list(stats.namespaces.keys()) if stats.namespaces else '无'}")
else:
    print("\nllmops 索引不存在，需要创建")
