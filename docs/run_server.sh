#!/bin/bash
# Quick start script for TCP Webcam Overlay Server

echo "=========================================="
echo "  TCP Webcam Overlay Server Launcher"
echo "=========================================="
echo ""

# Check if running from correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the cv_accessory_overlay root directory"
    exit 1
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "⚠️ Warning: Virtual environment exists but activate script not found"
    fi
else
    echo "⚠️ Virtual environment not found. Run: python app.py setup-venv"
fi

# Default settings
HOST="127.0.0.1"
PORT="8081"
USE_SVM="--no-svm"

# Check if accessories exist
HAT=""
EAR_LEFT=""
EAR_RIGHT=""

if [ -f "assets/variants/hat_blue.png" ]; then
    HAT="--hat assets/variants/hat_blue.png"
    echo "✅ Hat accessory found"
fi

if [ -f "assets/variants/earring_left_gold.png" ]; then
    EAR_LEFT="--ear-left assets/variants/earring_left_gold.png"
    echo "✅ Left earring accessory found"
fi

if [ -f "assets/variants/earring_right_gold.png" ]; then
    EAR_RIGHT="--ear-right assets/variants/earring_right_gold.png"
    echo "✅ Right earring accessory found"
fi

echo ""
echo "Starting server with settings:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  SVM: Disabled (faster)"
echo ""

# Run server
python example_gui_godot/tcp_webcam_overlay_server.py \
    --host "$HOST" \
    --port "$PORT" \
    $USE_SVM \
    $HAT \
    $EAR_LEFT \
    $EAR_RIGHT

echo ""
echo "Server stopped."
