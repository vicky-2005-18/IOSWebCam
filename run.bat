@echo off
echo ======================================================================
echo  WebCam Bridge - Starting...
echo ======================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Run: python -m venv venv
    echo Then: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting WebCam Bridge...
echo.
venv\Scripts\python.exe app.py

pause

