# 📚 Haar Cascade Training Guide - Custom Face Detection

## 🔍 Model yang Saat Ini Digunakan

### **Pre-trained Haar Cascades (OpenCV)**
Program saat ini menggunakan **8 Haar Cascade** pre-trained dari OpenCV:

| Cascade File | Fungsi | Path |
|-------------|--------|------|
| `haarcascade_frontalface_default.xml` | **Deteksi wajah depan (UTAMA)** | `assets/cascades/` |
| `haarcascade_frontalface_alt.xml` | Alternatif wajah depan | `assets/cascades/` |
| `haarcascade_frontalface_alt2.xml` | Alternatif wajah depan 2 | `assets/cascades/` |
| `haarcascade_frontalface_alt_tree.xml` | Tree-based frontal | `assets/cascades/` |
| `haarcascade_profileface.xml` | Wajah samping | `assets/cascades/` |
| `haarcascade_eye.xml` | Deteksi mata | `assets/cascades/` |
| `haarcascade_eye_tree_eyeglasses.xml` | Mata dengan kacamata | `assets/cascades/` |
| `haarcascade_smile.xml` | Deteksi senyum | `assets/cascades/` |

### **Kode yang Meload Cascade:**
File: `pipelines/infer.py` (Line 45-75)

```python
def _load_cascades(self) -> None:
    """Load all available Haar cascades."""
    self.cascades = {}
    
    cascade_files = {
        'face_default': 'haarcascade_frontalface_default.xml',
        'face_alt': 'haarcascade_frontalface_alt.xml',
        'face_alt2': 'haarcascade_frontalface_alt2.xml',
        # ... dll
    }
    
    for name, filename in cascade_files.items():
        path = self.cascade_dir / filename  # ← LOAD DARI SINI
        if path.exists():
            cascade = cv2.CascadeClassifier(str(path))
            self.cascades[name] = cascade
```

---

## ✅ Cara Mengganti dengan Custom Cascade

### **Opsi 1: Ganti File XML Langsung (PALING MUDAH)**

1. **Train custom cascade** Anda (lihat panduan di bawah)
2. **Copy file `.xml` hasil training** ke folder:
   ```bash
   assets/cascades/
   ```
3. **Rename** file Anda menjadi salah satu nama berikut:
   ```bash
   # Ganti cascade utama
   haarcascade_frontalface_default.xml
   
   # Atau tambah sebagai alternatif
   haarcascade_frontalface_custom.xml
   ```
4. **Restart server** - akan auto-load cascade baru

**Tidak perlu ubah kode!** Program akan otomatis load semua `.xml` di folder tersebut.

---

### **Opsi 2: Tambah Cascade Baru (REKOMENDASI)**

Edit file `pipelines/infer.py`:

```python
def _load_cascades(self) -> None:
    self.cascades = {}
    
    cascade_files = {
        'face_default': 'haarcascade_frontalface_default.xml',
        'face_alt': 'haarcascade_frontalface_alt.xml',
        'face_custom': 'my_custom_face_cascade.xml',  # ← TAMBAH INI
        # ... dll
    }
```

Lalu gunakan di `udp_webcam_overlay_server.py`:

```python
# Pilih cascade yang dipakai
detector.detect_faces_haar(gray_image, cascade_name='face_custom')
```

---

## 🏋️ Cara Training Custom Haar Cascade

### **Alat yang Dibutuhkan:**

1. **OpenCV (dengan contrib modules)** - Untuk `opencv_traincascade`
2. **Python 3.8+** - Untuk preprocessing dataset
3. **Dataset Gambar:**
   - **Positive samples**: Gambar wajah (target detection)
   - **Negative samples**: Gambar tanpa wajah (background)

---

## 📂 Langkah 1: Persiapan Dataset

### **A. Download Dataset Wajah (.png/.jpg)**

**Rekomendasi Dataset:**

1. **LFW (Labeled Faces in the Wild)**
   - Link: http://vis-www.cs.umass.edu/lfw/
   - ~13,000 gambar wajah
   
2. **CelebA**
   - Link: https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html
   - ~200,000 gambar celebrity
   
3. **WIDER FACE**
   - Link: http://shuoyang1213.me/WIDERFACE/
   - ~32,000 gambar dengan bounding box annotations

4. **Custom Dataset**
   - Foto wajah Anda sendiri (minimal 500-1000 gambar)
   - Gunakan webcam atau scrape dari internet

---

### **B. Struktur Folder Dataset**

```
dataset/
├── positive/          # Gambar wajah
│   ├── face_001.png
│   ├── face_002.png
│   ├── ...
│   └── face_1000.png
│
├── negative/          # Gambar non-wajah (landscape, bangunan, dll)
│   ├── bg_001.jpg
│   ├── bg_002.jpg
│   ├── ...
│   └── bg_2000.jpg
│
├── positive.txt       # List positive samples
├── negative.txt       # List negative samples
└── cascade/           # Output folder untuk cascade
```

---

