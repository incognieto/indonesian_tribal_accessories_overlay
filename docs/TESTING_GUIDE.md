# Package Switching - Testing & Troubleshooting Guide

## ✅ Yang Sudah Diperbaiki

### 1. Layout GUI (FIXED)
- **Sebelum**: Button terpotong, hanya 4 terlihat
- **Sesudah**: 
  - Grid 3 kolom (bukan 2)
  - Button size: 110x55 (lebih kecil)
  - Panel width: 400px (lebih lebar)
  - Semua 5 button terlihat ✅

### 2. Package System Architecture (IMPLEMENTED)
```python
# Server side - udp_webcam_overlay_server.py
self.all_accessory_variants = {}  # Load SEMUA variants
self.accessory_packages = {}      # 5 preset packages
self.current_package = 1          # Active package

# Methods:
_create_accessory_packages()  # Define 5 packages
_set_package(id)              # Internal switch
change_package(id)            # Public API (called from UDP)
```

### 3. UDP Command Protocol (IMPLEMENTED)
```
Client → Server: "PACKAGE:2"
Server → Client: "PACKAGE_SET:2:Blue & Silver"

atau jika error:
Server → Client: "PACKAGE_ERROR:Invalid package ID"
```

### 4. Godot Integration (IMPLEMENTED)
```gdscript
# UDPAccessoryOverlayController.gd
func _on_package_pressed(package_id: int):
    webcam_manager.send_command("PACKAGE:%d" % package_id)

# UDPAccessoryWebcamManager.gd
func send_command(command: String):
    udp_socket.put_packet(command.to_utf8_buffer())
```

## 🧪 Cara Testing

### Option 1: Test dengan Godot (Recommended)

**Terminal 1 - Start Server:**
```bash
cd example_gui_godot
python udp_webcam_overlay_server.py
# Atau jika kamera tidak tersedia:
python test_package_server.py
```

**Godot Editor:**
1. Open `UDPAccessoryOverlayScene.tscn`
2. Run scene (F5)
3. Click "Start UDP Receiver"
4. Click button "Pkg 1", "Pkg 2", dst
5. **Lihat console Godot** untuk output

**Expected Output di Godot Console:**
```
=== Package button 2 pressed ===
Sending package change command...
✉️ Command sent: PACKAGE:2
✅ Package change command sent: 2
```

**Expected Output di Terminal Server:**
```
📨 Received package command: PACKAGE:2 from ('127.0.0.1', xxxxx)
🔄 Switching to package 2...
🔧 Updated pipeline accessories: ['hat', 'earring_left', 'earring_right', 'piercing_nose']
   ✓ hat: True
   ✓ earring_left: True
   ✓ earring_right: True
   ✓ piercing_nose: True
✨ Switched to Package 2: Blue & Silver
📋 Active accessories: ['hat', 'earring_left', 'earring_right', 'piercing_nose']
```

### Option 2: Test dengan Script Python

**Terminal 1:**
```bash
python test_package_server.py
```

**Terminal 2:**
```bash
# Test package 1
python test_package_switch.py 1

# Test package 2
python test_package_switch.py 2

# Test package 3
python test_package_switch.py 3
```

**Expected Output:**
```
Terminal 2 (Client):
============================================================
  Package Switch Test
============================================================
Registering with server at 127.0.0.1:8888...
Server response: REGISTERED

✅ Registered successfully

📨 Sending command: PACKAGE:2
📬 Server response: PACKAGE_SET:2:Blue & Silver

✨ Package switched to 2: Blue & Silver

Terminal 1 (Server):
📨 Received: 'REGISTER' from ('127.0.0.1', 54321)
✅ Client connected: ('127.0.0.1', 54321) (Total: 1)
📤 Sent: 'REGISTERED' to ('127.0.0.1', 54321)

📨 Received: 'PACKAGE:2' from ('127.0.0.1', 54321)
🔄 Package switch request: 2
✨ Switched to Package 2: Blue & Silver
📋 Description: Cool modern style
📤 Sent: 'PACKAGE_SET:2:Blue & Silver' to ('127.0.0.1', 54321)
```

## 🔍 Troubleshooting

### Problem: Overlay tidak berubah saat klik button

**Diagnostic Steps:**

1. **Cek Godot Console**
   - Apakah ada `=== Package button X pressed ===`?
   - Jika TIDAK → Button tidak terhubung ke signal
   - Jika YA → Lanjut step 2

2. **Cek Command Sent**
   - Apakah ada `✉️ Command sent: PACKAGE:X`?
   - Jika TIDAK → WebcamManager tidak ready / tidak connected
   - Jika YA → Lanjut step 3

3. **Cek Server Log**
   - Apakah ada `📨 Received package command`?
   - Jika TIDAK → UDP packet hilang / firewall
   - Jika YA → Lanjut step 4

4. **Cek Package Switch**
   - Apakah ada `✨ Switched to Package X`?
   - Jika TIDAK → Error di `_set_package`
   - Jika YA → Lanjut step 5

