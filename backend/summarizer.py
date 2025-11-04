import subprocess

model = 'mistral-nemo'

def summarize_email(email_content):
    try:
        prompt = f"You are a virtual assistant, your job is to summarize my emails. Do not use bullet points:\n\n{email_content}\n\nSummary:"
        cmd = ["ollama", "run", model, prompt]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return res.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Summary generation timed out."
