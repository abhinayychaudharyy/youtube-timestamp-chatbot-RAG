import json
from app.services.youtube_service import YouTubeService
from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService

url = "https://www.youtube.com/watch?v=lpVkxuVmaLk"
question = "what is the video about"

print("Fetching transcript...")
transcript = YouTubeService.get_transcript(url)

print("Chunking...")
docs = YouTubeService.create_documents(transcript)

print("Embedding...")
vector_service = VectorStoreService()
store = vector_service.create_store(docs)

print("Searching...")
results = store.similarity_search(question, k=10)

print("Generating Answer...")
rag = RAGService()
answer = rag.answer_question(question, results)

print("\n--- ANSWER ---")
print(answer)
