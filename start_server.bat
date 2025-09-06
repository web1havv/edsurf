@echo off
echo 🚀 Starting Info Reeler Server...
echo ==================================

cd /d "%~dp0backend"

if not exist "main.py" (
    echo ❌ main.py not found in backend directory
    pause
    exit /b 1
)

echo ✅ Found main.py in backend directory
echo 🌐 Starting server on http://localhost:8000
echo 📱 Open your browser and go to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ==================================

python main.py
pause
