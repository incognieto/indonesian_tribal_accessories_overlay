# 🎭 UDP Webcam Server dengan Face Detection & Overlay

## 📋 Overview

Server ini mengintegrasikan sistem deteksi wajah dan overlay aksesoris ke dalam UDP streaming untuk Godot. Anda akan mendapatkan:

- ✅ Real-time face detection menggunakan Haar Cascade
- ✅ Accessory overlay (hat, earrings, piercing, tattoo)
- ✅ Optional SVM validation untuk akurasi lebih tinggi
- ✅ UDP streaming ke Godot client
- ✅ Low latency (<60ms)

---

## 🚀 Quick Start

### 1. Server Tanpa Overlay (Original)
```bash
python udp_webcam_server.py
```
Streaming webcam biasa tanpa face detection.

### 2. Server dengan Overlay (Recommended)
```bash
python udp_webcam_overlay_server.py --load-samples
```
Streaming dengan face detection dan sample accessories.

### 3. Server dengan SVM Validation
```bash
python udp_webcam_overlay_server.py --load-samples --use-svm
```
Menggunakan SVM untuk validasi wajah (butuh model terlatih).

---

## 📦 File-file yang Tersedia

### Server Scripts
```
example_gui_godot/
├── udp_webcam_server.py              ← Server basic (no overlay)
├── udp_webcam_overlay_server.py      ← Server with face detection & overlay ⭐
├── run_udp_server.sh/.bat            ← Launcher basic server
└── run_udp_overlay_server.sh/.bat    ← Launcher overlay server ⭐
```

### Godot Files
```
├── UDPAccessoryOverlayScene.tscn     ← Godot scene
├── UDPAccessoryOverlayController.gd  ← Controller
└── UDPAccessoryWebcamManager.gd      ← UDP manager
```

---

## ⚙️ Command Line Options

### Server dengan Overlay

```bash
python udp_webcam_overlay_server.py [OPTIONS]
```

**Server Settings:**
- `--host` : Server IP (default: 127.0.0.1)
- `--port` : Server port (default: 8888)

**Overlay Settings:**
- `--no-overlay` : Disable overlay system (streaming only)
- `--use-svm` : Enable SVM face validation (requires trained model)

**Paths:**
- `--cascade-dir` : Haar cascades directory (default: ../assets/cascades)
- `--models-dir` : SVM models directory (default: ../models)
- `--config` : Overlay config JSON (default: ../assets/overlay_config.json)

**Accessories (Manual):**
- `--hat` : Path to hat image
- `--ear-left` : Path to left earring image
- `--ear-right` : Path to right earring image
- `--piercing` : Path to nose piercing image
- `--tattoo-face` : Path to face tattoo image

**Quick Load:**
- `--load-samples` : Auto-load sample accessories from assets/variants ⭐

---

## 📝 Usage Examples

### Example 1: Basic Overlay dengan Samples
```bash
cd example_gui_godot
python udp_webcam_overlay_server.py --load-samples
```

**Output:**
```
======================================================================
  UDP WEBCAM SERVER - FACE DETECTION & ACCESSORY OVERLAY
======================================================================

🎭 Initializing Face Detection & Overlay System...
✅ Loaded overlay config from ../assets/overlay_config.json
✅ Face detector initialized
🎨 Loading accessories...
  ✓ hat: ../assets/variants/hat_example.png
  ✓ earring_left: ../assets/variants/earring_left_example.png
  ✓ earring_right: ../assets/variants/earring_right_example.png
  ✓ piercing_nose: ../assets/variants/piercing_nose_example.png
✅ Overlay system initialized
✅ Inference pipeline ready

🎥 Initializing optimized camera...
📌 Platform: Linux
🔍 Trying backend: V4L2...
✅ Camera ready with V4L2
📐 Resolution: 480x360 @ 15FPS

======================================================================

🚀 UDP Server: 127.0.0.1:8888
📊 Settings: 480x360, 15FPS, Q40
🎭 Overlay: Enabled
🤖 SVM: Disabled
🎨 Loaded accessories: hat, earring_left, earring_right, piercing_nose

⏳ Waiting for clients...
```

### Example 2: Custom Accessories
```bash
python udp_webcam_overlay_server.py \
  --hat ../assets/variants/hat_red.png \
  --ear-left ../assets/variants/earring_left_gold.png \
  --piercing ../assets/variants/piercing_nose_silver.png
```

### Example 3: Dengan SVM (High Accuracy)
```bash
# Pastikan model SVM sudah dilatih
python udp_webcam_overlay_server.py --load-samples --use-svm
```

### Example 4: No Overlay (Basic Streaming)
```bash
python udp_webcam_overlay_server.py --no-overlay
```

### Example 5: Custom Port & Host
```bash
python udp_webcam_overlay_server.py --host 0.0.0.0 --port 9999 --load-samples
```

---

## 🎮 Menjalankan di Godot

### Langkah 1: Start Server
```bash
# Terminal 1
cd example_gui_godot
python udp_webcam_overlay_server.py --load-samples
```

### Langkah 2: Run Godot Client
1. Buka Godot Engine
2. Import project `example_gui_godot/`
3. Open scene `UDPAccessoryOverlayScene.tscn`
4. Press **F6** (Run Scene)
5. Klik **"Start UDP Receiver"**

### Hasil
Video stream akan menampilkan:
- ✅ Face detection boxes (green)
- ✅ Accessories overlay (hat, earrings, piercing)
- ✅ Real-time FPS counter
- ✅ Smooth streaming

---

## 🎨 Menggunakan Accessories Sendiri

### Format Accessories
Semua accessories harus berformat **PNG dengan transparency (alpha channel)**.

