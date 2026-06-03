import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schema import ChatRequest
from app.services.youtube_service import YouTubeService
from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService
from app.utils.timestamp import seconds_to_time

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
def chat(data: ChatRequest):
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
        logger.info(f"Cache miss for video {video_id}. Ingesting transcript and creating vector store...")
        try:
            transcript = YouTubeService.get_transcript(data.video_url)
        except Exception as e:
            logger.error(f"Failed to retrieve transcript for video {video_id}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Could not retrieve transcript for the video. Please verify the URL and ensure transcripts/captions are enabled. Error: {str(e)}"
            )

        try:
            docs = YouTubeService.create_documents(transcript)
            if not docs:
                raise ValueError("Transcript is empty or has no content.")
            store = vector_service.create_store(docs)
            vector_stores_cache[video_id] = store
            logger.info(f"Successfully cached vector store for video {video_id}.")
        except Exception as e:
            logger.error(f"Failed to create vector store for video {video_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process transcript and create vector store: {str(e)}"
            )
    else:
        logger.info(f"Cache hit for video {video_id}. Reusing existing vector store.")

    try:
        results = store.similarity_search(data.question, k=10)
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    if not results:
        raise HTTPException(
            status_code=404, 
            detail="No relevant information found in the video transcript for your question."
        )
    try:
        answer = rag_service.answer_question(data.question, results)
    except Exception as e:
        logger.error(f"Failed to generate answer from Groq: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"LLM generation failed. Please verify your GROQ_API_KEY in the .env file. Error: {str(e)}"
        )
    start_time = results[0].metadata.get("start", 0)
    return {
        "answer": answer,
        "timestamp": seconds_to_time(start_time),
        "youtube_link": f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}s"
    }