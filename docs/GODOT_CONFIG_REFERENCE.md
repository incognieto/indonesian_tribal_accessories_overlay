# 🎮 Godot Configuration Quick Reference

## 📋 Checklist Setup

### ✅ **1. Copy Files ke Godot Project**

```
YourGodotProject/
└── example_gui_godot/         # Atau nama folder lain
    ├── AccessoryWebcamManager.gd
    ├── AccessoryOverlayController.gd
    └── AccessoryOverlayScene.tscn
```

### ✅ **2. Update Script Paths**

#### **File: `AccessoryOverlayScene.tscn`**
Line 3:
```gdscript
[ext_resource type="Script" path="res://example_gui_godot/AccessoryOverlayController.gd" id="1_controller"]
```

**Sesuaikan dengan struktur project Anda:**
```gdscript
# Contoh 1: Di folder scripts/
[ext_resource type="Script" path="res://scripts/AccessoryOverlayController.gd" id="1_controller"]

# Contoh 2: Di folder scenes/overlay/
[ext_resource type="Script" path="res://scenes/overlay/AccessoryOverlayController.gd" id="1_controller"]

# Contoh 3: Tetap di example_gui_godot/
[ext_resource type="Script" path="res://example_gui_godot/AccessoryOverlayController.gd" id="1_controller"]
```

#### **File: `AccessoryOverlayController.gd`**
Line 53:
```gdscript
var webcam_script = load("res://example_gui_godot/AccessoryWebcamManager.gd")
```

**Sesuaikan dengan lokasi file:**
```gdscript
# Jika di folder scripts/
var webcam_script = load("res://scripts/AccessoryWebcamManager.gd")

# Jika di folder yang sama dengan controller
var webcam_script = load("res://example_gui_godot/AccessoryWebcamManager.gd")
```

---

## 🔌 Server Connection Settings

### **Default Configuration (Localhost)**

**File: `AccessoryWebcamManager.gd`** (Line 10-11)
```gdscript
var server_host: String = "127.0.0.1"
var server_port: int = 8081
```

### **Remote Server Configuration**

Jika Python server berjalan di komputer lain:

```gdscript
var server_host: String = "192.168.1.100"  # Ganti dengan IP server
var server_port: int = 8081
```

**Cara cek IP server:**
- Windows: `ipconfig`
- Linux/Mac: `ifconfig` atau `ip addr`

---

## 🎨 UI Customization

### **Mengubah Ukuran Webcam Display**

**File: `AccessoryOverlayScene.tscn`**

Cari node `WebcamPanel` dan ubah `custom_minimum_size`:
```gdscript
[node name="WebcamPanel" type="Panel" parent="MainContainer/WebcamContainer"]
custom_minimum_size = Vector2(640, 480)  # Default
```

**Opsi:**
- `Vector2(320, 240)` - Small
- `Vector2(640, 480)` - Medium (default)
- `Vector2(800, 600)` - Large
- `Vector2(1280, 720)` - HD

### **Mengubah Warna Background**

Cari node `Background`:
```gdscript
[node name="Background" type="ColorRect" parent="."]
color = Color(0.1, 0.12, 0.15, 1)  # Dark blue-gray
```

**Contoh warna:**
```gdscript
color = Color(0, 0, 0, 1)           # Hitam
color = Color(0.2, 0.2, 0.2, 1)     # Abu-abu gelap
color = Color(0.05, 0.1, 0.2, 1)    # Biru gelap
```

---

## 🔧 Common Modifications

### **1. Auto-Connect on Start**

Edit `AccessoryOverlayController.gd`, tambahkan di `_ready()`:

```gdscript
func _ready():
    setup_ui()
    setup_webcam_manager()
    setup_fps_timer()
    
    # Auto-connect to server
    await get_tree().create_timer(1.0).timeout
    _on_connect_pressed()
```

### **2. Hide Status Label Faster/Slower**

Edit `_on_webcam_connection_changed()`:

```gdscript
# Hide status label after 3 seconds (default)
hide_timer.wait_time = 3.0

# Hide faster (1 second)
hide_timer.wait_time = 1.0

# Hide slower (5 seconds)
hide_timer.wait_time = 5.0

# Never hide (comment out timer)
# hide_timer.start()
```

### **3. Add Custom Status Messages**

Edit `AccessoryOverlayController.gd`:

```gdscript
func show_custom_status(message: String, color: Color, duration: float = 3.0):
    status_label.text = message
    status_label.modulate = color
    status_label.visible = true
    
    var timer = Timer.new()
    timer.wait_time = duration
    timer.one_shot = true
    timer.timeout.connect(func():
        status_label.visible = false
        timer.queue_free()
    )
    add_child(timer)
    timer.start()

# Usage:
# show_custom_status("Custom message!", Color.YELLOW, 5.0)
```

### **4. Add Keyboard Shortcuts**

Tambahkan di `AccessoryOverlayController.gd`:

```gdscript
func _input(event):
    if event is InputEventKey and event.pressed:
        match event.keycode:
            KEY_C:  # C untuk Connect
                _on_connect_pressed()
            KEY_D:  # D untuk Disconnect
                _on_disconnect_pressed()
            KEY_Q:  # Q untuk Quit
                get_tree().quit()
```

---

## 📊 Performance Tuning

