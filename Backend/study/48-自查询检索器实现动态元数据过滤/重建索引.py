"""
重建 Pinecone 索引脚本
将索引维度从 512 改为 384（匹配千帆 embedding-v1）
"""
import dotenv
from pinecone import Pinecone

dotenv.load_dotenv()

pc = Pinecone()

# 1. 删除旧索引
print("正在删除旧索引...")
pc.delete_index("llmops")
print("旧索引已删除")

# 2. 创建新索引（384维）
print("正在创建新索引（384维）...")
pc.create_index(
    name="llmops",
    dimension=384,  # 千帆 embedding-v1 是 384 维
    metric="cosine",
    spec=pc.ServerlessSpec(
        cloud="aws",
        region="us-east-1"  # 根据你的区域修改
    )
)
print("新索引创建成功！")

# 3. 等待索引就绪
import time
time.sleep(5)
print("索引已就绪，可以使用了")
