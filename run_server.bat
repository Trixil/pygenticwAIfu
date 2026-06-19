@echo off
setlocal

if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install pillow numpy fastapi uvicorn pydantic python-dotenv openai python-multipart slugify

uvicorn app.app:agenticwAIfuApp --host 127.0.0.1 --port 9000 --reload