from backend.gmail_client import fetch_unread_snippets
from backend.summarizer import summarize_email
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io
import soundfile as sf
from pydantic import BaseModel
import edge_tts

app = FastAPI()

class SynthesisRequest(BaseModel):
    text: str
    history_prompt: str | None = None

@app.get("/daily-digest")
def daily_digest():
    emails = fetch_unread_snippets(5)
    combined = "\n\n".join([f"From: {e['from']}\nSubject: {e['subject']}\n{e['snippet']}" for e in emails])
    summary = summarize_email(combined)
    return {"summary": summary, "emails": emails}

@app.get("/heart-beat")
def heart_beat():
    return {"status":"ok"}

@app.post("/synthesize")
def synthesize_text(req: SynthesisRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    text = req.text.strip()
    voice = req.history_prompt if req.history_prompt else "en-PH-RosaNeural"
    communicate = edge_tts.Communicate(text, voice)
    OUTPUT_FILE = "output.wav"
    with open(OUTPUT_FILE, "wb") as file:
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
    data, samplerate = sf.read(OUTPUT_FILE)
    buf = io.BytesIO()
    sf.write(buf, data, samplerate, format="WAV")
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/wav")