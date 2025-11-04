import subprocess
import sys
import os
import threading
import time
import webbrowser
import signal
import ctypes
import psutil
from pathlib import Path
import webview
from backend.main import app
import uvicorn
import socket

def kill_process(pid):
    if sys.platform == 'win32':
        try:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        except:
            pass
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass

PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400
SYNCHRONIZE = 0x00100000

def force_kill_win32(pid):
    if sys.platform != 'win32':
        return
        
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    handle = kernel32.OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION | SYNCHRONIZE,
                                False, pid)
    if handle:
        try:
            kernel32.TerminateProcess(handle, 1)
        finally:
            kernel32.CloseHandle(handle)

def get_base_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        return Path(__file__).parent

def run_backend():
    base_path = get_base_path()
    if base_path not in sys.path:
        sys.path.append(str(base_path))

    uvicorn.run(app, host="0.0.0.0", port=8009)

def find_streamlit_processes():
    streamlit_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'streamlit' in cmdline:
                    streamlit_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return streamlit_processes

def kill_streamlit():
    """Kill any running Streamlit processes"""
    if sys.platform == 'win32':
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'streamlit.exe'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        except:
            pass

def get_local_network_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80)) 
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

def run_frontend():
    local_ip = get_local_network_ip()
    base_path = get_base_path()
    
    os.environ.update({
        "STREAMLIT_SERVER_ADDRESS": local_ip,
        "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
        "STREAMLIT_SERVER_HEADLESS": "true",
        "STREAMLIT_SERVER_RUN_ON_SAVE": "false",
        "STREAMLIT_BROWSER_SERVER_ADDRESS": local_ip,
        "STREAMLIT_SERVER_ENABLE_CORS": "false",
        "STREAMLIT_BROWSER_ENABLE_CAMERA": "false",
        "STREAMLIT_BROWSER_FILE_WATCHER_TYPE": "none",
        "STREAMLIT_SERVER_PORT": "8501",
        "STREAMLIT_BROWSER_SERVER_PORT": "8501",
        "STREAMLIT_SERVER_FILE_WATCHER_TYPE": "none",
        "STREAMLIT_BROWSER_SHOW_ERROR_DETAILS": "false",
        "STREAMLIT_RUNNER_COMMAND": str(sys.executable)
    })
    frontend_path = base_path / "frontend" / "app.py"
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(frontend_path), 
         "--server.headless", "true",
         "--server.address", local_ip,
         "--server.enableCORS", "false",
         "--browser.serverAddress", local_ip,
         "--browser.gatherUsageStats", "false",
         "--server.enableXsrfProtection", "false",
         "--server.enableWebsocketCompression", "false"],
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0,
        shell=False
    )
    return process

def run_pywebview():
    time.sleep(3)
    if sys.platform == 'win32':
        webview.WEBVIEW_GUI = 'cef'
    window = webview.create_window(
        "Email Summarizer",
        f"http://{get_local_network_ip()}:8501",
        easy_drag=False,
        frameless=False,
        minimized=False,
        confirm_close=False
    )
    webview.start(debug=False)
    return window

def kill_streamlit_processes():
    try:
        streamlit_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'streamlit' in cmdline:
                        streamlit_processes.append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        for pid in streamlit_processes:
            try:
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            except:
                pass
    except:
        pass

def main():
    print("Starting Email Summarizer...")
    
    kill_streamlit()
    kill_streamlit_processes()
    
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    frontend_process = None
    try:
        frontend_process = run_frontend()
    except Exception as e:
        print(f"Error starting frontend: {e}")
        os._exit(1)

    try:
        window = run_pywebview()
    except Exception as e:
        print(f"Error starting pywebview: {e}")
        os._exit(1)
    
    def on_closing():
        try:
            if frontend_process and frontend_process.pid:
                kill_process(frontend_process.pid)
                force_kill_win32(frontend_process.pid)
            
            kill_streamlit()
            kill_streamlit_processes()
            
        except Exception as e:
            print(f"Error while terminating processes: {e}")
        finally:
            os._exit(0)

    window.events.closing += on_closing

if __name__ == "__main__":
    main()