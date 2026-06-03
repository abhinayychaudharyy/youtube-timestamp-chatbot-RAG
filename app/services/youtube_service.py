import re

from youtube_transcript_api import (
    YouTubeTranscriptApi
)

from langchain_core.documents import (
    Document
)


class YouTubeService:

    @staticmethod
    def extract_video_id(url):

        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"

        match = re.search(pattern, url)

        if not match:
            raise ValueError(
                "Invalid YouTube URL"
            )

        return match.group(1)

    @staticmethod
    def get_transcript(video_url):

        video_id = (
            YouTubeService
            .extract_video_id(video_url)
        )

        transcript = (
            YouTubeTranscriptApi()
            .fetch(video_id)
        )

        return transcript

    @staticmethod
    def create_documents(transcript, chunk_size=1000):

        docs = []
        current_text = ""
        current_start = None

        for item in transcript:
            if current_start is None:
                current_start = item.start

            current_text += item.text + " "

            if len(current_text) >= chunk_size:
                docs.append(
                    Document(
                        page_content=current_text.strip(),
                        metadata={
                            "start": current_start,
                            "duration": item.duration
                        }
                    )
                )
                current_text = ""
                current_start = None

        if current_text.strip():
            docs.append(
                Document(
                    page_content=current_text.strip(),
                    metadata={
                        "start": current_start if current_start is not None else 0.0,
                        "duration": 0.0
                    }
                )
            )

        return docs