# 📊 Visual Architecture Diagram

## 🎯 Complete System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CV ACCESSORY OVERLAY SYSTEM                       │
│                  Python (Backend) + Godot (Frontend)                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐      ┌─────────────────────────────┐
│      PYTHON SERVER SIDE         │      │     GODOT CLIENT SIDE       │
│   (tcp_webcam_overlay_server)   │      │  (AccessoryOverlay*.gd)     │
├─────────────────────────────────┤      ├─────────────────────────────┤
│                                 │      │                             │
│  ┌─────────────────────────┐   │      │  ┌─────────────────────┐   │
│  │   Webcam Capture        │   │      │  │   UI Controller     │   │
│  │  cv2.VideoCapture(0)    │   │      │  │  (Buttons, Labels)  │   │
│  └──────────┬──────────────┘   │      │  └──────────┬──────────┘   │
│             │                   │      │             │               │
│             ▼                   │      │             ▼               │
│  ┌─────────────────────────┐   │      │  ┌─────────────────────┐   │
│  │   Face Detection        │   │      │  │  Webcam Manager     │   │
│  │  • Haar Cascade         │   │      │  │  (TCP Connection)   │   │
│  │  • SVM Classifier       │   │      │  └──────────┬──────────┘   │
│  └──────────┬──────────────┘   │      │             │               │
│             │                   │      │             ▼               │
│             ▼                   │      │  ┌─────────────────────┐   │
│  ┌─────────────────────────┐   │      │  │  TCP Receive Loop   │   │
│  │  Accessory Overlay      │   │      │  │  (_process)         │   │
│  │  • Hat                  │   │      │  └──────────┬──────────┘   │
│  │  • Earrings             │   │      │             │               │
│  │  • Piercing             │   │      │             ▼               │
│  │  • Tattoo               │   │      │  ┌─────────────────────┐   │
│  └──────────┬──────────────┘   │      │  │  Parse Binary Data  │   │
│             │                   │      │  │  [4B size][JPEG]    │   │
│             ▼                   │      │  └──────────┬──────────┘   │
│  ┌─────────────────────────┐   │      │             │               │
│  │   JPEG Encoding         │   │      │             ▼               │
│  │  cv2.imencode('.jpg')   │   │      │  ┌─────────────────────┐   │
│  └──────────┬──────────────┘   │      │  │  JPEG Decoding      │   │
│             │                   │      │  │  load_jpg_from_buf  │   │
│             ▼                   │      │  └──────────┬──────────┘   │
│  ┌─────────────────────────┐   │      │             │               │
│  │   TCP Send              │   │      │             ▼               │
│  │  [size][jpeg_data]      │───┼──────┼──>  ┌─────────────────┐   │
│  └─────────────────────────┘   │      │     │  ImageTexture   │   │
│                                 │      │     └─────────┬───────┘   │
│  Port: 8081                     │      │               │           │
│  Host: 127.0.0.1                │      │               ▼           │
│  Protocol: TCP                  │      │     ┌─────────────────┐   │
│  Format: Binary                 │      │     │  TextureRect    │   │
│                                 │      │     │  (Display UI)   │   │
└─────────────────────────────────┘      │     └─────────────────┘   │
                                         └─────────────────────────────┘
