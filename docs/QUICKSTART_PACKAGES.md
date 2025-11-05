# Quick Start: Package System & Mirror Mode

## ✨ Fitur Baru

### 1. Mirror Mode (Kamera Cermin)
Kamera sekarang flip horizontal seperti selfie mode di smartphone - lebih natural!
- **Status**: Always ON
- **Untuk disable**: Edit `udp_webcam_overlay_server.py` line 13, ubah `mirror=True` → `mirror=False`

### 2. 5 Paket Aksesoris Preset
Tinggal klik tombol untuk ganti style lengkap!

## 📦 Daftar Paket

| Paket | Tema | Hat | Earrings | Piercing |
|-------|------|-----|----------|----------|
| 1 | Red & Gold | Red | Gold | Silver |
| 2 | Blue & Silver | Blue | Silver | Blue |
| 3 | Green & Diamond | Green | Diamond | Green |
| 4 | Pink & Purple | Pink | Pink | Pink |
| 5 | Rainbow Mix | Yellow | Red+Blue | Black |

## 🚀 Cara Menggunakan

### Server (Python)
```bash
cd example_gui_godot
python udp_webcam_overlay_server.py
```

Output yang benar:
```
🎨 Loading all accessory variants...
  ✓ Loaded 8 variants for hat
  ✓ Loaded 7 variants for earring_left
  ✓ Loaded 7 variants for earring_right
  ✓ Loaded 6 variants for piercing_nose

📦 Creating accessory packages...
  📦 Package 1: Red & Gold - Classic elegant look
  📦 Package 2: Blue & Silver - Cool modern style
  📦 Package 3: Green & Diamond - Fresh natural vibe
  📦 Package 4: Pink & Purple - Cute playful look
  📦 Package 5: Rainbow Mix - Bold colorful style
✨ Switched to Package 1: Red & Gold
```

### Client (Godot)
1. Buka `UDPAccessoryOverlayScene.tscn`
2. Run scene (F5)
3. Klik **"Start UDP Receiver"**
4. Klik tombol **"Package 1"** sampai **"Package 5"** untuk ganti style

## 🎨 UI Baru

Layout sekarang ada 3 panel:
1. **AccessoryPanel** (kiri) - Info UDP streaming
2. **ButtonsPanel** (tengah) - Tombol Connect/Disconnect
3. **PackagePanel** (kanan) - 5 tombol package (grid 2 kolom)

## 🔧 Troubleshooting

### Server tidak load accessories
**Cek**: Apakah ada folder `../assets/variants/`?
```bash
ls ../assets/variants/
# Harus ada: hat_*.png, earring_left_*.png, earring_right_*.png, piercing_nose_*.png
```

### Tombol package tidak muncul
**Cek**: Node `PackageButtons` ada di scene?
- Path: `MainContainer/ControlsContainer/PackagePanel/PackageButtons`
- Type: GridContainer
- Columns: 2

### Package tidak ganti saat diklik
**Cek log server**:
```
# Seharusnya muncul:
✉️ Command sent: PACKAGE:2
✨ Switched to Package 2: Blue & Silver
```

**Jika tidak muncul**:
1. Pastikan sudah connect ke server dulu
2. Check UDP port 8888 tidak di-block firewall
3. Lihat console Godot untuk error

### Mirror mode tidak jalan
**Cek**: `self.mirror = True` di line 13 `udp_webcam_overlay_server.py`
**Test**: Gerakkan tangan kanan - di video harus kiri (cermin)

## 📝 Catatan Penting

- **Tattoo belum ada**: Paket tidak include tattoo karena belum ada variants di folder
- **Variants kurang**: Jika warna tidak ada, paket pakai warna pertama yang tersedia
- **UDP = No retry**: Jika command hilang, klik tombol lagi
- **Package switching instant**: Tidak ada delay, langsung ganti

## 🎯 Next Steps

Bisa ditambahkan:
- [ ] Tombol toggle mirror mode di UI
- [ ] Preview thumbnail untuk tiap package
- [ ] Custom package editor
- [ ] Save/load package presets
- [ ] Per-client package (multi-user)

## 📚 Dokumentasi Lengkap

- **Package System**: `PACKAGE_SYSTEM.md`
- **UDP Protocol**: `UDP_IMPLEMENTATION.md`
- **Godot Integration**: `GODOT_INTEGRATION_GUIDE.md`
