from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, ".")
loader = FileSystemBlobLoader(file_path, show_progress=True)


for blob in loader.yield_blobs():
    print(blob.as_string())
