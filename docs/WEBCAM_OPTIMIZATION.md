# 🎥 Panduan Optimasi Webcam untuk FPS Tinggi

## ⚡ Cara Mengatasi Webcam yang Patah-Patah

### **Solusi 1: Turunkan Resolusi (PALING EFEKTIF)**

```bash
# TERCEPAT - 320x240 (sangat smooth, ~40-50 FPS)
python app.py webcam --camera 0 \
  --width 320 --height 240 \
  --hat assets/hat.png \
  --no-svm

# CEPAT - 640x480 (smooth, ~30-40 FPS)
python app.py webcam --camera 0 \
  --width 640 --height 480 \
  --hat assets/hat.png \
  --no-svm

# SEDANG - 1280x720 (moderate, ~20-25 FPS)
python app.py webcam --camera 0 \
  --width 1280 --height 720 \
  --hat assets/hat.png \
  --no-svm

# LAMBAT - 1920x1080 (mungkin patah-patah, ~10-15 FPS)
python app.py webcam --camera 0 \
  --width 1920 --height 1080 \
  --hat assets/hat.png \
  --no-svm
```

---

### **Solusi 2: Gunakan Mode `--no-svm` (WAJIB untuk Smooth)**

```bash
# TANPA --no-svm (lambat, ~10-15 FPS)
python app.py webcam --camera 0 --hat assets/hat.png

# DENGAN --no-svm (cepat, ~30-40 FPS)
python app.py webcam --camera 0 --hat assets/hat.png --no-svm
```

**Penjelasan:**
- `--no-svm` = hanya pakai Haar Cascade (deteksi cepat)
- Tanpa flag = pakai Haar + ORB + BoVW + SVM (deteksi akurat tapi lambat)

---

### **Solusi 3: Atur FPS Kamera**

```bash
# Set FPS ke 30 (default)
python app.py webcam --camera 0 --fps 30 --width 640 --height 480 --no-svm

# Set FPS ke 60 (jika kamera support)
python app.py webcam --camera 0 --fps 60 --width 640 --height 480 --no-svm

# Set FPS ke 15 (untuk komputer lemah)
python app.py webcam --camera 0 --fps 15 --width 640 --height 480 --no-svm
```

---

## 🚀 Konfigurasi Rekomendasi

### **Untuk Komputer Lambat / Laptop**
```bash
python app.py webcam --camera 0 \
  --width 320 --height 240 \
  --fps 30 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --no-svm
```
**Expected FPS:** ~40-50 FPS ⚡

---

### **Untuk Komputer Standar**
```bash
python app.py webcam --camera 0 \
  --width 640 --height 480 \
  --fps 30 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --piercing assets/piercing_nose.png \
  --no-svm
```
**Expected FPS:** ~30-35 FPS ✅

---

### **Untuk Komputer Kencang**
```bash
python app.py webcam --camera 0 \
  --width 1280 --height 720 \
  --fps 30 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --piercing assets/piercing_nose.png \
  --tattoo-face assets/tattoo_face.png \
  --no-svm
```
**Expected FPS:** ~20-25 FPS 🎯

---

### **Untuk Akurasi Maksimal (tapi lambat)**
```bash
python app.py webcam --camera 0 \
  --width 640 --height 480 \
  --fps 30 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --piercing assets/piercing_nose.png
# Catatan: TANPA --no-svm (akan gunakan SVM validation)
```
**Expected FPS:** ~15-18 FPS (tapi deteksi lebih akurat)

---

## 📊 Perbandingan Performa

| Resolusi    | Mode      | Expected FPS | Kualitas Visual | Rekomendasi        |
|-------------|-----------|--------------|-----------------|---------------------|
| 320x240     | --no-svm  | 40-50 FPS    | ⭐⭐            | Laptop lemah        |
| 640x480     | --no-svm  | 30-35 FPS    | ⭐⭐⭐          | **Rekomendasi**     |
| 1280x720    | --no-svm  | 20-25 FPS    | ⭐⭐⭐⭐        | PC menengah         |
| 1920x1080   | --no-svm  | 10-15 FPS    | ⭐⭐⭐⭐⭐      | PC kencang          |
| 640x480     | with SVM  | 15-18 FPS    | ⭐⭐⭐⭐        | Akurasi maksimal    |
| 1280x720    | with SVM  | 8-12 FPS     | ⭐⭐⭐⭐⭐      | Demo/presentasi     |

---

## 🎮 Kontrol Keyboard

Saat webcam berjalan, gunakan keyboard:

- **`h`** - Toggle topi (hat) on/off
- **`e`** - Toggle anting (earrings) on/off
- **`p`** - Toggle tindik hidung (piercing) on/off
- **`t`** - Toggle tato wajah (tattoo) on/off
- **`q`** - Keluar (quit)

---

## 🔧 Tips Tambahan

### **1. Cek Hardware Kamera**
```bash
# List semua kamera yang tersedia
ls /dev/video*

# Jika punya 2 kamera, coba --camera 1
python app.py webcam --camera 1 --width 640 --height 480 --no-svm
```

### **2. Nonaktifkan Program Lain**
- Tutup browser (Chrome, Firefox)
- Tutup aplikasi video call (Zoom, Teams)
- Tutup software editing berat

### **3. Gunakan Lebih Sedikit Aksesori**
```bash
# Hanya topi (paling cepat)
python app.py webcam --camera 0 \
  --hat assets/hat.png \
  --enable hat \
  --no-svm

# Topi + anting saja
python app.py webcam --camera 0 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --enable hat,ear \
  --no-svm
```

### **4. Update Driver Kamera**
- Linux: `sudo apt update && sudo apt install v4l-utils`
- Windows: Update driver di Device Manager
- Mac: Update macOS ke versi terbaru

---

## 🐛 Troubleshooting

### **Masih Patah-Patah Setelah Optimasi?**

1. **Coba resolusi paling rendah:**
   ```bash
   python app.py webcam --camera 0 --width 320 --height 240 --hat assets/hat.png --no-svm
   ```

2. **Cek apakah kamera support resolusi yang diminta:**
   ```bash
   # Install v4l-utils (Linux)
   sudo apt install v4l-utils
   
   # Cek resolusi yang didukung
   v4l2-ctl --list-formats-ext -d /dev/video0
   ```

3. **Test tanpa aksesori overlay:**
   Modifikasi `pipelines/infer.py` untuk skip overlay processing

4. **Gunakan kamera eksternal USB:**
   Kamera built-in laptop biasanya lebih lambat

---

## 📝 Command Lengkap (Copy-Paste Ready)

### **Tercepat & Paling Smooth:**
```bash
python app.py webcam --camera 0 --width 320 --height 240 --fps 30 --hat assets/hat.png --ear-left assets/earring_left.png --ear-right assets/earring_right.png --no-svm
```

### **Balance Speed & Quality:**
```bash
python app.py webcam --camera 0 --width 640 --height 480 --fps 30 --hat assets/hat.png --ear-left assets/earring_left.png --ear-right assets/earring_right.png --piercing assets/piercing_nose.png --no-svm
```

### **Best Quality (jika PC kuat):**
```bash
python app.py webcam --camera 0 --width 1280 --height 720 --fps 30 --hat assets/hat.png --ear-left assets/earring_left.png --ear-right assets/earring_right.png --piercing assets/piercing_nose.png --tattoo-face assets/tattoo_face.png --no-svm
```

---

**Selamat mencoba! 🎉**
