# 🎮 Godot Integration - CV Accessory Overlay System

Integrasi antara **Python (OpenCV + AI)** dan **Godot Engine (GUI)** untuk sistem overlay aksesoris real-time.

---

## 📁 File Structure

```
example_gui_godot/
├── tcp_webcam_overlay_server.py    # Python: TCP server dengan overlay aksesoris
├── AccessoryWebcamManager.gd       # Godot: Manager untuk koneksi TCP
├── AccessoryOverlayController.gd   # Godot: Controller UI utama
├── AccessoryOverlayScene.tscn      # Godot: Scene file (UI layout)
└── GODOT_INTEGRATION_GUIDE.md      # Panduan ini
```

---

## 🚀 Quick Start

### **1. Setup Python Server**

#### **A. Install Dependencies**
```bash
# Dari root folder cv_accessory_overlay
pip install -r requirements.txt
```

#### **B. Siapkan Assets (Opsional)**
```bash
# Download Haar cascades jika belum ada
python app.py fetch-cascades

# Buat sample accessories (opsional)
python app.py create-sample-data
```

#### **C. Jalankan Server**

**Tanpa SVM (Hanya Haar Cascade):**
```bash
python example_gui_godot/tcp_webcam_overlay_server.py --no-svm
```

**Dengan SVM (Perlu model terlatih):**
```bash
python example_gui_godot/tcp_webcam_overlay_server.py
```

**Dengan Accessories:**
```bash
python example_gui_godot/tcp_webcam_overlay_server.py \
    --no-svm \
    --hat assets/variants/hat_0001.png \
    --ear-left assets/variants/earring_left_0001.png \
    --ear-right assets/variants/earring_right_0001.png
```

**Custom Server Settings:**
```bash
python example_gui_godot/tcp_webcam_overlay_server.py \
    --host 127.0.0.1 \
    --port 8081 \
    --no-svm \
    --hat path/to/hat.png
```

#### **Output yang Diharapkan:**
```
=== TCP Webcam Overlay Server for Godot ===
🤖 Initializing inference pipeline...
⚠️ SVM loading failed: ... Running without SVM validation.
✅ Loaded accessory: hat
✅ Inference pipeline ready with 1 accessories
🎥 Initializing camera...
✅ Camera ready: 640x480 @ 15FPS
🚀 TCP Webcam Overlay Server: 127.0.0.1:8081
📊 Settings: 640x480, 15FPS, Q60
🎨 Accessories: hat
```

---

### **2. Setup Godot Project**

#### **A. Buat Project Godot Baru**
1. Buka **Godot Engine 4.x**
2. Buat project baru atau buka project yang ada
3. Pastikan project menggunakan **Godot 4.x** (GDScript 2.0)

#### **B. Copy File-file GDScript**

Copy file-file berikut ke project Godot Anda:

```
YourGodotProject/
├── example_gui_godot/
│   ├── AccessoryWebcamManager.gd
│   ├── AccessoryOverlayController.gd
│   └── AccessoryOverlayScene.tscn
```

**Atau** sesuaikan path di scene file:
- Edit `AccessoryOverlayScene.tscn`
- Ubah path script sesuai struktur project Anda

#### **C. Konfigurasi Path di Scene**

Buka `AccessoryOverlayScene.tscn` dan pastikan path script benar:

```gdscript
[ext_resource type="Script" path="res://example_gui_godot/AccessoryOverlayController.gd" id="1_controller"]
```

Sesuaikan dengan struktur folder Anda, misalnya:
```gdscript
[ext_resource type="Script" path="res://scripts/AccessoryOverlayController.gd" id="1_controller"]
```

#### **D. Update Path di Controller**

Edit `AccessoryOverlayController.gd`, line ~53:

```gdscript
var webcam_script = load("res://example_gui_godot/AccessoryWebcamManager.gd")
```

Sesuaikan dengan path Anda:
```gdscript
var webcam_script = load("res://scripts/AccessoryWebcamManager.gd")
```

---

### **3. Jalankan Aplikasi**

#### **Step 1: Start Python Server**
```bash
python example_gui_godot/tcp_webcam_overlay_server.py --no-svm --hat assets/variants/hat_0001.png
```

#### **Step 2: Run Godot Scene**
1. Buka Godot Editor
2. Buka scene `AccessoryOverlayScene.tscn`
3. Tekan **F5** (Run) atau **F6** (Run Current Scene)
4. Klik tombol **"Connect to Server"**

#### **Expected Result:**
- Webcam feed muncul dengan overlay aksesoris
- Status: "✅ Terhubung - Stream aktif"
- FPS counter muncul di pojok kanan atas

---

## ⚙️ Konfigurasi

### **Python Server Configuration**

File: `tcp_webcam_overlay_server.py`

```python
# Network Settings
host = '127.0.0.1'    # Server IP
port = 8081           # Server port

# Video Settings
target_fps = 15       # Frame rate (10-30)
jpeg_quality = 60     # JPEG quality (40-90)
frame_width = 640     # Resolution width
frame_height = 480    # Resolution height
```

### **Godot Client Configuration**

File: `AccessoryWebcamManager.gd`

```gdscript
# Server connection
var server_host: String = "127.0.0.1"
var server_port: int = 8081
```

**Jika server di komputer lain:**
```gdscript
var server_host: String = "192.168.1.100"  # IP komputer server
var server_port: int = 8081
```

---

## 🔧 Troubleshooting

### **Problem: "Connection error" / "Connection lost"**

**Solusi:**
1. Pastikan Python server sudah berjalan
2. Cek firewall tidak memblokir port 8081
3. Verifikasi IP dan port sesuai di client dan server

### **Problem: "Camera initialization failed"**

