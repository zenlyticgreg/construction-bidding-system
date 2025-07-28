@echo off
REM PACE - Project Analysis & Construction Estimating - Run Script for Windows

echo 📊  Starting PACE - Project Analysis & Construction Estimating...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data\uploads" mkdir data\uploads
if not exist "data\temp" mkdir data\temp
if not exist "data\backups" mkdir data\backups
if not exist "data\cache" mkdir data\cache
if not exist "logs" mkdir logs
if not exist "output\catalogs" mkdir output\catalogs
if not exist "output\bids" mkdir output\bids
if not exist "output\reports" mkdir output\reports
if not exist "output\analyses" mkdir output\analyses

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found
    pause
    exit /b 1
)

REM Start the application
echo 🚀 Starting PACE application...
echo 📊 Application will be available at: http://localhost:8501
echo 🔄 Press Ctrl+C to stop the application
echo.

streamlit run main.py --server.port 8501 --server.address 0.0.0.0 