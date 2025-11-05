# 📦 UDP Accessory Overlay - Complete Package

## ✅ File-file yang Telah Dibuat

### 🎮 Godot Files
```
example_gui_godot/
├── UDPAccessoryOverlayScene.tscn      ✅ Scene untuk UDP interface
├── UDPAccessoryOverlayController.gd   ✅ Controller logic untuk UDP
└── UDPAccessoryWebcamManager.gd       ✅ UDP packet handler & assembler
```

### 🐍 Python Server
```
example_gui_godot/
└── udp_webcam_server.py               ✅ Sudah ada (existing)
```

### 📜 Helper Scripts
```
example_gui_godot/
├── run_udp_server.sh                  ✅ Linux/Mac launcher
└── run_udp_server.bat                 ✅ Windows launcher
```

### 📚 Documentation
```
example_gui_godot/
├── QUICKSTART_UDP.md                  ✅ Quick start guide (3 langkah)
├── CARA_MENJALANKAN_UDP.md           ✅ Panduan lengkap & troubleshooting
└── UDP_VS_TCP_COMPARISON.md          ✅ Perbandingan UDP vs TCP
```

---

## 🎯 Cara Menggunakan

### Option 1: Quick Start (Tercepat)
Ikuti `QUICKSTART_UDP.md`:
1. `python udp_webcam_server.py`
2. Buka Godot → `UDPAccessoryOverlayScene.tscn` → F6
3. Klik "Start UDP Receiver"

### Option 2: Detailed Guide
Baca `CARA_MENJALANKAN_UDP.md` untuk:
- Setup lengkap
- Konfigurasi detail
- Performance tuning
- Troubleshooting

### Option 3: Script Launcher
**Windows**: Double-click `run_udp_server.bat`
**Linux/Mac**: 
```bash
chmod +x run_udp_server.sh
./run_udp_server.sh
```

---

## 🔑 Konfigurasi Penting

### Port Configuration
**Server & Client HARUS sama!**

```python
# udp_webcam_server.py (Line 14)
def __init__(self, host='127.0.0.1', port=8888):
```

```gdscript
# UDPAccessoryWebcamManager.gd (Line 9)
var server_port: int = 8888
```

### Protocol Details
```
Protocol: UDP (User Datagram Protocol)
Port: 8888
Format: Packetized JPEG frames
Packet Structure:
  [0-3]  Sequence number (uint32 big-endian)
  [4-7]  Total packets (uint32 big-endian)
  [8-11] Packet index (uint32 big-endian)
  [12..] JPEG data chunk
```

---

## 📊 Fitur-fitur

### ✅ Di UDPAccessoryWebcamManager.gd
- [x] UDP socket binding
- [x] Client registration (REGISTER/UNREGISTER)
- [x] Packet reassembly dari multiple chunks
- [x] Frame timeout detection (2 detik)
- [x] Packet loss tracking
- [x] FPS monitoring
- [x] JPEG decoding
- [x] Signal emission ke UI

### ✅ Di UDPAccessoryOverlayController.gd
- [x] UI setup & management
- [x] Connect/Disconnect buttons
- [x] Status label dengan auto-hide
- [x] FPS display (real-time)
- [x] Stats label untuk packet loss
- [x] Placeholder image
- [x] Cleanup on exit

### ✅ Di UDPAccessoryOverlayScene.tscn
- [x] Professional UI layout
- [x] Webcam feed display (640x480)
- [x] Status overlay labels
- [x] FPS counter (top-right)
- [x] Stats counter (bottom-right)
- [x] Connection buttons
- [x] Info panels
- [x] Color scheme untuk UDP (biru)

---

## 🆚 UDP vs TCP - Pilih Mana?

### Gunakan UDP Jika:
- ✅ Butuh low latency (<50ms)
- ✅ Real-time streaming penting
- ✅ Frame drop acceptable
- ✅ Network stabil (LAN/WiFi bagus)
- ✅ Multiple clients

### Gunakan TCP Jika:
- ✅ Semua frame harus sampai
- ✅ Recording/archival
- ✅ Network tidak stabil
- ✅ Quality > Speed

---

## 📈 Performance Expectations

### Default Settings (480x360, Q40, 15FPS)
```
Latency:     30-60ms
Client FPS:  13-15
Bandwidth:   3-5 MB/s
Packet Loss: 0-2%
CPU Usage:   10-20%
```

