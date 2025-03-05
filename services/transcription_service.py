# app/services/transcription_service.py
import io
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio_file(file_obj: io.BytesIO, filename: str, content_type: str) -> str:
    """Uses OpenAI's Whisper model to transcribe an audio file."""
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, file_obj, content_type)
    )
    if not transcript.text:
        raise Exception("Transcription returned empty text.")
    return transcript.text

def summarize_transcript(transcript_text: str) -> str:
    """Uses OpenAI's GPT model to summarize a transcript into bullet points."""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Summarize this transcript into bullet points."},
            {"role": "user", "content": transcript_text}
        ]
    )
    summary = response.choices[0].message.content
    return summary