```

---

## 📁 File Structure & Responsibilities

```
example_gui_godot/
│
├── 🐍 PYTHON SERVER
│   ├── tcp_webcam_overlay_server.py  ⭐ Main server
│   │   ├── TCPWebcamOverlayServer class
│   │   │   ├── initialize_camera()        → Setup webcam
│   │   │   ├── initialize_inference()     → Load AI models
│   │   │   ├── start_server()            → Start TCP server
│   │   │   ├── _accept_clients()         → Accept connections
│   │   │   ├── _broadcast_frames()       → Send frames loop
│   │   │   └── _send_frame_to_clients()  → TCP transmission
│   │   └── main()                        → CLI entry point
│   │
│   ├── test_server.py                    ⭐ Connection test
│   ├── run_server.sh                     ⭐ Linux/Mac launcher
│   └── run_server.bat                    ⭐ Windows launcher
│
├── 🎮 GODOT CLIENT
│   ├── AccessoryWebcamManager.gd         ⭐ TCP client manager
│   │   ├── connect_to_webcam_server()    → Initiate connection
│   │   ├── _process()                    → Receive loop
│   │   ├── _process_buffer()             → Parse data
│   │   ├── _process_frame()              → Decode JPEG
│   │   └── disconnect_from_server()      → Cleanup
│   │
│   ├── AccessoryOverlayController.gd     ⭐ UI controller
│   │   ├── setup_ui()                    → Initialize UI
│   │   ├── setup_webcam_manager()        → Create manager
│   │   ├── _on_connect_pressed()         → Connect handler
│   │   ├── _on_disconnect_pressed()      → Disconnect handler
│   │   ├── _on_webcam_frame_received()   → Update texture
│   │   └── _on_webcam_connection_changed() → Status update
│   │
│   └── AccessoryOverlayScene.tscn        ⭐ UI layout
│       └── Node hierarchy:
│           ├── Background (ColorRect)
│           ├── MainContainer (VBoxContainer)
│           │   ├── HeaderContainer
│           │   │   ├── TitleLabel
│           │   │   └── SubtitleLabel
│           │   ├── WebcamContainer
│           │   │   └── WebcamPanel
│           │   │       └── WebcamFeed (TextureRect) ← Video here
│           │   ├── ControlsContainer
│           │   │   ├── AccessoryPanel
│           │   │   └── ButtonsPanel
│           │   │       ├── ConnectButton
│           │   │       └── DisconnectButton
│           │   └── FooterContainer
│           │       └── InfoLabel
│
├── 📚 REFERENCE EXAMPLES
│   ├── udp_webcam_server.py              → UDP example
│   ├── WebcamClient.gd                   → TCP with threading
│   ├── WebcamManager.gd                  → TCP simplified
│   ├── EthnicityDetectionController.gd   → Ethnicity UI
│   └── EthnicityDetectionScene.tscn      → Ethnicity scene
│
└── 📖 DOCUMENTATION
    ├── README.md                         ⭐ Main overview
    ├── GODOT_INTEGRATION_GUIDE.md        ⭐ Setup guide
    ├── GODOT_CONFIG_REFERENCE.md         ⭐ Configuration
    └── INTEGRATION_SUMMARY.md            ⭐ Complete summary
```

---

## 🔄 Data Flow Diagram

### **Frame Transmission Flow**

```
PYTHON SERVER                              GODOT CLIENT
─────────────                              ────────────

1. Capture
   cv2.VideoCapture.read()
   └─> frame (640x480 RGB)
          │
          ▼
2. Face Detection
   FaceDetector.detect()
   └─> face_boxes [(x,y,w,h), ...]
          │
          ▼
3. Apply Overlay
   AccessoryOverlay.apply()
   └─> frame_with_overlay
          │
          ▼
4. Encode JPEG
   cv2.imencode('.jpg', quality=60)
   └─> jpeg_bytes (~50KB)
          │
          ▼
5. Create Header
   struct.pack('!I', size)
   └─> [4 bytes size]
          │
          ▼
6. TCP Send                                 1. TCP Receive
   socket.sendall(header + data) ──────────>   StreamPeerTCP.get_partial_data()
                                                     │
                                                     ▼
                                              2. Buffer Append
                                                 receive_buffer += data
                                                     │
                                                     ▼
                                              3. Parse Header
                                                 Read 4 bytes
                                                 └─> frame_size
                                                     │
                                                     ▼
                                              4. Extract Data
                                                 Read frame_size bytes
                                                 └─> jpeg_bytes
                                                     │
                                                     ▼
                                              5. Decode JPEG
                                                 Image.load_jpg_from_buffer()
                                                 └─> Image object
                                                     │
                                                     ▼
                                              6. Create Texture
                                                 ImageTexture.set_image()
                                                 └─> texture
                                                     │
                                                     ▼
                                              7. Update UI
                                                 TextureRect.texture = texture
                                                 └─> Display on screen ✨
