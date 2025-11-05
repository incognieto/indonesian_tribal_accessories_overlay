# Accessory Package System

## Overview
Sistem paket aksesoris memungkinkan switching cepat antara kombinasi aksesoris yang telah di-preset dengan warna yang berbeda. Package system dilengkapi dengan mirror mode untuk tampilan selfie yang natural.

## Features

### 1. Mirror Mode
- **Fungsi**: Flip frame secara horizontal untuk memberikan efek mirror seperti kamera depan smartphone
- **Implementasi**: `cv2.flip(frame, 1)` di server sebelum processing
- **Status**: Enabled by default (`self.mirror = True`)

### 2. Preset Packages
Lima paket aksesoris dengan kombinasi warna berbeda:

#### Package 1: Red & Gold
- Hat: Red
- Earrings: Gold (left & right)
- Piercing: Silver

#### Package 2: Blue & Silver
- Hat: Blue
- Earrings: Silver (left & right)
- Piercing: Blue

#### Package 3: Green & Diamond
- Hat: Green
- Earrings: Diamond (left & right)
- Piercing: Green

#### Package 4: Pink & Purple
- Hat: Pink
- Earrings: Pink (left & right)
- Piercing: Pink

#### Package 5: Rainbow Mix
- Hat: Yellow
- Earrings: Red (left), Blue (right)
- Piercing: Black

## Architecture

### Server Side (Python)
File: `udp_webcam_overlay_server.py`

**Key Components:**
```python
# Instance variables
self.mirror = True  # Enable mirror mode
self.all_accessory_variants = {}  # All available variants grouped by type
self.accessory_packages = {}  # 5 preset packages
self.current_package = 1  # Active package ID

# Methods
_create_accessory_packages()  # Define 5 preset packages
_set_package(package_id)       # Switch to specific package
change_package(package_id)     # Public API for package switching
```

**Variant Loading:**
- Scans `../assets/variants/` directory
- Groups by type: hat, earring_left, earring_right, piercing_nose
- Extracts color from filename: `hat_red.png` → color='red'
- Stores as list of dicts with: name, color, path, image

**Package Creation:**
```python
def _create_accessory_packages(self):
    # Helper to find variant by color
    def find_variant(acc_type, color):
        for variant in self.all_accessory_variants.get(acc_type, []):
            if variant['color'] == color:
                return variant['image']
        # Fallback to first available
        return self.all_accessory_variants[acc_type][0]['image']
    
    # Package definitions...
    self.accessory_packages[1] = {
        'name': 'Red & Gold',
        'description': 'Classic elegant look',
        'accessories': {
            'hat': find_variant('hat', 'red'),
            'earring_left': find_variant('earring_left', 'gold'),
            # ...
        }
    }
```

**UDP Command Protocol:**
- Client sends: `"PACKAGE:1"` to `"PACKAGE:5"`
- Server responds: `"PACKAGE_SET:1:Red & Gold"` on success
- Server responds: `"PACKAGE_ERROR:Invalid package ID"` on error

### Client Side (Godot GDScript)
Files: `UDPAccessoryOverlayController.gd`, `UDPAccessoryWebcamManager.gd`, `UDPAccessoryOverlayScene.tscn`

**Controller:**
```gdscript
# UI Setup
func setup_package_buttons():
    # Creates 5 buttons in GridContainer
    # Each button shows package ID and name
    # Styled with blue theme
    # Connected to _on_package_pressed(pkg_id)

# Handler
func _on_package_pressed(package_id: int):
    # Check connection status
    # Send "PACKAGE:N" command via webcam_manager
    # Update UI status
```

**WebcamManager:**
```gdscript
func send_command(command: String):
    # Send command to server via UDP
    # Used for package switching
    var command_msg = command.to_utf8_buffer()
    udp_socket.put_packet(command_msg)
```

