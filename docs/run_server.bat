@echo off
REM Quick start script for TCP Webcam Overlay Server (Windows)

echo ==========================================
echo   TCP Webcam Overlay Server Launcher
echo ==========================================
echo.

REM Check if running from correct directory
if not exist "app.py" (
    echo [X] Error: Please run this script from the cv_accessory_overlay root directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist ".venv" (
    echo [√] Virtual environment found
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
        echo [√] Virtual environment activated
    ) else (
        echo [!] Warning: Virtual environment exists but activate script not found
    )
) else (
    echo [!] Virtual environment not found. Run: python app.py setup-venv
)

REM Default settings
set HOST=127.0.0.1
set PORT=8081
set USE_SVM=--no-svm

REM Check if accessories exist
set HAT=
set EAR_LEFT=
set EAR_RIGHT=

if exist "assets\variants\hat_blue.png" (
    set HAT=--hat assets/variants/hat_blue.png
    echo [√] Hat accessory found
)

if exist "assets\variants\earring_left_gold.png" (
    set EAR_LEFT=--ear-left assets/variants/earring_left_gold.png
    echo [√] Left earring accessory found
)

if exist "assets\variants\earring_right_gold.png" (
    set EAR_RIGHT=--ear-right assets/variants/earring_right_gold.png
    echo [√] Right earring accessory found
)

echo.
echo Starting server with settings:
echo   Host: %HOST%
echo   Port: %PORT%
echo   SVM: Disabled (faster)
echo.

REM Run server
python example_gui_godot\tcp_webcam_overlay_server.py --host %HOST% --port %PORT% %USE_SVM% %HAT% %EAR_LEFT% %EAR_RIGHT%

echo.
echo Server stopped.
pause
