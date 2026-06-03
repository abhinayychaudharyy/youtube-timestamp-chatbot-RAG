from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreService:

    def __init__(self):

        self.embeddings = (
            HuggingFaceEmbeddings(
                model_name=
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        )

    def create_store(self, docs):

        store = FAISS.from_documents(
            docs,
            self.embeddings
        )

        return store