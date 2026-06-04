from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    video_url: str
    question: str


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float


class ChatWithTranscriptRequest(BaseModel):
    video_url: str
    question: str
    transcript: Optional[List[TranscriptSegment]] = None