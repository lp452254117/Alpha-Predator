@echo off
call venv\Scripts\activate.bat
cmd /k uvicorn src.api.main:app --reload --port 8000