5. **Cek Accessories Update**
   - Apakah ada `🔧 Updated pipeline accessories`?
   - Jika TIDAK → Pipeline tidak di-update
   - Jika YA → **Package sudah switch!**

### Problem: Command tidak sampai ke server

**Possible Causes:**
- Godot belum connect (`get_connection_status() == false`)
- Firewall block UDP port 8888
- Server tidak jalan
- IP/Port salah

**Solutions:**
```gdscript
# Di Godot, cek:
print("Connected: ", webcam_manager.get_connection_status())

# Pastikan sudah klik "Start UDP Receiver" dulu
# Status label harus "Connected" bukan "Disconnected"
```

### Problem: Server switch package tapi overlay tetap sama

**Diagnosis:**
Ini adalah masalah **threading** atau **reference**.

**Check 1 - Threading:**
```python
# Di _set_package, pastikan update BOTH:
self.accessories = new_accessories  # ← Server accessories
self.inference_pipeline.accessories = self.accessories  # ← Pipeline accessories
```

**Check 2 - Reference:**
```python
# Verify dengan print:
print(f"Server accessories: {id(self.accessories)}")
print(f"Pipeline accessories: {id(self.inference_pipeline.accessories)}")
# Keduanya harus sama!
```

**Check 3 - Overlay Call:**
```python
# Di _broadcast_frames:
frame = self.inference_pipeline.process_image(...)
# ^ Ini harus pakai pipeline.accessories, bukan self.accessories lama
```

## 💡 Tips Debugging

### 1. Enable Verbose Logging
Edit `udp_webcam_overlay_server.py`:
```python
# Di _broadcast_frames, tambahkan:
if frame_count % 30 == 0:  # Setiap 30 frames
    print(f"🎨 Frame {frame_count}: Using accessories from package {self.current_package}")
    print(f"   Active: {list(self.accessories.keys())}")
```

### 2. Visual Indicator
Tambahkan text overlay yang menunjukkan package:
```python
# Di _broadcast_frames, setelah process_image:
cv2.putText(
    frame,
    f"Package {self.current_package}",
    (10, 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (0, 255, 0),
    2
)
```

### 3. Test Tanpa Kamera
Gunakan `test_package_server.py` untuk test protokol UDP tanpa butuh kamera

## 📊 Checklist Implementasi

Server Side:
- [x] Load semua variants di startup
- [x] Create 5 preset packages
- [x] Implement `_set_package()` method
- [x] Implement `change_package()` API
- [x] Handle UDP "PACKAGE:N" command
- [x] Update `inference_pipeline.accessories`
- [x] Add verbose logging

Client Side (Godot):
- [x] Create package buttons (5 buttons)
- [x] Style buttons dengan tema blue
- [x] Connect button signals ke handler
- [x] Implement `send_command()` in WebcamManager
- [x] Add debugging prints
- [x] Fix GridContainer layout (3 columns)

Testing:
- [x] Create `test_package_server.py` (simple server)
- [x] Create `test_package_switch.py` (client test)
- [ ] Test dengan real server + Godot ← **NEED TO DO**
- [ ] Verify overlay berubah ← **NEED TO DO**

## 🎯 Next Steps

1. **Test dengan sistem yang punya kamera**
   - Jalankan `udp_webcam_overlay_server.py`
   - Buka Godot scene dan test package switching
   - Verifikasi overlay berubah di video

2. **Jika overlay tidak berubah:**
   - Follow troubleshooting steps di atas
   - Tambahkan visual indicator (package number di frame)
   - Check log di both Godot dan Python

3. **Jika sudah berfungsi:**
   - Bisa tambahkan animasi transisi antar package
   - Bisa tambahkan preview thumbnail per package
   - Bisa tambahkan custom package editor

## 📝 Known Limitations

1. **No Camera = No Test**: Server butuh kamera untuk test overlay
   - Workaround: Pakai `test_package_server.py` untuk test command protocol

2. **WSL Camera Issue**: WSL tidak bisa akses webcam langsung
   - Workaround: Test di Windows native atau Linux dengan kamera

3. **Threading Race Condition**: Mungkin ada delay kecil antara command dan frame update
   - Normalnya 1-2 frame (< 200ms)
   - Jika lebih lama, ada masalah

4. **Package Switch Instant**: Tidak ada animasi transisi
   - Frame berikutnya langsung pakai overlay baru
   - Bisa terlihat "jumping" jika face detected

## 📚 File References

- **Server**: `udp_webcam_overlay_server.py` (Main server with camera)
- **Test Server**: `test_package_server.py` (No camera, protocol test only)
- **Test Client**: `test_package_switch.py` (Python UDP client)
- **Godot Controller**: `UDPAccessoryOverlayController.gd`
- **Godot Manager**: `UDPAccessoryWebcamManager.gd`
- **Scene**: `UDPAccessoryOverlayScene.tscn`
