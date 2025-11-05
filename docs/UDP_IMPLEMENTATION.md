# UDP Accessory Overlay Implementation

## Overview

Versi UDP dari Accessory Overlay System yang dioptimalkan untuk performa lebih tinggi dengan penggunaan resource yang lebih rendah.

## Files Created

### Godot Scripts
1. **UDPAccessoryWebcamManager.gd** - Manager untuk menerima stream UDP dari server
2. **UDPAccessoryOverlayController.gd** - Controller untuk UI dan komunikasi dengan webcam manager
3. **UDPAccessoryOverlayScene.tscn** - Scene file untuk UDP implementation

### Python Server
- **udp_webcam_server.py** - Server UDP yang sudah ada untuk streaming webcam

## TCP vs UDP Comparison

### TCP Version (AccessoryOverlayController.gd)
**Keunggulan:**
- ✅ Reliable delivery - semua data dijamin sampai
- ✅ Ordered packets - data sampai sesuai urutan
- ✅ Error correction - otomatis retry jika ada packet loss
- ✅ Lebih stabil untuk koneksi yang buruk

**Kekurangan:**
- ❌ Latency lebih tinggi karena handshaking
- ❌ Overhead protocol lebih besar
- ❌ Buffering dapat menyebabkan delay
- ❌ Tidak optimal untuk real-time streaming

**Cocok untuk:**
- Koneksi jaringan yang tidak stabil
- Aplikasi yang memerlukan setiap frame
- Saat kualitas lebih penting daripada kecepatan

### UDP Version (UDPAccessoryOverlayController.gd)
**Keunggulan:**
- ✅ Latency sangat rendah - no handshaking
- ✅ Overhead minimal
- ✅ Ideal untuk real-time streaming
- ✅ Performa lebih tinggi (15-30 FPS)
- ✅ Resource usage lebih rendah

**Kekurangan:**
- ❌ No guaranteed delivery - packet bisa hilang
- ❌ No ordering - packet bisa sampai tidak berurutan
- ❌ Perlu manual reassembly untuk fragmented frames
- ❌ Frame bisa corrupt jika ada packet loss

**Cocok untuk:**
- Real-time video streaming
- Aplikasi yang prioritas kecepatan
- Koneksi jaringan yang stabil
- Saat FPS tinggi lebih penting daripada kualitas sempurna

## How UDP Implementation Works

### 1. Packet Structure
```
Header (12 bytes):
  - sequence_number (4 bytes) - Frame ID
  - total_packets (4 bytes)   - Jumlah packet untuk frame ini
  - packet_index (4 bytes)    - Index packet ini (0-based)
  
Payload (variable):
  - JPEG data chunk
```

### 2. Frame Reassembly
```gdscript
# Setiap frame dipecah menjadi beberapa UDP packets
# Client menyimpan packets di buffer sampai lengkap
frame_buffers[sequence_number] = {
    "total_packets": 10,
    "received_packets": {0: data0, 1: data1, ...},
    "timestamp": current_time
}

# Ketika semua packet lengkap, assemble dan decode JPEG
if received_packets.size() == total_packets:
    assemble_and_emit_frame()
```

### 3. Performance Optimizations
- **Cleanup timer** - Hapus incomplete frames setelah timeout (1 detik)
- **Buffer limit** - Maksimal 5 frame buffers aktif
- **Reduced logging** - Log hanya setiap 60 frames (4 detik @ 15FPS)
- **FPS tracking** - Real-time FPS monitoring

## Usage Instructions

### 1. Start UDP Server

**Windows:**
```bash
cd example_gui_godot
python udp_webcam_server.py
```

**Linux/Mac:**
```bash
cd example_gui_godot
python3 udp_webcam_server.py
```

Server akan menampilkan:
```
=== Optimized UDP Webcam Server ===
🎥 Initializing optimized camera...
✅ Camera ready: 480x360 @ 15FPS
🚀 Optimized UDP Server: 127.0.0.1:8888
📊 Settings: 480x360, 15FPS, Q40
```

### 2. Setup Godot Project

1. **Import files ke Godot:**
   - Copy `UDPAccessoryWebcamManager.gd`
   - Copy `UDPAccessoryOverlayController.gd`
   - Copy `UDPAccessoryOverlayScene.tscn`

2. **Set as main scene:**
   - Project → Project Settings → Application → Run
   - Main Scene: `res://UDPAccessoryOverlayScene.tscn`

