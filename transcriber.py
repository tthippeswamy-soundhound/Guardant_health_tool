import os
from openai import OpenAI


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file using OpenAI Whisper API."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )

    return response
