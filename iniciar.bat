@echo off
echo ========================================
echo Starting Academic Harvester...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please follow the installation instructions in instrucoes.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if requirements are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Create data directories if they don't exist
if not exist "data\resultados" mkdir data\resultados

REM Start Streamlit
echo.
echo Academic Harvester is starting...
echo The application will open in your default browser.
echo To stop the application, press Ctrl+C in this window.
echo.
streamlit run app.py

REM Keep window open if error occurs
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)