### **C. Crop Wajah dari Dataset**

Jika dataset Anda belum di-crop, gunakan script ini:

```python
# crop_faces.py
import cv2
import os
from pathlib import Path

def crop_faces(input_dir, output_dir, size=(24, 24)):
    """Crop faces from images using pre-trained cascade."""
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    count = 0
    
    for img_file in Path(input_dir).glob('*.jpg') + Path(input_dir).glob('*.png'):
        img = cv2.imread(str(img_file))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_crop, size)
            
            output_path = Path(output_dir) / f"face_{count:04d}.png"
            cv2.imwrite(str(output_path), face_resized)
            count += 1
    
    print(f"✅ Cropped {count} faces to {output_dir}")

# Jalankan
crop_faces('dataset/raw_images', 'dataset/positive', size=(50, 50))
```

---

## 📝 Langkah 2: Buat File Deskripsi

### **A. Generate `positive.txt`**

Format: `image_path num_objects x y width height`

```python
# create_positive_txt.py
from pathlib import Path

positive_dir = Path('dataset/positive')
output_file = 'dataset/positive.txt'

with open(output_file, 'w') as f:
    for idx, img_file in enumerate(sorted(positive_dir.glob('*.png'))):
        # Asumsi: wajah sudah di-crop, jadi box = seluruh gambar
        img = cv2.imread(str(img_file), 0)
        h, w = img.shape
        
        # Format: path num_objects x y width height
        line = f"{img_file} 1 0 0 {w} {h}\n"
        f.write(line)

print(f"✅ Created {output_file}")
```

Output `positive.txt`:
```
dataset/positive/face_0001.png 1 0 0 50 50
dataset/positive/face_0002.png 1 0 0 50 50
dataset/positive/face_0003.png 1 0 0 50 50
...
```

---

### **B. Generate `negative.txt`**

Format: `image_path` (satu per baris)

```python
# create_negative_txt.py
from pathlib import Path

negative_dir = Path('dataset/negative')
output_file = 'dataset/negative.txt'

with open(output_file, 'w') as f:
    for img_file in sorted(negative_dir.glob('*.jpg')):
        f.write(f"{img_file}\n")

print(f"✅ Created {output_file}")
```

Output `negative.txt`:
```
dataset/negative/bg_001.jpg
dataset/negative/bg_002.jpg
dataset/negative/bg_003.jpg
...
```

---

## 🔨 Langkah 3: Create Samples (Vec File)

Gunakan `opencv_createsamples` untuk membuat file `.vec`:

```bash
opencv_createsamples \
  -info dataset/positive.txt \
  -num 1000 \
  -w 24 \
  -h 24 \
  -vec dataset/positive.vec
```

**Parameter:**
- `-info`: Path ke `positive.txt`
- `-num`: Jumlah positive samples
- `-w`, `-h`: Ukuran sample (24x24 recommended)
- `-vec`: Output file

**Output:**
```
✅ Created dataset/positive.vec (1000 samples)
```

---

## 🚀 Langkah 4: Training Cascade

### **Command Dasar:**

```bash
opencv_traincascade \
  -data dataset/cascade \
  -vec dataset/positive.vec \
  -bg dataset/negative.txt \
  -numPos 800 \
  -numNeg 1600 \
  -numStages 20 \
  -w 24 \
  -h 24 \
  -featureType HAAR \
  -mode ALL \
  -minHitRate 0.995 \
  -maxFalseAlarmRate 0.5 \
  -precalcValBufSize 2048 \
  -precalcIdxBufSize 2048
```

### **Parameter Penting:**

| Parameter | Nilai | Deskripsi |
|-----------|-------|-----------|
| `-data` | `dataset/cascade` | Output folder |
| `-vec` | `positive.vec` | Vec file dari step 3 |
| `-bg` | `negative.txt` | List negative images |
| `-numPos` | `800` | Jumlah positive (80% dari total) |
| `-numNeg` | `1600` | Jumlah negative (2x positive) |
| `-numStages` | `20` | Jumlah stage cascade (lebih banyak = lebih akurat tapi lambat) |
| `-w`, `-h` | `24`, `24` | Ukuran sample |
| `-featureType` | `HAAR` | Jenis fitur (HAAR/LBP/HOG) |
| `-minHitRate` | `0.995` | Min detection rate per stage |
| `-maxFalseAlarmRate` | `0.5` | Max false positive per stage |

### **Training Time:**
- **CPU**: 2-7 hari (tergantung `numStages`)
- **GPU**: Tidak didukung oleh `opencv_traincascade`
- **Tips**: Mulai dengan `numStages=10` untuk testing cepat

### **Output:**
```
Training stage 0...
Training stage 1...
...
Training stage 19...
✅ cascade.xml created in dataset/cascade/
```

---

## 📦 Langkah 5: Implementasi di Program

### **A. Copy Cascade ke Project**

```bash
cp dataset/cascade/cascade.xml \
   assets/cascades/my_custom_face.xml
```

### **B. Update Code (Opsional)**

