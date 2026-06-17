@echo off
cd /d "%~dp0"

echo Starting backend...
start "RAG Backend" cmd /c "python main.py"

echo Starting frontend...
cd frontend
start "RAG Frontend" cmd /c "npm run dev"

echo.
echo Both servers started. Close the windows to stop.
pause
