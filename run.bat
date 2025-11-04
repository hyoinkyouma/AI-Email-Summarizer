@echo off
if not exist "env\Scripts\activate.bat" (
    echo Virtual environment not found. Please create it with: python -m venv venv
    pause
    exit /b
)
call env\Scripts\activate.bat
start "" python app.py
exit 0