# 🚀 Panduan Lengkap: Menjalankan UDP Accessory Overlay

## 📋 Daftar Isi
1. [Persiapan](#persiapan)
2. [Konfigurasi Godot](#konfigurasi-godot)
3. [Menjalankan Server Python](#menjalankan-server-python)
4. [Menjalankan Client Godot](#menjalankan-client-godot)
5. [Troubleshooting](#troubleshooting)

---

## 1. Persiapan

### ✅ Prasyarat
- **Godot Engine 4.x** terinstal
- **Python 3.8+** dengan dependencies:
  ```bash
  pip install opencv-python numpy
  ```
- **Webcam** terhubung ke komputer
- **Port 8888** tidak digunakan aplikasi lain

### 📁 File-file yang Diperlukan
```
example_gui_godot/
├── UDPAccessoryOverlayScene.tscn     ← Scene untuk UDP
├── UDPAccessoryOverlayController.gd  ← Controller UDP
├── UDPAccessoryWebcamManager.gd      ← Manager UDP
├── udp_webcam_server.py              ← Python server
└── project.godot                      ← Godot project file
```

---

## 2. Konfigurasi Godot

### A. Buka Project di Godot

1. **Jalankan Godot Engine**
   ```
   Double-click Godot executable atau jalankan dari terminal
   ```

2. **Import/Open Project**
   - Klik "Import" atau "Scan"
   - Navigate ke folder: `cv_accessory_overlay/example_gui_godot/`
   - Pilih file `project.godot`
   - Klik "Import & Edit"

### B. Verifikasi File Scripts

Di Godot Editor, pastikan file-file berikut ada di FileSystem panel:

```
res://
├── UDPAccessoryOverlayScene.tscn
├── UDPAccessoryOverlayController.gd
├── UDPAccessoryWebcamManager.gd
└── project.godot
```

### C. Konfigurasi Scene

1. **Buka Scene UDP**
   - Di FileSystem panel, double-click `UDPAccessoryOverlayScene.tscn`

2. **Verifikasi Node Structure**
   ```
   UDPAccessoryOverlayUI (Control)
   ├── Background (ColorRect)
   ├── MainContainer (VBoxContainer)
   │   ├── HeaderContainer
   │   │   ├── TitleLabel
   │   │   └── SubtitleLabel
   │   ├── WebcamContainer
   │   │   └── WebcamPanel
   │   │       └── WebcamFeed (TextureRect)
   │   │           ├── StatusLabel
   │   │           ├── FPSLabel
   │   │           └── StatsLabel
   │   ├── ControlsContainer
   │   │   ├── AccessoryPanel
   │   │   └── ButtonsPanel
   │   │       └── ConnectButton
   │   │           └── DisconnectButton
   │   └── FooterContainer
   ```

3. **Set as Main Scene** (Optional)
   - Klik kanan pada `UDPAccessoryOverlayScene.tscn`
   - Pilih "Set as Main Scene"

### D. Konfigurasi Port (jika perlu)

Jika ingin menggunakan port berbeda dari 8888:

1. **Edit `UDPAccessoryWebcamManager.gd`**
   ```gdscript
   # Line 9
   var server_port: int = 8888  # Ganti dengan port yang diinginkan
   ```

2. **Edit `udp_webcam_server.py`**
   ```python
   # Line 14
   def __init__(self, host='127.0.0.1', port=8888):  # Ganti port
   ```

3. **Update Info di Scene**
   - Pilih node `ServerInfo` 
   - Di Inspector, edit property `Text`:
     ```
     Server: 127.0.0.1:XXXX  ← Ganti XXXX dengan port baru
     ```

---

## 3. Menjalankan Server Python

### A. Via Terminal (Recommended)

1. **Buka Terminal**
   ```bash
   cd /path/to/cv_accessory_overlay/example_gui_godot
   ```

2. **Jalankan Server**
   ```bash
   python udp_webcam_server.py
   ```

3. **Output yang Diharapkan**
   ```
   === Optimized UDP Webcam Server ===
   🎥 Initializing optimized camera...
   ✅ Camera ready: 480x360 @ 15FPS
   🚀 Optimized UDP Server: 127.0.0.1:8888
   📊 Settings: 480x360, 15FPS, Q40
   ```

### B. Via Batch/Shell Script (Windows/Linux)

**Windows**: Double-click `run_udp_server.bat`
```batch
@echo off
python udp_webcam_server.py
pause
```

**Linux/Mac**: 
```bash
chmod +x run_udp_server.sh
./run_udp_server.sh
```

### C. Konfigurasi Server (Advanced)

Edit `udp_webcam_server.py` untuk menyesuaikan performa:

```python
class UDPWebcamServer:
    def __init__(self, host='127.0.0.1', port=8888):
        # EDIT INI untuk performance tuning:
        self.max_packet_size = 32768   # Ukuran paket (bytes)
        self.target_fps = 15           # Target FPS
        self.jpeg_quality = 40         # Kualitas JPEG (1-100)
        self.frame_width = 480         # Lebar frame
        self.frame_height = 360        # Tinggi frame
```

**Panduan Tuning:**
- **FPS Lebih Tinggi**: Naikkan `target_fps` ke 20-30 (butuh bandwidth lebih)
- **Kualitas Lebih Baik**: Naikkan `jpeg_quality` ke 60-80 (ukuran file lebih besar)
- **Latency Rendah**: Kecilkan `max_packet_size` ke 16384 (lebih banyak paket)
- **Bandwidth Rendah**: Kecilkan resolusi atau quality

---

## 4. Menjalankan Client Godot

### A. Dari Godot Editor

1. **Pastikan Scene Terbuka**
   - `UDPAccessoryOverlayScene.tscn` harus open di editor

2. **Run Scene**
   - Tekan **F6** (Run Current Scene), atau
   - Klik tombol "Play Scene" (▶️ dengan ikon scene)

3. **Window Godot Terbuka**
   - Title: "CV Accessory Overlay System (UDP)"
   - Background biru gelap
   - Placeholder video di tengah

### B. Connect ke Server

1. **Klik Button "Start UDP Receiver"**
   - Button berubah menjadi disabled
   - Status label: "Membuka UDP socket..."

2. **Server Menerima Koneksi**
   Di terminal Python, akan muncul:
   ```
   ✅ Client: ('127.0.0.1', 54321) (Total: 1)
   📤 Frame 1: 28KB → 1 clients
   ```

3. **Video Stream Dimulai**
   - Status label hilang setelah 3 detik
   - FPS counter muncul (hijau, pojok kanan atas)
   - Stats label: "UDP: No packet loss"
   - Video dari webcam muncul dengan overlay

### C. Disconnect dari Server

1. **Klik Button "Stop Receiver"**
   - Stream berhenti
   - Placeholder kembali muncul
   - Status: "UDP socket ditutup"

2. **Di Terminal Python**:
   ```
   ❌ Client left: ('127.0.0.1', 54321)
   ```

---

## 5. Troubleshooting

### ❌ Problem: "Camera initialization failed"

**Penyebab**: Webcam tidak terdeteksi atau digunakan aplikasi lain

**Solusi**:
1. Pastikan webcam terhubung dan driver terinstal
2. Tutup aplikasi lain yang menggunakan webcam (Zoom, Teams, etc.)
3. Test webcam:
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   print("Webcam OK" if ret else "Webcam FAIL")
   ```
4. Jika menggunakan Linux, coba tanpa `CAP_DSHOW`:
   ```python
   self.camera = cv2.VideoCapture(0)  # Hapus , cv2.CAP_DSHOW
   ```

---

### ❌ Problem: "Failed to bind UDP socket"

**Penyebab**: Port 8888 sudah digunakan

**Solusi**:
1. Cek port yang digunakan:
   ```bash
   # Windows
   netstat -ano | findstr :8888
   
   # Linux/Mac
   lsof -i :8888
   ```
2. Ganti port di kedua file (server.py dan Manager.gd)
3. Atau kill process yang menggunakan port tersebut

---

### ❌ Problem: "No video appears in Godot"

**Penyebab**: Paket tidak sampai atau firewall blocking

**Solusi**:

1. **Cek Firewall**
   - Windows: Allow Python di Windows Firewall
   - Linux: `sudo ufw allow 8888/udp`

2. **Cek Logs di Godot Console**
   - Buka "Output" panel di Godot
   - Cari pesan error atau warning

3. **Test Koneksi Manual**
   ```python
   import socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.bind(('127.0.0.1', 8888))
   print("Server listening...")
   data, addr = sock.recvfrom(1024)
   print(f"Received: {data} from {addr}")
   ```

4. **Enable Debug di UDPAccessoryWebcamManager.gd**
   - Hapus comment `if total_packets_received % 30 == 0:` menjadi setiap paket
   - Lihat apakah paket diterima

---

### ⚠️ Problem: "High packet loss"

**Penyebab**: Network congestion atau buffer overflow

**Solusi**:

1. **Kurangi FPS di server**
   ```python
   self.target_fps = 10  # Turun dari 15
   ```

2. **Kurangi resolusi**
   ```python
   self.frame_width = 320
   self.frame_height = 240
   ```

3. **Kurangi kualitas JPEG**
   ```python
   self.jpeg_quality = 30  # Turun dari 40
   ```

4. **Perbesar buffer**
   ```python
   self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)  # 1MB
   ```

---

### 🐌 Problem: "Low FPS (< 10)"

**Penyebab**: CPU terbatas atau network bottleneck

**Solusi**:

1. **Optimalkan Server Settings** (lihat section 3C)

2. **Disable Debug Prints**
   - Comment out semua `print()` di Manager.gd dan server.py

3. **Upgrade Packet Size** (jika bandwidth cukup)
   ```python
   self.max_packet_size = 60000  # Lebih besar = lebih sedikit paket
   ```

4. **Check CPU Usage**
   ```bash
   # Task Manager (Windows)
   # top/htop (Linux)
   ```

---

## 📊 Monitoring & Statistics

### Di Godot Client

**FPS Label** (hijau, top-right)
```
FPS: 14.8  ← Frame rate yang diterima
```

**Stats Label** (biru, bottom-right)
```
UDP: No packet loss  ← Jika tidak ada packet hilang
Packet Loss: 23      ← Jumlah paket yang hilang
```

### Di Python Server Terminal

```
📤 Frame 61: 28KB → 1 clients  ← Setiap 4 detik
```

**Format**:
- `Frame 61`: Sequence number frame
- `28KB`: Ukuran JPEG yang dikirim
- `1 clients`: Jumlah client terhubung

---

## 🎯 Performance Benchmark

### Konfigurasi Default
```
Resolution: 480x360
FPS: 15
Quality: 40
Packet Size: 32KB
```

**Expected Performance:**
- **Latency**: 30-60ms
- **FPS Client**: 13-15
- **Bandwidth**: ~3-5 MB/s
- **Packet Loss**: 0-2%
- **CPU Usage**: 10-20%

### Konfigurasi High Quality
```
Resolution: 640x480
FPS: 25
Quality: 70
Packet Size: 60KB
```

**Expected Performance:**
- **Latency**: 50-100ms
- **FPS Client**: 20-25
- **Bandwidth**: ~8-12 MB/s
- **Packet Loss**: 2-5%
- **CPU Usage**: 20-40%

---

## 🔧 Advanced: Multiple Clients

Server mendukung multiple clients secara otomatis!

**Langkah:**
1. Jalankan 1 instance Python server
2. Buka multiple Godot windows (Run multiple instances)
3. Connect semua client

**Di server:**
```
✅ Client: ('127.0.0.1', 54321) (Total: 1)
✅ Client: ('127.0.0.1', 54322) (Total: 2)
✅ Client: ('127.0.0.1', 54323) (Total: 3)
📤 Frame 1: 28KB → 3 clients
```

---

## 📝 Summary Checklist

Sebelum menjalankan, pastikan:

- [ ] Godot 4.x terinstal
- [ ] Python dengan opencv-python terinstal
- [ ] Webcam terhubung dan berfungsi
- [ ] Port 8888 tidak digunakan
- [ ] File .gd dan .tscn ada di project
- [ ] Scene sudah di-import di Godot
- [ ] Server Python berjalan (`python udp_webcam_server.py`)
- [ ] Godot scene running (F6)
- [ ] Klik "Start UDP Receiver"
- [ ] Video stream muncul!

---

## 🎉 Selamat!

Jika semua berjalan lancar, Anda sekarang memiliki:
- ✅ Real-time webcam streaming via UDP
- ✅ Low-latency video transmission
- ✅ Frame reassembly dan packet loss handling
- ✅ Multiple client support
- ✅ Performance monitoring

**Next Steps:**
- Tambahkan face detection overlay
- Implement accessory selection
- Add recording/screenshot features
- Optimize untuk production use

Happy coding! 🚀
