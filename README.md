# Email Summarizer with Voice Synthesis

A modern email management tool that fetches your unread Gmail messages, provides AI-powered summaries, and can read them aloud using text-to-speech synthesis.

## Features

- Fetches unread emails from Gmail
- Creates concise summaries of your emails
- Provides a daily digest of your important messages
- Text-to-speech capability to listen to your email summaries
- Clean and intuitive Streamlit web interface
- FastAPI backend for efficient processing

## Project Structure

```
email-summarizer/
├── backend/
│   ├── credentials.json     # Google API credentials
│   ├── gmail_client.py     # Gmail API integration
│   ├── main.py            # FastAPI backend server
│   ├── summarizer.py      # Email summarization logic
│   └── token.pickle       # Gmail API token storage
└── frontend/
    └── app.py            # Streamlit web interface
```

## Prerequisites

- Python 3.11+
- Gmail API credentials
- CUDA-capable GPU (optional, for faster voice synthesis)
- Ollama

## Dependencies

Backend:

- fastapi
- uvicorn[standard]
- google-auth
- google-auth-oauthlib
- google-api-python-client
- python-dotenv
- bark (for voice synthesis)
- torch
- soundfile
- numpy
- ollama

Frontend:

- streamlit
- requests

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd email-summarizer
```

2. Create and activate a virtual environment:

```bash
python -m venv env
# On Windows
.\env\Scripts\activate
# On Unix or MacOS
source env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up Google API credentials:
   - Place your `credentials.json` file in the `backend` directory
   - Run the application once to authenticate with Gmail

## Running the Application

1. Make sure Ollama is running in the background

2. Start the backend server:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8009
```

3. Start the frontend application:

```bash
cd frontend
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## Usage

1. Click the "Fetch Digest" button to get your latest unread emails
2. Review the AI-generated summary of your emails
3. Click "Speak Summary" to hear the summary read aloud
4. View individual email details below the summary

## Note

Make sure to keep your `credentials.json` and `token.pickle` files secure and never commit them to version control.

## License

[Add your license information here]
