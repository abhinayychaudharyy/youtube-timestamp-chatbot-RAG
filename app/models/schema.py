from pydantic import BaseModel


class ChatRequest(BaseModel):

    video_url: str

    question: str