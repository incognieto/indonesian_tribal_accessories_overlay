# Accessory Settings Manual Control - Documentation

## 📋 Overview

Sistem settings manual memungkinkan pengguna untuk mengatur parameter aksesoris (hat, earrings, piercing) secara real-time melalui GUI Godot.

---

## 🎯 Fitur yang Ditambahkan

### ✅ Parameter yang Dapat Diatur:

#### 🎩 **HAT (Topi)**
- **Scale** (Ukuran): 0.5 - 2.0 (default: 1.2)
- **Y Offset** (Ketinggian): -1.0 - 1.0 (default: -0.25)

#### 💎 **EARRINGS (Anting)**
- **Scale** (Ukuran): 0.05 - 0.5 (default: 0.15)
- **Y Offset** (Posisi Vertikal): 0.3 - 0.9 (default: 0.65)

#### 👃 **PIERCING (Tindik Hidung)**
- **Scale** (Ukuran): 0.03 - 0.2 (default: 0.08)
- **Y Offset** (Posisi Vertikal): 0.3 - 0.8 (default: 0.58)

---

## 🏗️ Arsitektur

### Flow Diagram:
```
┌─────────────────┐     Settings     ┌──────────────────────┐
│  Godot Client   │ ───────JSON────→ │  Python UDP Server   │
│  (GUI Sliders)  │                  │  (Overlay System)    │
└─────────────────┘                  └──────────────────────┘
        ↓                                       ↓
  User adjusts                          Update overlay_system
    sliders                               .config dictionary
        ↓                                       ↓
   Click "Apply"                          Apply to next frame
        ↓                                       ↓
  Send UDP packet                        Real-time effect
   "SETTINGS:{json}"                       on webcam
```

---

## 📁 File yang Ditambahkan/Dimodifikasi

### **1. File Baru:**

#### `AccessorySettingsPanel.tscn`
Scene file untuk settings panel dengan sliders dan controls.

#### `AccessorySettingsPanel.gd`
Script standalone untuk settings panel (tidak digunakan karena integrated ke scene utama).

### **2. File yang Dimodifikasi:**

#### `UDPAccessoryOverlayScene.tscn`
```gdscript
+ [node name="SettingsButton"]           # Button untuk buka settings
+ [node name="AccessorySettingsPanel"]   # Settings panel embedded
  - VBoxContainer dengan sliders untuk setiap parameter
```

#### `UDPAccessoryOverlayController.gd`
```gdscript
+ @onready var settings_button            # Reference ke button
+ @onready var settings_panel             # Reference ke panel
+ @onready var hat_scale_slider           # Slider controls
+ @onready var earring_scale_slider
+ @onready var piercing_scale_slider
+ func connect_settings_controls()        # Setup connections
+ func _on_settings_pressed()             # Toggle panel visibility
+ func _on_settings_apply()               # Send settings to server
+ func _on_settings_reset()               # Reset to defaults
+ func _on_*_changed(value)               # Update value labels
```

#### `UDPAccessoryWebcamManager.gd`
```gdscript
+ func send_settings_update(settings)     # Send JSON to server
+ func send_package_switch(package_id)    # Separate package method
```

#### `udp_webcam_overlay_server.py`
```python
+ def _apply_settings_update(settings_data)  # Apply settings to overlay
+ # Handler for "SETTINGS:{json}" command
```

---

## 🚀 Cara Penggunaan

### **1. Jalankan Server Python**
```bash
cd example_gui_godot
python udp_webcam_overlay_server.py --overlay --mirror
```

### **2. Jalankan Godot Client**
- Buka project di Godot
- Run scene `UDPAccessoryOverlayScene.tscn`
- Click "Start UDP Receiver"

### **3. Buka Settings Panel**
- Click button "⚙️ Settings"
- Panel settings akan muncul di tengah

### **4. Adjust Parameters**
- Drag sliders untuk mengatur parameter
- Values akan update real-time di label
- Lihat perubahan pada value display

### **5. Apply Settings**
- Click "✅ Apply" untuk mengirim ke server
- Settings akan diterapkan pada frame berikutnya
- Status "Settings applied!" akan muncul

### **6. Reset (Opsional)**
- Click "🔄 Reset" untuk kembali ke default values
- Tidak perlu apply lagi, hanya reset slider values

---

## 📊 Format Data Settings

### **JSON Structure yang Dikirim:**

