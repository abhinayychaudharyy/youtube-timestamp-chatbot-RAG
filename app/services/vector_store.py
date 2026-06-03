from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.config import load_dotenv
import os

load_dotenv()


class VectorStoreService:

    def __init__(self):
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=os.getenv("HF_TOKEN")
        )

    def create_store(self, docs):
        return FAISS.from_documents(docs, self.embeddings)