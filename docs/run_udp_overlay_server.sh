#!/bin/bash
echo "========================================="
echo "  UDP Webcam Overlay Server Launcher"
echo "========================================="
echo ""
echo "🎭 Starting UDP Server with Face Detection & Overlay..."
echo "   Port: 8888"
echo "   Protocol: UDP"
echo "   Features: Face Detection + Accessory Overlay"
echo ""

# Run with sample accessories
python3 udp_webcam_overlay_server.py --load-samples

echo ""
echo "Server stopped."