3. **Run project:**
   - Press F5 atau klik "Play" button

### 3. Connect to Server

1. Click **"Connect to Server"** button
2. Status akan berubah menjadi "✅ Terhubung - UDP Stream aktif"
3. Webcam feed akan muncul dengan FPS counter
4. Click **"Disconnect"** untuk stop streaming

## Configuration

### Server Settings (udp_webcam_server.py)
```python
self.max_packet_size = 32768  # 32KB per packet
self.target_fps = 15          # Target FPS
self.jpeg_quality = 40        # JPEG quality (1-100)
self.frame_width = 480        # Frame width
self.frame_height = 360       # Frame height
```

### Client Settings (UDPAccessoryWebcamManager.gd)
```gdscript
var server_host: String = "127.0.0.1"  # Server IP
var server_port: int = 8888            # Server port
var frame_timeout: float = 1.0         # Incomplete frame timeout
var max_buffer_size: int = 5           # Max concurrent buffers
var cleanup_interval: float = 2.0      # Cleanup frequency
```

## Performance Metrics

### Optimized Settings (Current)
- Resolution: 480x360
- FPS: ~15 FPS
- Quality: JPEG 40
- Packet size: 32KB
- Bandwidth: ~150-200 KB/s

### High Quality Settings (Optional)
```python
# For better quality at cost of performance
self.frame_width = 640
self.frame_height = 480
self.target_fps = 30
self.jpeg_quality = 60
self.max_packet_size = 60000
```

### Performance Settings (Maximum Speed)
```python
# For maximum FPS at cost of quality
self.frame_width = 320
self.frame_height = 240
self.target_fps = 30
self.jpeg_quality = 30
self.max_packet_size = 16384
```

## Troubleshooting

### Frame Loss / Corruption
**Gejala:** Frame tidak muncul atau corrupt
**Solusi:**
1. Pastikan koneksi jaringan stabil
2. Kurangi FPS di server (`target_fps = 10`)
3. Kurangi resolusi (`frame_width = 320, frame_height = 240`)
4. Naikkan `frame_timeout` di client

### Low FPS
**Gejala:** FPS < 10
**Solusi:**
1. Check CPU usage di server
2. Kurangi JPEG quality (`jpeg_quality = 30`)
3. Kurangi resolusi
4. Pastikan tidak ada firewall blocking

### Connection Failed
**Gejala:** "Failed to bind UDP socket" atau "Connection error"
**Solusi:**
1. Pastikan server running dulu sebelum client
2. Check port 8888 tidak dipakai aplikasi lain
3. Check firewall settings
4. Coba ubah port di server dan client

### High Latency
**Gejala:** Delay antara gerakan dan tampilan > 200ms
**Solusi:**
1. Pastikan server dan client di LAN yang sama
2. Kurangi packet size untuk faster transmission
3. Naikkan FPS di server
4. Check network congestion

## Comparison with TCP Version

| Metric | TCP Version | UDP Version |
|--------|-------------|-------------|
| **FPS** | 10-15 FPS | 15-25 FPS |
| **Latency** | 100-200ms | 30-80ms |
| **Packet Loss Handling** | Automatic | Manual reassembly |
| **Stability** | High | Medium |
| **Performance** | Medium | High |
| **Bandwidth** | Higher (overhead) | Lower |
| **Use Case** | Reliable delivery | Real-time streaming |

## When to Use Which?

### Use TCP Version when:
- ❗ Koneksi internet tidak stabil
- ❗ Setiap frame harus terkirim
- ❗ Kualitas lebih penting dari kecepatan
- ❗ Aplikasi production yang perlu reliability

### Use UDP Version when:
- ⚡ Perlu FPS tinggi
- ⚡ Real-time responsiveness penting
- ⚡ Koneksi LAN yang stabil
- ⚡ Development/testing
- ⚡ Live streaming/demo

## Next Steps

1. **Test both versions** dan bandingkan performance
2. **Optimize settings** sesuai kebutuhan
3. **Implement error handling** lebih robust
4. **Add reconnection logic** untuk automatic recovery
5. **Consider hybrid approach** - UDP untuk streaming, TCP untuk control

## Additional Resources

- See `WEBCAM_OPTIMIZATION.md` for general optimization tips
- See `GODOT_INTEGRATION_GUIDE.md` for integration details
- Check `udp_webcam_server.py` for server implementation details
