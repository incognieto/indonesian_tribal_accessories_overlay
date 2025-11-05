# ⚡ Quick Start - UDP Accessory Overlay

## 🚀 Cara Cepat (3 Langkah)

### 1️⃣ Jalankan Server Python
```bash
cd cv_accessory_overlay/example_gui_godot
python udp_webcam_server.py
```
**Output:**
```
✅ Camera ready: 480x360 @ 15FPS
🚀 Optimized UDP Server: 127.0.0.1:8888
```

---

### 2️⃣ Buka di Godot
1. Import project: `example_gui_godot/project.godot`
2. Open scene: `UDPAccessoryOverlayScene.tscn`
3. Press **F6** (Run Scene)

---

### 3️⃣ Connect di Godot
1. Klik tombol **"Start UDP Receiver"**
2. Video stream akan muncul!

---

## 📋 Konfigurasi Godot

### File Structure
```
res://
├── UDPAccessoryOverlayScene.tscn       ← Open ini & tekan F6
├── UDPAccessoryOverlayController.gd    ← Auto-attached
└── UDPAccessoryWebcamManager.gd        ← Auto-loaded
```

### Scene Hierarchy (sudah configured)
```
UDPAccessoryOverlayUI
├── MainContainer
│   ├── WebcamContainer
│   │   └── WebcamFeed (TextureRect)  ← Video muncul di sini
│   └── ButtonsPanel
│       ├── ConnectButton              ← Klik ini untuk start
│       └── DisconnectButton
```

### Settings (default - sudah OK)
```gdscript
# UDPAccessoryWebcamManager.gd (Line 9)
var server_host: String = "127.0.0.1"
var server_port: int = 8888
```

---

## 🔧 Troubleshooting Cepat

| Problem | Solution |
|---------|----------|
| ❌ Camera failed | Tutup app lain yang pakai webcam |
| ❌ Port error | Ganti port 8888 → 8889 di kedua file |
| ❌ No video | Check firewall, allow Python |
| 🐌 Low FPS | Turunkan quality di server.py |
| ⚠️ Packet loss | Turunkan FPS atau resolusi |

---

## ⚙️ Performance Tuning

Edit `udp_webcam_server.py` (Line 23-27):

```python
# FAST (Low Quality)
self.target_fps = 10
self.jpeg_quality = 30
self.frame_width = 320
self.frame_height = 240

# BALANCED (Default) ✅
self.target_fps = 15
self.jpeg_quality = 40
self.frame_width = 480
self.frame_height = 360

# HIGH QUALITY (High CPU/Bandwidth)
self.target_fps = 25
self.jpeg_quality = 70
self.frame_width = 640
self.frame_height = 480
```

---

## 📊 Monitoring

### Di Godot (top-right corner)
```
FPS: 14.8           ← Green label
UDP: No packet loss ← Blue label (bottom-right)
```

### Di Python Terminal
```
📤 Frame 61: 28KB → 1 clients
```

---

## 🎯 Expected Performance

| Mode | FPS | Latency | Bandwidth |
|------|-----|---------|-----------|
| Fast | 10 | 20ms | 1-2 MB/s |
| Default | 15 | 30ms | 3-5 MB/s |
| High | 25 | 60ms | 8-12 MB/s |

---

## 📝 Checklist

- [ ] Python + opencv installed
- [ ] Webcam working
- [ ] Run `python udp_webcam_server.py`
- [ ] See "✅ Camera ready"
- [ ] Open Godot project
- [ ] Open `UDPAccessoryOverlayScene.tscn`
- [ ] Press F6
- [ ] Click "Start UDP Receiver"
- [ ] 🎉 Video appears!

---

## 🆚 UDP vs TCP

| Feature | UDP | TCP |
|---------|-----|-----|
| Speed | ⚡ Fast | 🐌 Slower |
| Latency | 30-60ms | 100-200ms |
| Reliability | Packet loss OK | 100% reliable |
| Use Case | Real-time | Recording |

**Pilih UDP jika:**
- Butuh low latency
- Live streaming/gaming
- Frame drop acceptable

**File untuk TCP:**
- `AccessoryOverlayScene.tscn`
- Port 8081
- Run: `python tcp_webcam_overlay_server.py`

---

## 🔗 Links

- **Full Guide**: `CARA_MENJALANKAN_UDP.md`
- **Comparison**: `UDP_VS_TCP_COMPARISON.md`
- **Architecture**: `GODOT_INTEGRATION_GUIDE.md`

---

**🎉 That's it! Simple kan?**