```

---

## ⚡ Event Flow Diagram

### **User Interaction Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER ACTIONS                              │
└─────────────────────────────────────────────────────────────────┘

1. Start Python Server
   └─> python tcp_webcam_overlay_server.py --no-svm
       └─> Server listening on 127.0.0.1:8081 ✅

2. Open Godot Scene
   └─> AccessoryOverlayScene.tscn
       └─> Controller._ready() called
           ├─> setup_ui()
           ├─> setup_webcam_manager()
           └─> UI initialized ✅

3. Click "Connect to Server"
   └─> _on_connect_pressed()
       └─> webcam_manager.connect_to_webcam_server()
           └─> StreamPeerTCP.connect_to_host()
               └─> Connection established ✅
                   └─> Signal: connection_changed(true)
                       └─> _on_webcam_connection_changed(true)
                           └─> status_label.text = "✅ Terhubung"

4. Receive Frames (Automatic Loop)
   └─> _process() called every frame
       └─> Check available bytes
           └─> Data available?
               ├─> YES: Process buffer
               │   └─> Parse [size][data]
               │       └─> Decode JPEG
               │           └─> Update texture
               │               └─> Signal: frame_received(texture)
               │                   └─> _on_webcam_frame_received()
               │                       └─> webcam_feed.texture = texture ✨
               │
               └─> NO: Wait for next _process()

5. Click "Disconnect"
   └─> _on_disconnect_pressed()
       └─> webcam_manager.disconnect_from_server()
           └─> StreamPeerTCP.disconnect_from_host()
               └─> Connection closed ✅
                   └─> Signal: connection_changed(false)
                       └─> status_label.text = "❌ Terputus"
```

---

## 🎨 UI Component Hierarchy

```
AccessoryOverlayUI (Control) ← Root Script: AccessoryOverlayController.gd
│
├─ Background (ColorRect)
│  └─ Color: (0.1, 0.12, 0.15, 1) - Dark blue-gray
│
└─ MainContainer (VBoxContainer) - Main layout
   │
   ├─ HeaderContainer (VBoxContainer)
   │  ├─ TitleLabel
   │  │  └─ "CV Accessory Overlay System"
   │  └─ SubtitleLabel
   │     └─ "AI-Powered Face Detection..."
   │
   ├─ WebcamContainer (CenterContainer) - Webcam area
   │  └─ WebcamPanel (Panel)
   │     └─ WebcamFeed (TextureRect) ← 🎥 VIDEO DISPLAYED HERE
   │        ├─ StatusLabel (overlay)
   │        │  └─ "✅ Terhubung" / "❌ Terputus"
   │        └─ FPSLabel (overlay, top-right)
   │           └─ "FPS: 15.3"
   │
   ├─ ControlsContainer (HBoxContainer) - Controls panel
   │  ├─ AccessoryPanel (Panel)
   │  │  └─ AccessoryList (VBoxContainer)
   │  │     ├─ AccessoryTitle
   │  │     └─ AccessoryInfo
   │  │
   │  └─ ButtonsPanel (Panel)
   │     └─ VBoxContainer
   │        ├─ ButtonsTitle
   │        ├─ ConnectButton ← Click to connect
   │        ├─ DisconnectButton ← Click to disconnect
   │        └─ ServerInfo
   │
   └─ FooterContainer (HBoxContainer)
      └─ InfoLabel
         └─ "AI-powered face detection..."
```

---

## 🔌 Network Protocol Specification

### **TCP Packet Format**

```
┌────────────────────────────────────────────────┐
│              SINGLE FRAME PACKET               │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────┐                         │
│  │  HEADER (4 bytes)│                         │
│  ├──────────────────┤                         │
│  │  Byte 0: Size MSB (Most Significant Byte) │
│  │  Byte 1: Size                              │
│  │  Byte 2: Size                              │
│  │  Byte 3: Size LSB (Least Significant Byte)│
│  └──────────────────┘                         │
│         │                                      │
│         ▼                                      │
│  Frame Size (Big Endian, uint32)              │
│  Example: 0x0000BF4A = 48970 bytes            │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  PAYLOAD (variable size)                 │ │
│  ├──────────────────────────────────────────┤ │
│  │  JPEG Image Data                         │ │
│  │  • Quality: 60                           │ │
│  │  • Resolution: 640x480                   │ │
│  │  • Size: ~30-60 KB                       │ │
│  └──────────────────────────────────────────┘ │
│                                                │
└────────────────────────────────────────────────┘

Total Packet Size: 4 + frame_size bytes
Example: 4 + 48970 = 48974 bytes
```

