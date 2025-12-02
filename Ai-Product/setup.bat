@echo off
echo ========================================
echo Universal AI Workspace - Quick Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo [1/6] Setting up backend...
echo.

REM Create backend virtual environment
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Setup environment file
if not exist .env (
    echo Creating backend .env file...
    copy .env.example .env
    echo.
    echo ==========================================
    echo IMPORTANT: Please edit backend\.env file
    echo and add your OpenAI API key and other settings
    echo ==========================================
    echo.
    pause
)

cd ..

echo.
echo [2/6] Setting up frontend...
echo.

cd frontend

REM Install Node.js dependencies
if not exist node_modules (
    echo Installing Node.js dependencies...
    call npm install
)

REM Setup environment file
if not exist .env.local (
    echo Creating frontend .env.local file...
    copy .env.example .env.local
)

cd ..

echo.
echo [3/6] Checking Docker...
echo.

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker is not installed or not running.
    echo You can either:
    echo   1. Install Docker Desktop and run: docker-compose up -d
    echo   2. Install PostgreSQL, Redis, and ChromaDB manually
    echo.
) else (
    echo Docker found! You can start services with: docker-compose up -d
)

echo.
echo [4/6] Setup Summary
echo.
echo ========================================
echo Backend Setup:       COMPLETE
echo Frontend Setup:      COMPLETE
echo Docker Check:        %errorlevel%
echo ========================================
echo.

echo [5/6] Next Steps
echo.
echo 1. Make sure to edit backend\.env with your API keys
echo.
echo 2. Start the database services:
echo    Option A (Docker): docker-compose up -d
echo    Option B (Manual): Start PostgreSQL, Redis, ChromaDB manually
echo.
echo 3. Start the backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload --port 8001
echo.
echo 4. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 5. Open http://localhost:3000 in your browser
echo.

echo [6/6] Creating quick-start scripts...
echo.

REM Create backend start script
echo @echo off > start-backend.bat
echo cd backend >> start-backend.bat
echo call venv\Scripts\activate >> start-backend.bat
echo uvicorn app.main:app --reload --port 8001 >> start-backend.bat

REM Create frontend start script
echo @echo off > start-frontend.bat
echo cd frontend >> start-frontend.bat
echo npm run dev >> start-frontend.bat

echo Created start-backend.bat and start-frontend.bat
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Quick Start Commands:
echo   start-backend.bat   - Start the backend API
echo   start-frontend.bat  - Start the frontend UI
echo.
pause
