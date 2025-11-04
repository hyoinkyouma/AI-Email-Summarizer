import subprocess
import sys
import os
import threading
import time
import webbrowser
from pathlib import Path
import webview


def run_backend():
    sys.path.append(str(Path(__file__).parent))
    from backend.main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)

def run_frontend():
    frontend_path = Path(__file__).parent / "frontend" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit","run", str(frontend_path)], 
                  env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)})

def run_pywebview():
    window = webview.create_window("Email Summarizer", "http://localhost:8501", easy_drag=False)
    window.events.closed += lambda: os._exit(0)
    webview.start()
    window.set_title("Email Summarizer")
    
def main():
    print("Starting Email Summarizer...")
    
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    front_end_thread = threading.Thread(target=run_frontend, daemon=True)
    front_end_thread.start()

    run_pywebview()

if __name__ == "__main__":
    main()