### Struktur
```
assets/variants/
├── hat_*.png                 ← Topi
├── earring_left_*.png        ← Anting kiri
├── earring_right_*.png       ← Anting kanan
├── piercing_nose_*.png       ← Piercing hidung
└── tattoo_face_*.png         ← Tato wajah
```

### Cara Membuat
1. Buat gambar dengan background transparan
2. Save sebagai PNG
3. Simpan di `assets/variants/`
4. Gunakan dengan `--hat path/to/your/hat.png`

### Quick Create Samples
```bash
cd ..  # ke root project
python app.py create-sample-data --assets-dir assets
```

---

## 🔧 Troubleshooting

### ❌ Problem: "Failed to initialize face detection"

**Penyebab:** Haar cascade files tidak ditemukan

**Solusi:**
```bash
cd ..  # ke root project
python app.py fetch-cascades --dest assets/cascades
```

---

### ❌ Problem: "SVM model not found"

**Penyebab:** Model SVM belum dilatih

**Solusi Option 1 - Disable SVM:**
```bash
python udp_webcam_overlay_server.py --load-samples  # Tanpa --use-svm
```

**Solusi Option 2 - Train SVM:**
```bash
cd ..  # ke root project
# Persiapkan dataset dulu
python app.py train --pos-dir data/faces_pos --neg-dir data/faces_neg
```

---

### ❌ Problem: "Accessories not found"

**Penyebab:** File accessory tidak ada

**Solusi:**
```bash
# Buat sample accessories
cd ..
python app.py create-sample-data --assets-dir assets

# Atau gunakan path absolut
python udp_webcam_overlay_server.py --hat /full/path/to/hat.png
```

---

### ⚠️ Problem: "Low FPS dengan Overlay"

**Penyebab:** Face detection + overlay memakan CPU

**Solusi:**
1. Turunkan resolusi di server:
   ```python
   # Edit udp_webcam_overlay_server.py line 24-25
   self.frame_width = 320   # dari 480
   self.frame_height = 240  # dari 360
   ```

2. Turunkan FPS target:
   ```python
   # Line 23
   self.target_fps = 10  # dari 15
   ```

3. Disable SVM jika tidak perlu:
   ```bash
   # Jangan gunakan --use-svm
   ```

---

### 🎯 Performance Tips

**Untuk Low-End PC:**
```python
# Edit server settings
self.target_fps = 10
self.frame_width = 320
self.frame_height = 240
self.jpeg_quality = 30
```

**Untuk High Performance:**
```python
self.target_fps = 25
self.frame_width = 640
self.frame_height = 480
self.jpeg_quality = 60
```

---

## 📊 Performance Benchmark

### Tanpa Overlay
- FPS: 15
- CPU: 10-15%
- Latency: 30ms

### Dengan Overlay (Haar Only)
- FPS: 12-15
- CPU: 25-35%
- Latency: 40-60ms

### Dengan Overlay + SVM
- FPS: 8-12
- CPU: 40-50%
- Latency: 60-100ms

---

## 🔄 Workflow Diagram

```
┌─────────────────────┐
│  Python Server      │
│  (Port 8888)        │
│                     │
│ 1. Capture frame    │
│ 2. Detect faces     │ ← Haar Cascade
│ 3. Validate (SVM)   │ ← Optional
│ 4. Apply overlay    │ ← Accessories
│ 5. Encode JPEG      │
│ 6. Split packets    │
│ 7. Send UDP         │
└──────────┬──────────┘
           │
           │ UDP Packets
           │ [Seq|Total|Idx|Data]
           ▼
┌──────────────────────┐
│  Godot Client        │
│  (UDPManager.gd)     │
│                      │
│ 1. Recv packets      │
│ 2. Reassemble        │
│ 3. Decode JPEG       │
│ 4. Display           │
└──────────────────────┘
```

---

## 🎓 Advanced Usage

### Multiple Accessories
```bash
python udp_webcam_overlay_server.py \
  --hat ../assets/variants/hat_red.png \
  --ear-left ../assets/variants/earring_left_gold.png \
  --ear-right ../assets/variants/earring_right_gold.png \
  --piercing ../assets/variants/piercing_nose_silver.png \
  --tattoo-face ../assets/variants/tattoo_face_tribal.png
```

### Custom Configuration
Edit `assets/overlay_config.json`:
```json
{
  "hat": {
    "offset_x": 0.0,
    "offset_y": -0.6,
    "scale": 1.4
  },
  "earring_left": {
    "offset_x": -0.35,
    "offset_y": 0.1,
    "scale": 0.15
  }
}
```

### Remote Access
```bash
# Server (allow external connections)
python udp_webcam_overlay_server.py --host 0.0.0.0 --port 8888 --load-samples

# Client: Edit UDPAccessoryWebcamManager.gd
var server_host: String = "192.168.1.100"  # IP server
```

---

## 📚 Next Steps

1. **Customize Accessories**: Buat accessory sendiri
2. **Train SVM**: Latih model untuk akurasi lebih tinggi
3. **Add More Accessories**: Tambah jenis accessory baru
4. **Optimize Performance**: Tune settings untuk PC Anda
5. **Create Variants**: Buat banyak variasi accessory

---

## ✅ Checklist

Sebelum menjalankan, pastikan:

- [ ] Python 3.8+ installed
- [ ] OpenCV installed (`pip install opencv-python`)
- [ ] Haar cascades downloaded (di `../assets/cascades/`)
- [ ] Sample accessories exist (di `../assets/variants/`)
- [ ] Webcam terdeteksi (`ls /dev/video*`)
- [ ] Port 8888 available
- [ ] Godot 4.x installed
- [ ] Scene files di-import

---

**🎉 Selamat! Anda sekarang punya streaming webcam dengan face detection dan accessory overlay real-time!**

Happy streaming! 🚀