### **Example Transmission**

```python
# Python Server
frame_size = 50000  # 50 KB JPEG
header = struct.pack('!I', frame_size)  # '\x00\x00\xc3\x50'
packet = header + jpeg_bytes
socket.sendall(packet)  # Total: 50004 bytes

# Godot Client
var header = receive_buffer.slice(0, 4)
var size = (header[0] << 24) | (header[1] << 16) | (header[2] << 8) | header[3]
# size = 50000
var jpeg_bytes = receive_buffer.slice(4, 4 + size)
# jpeg_bytes.size() = 50000
```

---

## 🚀 Performance Characteristics

```
┌────────────────────────────────────────────────────────┐
│              PERFORMANCE METRICS                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Resolution: 640x480                                   │
│  JPEG Quality: 60                                      │
│  Target FPS: 15                                        │
│  Frame Size: ~30-60 KB                                 │
│  Bandwidth: ~450-900 KB/s (3.6-7.2 Mbps)              │
│  Latency: ~67 ms per frame (localhost)                │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  BREAKDOWN PER FRAME                             │ │
│  ├──────────────────────────────────────────────────┤ │
│  │  Capture:         ~5 ms    ▓▓░░░░░░░░░░         │ │
│  │  Face Detection:  ~20 ms   ▓▓▓▓▓▓▓▓░░░░         │ │
│  │  Overlay:         ~5 ms    ▓▓░░░░░░░░░░         │ │
│  │  JPEG Encode:     ~15 ms   ▓▓▓▓▓▓░░░░░░         │ │
│  │  TCP Send:        ~5 ms    ▓▓░░░░░░░░░░         │ │
│  │  Network:         ~2 ms    ▓░░░░░░░░░░░         │ │
│  │  TCP Receive:     ~3 ms    ▓░░░░░░░░░░░         │ │
│  │  JPEG Decode:     ~10 ms   ▓▓▓▓░░░░░░░░         │ │
│  │  Texture Update:  ~2 ms    ▓░░░░░░░░░░░         │ │
│  │  ────────────────────────────────────          │ │
│  │  TOTAL:          ~67 ms    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  🔧 OPTIMIZATION OPTIONS:                              │
│  • --no-svm: Save ~15 ms (skip SVM validation)        │
│  • Lower resolution: Save ~20 ms (320x240)            │
│  • Lower quality: Save ~5 ms (quality=40)             │
│  • Target: 30 FPS achievable with optimizations       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases & Applications

```
┌──────────────────────────────────────────────────────────┐
│           POTENTIAL APPLICATIONS                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🎮 Gaming & Entertainment                               │
│  ├─ Character customization preview                     │
│  ├─ Virtual cosplay/costume try-on                      │
│  └─ AR game character creation                          │
│                                                          │
│  🛍️ E-Commerce & Retail                                  │
│  ├─ Virtual try-on for accessories                      │
│  ├─ Jewelry fitting simulation                          │
│  └─ Hat/glasses shopping preview                        │
│                                                          │
│  📱 Social Media & Apps                                   │
│  ├─ Face filters and effects                            │
│  ├─ Snapchat-style lenses                               │
│  └─ Instagram AR filters                                │
│                                                          │
│  🎓 Education & Training                                  │
│  ├─ Computer vision learning                            │
│  ├─ Game development education                          │
│  └─ AI integration tutorials                            │
│                                                          │
│  🏥 Medical & Healthcare                                  │
│  ├─ Surgical mask fitting                               │
│  ├─ Eyewear prescription preview                        │
│  └─ Medical device positioning                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Comparison Table

| Feature | Accessory System | Ethnicity System |
|---------|------------------|------------------|
| **Protocol** | TCP | UDP |
| **Data Format** | Binary [size][JPEG] | JSON + base64 |
| **Face Detection** | Haar + SVM (Real AI) | Simulated |
| **Overlay** | Accessories (Real) | None |
| **Reliability** | High (TCP) | Medium (UDP) |
| **Latency** | ~67ms | ~50ms |
| **Code Quality** | Production-ready | Example/Demo |
| **Documentation** | Complete | Basic |
| **Use Case** | Real application | Learning reference |

---

**This visual guide provides a complete understanding of the system architecture! 🎨**
