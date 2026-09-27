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

REM ── Cloudflare Quick Tunnel (automatic HTTPS, no account needed) ────────
REM The app will auto-start a Cloudflare tunnel and show the URL + QR code.
REM URL changes each restart. For a permanent URL you need a domain on Cloudflare.

echo Starting WebCam Bridge...
echo.
venv\Scripts\python.exe app.py

pause

