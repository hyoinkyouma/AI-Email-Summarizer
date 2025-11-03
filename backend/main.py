from backend.gmail_client import fetch_unread_snippets
from backend.summarizer import summarize_email
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from bark import generate_audio, SAMPLE_RATE, preload_models
import torch
import numpy as np
import io
import soundfile as sf
from pydantic import BaseModel
import re

app = FastAPI()

preload_models()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class SynthesisRequest(BaseModel):
    text: str
    history_prompt: str | None = None

@app.get("/daily-digest")
def daily_digest():
    emails = fetch_unread_snippets(5)
    combined = "\n\n".join([f"From: {e['from']}\nSubject: {e['subject']}\n{e['snippet']}" for e in emails])
    summary = summarize_email(combined)
    return {"summary": summary, "emails": emails}

@app.post("/synthesize")
def synthesize_text(req: SynthesisRequest):
    text = req.text.strip()
    raw_parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = [s.strip() for s in raw_parts if s.strip()]
    print(sentences)
    audio_chunks = []
    if not sentences:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        with torch.cuda.amp.autocast(enabled=(DEVICE == "cuda")):
            for i, sentence in enumerate(sentences):
                audio_array = generate_audio(sentence, history_prompt=req.history_prompt or None)
                audio_chunks.append(audio_array)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    buf = io.BytesIO()
    audio_np = np.concatenate(audio_chunks)

    # Convert to float32 if needed
    if audio_np.dtype == np.float16:
        audio_np = audio_np.astype(np.float32)

    sf.write(buf, audio_np, SAMPLE_RATE, format="WAV")
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="audio/wav")