### Optimized Settings
Edit di `udp_webcam_server.py`:
```python
# Fast Mode (Low quality, high speed)
self.target_fps = 10
self.jpeg_quality = 30
self.frame_width = 320
self.frame_height = 240

# High Quality Mode (High quality, more bandwidth)
self.target_fps = 25
self.jpeg_quality = 70
self.frame_width = 640
self.frame_height = 480
```

---

## 🐛 Common Issues & Solutions

### Port sudah digunakan
```bash
# Check port
netstat -ano | findstr :8888  # Windows
lsof -i :8888                 # Linux/Mac

# Solution: Ganti port di kedua file (server.py & Manager.gd)
```

### No video appears
```
1. Check firewall (allow Python)
2. Check server running (terminal output)
3. Check Godot console for errors
4. Restart both server & client
```

### High packet loss
```
1. Reduce FPS (target_fps = 10)
2. Reduce quality (jpeg_quality = 30)
3. Reduce resolution (320x240)
4. Check network stability
```

---

## 🔄 Workflow Diagram

```
┌─────────────────┐
│  Python Server  │
│  (Port 8888)    │
│                 │
│ 1. Capture cam  │
│ 2. Encode JPEG  │
│ 3. Split packets│
│ 4. Send via UDP │
└────────┬────────┘
         │ UDP Packets
         │ [Seq|Total|Idx|Data]
         ▼
┌─────────────────┐
│  Godot Client   │
│ (UDPManager.gd) │
│                 │
│ 1. Recv packets │
│ 2. Reassemble   │
│ 3. Decode JPEG  │
│ 4. Display      │
└─────────────────┘
```

---

## 📝 Next Steps (Optional Enhancements)

### Untuk Development Lebih Lanjut:
- [ ] Add face detection overlay
- [ ] Implement accessory selection UI
- [ ] Add recording feature
- [ ] Implement screenshot capture
- [ ] Add network statistics graph
- [ ] Implement adaptive quality (auto-adjust based on packet loss)
- [ ] Add audio streaming
- [ ] Multi-camera support

### For Production:
- [ ] Error recovery mechanisms
- [ ] Reconnection logic
- [ ] Logging system
- [ ] Configuration file (JSON/YAML)
- [ ] User preferences
- [ ] Security (encryption)

---

## 📞 Testing Checklist

Sebelum deploy, test semua scenario:

- [ ] ✅ Normal operation (connect, stream, disconnect)
- [ ] ✅ Multiple connects/disconnects
- [ ] ✅ Server restart while client running
- [ ] ✅ Client restart while server running
- [ ] ✅ Network interruption recovery
- [ ] ✅ High packet loss scenario (poor network)
- [ ] ✅ Multiple clients simultaneously
- [ ] ✅ Long running session (>1 hour)
- [ ] ✅ Different resolution settings
- [ ] ✅ Different quality settings

---

## 🎓 Learning Resources

### Godot UDP Networking
- [Godot PacketPeerUDP Docs](https://docs.godotengine.org/en/stable/classes/class_packetpeerudp.html)
- [High-level Multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)

### UDP Protocol
- [UDP vs TCP Explained](https://www.cloudflare.com/learning/ddos/glossary/user-datagram-protocol-udp/)
- [Network Programming in Python](https://realpython.com/python-sockets/)

### Video Streaming
- [Real-time Video Streaming](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html)
- [JPEG Compression](https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html)

---

## ✨ Credits

**Created for**: ETS Pengolahan Citra Digital  
**Technology Stack**: 
- Godot Engine 4.x (GDScript)
- Python 3.x + OpenCV
- UDP Protocol for low-latency streaming

**Project**: CV Accessory Overlay System  
**Version**: UDP Implementation v1.0

---

## 📄 License

Lihat `LICENSE` file di root project.

---

**🎉 Selamat! Anda sekarang punya complete UDP streaming system!**

Jika ada pertanyaan atau issue, cek:
1. `QUICKSTART_UDP.md` - Quick answers
2. `CARA_MENJALANKAN_UDP.md` - Detailed guide
3. `UDP_VS_TCP_COMPARISON.md` - Protocol comparison

**Happy Streaming! 🚀**