**Scene Layout:**
- New `PackagePanel` added to `ControlsContainer`
- `PackageButtons` GridContainer (2 columns)
- Buttons created dynamically by controller
- Blue color scheme matching UDP theme

## Usage

### Server Setup
1. Server automatically loads all variants on initialization
2. Creates 5 preset packages with different color combinations
3. Starts with Package 1 active
4. Listens for `PACKAGE:N` commands from clients

### Client Usage
1. Connect to server via "Start UDP Receiver" button
2. Click any of the 5 package buttons to switch
3. Accessories change in real-time
4. Status label shows "📦 Switching to Package N..."

### Testing
```bash
# Start server with overlay enabled
cd example_gui_godot
python udp_webcam_overlay_server.py

# In Godot:
# 1. Open UDPAccessoryOverlayScene.tscn
# 2. Run scene (F5)
# 3. Click "Start UDP Receiver"
# 4. Try different package buttons
```

## Technical Details

### Frame Processing Pipeline
```python
def _broadcast_frames(self):
    ret, frame = self.camera.read()
    
    # Step 1: Mirror mode
    if self.mirror:
        frame = cv2.flip(frame, 1)
    
    # Step 2: Face detection + overlay
    if self.use_overlay:
        enabled_accessories = []
        if 'hat' in self.accessories:
            enabled_accessories.append('hat')
        # ... map accessories to shorthand
        
        frame = self.inference_pipeline.process_image(
            frame,
            enabled_accessories=enabled_accessories,
            use_svm=self.use_svm
        )
    
    # Step 3: JPEG encoding & UDP broadcast
```

### Package Switching Flow
```
Client                          Server
  |                               |
  |---- PACKAGE:2 (UDP) -------> |
  |                              | change_package(2)
  |                              | _set_package(2)
  |                              | - Update self.accessories
  |                              | - Update inference_pipeline
  | <--- PACKAGE_SET:2:Blue... --|
  |                               |
  | (Next frames show new pkg)   |
```

## Color Detection Algorithm
```python
# Extract color from filename
def get_color_from_filename(filename):
    # hat_red.png -> 'red'
    # earring_left_gold.png -> 'gold'
    name_without_ext = filename.replace('.png', '')
    parts = name_without_ext.split('_')
    return parts[-1]  # Last part is color
```

## Limitations & Notes

1. **Variant Availability**: 
   - Package uses fallback to first variant if specific color not found
   - Ensure all colors exist in variants folder for best results

2. **Mirror Mode**:
   - Affects ALL frames (cannot disable per-client)
   - To disable: set `self.mirror = False` in `__init__`

3. **UDP Protocol**:
   - Package commands are not acknowledged with retry
   - If command lost, client must resend
   - Future: Add ACK/NACK protocol

4. **Performance**:
   - Package switching updates pipeline in-place
   - No frame drops during switch
   - Overlay applied on every frame

## Future Enhancements

- [ ] Custom package creation via Godot UI
- [ ] Package preview thumbnails
- [ ] Save/load package presets
- [ ] Per-client package selection (multi-client support)
- [ ] Command ACK/NACK protocol
- [ ] Package transition animations
- [ ] Mirror mode toggle button in UI

## Troubleshooting

### Packages not switching
- Check server logs: `✨ Switched to Package N`
- Verify connection status in Godot
- Check UDP firewall rules

### Wrong colors displayed
- Verify variant files exist in `../assets/variants/`
- Check filename format: `type_color.png`
- Review server startup logs for variant loading

### Mirror mode not working
- Check `self.mirror = True` in server init
- Verify frame processing order (mirror before overlay)
- Test with simple frame without overlay

## References
- Main server: `udp_webcam_overlay_server.py`
- Controller: `UDPAccessoryOverlayController.gd`
- Manager: `UDPAccessoryWebcamManager.gd`
- Scene: `UDPAccessoryOverlayScene.tscn`
- UDP Guide: `UDP_IMPLEMENTATION.md`
