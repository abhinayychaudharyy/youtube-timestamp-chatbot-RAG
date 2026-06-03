from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY


class RAGService:

    def __init__(self):

        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,

            model_name="llama-3.3-70b-versatile"
        )

    def answer_question(
        self,
        question,
        retrieved_docs
    ):

        context = "\n".join(
            [
                doc.page_content
                for doc
                in retrieved_docs
            ]
        )

        prompt = f"""
        You are an expert AI assistant tasked with answering questions about a YouTube video.
        Use the following retrieved transcript excerpts as your primary source of truth, but synthesize this with your own expansive knowledge to provide a highly detailed, insightful, and comprehensive answer.

        Context from video:
        {context}

        User's Question:
        {question}

        Please provide a deep, well-structured, and comprehensive response.
        """

        response = self.llm.invoke(
            prompt
        )

        return response.content