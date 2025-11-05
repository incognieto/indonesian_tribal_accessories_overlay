# ⚡ Quick Reference - UDP Overlay Server

## 🚀 Menjalankan

### Cara Termudah (Recommended)
```bash
cd example_gui_godot
./run_udp_overlay_server.sh          # Linux/Mac
run_udp_overlay_server.bat           # Windows
```

### Manual
```bash
# Basic dengan sample accessories
python udp_webcam_overlay_server.py --load-samples

# Dengan SVM validation
python udp_webcam_overlay_server.py --load-samples --use-svm

# Tanpa overlay (streaming only)
python udp_webcam_server.py
```

---

## 🎮 Di Godot

1. Open `UDPAccessoryOverlayScene.tscn`
2. Press **F6**
3. Click **"Start UDP Receiver"**
4. Video dengan face detection & overlay muncul!

---

## 🎯 Fitur yang Diimplementasikan

| Fitur | Status | Keterangan |
|-------|--------|------------|
| UDP Streaming | ✅ | Low latency, 15 FPS |
| Face Detection | ✅ | Haar Cascade multi-face |
| Hat Overlay | ✅ | Auto-positioned on head |
| Earrings | ✅ | Left & right ear |
| Piercing | ✅ | Nose piercing |
| Tattoo | ✅ | Face tattoo |
| SVM Validation | ✅ | Optional, for accuracy |
| Multi-client | ✅ | Support multiple Godot clients |

---

## ⚙️ Performance

| Mode | FPS | CPU | Latency |
|------|-----|-----|---------|
| No Overlay | 15 | 10% | 30ms |
| Haar Only | 13 | 30% | 50ms |
| Haar + SVM | 10 | 45% | 80ms |

---

## 📁 File Structure

```
example_gui_godot/
├── udp_webcam_overlay_server.py  ← Server dengan overlay ⭐
├── run_udp_overlay_server.sh     ← Launcher
├── UDPAccessoryOverlayScene.tscn ← Godot scene
└── UDPAccessoryWebcamManager.gd  ← UDP client

../assets/
├── cascades/                     ← Haar cascades
├── variants/                     ← Accessories images
└── overlay_config.json           ← Position config
```

---

## 🔧 Quick Fixes

### No Face Detected
```bash
# Check cascades
ls ../assets/cascades/*.xml

# If missing:
cd ..
python app.py fetch-cascades
```

### No Accessories
```bash
# Create samples
cd ..
python app.py create-sample-data
```

### Low FPS
```python
# Edit server line 23-25:
self.target_fps = 10
self.frame_width = 320
self.frame_height = 240
```

---

## 📊 Comparison

### Original (`udp_webcam_server.py`)
- ✅ Fast (15 FPS)
- ✅ Simple
- ❌ No face detection
- ❌ No overlay

### Overlay (`udp_webcam_overlay_server.py`)
- ✅ Face detection
- ✅ Accessory overlay
- ✅ Configurable
- ⚠️ Slightly slower (12-15 FPS)

---

## 🎨 Customize Accessories

```bash
# Use your own
python udp_webcam_overlay_server.py \
  --hat path/to/hat.png \
  --ear-left path/to/earring.png \
  --piercing path/to/piercing.png
```

**Format:** PNG with transparency

---

## ✅ Checklist

Setup:
- [ ] Haar cascades downloaded
- [ ] Sample accessories created  
- [ ] Webcam working
- [ ] Port 8888 free

Run:
- [ ] Start server: `python udp_webcam_overlay_server.py --load-samples`
- [ ] See "✅ Camera ready"
- [ ] See "🎨 Loaded accessories"
- [ ] Open Godot scene
- [ ] Press F6
- [ ] Click "Start UDP Receiver"
- [ ] 🎉 Face with accessories appears!

---

## 📚 Docs

- **Full Guide**: `UDP_OVERLAY_GUIDE.md`
- **Quick Start UDP**: `QUICKSTART_UDP.md`
- **Troubleshooting**: `CARA_MENJALANKAN_UDP.md`

---

**🚀 Ready to stream dengan face detection & overlay!**