```json
{
    "hat": {
        "scale_factor": 1.5,
        "y_offset_factor": -0.3
    },
    "earring": {
        "scale_factor": 0.2,
        "y_offset_factor": 0.7
    },
    "piercing": {
        "scale_factor": 0.1,
        "y_offset_factor": 0.6
    }
}
```

### **UDP Command Format:**
```
SETTINGS:{"hat":{"scale_factor":1.5,"y_offset_factor":-0.3},...}
```

---

## 🔧 Implementasi Detail

### **Godot Side (Client):**

```gdscript
# Collect settings from sliders
var settings_data = {
    "hat": {
        "scale_factor": hat_scale_slider.value,
        "y_offset_factor": hat_y_offset_slider.value
    },
    "earring": {
        "scale_factor": earring_scale_slider.value,
        "y_offset_factor": earring_y_offset_slider.value
    },
    "piercing": {
        "scale_factor": piercing_scale_slider.value,
        "y_offset_factor": piercing_y_offset_slider.value
    }
}

# Send via UDP
webcam_manager.send_settings_update(settings_data)
```

### **Python Side (Server):**

```python
# Parse command
if message.startswith("SETTINGS:"):
    settings_json = message[9:]
    settings_data = json.loads(settings_json)
    
    # Apply to overlay system
    self._apply_settings_update(settings_data)

# Update config
def _apply_settings_update(self, settings_data):
    for acc_type, settings in settings_data.items():
        config_key = self._get_config_key(acc_type)
        self.overlay_system.config[config_key].update(settings)
```

---

## 🎨 UI Layout

```
┌─────────────────────────────────────────┐
│         ⚙️ Accessory Settings          │
├─────────────────────────────────────────┤
│  🎩 HAT (Topi)                         │
│  Scale:                           1.20 │
│  ╍╍╍╍╍╍╍╍╍╍╍╍╍○╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍  │
│  Y Offset:                       -0.25 │
│  ╍╍○╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍  │
├─────────────────────────────────────────┤
│  💎 EARRINGS (Anting)                  │
│  Scale:                           0.15 │
│  ╍╍╍○╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍  │
│  Y Offset:                        0.65 │
│  ╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍○╍╍╍╍╍╍╍╍╍╍╍╍╍╍  │
├─────────────────────────────────────────┤
│  👃 PIERCING (Tindik)                  │
│  Scale:                           0.08 │
│  ╍○╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍  │
│  Y Offset:                        0.58 │
│  ╍╍╍╍╍╍╍╍╍╍╍○╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍  │
├─────────────────────────────────────────┤
│  [ ✅ Apply ]  [ 🔄 Reset ]           │
│  [    ✖️ Close     ]                   │
└─────────────────────────────────────────┘
```

---

## ⚡ Performance Notes

- **Real-time Update:** Settings diterapkan pada frame berikutnya setelah apply
- **No Lag:** UDP connectionless protocol = minimal latency
- **Smooth Sliding:** Value labels update instantly saat drag slider
- **Persistent:** Settings tetap aktif sampai di-reset atau diubah lagi

---

## 🐛 Troubleshooting

### **Settings tidak diterapkan:**
- ✅ Pastikan sudah connect ke server (UDP connected)
- ✅ Check console untuk error messages
- ✅ Verify JSON format valid

### **Panel tidak muncul:**
- ✅ Check SettingsButton ada dan connected
- ✅ Verify settings_panel reference valid

### **Slider tidak bekerja:**
- ✅ Check slider connections di connect_settings_controls()
- ✅ Verify value labels di-update

---

## 📈 Future Enhancements

Potential improvements:
- [ ] Save/Load presets
- [ ] Per-accessory visibility toggle
- [ ] Color picker untuk variant selection
- [ ] Rotation angle control
- [ ] Opacity control untuk tattoos
- [ ] X offset controls untuk positioning
- [ ] Live preview mode (update without apply button)
- [ ] Keyboard shortcuts untuk quick adjustments

---

## ✨ Kesimpulan

**Fitur settings manual** memberikan kontrol penuh kepada pengguna untuk:
- ✅ Adjust ukuran aksesoris secara presisi
- ✅ Fine-tune posisi vertical untuk setiap aksesoris
- ✅ Reset ke default dengan satu click
- ✅ Real-time preview tanpa restart server
- ✅ Kombinasi dengan package system untuk flexibility maksimal

**Status:** ✅ Fully Implemented & Tested
**Integration:** Seamless dengan existing package system
**Platform:** Cross-platform (Windows, Linux, macOS)

---

**Last Updated:** November 5, 2025
**Version:** 1.0.0
