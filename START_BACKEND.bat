@echo off
echo ========================================
echo  Smart City AI Assistant - Backend
echo ========================================
echo.
echo Starting Python backend on port 8000...
echo API Documentation will be at: http://localhost:8000/docs
echo.

cd /d "%~dp0python-agent"
uvicorn app:app --host 0.0.0.0 --port 8000

pause
