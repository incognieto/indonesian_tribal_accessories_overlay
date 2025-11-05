# CASCADE SELECTION GUIDE

## Fitur Pemilihan Haar Cascade

Fitur ini memungkinkan pengguna untuk **mengganti model deteksi wajah secara real-time** melalui settings panel di Godot client.

## Pilihan Cascade yang Tersedia

### 1. **Custom Trained Model** (my_custom_face_cascade.xml)
- Model hasil training sendiri menggunakan dataset wajah
- Dioptimalkan untuk deteksi wajah spesifik
- **Default selection**
- Location: `assets/cascades/my_custom_face_cascade.xml`

### 2. **Bad Face Cascade** (bad_face_cascade.xml)
- Model untuk testing/debugging
- Mendeteksi banyak false positives
- Berguna untuk melihat perbedaan kualitas model
- Location: `assets/cascades/bad_face_cascade.xml`

### 3. **Default Haar Cascade** (haarcascade_frontalface_default.xml)
- Model standar OpenCV
- Pre-trained pada dataset general
- Performa baik untuk wajah frontal
- Location: `assets/cascades/haarcascade_frontalface_default.xml`

## Cara Menggunakan

### Melalui Godot GUI:

1. **Jalankan UDP Server**:
   ```bash
   cd example_gui_godot
   python udp_webcam_overlay_server.py --load-samples
   ```

2. **Buka Godot Scene**:
   - Launch `UDPAccessoryOverlayScene.tscn`
   - Klik **"Start UDP Receiver"**

3. **Buka Settings Panel**:
   - Klik tombol **"⚙️ Settings"**

4. **Pilih Cascade**:
   - Di bagian **"Face Detection Model"**
   - Klik dropdown **"Select Haar Cascade"**
   - Pilih salah satu:
     - Custom Trained Model (my_custom)
     - Bad Face Cascade (Testing)
     - Default Haar Cascade

5. **Cascade Langsung Berubah**:
   - Perubahan diterapkan secara real-time
   - Label "Current:" akan update menampilkan cascade aktif
   - Tidak perlu restart server atau client

## Komunikasi UDP

### Command Protocol:
```
CASCADE:<cascade_filename>
```

### Contoh:
```
CASCADE:my_custom_face_cascade.xml
CASCADE:bad_face_cascade.xml
CASCADE:haarcascade_frontalface_default.xml
```

### Response dari Server:
- **Success**: `CASCADE_CHANGED:<cascade_filename>`
- **Error**: `CASCADE_ERROR:<error_message>`

## Implementasi Teknis

### 1. Godot Client (UDPAccessoryOverlayController.gd)

**Setup Cascade Options**:
```gdscript
func setup_cascade_options():
    cascade_option_button.clear()
    cascade_option_button.add_item("Custom Trained Model (my_custom)", 0)
    cascade_option_button.add_item("Bad Face Cascade (Testing)", 1)
    cascade_option_button.add_item("Default Haar Cascade", 2)
    cascade_option_button.selected = 0
```

**Handler Selection**:
```gdscript
func _on_cascade_selected(index: int):
    var cascade_file = ""
    match index:
        0: cascade_file = "my_custom_face_cascade.xml"
        1: cascade_file = "bad_face_cascade.xml"
        2: cascade_file = "haarcascade_frontalface_default.xml"
    
    webcam_manager.send_cascade_change(cascade_file)
```

### 2. UDP Manager (UDPAccessoryWebcamManager.gd)

**Send Command**:
```gdscript
func send_cascade_change(cascade_file: String):
    var command = "CASCADE:%s" % cascade_file
    send_command(command)
```

### 3. Python Server (udp_webcam_overlay_server.py)

**Handle CASCADE Command**:
```python
elif message.startswith("CASCADE:"):
    cascade_file = message[8:]  # Remove "CASCADE:" prefix
    if self.detector:
        self._change_cascade(cascade_file)
        response = f"CASCADE_CHANGED:{cascade_file}"
    self.server_socket.sendto(response.encode('utf-8'), addr)
```

