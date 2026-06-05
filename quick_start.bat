@echo off
echo ========================================================
echo Groww Genie - Quick Start Execution
echo ========================================================

echo.
echo [1/6] Checking for .env file...
if not exist ".env" (
    echo .env not found. Copying .env.example to .env...
    copy .env.example .env
    echo PLEASE EDIT .env AND ADD YOUR GROQ_API_KEY BEFORE CONTINUING!
    pause
) else (
    echo .env found.
)

echo.
echo [2/6] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/6] Building vector database from corpus...
python ingest.py

echo.
echo [4/6] Running automated compliance tests...
python verify_rag.py

echo.
echo [5/6] Launching backend API on port 8000...
start cmd /k "uvicorn api:app --port 8000"

echo.
echo [6/6] Launching Angular frontend...
cd frontend
start cmd /k "npm start"

echo.
echo All services launched!
echo Backend API running at http://localhost:8000
echo Angular UI will be available at http://localhost:4200
echo ========================================================
pause
