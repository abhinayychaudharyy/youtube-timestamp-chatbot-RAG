import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schema import ChatWithTranscriptRequest
from app.services.youtube_service import YouTubeService
from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService
from app.utils.timestamp import seconds_to_time
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="YouTube RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    vector_service = VectorStoreService()
    rag_service = RAGService()
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    vector_service = None
    rag_service = None

vector_stores_cache = {}

@app.post("/chat")
def chat(data: ChatWithTranscriptRequest):
    global vector_service, rag_service
    if vector_service is None:
        vector_service = VectorStoreService()
    if rag_service is None:
        rag_service = RAGService()

    try:
        video_id = YouTubeService.extract_video_id(data.video_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    store = vector_stores_cache.get(video_id)

    if not store:
        logger.info(f"Cache miss for {video_id}. Building vector store from extension transcript...")
        try:
            if not data.transcript:
                raise ValueError("Transcript is empty.")

            docs = []
            current_text = ""
            current_start = None
            current_duration = 0.0

            for seg in data.transcript:
                if current_start is None:
                    current_start = seg.start
                current_text += seg.text + " "
                current_duration = seg.duration

                if len(current_text) >= 1000:
                    docs.append(Document(
                        page_content=current_text.strip(),
                        metadata={"start": current_start, "duration": current_duration}
                    ))
                    current_text = ""
                    current_start = None

            if current_text.strip():
                docs.append(Document(
                    page_content=current_text.strip(),
                    metadata={"start": current_start or 0.0, "duration": current_duration}
                ))

            if not docs:
                raise ValueError("Could not build any document chunks from transcript.")

            store = vector_service.create_store(docs)
            vector_stores_cache[video_id] = store
            logger.info(f"Cached vector store for {video_id}.")
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process transcript: {str(e)}")
    else:
        logger.info(f"Cache hit for {video_id}.")

    try:
        results = store.similarity_search(data.question, k=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    if not results:
        raise HTTPException(status_code=404, detail="No relevant information found in the transcript.")

    try:
        answer = rag_service.answer_question(data.question, results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    start_time = results[0].metadata.get("start", 0)
    return {
        "answer": answer,
        "timestamp": seconds_to_time(start_time),
        "youtube_link": f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}s"
    }