Edit `pipelines/infer.py`:

```python
cascade_files = {
    'face_default': 'haarcascade_frontalface_default.xml',
    'face_custom': 'my_custom_face.xml',  # ← Custom cascade Anda
}
```

### **C. Test Custom Cascade**

```python
# test_custom_cascade.py
import cv2

cascade = cv2.CascadeClassifier('assets/cascades/my_custom_face.xml')

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    cv2.imshow('Custom Cascade', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## ⚙️ Konfigurasi di Program yang Ada

### **File yang Perlu Diubah:**

#### **1. `pipelines/infer.py`** (Optional - jika tambah cascade baru)
```python
# Line 50-60
cascade_files = {
    'face_default': 'haarcascade_frontalface_default.xml',
    'face_custom': 'my_custom_face.xml',  # ← TAMBAH INI
}
```

#### **2. `assets/overlay_config.json`** (Tuning parameters)
```json
{
  "haar": {
    "face": {
      "scaleFactor": 1.1,    // Coba 1.05-1.3 untuk custom cascade
      "minNeighbors": 5,     // Coba 3-7 untuk balance akurasi/FPS
      "minSize": [30, 30]    // Min ukuran wajah (pixels)
    }
  }
}
```

#### **3. Tidak Perlu Ubah:**
- ❌ `udp_webcam_overlay_server.py` - sudah auto-load dari folder
- ❌ `UDPAccessoryOverlayController.gd` - client side, tidak tahu cascade
- ❌ `overlay.py` - hanya overlay, bukan detection

---

## 🎯 Quick Start - Training dengan Dataset Kecil

Untuk testing cepat (2-3 jam training):

```bash
# 1. Download 500 gambar wajah + 1000 background
# 2. Crop wajah
python crop_faces.py

# 3. Create descriptor files
python create_positive_txt.py
python create_negative_txt.py

# 4. Create samples
opencv_createsamples -info positive.txt -num 500 -w 24 -h 24 -vec positive.vec

# 5. Train (FAST VERSION)
opencv_traincascade \
  -data cascade_output \
  -vec positive.vec \
  -bg negative.txt \
  -numPos 400 \
  -numNeg 800 \
  -numStages 10 \
  -w 24 -h 24 \
  -featureType HAAR

# 6. Copy hasil
cp cascade_output/cascade.xml assets/cascades/my_face.xml

# 7. Test
python test_custom_cascade.py
```

---

## 📊 Tips Optimasi

### **Untuk Akurasi Tinggi:**
- ✅ Gunakan dataset besar (5000+ positive, 10000+ negative)
- ✅ `numStages = 20-25`
- ✅ `minHitRate = 0.999`
- ✅ Variasi pose, lighting, background

### **Untuk Training Cepat:**
- ✅ Dataset kecil (500 positive, 1000 negative)
- ✅ `numStages = 10-12`
- ✅ `minHitRate = 0.99`

### **Untuk Real-time Performance:**
- ✅ `scaleFactor = 1.3` (lebih cepat, kurang akurat)
- ✅ `minNeighbors = 3` (lebih cepat, lebih false positive)
- ✅ Ukuran window lebih besar

---

## 🔗 Resources

- **OpenCV Cascade Training Tutorial**: https://docs.opencv.org/4.x/dc/d88/tutorial_traincascade.html
- **Naotoshi Seo's Guide**: http://note.sonots.com/SciSoftware/haartraining.html
- **Dataset LFW**: http://vis-www.cs.umass.edu/lfw/
- **WIDER FACE**: http://shuoyang1213.me/WIDERFACE/

---

## ❓ FAQ

**Q: Berapa lama training?**
A: 2-7 hari untuk 20 stages dengan 1000+ samples. Gunakan `numStages=10` untuk testing cepat (2-3 jam).

**Q: Apakah bisa pakai GPU?**
A: Tidak, `opencv_traincascade` hanya CPU. Alternatif: gunakan YOLO/SSD untuk GPU-accelerated.

**Q: Cascade hasil training tidak akurat?**
A: 
- Tambah jumlah positive/negative samples
- Tingkatkan `numStages`
- Pastikan dataset berkualitas (crop rapi, lighting bagus)
- Tune `minHitRate` dan `maxFalseAlarmRate`

**Q: Error "Bad argument (Can not get new positive sample)"?**
A: `numPos` terlalu tinggi. Kurangi jadi 80% dari total samples.

---

## 📝 Summary

| Task | Command/File |
|------|--------------|
| **Ganti cascade** | Copy `.xml` ke `assets/cascades/` |
| **Konfigurasi** | Edit `haar.face` di `overlay_config.json` |
| **Training** | `opencv_traincascade` (2-7 hari) |
| **Testing** | `python test_custom_cascade.py` |
| **Auto-load** | Restart server, otomatis load dari folder |

**Kesimpulan:** Cukup **ganti file .xml** di folder `assets/cascades/`, tidak perlu ubah kode Python/Godot! 🎉