**Solusi:**
1. Cek webcam terhubung dan tidak digunakan aplikasi lain
2. Ganti `cv2.CAP_DSHOW` ke `cv2.CAP_ANY` (line 61 di server)
3. Test webcam dengan: `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`

### **Problem: "Failed to decode frame"**

**Solusi:**
1. Kurangi `jpeg_quality` di server (line 29)
2. Periksa network bandwidth
3. Cek buffer size mencukupi

### **Problem: "AccessoryWebcamManager.gd not found"**

**Solusi:**
1. Verifikasi path file di `AccessoryOverlayController.gd`
2. Pastikan file ada di lokasi yang benar
3. Gunakan path absolut: `res://path/to/AccessoryWebcamManager.gd`

### **Problem: Low FPS**

**Solusi:**
1. Turunkan resolusi: `frame_width = 320, frame_height = 240`
2. Kurangi `target_fps = 10`
3. Tingkatkan `jpeg_quality` untuk kompresi lebih besar
4. Disable SVM: `--no-svm`

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────┐
│     Python Server (Backend)         │
│                                     │
│  1. cv2.VideoCapture(0)             │
│     └─> Baca frame dari webcam      │
│                                     │
│  2. FaceDetector.detect()           │
│     └─> Deteksi wajah (Haar+SVM)    │
│                                     │
│  3. AccessoryOverlay.apply()        │
│     └─> Terapkan overlay aksesoris  │
│                                     │
│  4. cv2.imencode('.jpg', frame)     │
│     └─> Encode ke JPEG              │
│                                     │
│  5. TCP Socket Send                 │
│     └─> [4-byte size][JPEG data]    │
└────────────┬────────────────────────┘
             │ TCP/IP (Port 8081)
             ▼
┌─────────────────────────────────────┐
│    Godot Client (Frontend)          │
│                                     │
│  1. StreamPeerTCP.connect()         │
│     └─> Koneksi ke Python server    │
│                                     │
│  2. _process() loop                 │
│     └─> Polling data available      │
│                                     │
│  3. Parse [size][data]              │
│     └─> Extract JPEG bytes          │
│                                     │
│  4. Image.load_jpg_from_buffer()    │
│     └─> Decode JPEG ke Image        │
│                                     │
│  5. ImageTexture.set_image()        │
│     └─> Convert ke Texture          │
│                                     │
│  6. TextureRect.texture = ...       │
│     └─> Tampilkan di UI             │
└─────────────────────────────────────┘
```

---

## 🎨 Customization

### **Menambah UI Elements**

Edit `AccessoryOverlayScene.tscn` atau di Godot Editor:

1. Tambah node baru (Button, Label, dll)
2. Di `AccessoryOverlayController.gd`, tambah `@onready var`:
   ```gdscript
   @onready var my_button = $Path/To/MyButton
   ```
3. Setup event di `_ready()`:
   ```gdscript
   my_button.pressed.connect(_on_my_button_pressed)
   ```

### **Menambah Accessory Control**

Di `AccessoryOverlayController.gd`:

```gdscript
func toggle_accessory(accessory_name: String):
    """Toggle specific accessory on/off"""
    # Implementasi untuk mengirim command ke server
    # Atau handle di client side
    pass
```

### **Custom Styling**

Edit theme di Godot Editor:
1. Pilih node (Button, Label, dll)
2. Inspector → Theme Overrides
3. Modify colors, fonts, sizes

---

## 🔐 Security Notes

⚠️ **Peringatan:**
- Server ini untuk **development/testing** saja
- Tidak ada enkripsi (plaintext TCP)
- Tidak ada autentikasi
- Untuk production, gunakan TLS/SSL dan authentication

---

## 📝 Notes

### **Protocol Details**

**Data Format:**
```
[4 bytes: frame_size (big endian)]
[frame_size bytes: JPEG data]
```

**Example:**
```
0x00 0x00 0x3F 0xA8  → frame_size = 16296 bytes
[16296 bytes JPEG data]
```

### **Performance Tips**

1. **Optimize Resolution:** 320x240 lebih cepat dari 640x480
2. **Adjust JPEG Quality:** 40-60 balance antara size dan quality
3. **Network:** Gunakan localhost untuk latency minimal
4. **Buffer Size:** Server buffer 1 frame, minimize delay

### **Future Improvements**

- [ ] UDP protocol untuk lower latency
- [ ] WebSocket support
- [ ] Multi-client broadcasting
- [ ] Accessory toggle via UI
- [ ] Recording functionality
- [ ] Screenshot capture

---

## 📚 Additional Resources

- **Godot Docs:** https://docs.godotengine.org/
- **OpenCV Python:** https://opencv-python-tutroals.readthedocs.io/
- **TCP Networking:** https://docs.python.org/3/library/socket.html

---

## ❓ FAQ

**Q: Bisa pakai UDP seperti `udp_webcam_server.py`?**  
A: Bisa, tapi perlu handle packet loss dan reordering. TCP lebih reliable untuk localhost.

**Q: Kenapa pakai TCP bukan WebSocket?**  
A: Lebih simple, native support di Godot. WebSocket bisa diimplementasi untuk web export.

**Q: Bisa jalankan server di komputer lain?**  
A: Ya, ganti `server_host` di client ke IP server, pastikan firewall allow port 8081.

**Q: Bagaimana cara menambah accessories?**  
A: Jalankan server dengan argument `--hat`, `--ear-left`, dll. pointing ke file PNG.

---

## 📧 Support

Jika ada masalah, cek:
1. Console output Python server
2. Godot debugger output (F7)
3. Network connection dengan `telnet 127.0.0.1 8081`

---

**Happy Coding! 🚀**