### **Reduce Update Frequency (Save CPU)**

Edit `AccessoryOverlayController.gd`, `setup_fps_timer()`:

```gdscript
fps_update_timer.wait_time = 0.5  # Default: Update setiap 0.5 detik
fps_update_timer.wait_time = 1.0  # Slower: Update setiap 1 detik
fps_update_timer.wait_time = 0.1  # Faster: Update setiap 0.1 detik
```

### **Disable FPS Display**

Comment out di `_ready()`:
```gdscript
# setup_fps_timer()
```

Dan hide label:
```gdscript
fps_label.visible = false
```

---

## 🐛 Debugging

### **Enable Debug Prints**

Tambahkan di `AccessoryWebcamManager.gd`, `_process_frame()`:

```gdscript
func _process_frame(jpeg_data: PackedByteArray):
    print("Received frame: %d bytes" % jpeg_data.size())  # Debug
    
    if jpeg_data.size() > 0:
        var image = Image.new()
        var load_error = image.load_jpg_from_buffer(jpeg_data)
        
        if load_error == OK:
            print("Image loaded: %dx%d" % [image.get_width(), image.get_height()])  # Debug
            # ... rest of code
```

### **Monitor Connection State**

Tambahkan di `_process()`:

```gdscript
func _process(_delta):
    if not tcp_client:
        return
    
    var status = tcp_client.get_status()
    
    # Debug print (every 60 frames)
    if Engine.get_process_frames() % 60 == 0:
        print("TCP Status: %d, Connected: %s" % [status, webcam_connected])
    
    # ... rest of code
```

---

## 📝 Node Paths Reference

Jika error "node not found", cek path berikut di `AccessoryOverlayController.gd`:

```gdscript
@onready var webcam_feed = $MainContainer/WebcamContainer/WebcamPanel/WebcamFeed
@onready var status_label = $MainContainer/WebcamContainer/WebcamPanel/WebcamFeed/StatusLabel
@onready var fps_label = $MainContainer/WebcamContainer/WebcamPanel/WebcamFeed/FPSLabel
@onready var title_label = $MainContainer/HeaderContainer/TitleLabel
@onready var subtitle_label = $MainContainer/HeaderContainer/SubtitleLabel
@onready var accessory_list = $MainContainer/ControlsContainer/AccessoryPanel/AccessoryList
@onready var connect_button = $MainContainer/ControlsContainer/ButtonsPanel/VBoxContainer/ConnectButton
@onready var disconnect_button = $MainContainer/ControlsContainer/ButtonsPanel/VBoxContainer/DisconnectButton
@onready var info_label = $MainContainer/FooterContainer/InfoLabel
```

**Cara cek path yang benar:**
1. Buka scene di Godot Editor
2. Klik node yang ingin di-reference
3. Copy node path (klik kanan → Copy Node Path)
4. Paste di `@onready var`

---

## 🚀 Advanced: Multiple Cameras

Jika ingin support multiple camera sources:

```gdscript
# AccessoryWebcamManager.gd
var server_configs = [
    {"host": "127.0.0.1", "port": 8081},  # Camera 1
    {"host": "192.168.1.100", "port": 8081},  # Camera 2
]

func connect_to_camera(camera_index: int):
    var config = server_configs[camera_index]
    server_host = config["host"]
    server_port = config["port"]
    connect_to_webcam_server()
```

---

## 📚 Scene Tree Structure

```
AccessoryOverlayUI (Control) - ROOT
├── Background (ColorRect)
└── MainContainer (VBoxContainer)
    ├── HeaderContainer (VBoxContainer)
    │   ├── TitleLabel
    │   └── SubtitleLabel
    ├── WebcamContainer (CenterContainer)
    │   └── WebcamPanel (Panel)
    │       └── WebcamFeed (TextureRect) ← Video ditampilkan di sini
    │           ├── StatusLabel
    │           └── FPSLabel
    ├── ControlsContainer (HBoxContainer)
    │   ├── AccessoryPanel (Panel)
    │   │   └── AccessoryList (VBoxContainer)
    │   └── ButtonsPanel (Panel)
    │       └── VBoxContainer
    │           ├── ConnectButton ← Koneksi ke server
    │           └── DisconnectButton ← Putus koneksi
    └── FooterContainer (HBoxContainer)
        └── InfoLabel
```

---

## ✨ Tips & Tricks

### **Tip 1: Full Screen Mode**
```gdscript
func _input(event):
    if event is InputEventKey and event.keycode == KEY_F11 and event.pressed:
        if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_WINDOWED:
            DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
        else:
            DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
```

### **Tip 2: Save Screenshot**
```gdscript
func save_screenshot():
    if webcam_feed.texture:
        var image = webcam_feed.texture.get_image()
        var timestamp = Time.get_unix_time_from_system()
        image.save_png("screenshot_%d.png" % timestamp)
        print("Screenshot saved!")
```

### **Tip 3: Reconnect on Disconnect**
```gdscript
# Auto-reconnect setelah disconnect
func _on_webcam_connection_changed(connected: bool):
    if not connected:
        # Tunggu 3 detik, lalu reconnect
        await get_tree().create_timer(3.0).timeout
        if is_inside_tree():
            _on_connect_pressed()
```

---

**Happy Godot Development! 🎮**
