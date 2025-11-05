# UDP vs TCP Accessory Overlay - Perbandingan

## File-file yang Dibuat

### Versi TCP (Original)
- `AccessoryOverlayController.gd` - Controller utama untuk TCP
- `AccessoryWebcamManager.gd` - Manager untuk stream TCP
- `AccessoryOverlayScene.tscn` - Scene untuk TCP
- Server: `tcp_webcam_overlay_server.py` (Port 8081)

### Versi UDP (Baru)
- `UDPAccessoryOverlayController.gd` - Controller utama untuk UDP
- `UDPAccessoryWebcamManager.gd` - Manager untuk stream UDP  
- `UDPAccessoryOverlayScene.tscn` - Scene untuk UDP
- Server: `udp_webcam_server.py` (Port 8082)

## Perbedaan Utama

### TCP Version
**Kelebihan:**
- ✅ Reliable - Semua data dijamin sampai
- ✅ Terurut - Data sampai sesuai urutan
- ✅ Error checking built-in
- ✅ Cocok untuk koneksi lambat/tidak stabil

**Kekurangan:**
- ❌ Latency lebih tinggi (handshaking)
- ❌ Head-of-line blocking (paket lambat menahan yang lain)
- ❌ Overhead lebih besar

**Cara Kerja:**
1. Client connect ke server TCP
2. Server kirim header (4 bytes) untuk ukuran frame
3. Server kirim data JPEG lengkap
4. Client parse dan decode
5. Repeat untuk frame berikutnya

### UDP Version
**Kelebihan:**
- ✅ Latency rendah (no handshaking)
- ✅ Throughput lebih tinggi
- ✅ Tidak ada blocking
- ✅ Cocok untuk streaming real-time

**Kekurangan:**
- ❌ Unreliable - Paket bisa hilang
- ❌ Tidak terurut - Perlu reassembly
- ❌ Perlu implementasi packet loss handling
- ❌ Tidak cocok untuk koneksi sangat buruk

**Cara Kerja:**
1. Client bind UDP socket ke port
2. Server pecah frame JPEG ke beberapa paket (max 60KB/paket)
3. Setiap paket punya header:
   - Frame ID (4 bytes)
   - Packet number (4 bytes)  
   - Total packets (4 bytes)
   - Data size (4 bytes)
   - Payload (JPEG chunk)
4. Client terima paket, reassemble berdasarkan Frame ID
5. Setelah lengkap, decode dan tampilkan
6. Jika timeout (2 detik), buang frame incomplete

## Struktur Paket UDP

```
[Frame ID][Packet#][Total][Size][...JPEG Data...]
  4 bytes  4 bytes  4 bytes 4 bytes   Variable
```

### Contoh:
Frame JPEG 180KB dipecah menjadi 3 paket:
- Paket 0: Frame=1, Num=0, Total=3, Size=60000, Data=[0:60000]
- Paket 1: Frame=1, Num=1, Total=3, Size=60000, Data=[60000:120000]
- Paket 2: Frame=1, Num=2, Total=3, Size=60000, Data=[120000:180000]

## Konfigurasi

### TCP (AccessoryWebcamManager.gd)
```gdscript
var server_host: String = "127.0.0.1"
var server_port: int = 8081
```

### UDP (UDPAccessoryWebcamManager.gd)
```gdscript
var server_host: String = "127.0.0.1"
var server_port: int = 8082
const MAX_PACKET_SIZE = 60000
const FRAME_TIMEOUT = 2.0
```

## Cara Menggunakan

### Menjalankan Server TCP
```bash
cd example_gui_godot
python tcp_webcam_overlay_server.py
```

### Menjalankan Server UDP
```bash
cd example_gui_godot
python udp_webcam_server.py
```

### Di Godot
1. **Untuk TCP**: Buka `AccessoryOverlayScene.tscn`
2. **Untuk UDP**: Buka `UDPAccessoryOverlayScene.tscn`
3. Klik tombol "Connect"
4. Stream akan dimulai

## Monitoring & Debugging

### TCP
- Status koneksi: Connected/Disconnected
- FPS counter
- Frame receive log

### UDP
- Status socket: Bound/Closed
- FPS counter
- Packet loss counter
- Frame reassembly log
- Timeout detection

## Statistik yang Ditampilkan

### TCP
```
FPS: 25.3
Status: Connected
```

### UDP
```
FPS: 28.7
Packet Loss: 5
Status: UDP: No packet loss
```

## Kapan Menggunakan Mana?

### Gunakan TCP jika:
- Koneksi internet tidak stabil
- Semua frame harus sampai (recording, archival)
- Latency 100-200ms masih acceptable
- Kualitas lebih penting dari kecepatan

### Gunakan UDP jika:
- Koneksi internet bagus (LAN/WiFi stabil)
- Real-time lebih penting (live streaming, gaming)
- Latency harus minimal (<50ms)
- Frame drop acceptable (bisa skip frame)
- Kecepatan lebih penting dari reliability

## Performance Comparison (Estimasi)

| Metric | TCP | UDP |
|--------|-----|-----|
| Latency | 100-200ms | 20-50ms |
| FPS (LAN) | 20-25 | 25-30 |
| FPS (WiFi) | 15-20 | 20-28 |
| Packet Loss | 0% | 0-5% |
| CPU Usage | Medium | Low |
| Bandwidth | +10-20% overhead | Minimal overhead |

## Troubleshooting

### TCP
**Problem**: Frozen frames, stuttering
- Cause: Network congestion, slow connection
- Solution: Reduce frame size, lower FPS di server

### UDP
**Problem**: Many packet loss
- Cause: Network congestion, firewall
- Solution: Check firewall, reduce packet size, use TCP instead

**Problem**: Incomplete frames
- Cause: Packet reordering, loss
- Solution: Increase FRAME_TIMEOUT, reduce frame size

## Advanced: Hybrid Approach

Untuk aplikasi profesional, pertimbangkan:
- UDP untuk video stream (speed)
- TCP untuk control messages (reliability)
- Automatic fallback TCP jika UDP packet loss > 10%

## Code Example: Switching Between TCP/UDP

```gdscript
# config.gd
enum StreamMode { TCP, UDP }
var current_mode = StreamMode.UDP

# main_controller.gd
func setup_manager():
    if current_mode == StreamMode.TCP:
        webcam_manager = TCPManager.new()
    else:
        webcam_manager = UDPManager.new()
```

## Kesimpulan

Kedua protokol punya use case masing-masing:
- **TCP**: Reliable, cocok untuk production yang butuh semua frame
- **UDP**: Fast, cocok untuk demo real-time dan low-latency apps

Pilih sesuai kebutuhan aplikasi Anda!