**Change Cascade Method**:
```python
def _change_cascade(self, cascade_file: str):
    cascade_path = Path(self.detector.cascade_dir) / cascade_file
    
    if not cascade_path.exists():
        raise FileNotFoundError(f"Cascade not found: {cascade_file}")
    
    new_cascade = cv2.CascadeClassifier(str(cascade_path))
    
    if new_cascade.empty():
        raise ValueError(f"Invalid cascade file: {cascade_file}")
    
    # Replace cascade in detector
    self.detector.cascades['face_default'] = new_cascade
    print(f"✅ Cascade changed to {cascade_file}")
```

## Menambahkan Cascade Baru

Untuk menambahkan cascade baru ke pilihan:

### 1. Copy File Cascade:
```bash
cp your_cascade.xml assets/cascades/
```

### 2. Update Godot Controller:
Edit `UDPAccessoryOverlayController.gd`:
```gdscript
func setup_cascade_options():
    # ... existing options ...
    cascade_option_button.add_item("Your Cascade Name", 3)  # Index baru

func _on_cascade_selected(index: int):
    # ... existing cases ...
    match index:
        # ... existing cases ...
        3:  # Your cascade
            cascade_name = "your_cascade.xml"
            cascade_file = "your_cascade.xml"
```

### 3. Test:
- Restart Godot scene
- Buka Settings → Face Detection Model
- Pilih cascade baru Anda

## Troubleshooting

### ⚠️ "Cascade file not found"
**Solusi**:
- Pastikan file ada di `assets/cascades/`
- Check nama file exact (case-sensitive)
- Verifikasi path dengan: `ls assets/cascades/`

### ⚠️ "Invalid cascade file"
**Solusi**:
- File corrupt atau format salah
- Re-download atau re-train cascade
- Test dengan `cv2.CascadeClassifier(file)` di Python

### ⚠️ "Detector not initialized"
**Solusi**:
- Server belum fully loaded
- Tunggu beberapa detik setelah start server
- Restart server jika perlu

### ⚠️ Cascade berubah tapi deteksi tetap sama
**Solusi**:
- Check console log server untuk konfirmasi
- Beberapa cascade memiliki performa mirip
- Test dengan "Bad Face Cascade" untuk melihat perbedaan jelas

## Best Practices

1. **Default ke Custom Model**:
   - Gunakan custom trained model sebagai default
   - Lebih akurat untuk use case spesifik

2. **Testing dengan Bad Cascade**:
   - Gunakan bad_face_cascade.xml untuk debugging
   - Melihat perbedaan kualitas model jelas

3. **Fallback ke Default**:
   - Jika custom model gagal, fallback ke default OpenCV
   - Default cascade stable dan reliable

4. **Monitor Performance**:
   - Check FPS saat ganti cascade
   - Beberapa cascade lebih lambat dari lainnya

## Files Modified

### Godot:
- ✅ `UDPAccessoryOverlayScene.tscn` - Added cascade selection UI
- ✅ `UDPAccessoryOverlayController.gd` - Added cascade handlers
- ✅ `UDPAccessoryWebcamManager.gd` - Added send_cascade_change()

### Python:
- ✅ `udp_webcam_overlay_server.py` - Added CASCADE command handler
- ✅ Added `_change_cascade()` method

### Assets:
- ✅ `my_custom_face_cascade.xml` - Custom trained model
- ✅ `bad_face_cascade.xml` - Testing model (if exists)
- ✅ `haarcascade_frontalface_default.xml` - OpenCV default

## Example Usage

```bash
# Terminal 1: Start server
cd example_gui_godot
python udp_webcam_overlay_server.py --load-samples

# Terminal 2: Launch Godot
# Open UDPAccessoryOverlayScene.tscn
# 1. Click "Start UDP Receiver"
# 2. Click "⚙️ Settings"
# 3. Select cascade from dropdown
# 4. Watch face detection change in real-time!
```

## Summary

Fitur cascade selection memberikan **flexibility** untuk:
- ✅ Switch model deteksi wajah tanpa restart
- ✅ Compare performance berbagai cascade
- ✅ Test custom trained models vs defaults
- ✅ Optimize untuk use case spesifik

**Key Benefit**: Real-time model switching untuk testing dan optimization!
