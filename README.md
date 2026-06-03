# YouTube Timestamp Chatbot 🚀

An AI-powered Retrieval-Augmented Generation (RAG) application that allows users to chat with YouTube videos using natural language. The system extracts video transcripts, generates semantic embeddings, stores them in a FAISS vector database, and uses Groq's Qwen LLM to answer questions with precise video timestamps.

---

# 📌 Problem Statement

Long-form YouTube videos often contain valuable information, but finding a specific topic requires manually searching through hours of content.

This project solves that problem by enabling users to:

* Ask questions about a YouTube video.
* Receive context-aware answers.
* Get the exact timestamp where the topic is discussed.
* Jump directly to the relevant video section.

---

# 🏗️ System Architecture

```text
                        ┌──────────────────┐
                        │  YouTube Video   │
                        └─────────┬────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │ Transcript Extraction  │
                     │ YouTube Transcript API │
                     └─────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │  Document Creation      │
                    │ + Timestamp Metadata    │
                    └─────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ Text Chunking Pipeline  │
                    └─────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ HuggingFace Embeddings  │
                    │ all-MiniLM-L6-v2        │
                    └─────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │     FAISS Vector DB     │
                    └─────────┬───────────────┘
                              │
                User Question │
                              ▼
                    ┌─────────────────────────┐
                    │ Semantic Similarity     │
                    │ Retrieval               │
                    └─────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ Retrieved Context       │
                    └─────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ Groq Qwen LLM           │
                    │ RAG Answer Generation   │
                    └─────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ Answer + Timestamp      │
                    │ + YouTube Jump Link     │
                    └─────────────────────────┘
```

---

# ⚡ Core Features

* Natural language interaction with YouTube videos
* Retrieval-Augmented Generation (RAG)
* Semantic search using vector embeddings
* Timestamp-aware retrieval
* Direct YouTube timestamp links
* FastAPI backend
* FAISS vector database
* Groq-powered Qwen LLM integration
* Vector store caching for improved performance
* Modular service-based architecture

---

# 🧠 RAG Pipeline Explained

## 1. Transcript Extraction

The system extracts video transcripts using the YouTube Transcript API.

Example:

```json
[
  {
    "text": "Today we will discuss Retrieval Augmented Generation",
    "start": 120.5,
    "duration": 5.2
  }
]
```

Each transcript segment contains:

* Text
* Start Timestamp
* Duration

---

## 2. Document Creation

Transcript entries are converted into LangChain Documents.

Example:

```python
Document(
    page_content="Today we will discuss RAG",
    metadata={
        "start": 120.5,
        "duration": 5.2
    }
)
```

Metadata is preserved for timestamp retrieval.

---

## 3. Text Chunking

Large transcripts are split into manageable chunks.

Purpose:

* Improve retrieval quality
* Reduce embedding noise
* Maintain context boundaries

---

## 4. Embedding Generation

The system uses:

Model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Each chunk is converted into a 384-dimensional vector.

Example:

```text
"What is RAG?"
```

↓

```text
[0.42, -0.12, 0.89, ...]
```

These vectors capture semantic meaning.

---

## 5. Vector Storage

Embeddings are stored inside FAISS.

FAISS enables:

* Fast similarity search
* Efficient vector indexing
* Low-latency retrieval

---

## 6. Semantic Retrieval

When a user asks a question:

```text
What is Retrieval-Augmented Generation?
```

The question is embedded.

FAISS retrieves the most semantically relevant transcript chunks.

Example:

```text
Chunk 1
Chunk 2
Chunk 3
```

---

## 7. Context Injection

Retrieved chunks are combined into context.

Example:

```text
Context:
RAG combines retrieval systems with language models...

Question:
What is RAG?
```

---

## 8. Answer Generation

The context and question are sent to Groq's Qwen model.

The LLM generates an answer strictly based on retrieved transcript content.

This prevents hallucinations and improves factual accuracy.

---

## 9. Timestamp Retrieval

The retrieved chunk contains metadata.

Example:

```python
{
   "start": 755
}
```

The timestamp is converted to:

```text
00:12:35
```

and returned to the user.

---

## 10. YouTube Deep Link Generation

The system automatically creates a timestamp URL.

Example:

```text
https://www.youtube.com/watch?v=VIDEO_ID&t=755s
```

Clicking the link opens the video at the exact moment the topic is discussed.

---

# 🔥 Caching Strategy

To avoid reprocessing videos repeatedly:

```python
vector_stores_cache = {}
```

Workflow:

```text
First Request
    ↓
Transcript Extraction
    ↓
Embeddings
    ↓
FAISS Creation
    ↓
Cache Store

Second Request
    ↓
Reuse Existing FAISS Store
```

Benefits:

* Faster response times
* Reduced embedding computation
* Better scalability

---

# 📁 Project Structure

```text
youtube-ai-chatbot/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   └── schema.py
│   │
│   ├── services/
│   │   ├── youtube_service.py
│   │   ├── vector_store.py
│   │   └── rag_service.py
│   │
│   └── utils/
│       └── timestamp.py
│
├── requirements.txt
├── .env
├── run.py
└── README.md
```

---

# 🛠️ Tech Stack

## Backend

* Python
* FastAPI

## AI & RAG

* LangChain
* Groq
* Qwen LLM

## Embeddings

* Hugging Face Sentence Transformers
* all-MiniLM-L6-v2

## Vector Database

* FAISS

## Data Source

* YouTube Transcript API

---

# 📊 API Example

## Request

```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "question": "What is RAG?"
}
```

## Response

```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "timestamp": "00:12:35",
  "youtube_link": "https://www.youtube.com/watch?v=VIDEO_ID&t=755s"
}
```

---

# 🚀 Future Improvements

* Chrome Extension Integration
* Whisper-based fallback transcription
* Pinecone Vector Database
* Multi-video chat support
* Conversation memory
* YouTube playlist ingestion
* Agentic RAG workflow
* Hybrid search (Vector + Keyword)
* Streaming responses
* User authentication
* Cloud deployment

---

# 🎯 Key Concepts Demonstrated

* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Vector Embeddings
* FAISS Indexing
* Prompt Engineering
* Context Injection
* Metadata Retrieval
* FastAPI Development
* LLM Integration
* Groq Inference
* YouTube Data Processing

---

# 👨‍💻 Author

Abhinay Chaudhary

AI & Full Stack Developer | GenAI Enthusiast | Building AI-powered applications using RAG, LangChain, Vector Databases, and Large Language Models.
