import subprocess

model = 'mistral-nemo'

def summarize_email(email_content):
    try:
        prompt = f"Your response will be fed into a tts model. Summarize the following email content in a conversational and concise manner as if you're dictating it, do not use bullet points:\n\n{email_content}\n\nSummary:"
        cmd = ["ollama", "run", model, prompt]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return res.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Summary generation timed out."
