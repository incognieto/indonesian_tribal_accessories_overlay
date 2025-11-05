# CV Accessory Overlay - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
cd cv_accessory_overlay

# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate
# OR Windows
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Download Required Files

```bash
# Download Haar cascade XML files
python app.py fetch-cascades --dest assets/cascades

# Create sample accessory images
python app.py create-sample-data --assets-dir assets
```

### 3. Quick Test (No Training Required)

```bash
# Test Haar detection only (no SVM, faster)
python app.py infer \
  --image your_photo.jpg \
  --out result.jpg \
  --hat assets/hat.png \
  --no-svm \
  --show
```

---

## 📦 For Full Pipeline (with SVM)

### Prepare Dataset

**Option A: Use existing face crops**
```
data/
  faces_pos/     # Put face images here (100+ recommended)
  faces_neg/     # Put non-face images here (200+ recommended)
```

**Option B: Auto-generate from full images**
```bash
python app.py prepare-dataset \
  --images-dir /path/to/your/photos \
  --output-pos data/faces_pos \
  --output-neg data/faces_neg
```

### Train Model

```bash
python app.py train \
  --pos-dir data/faces_pos \
  --neg-dir data/faces_neg \
  --k 256 \
  --svm linear
```

Expected time: ~2-10 minutes (depending on dataset size)

### Run Inference

```bash
# Image
python app.py infer \
  --image input.jpg \
  --out output.jpg \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --piercing assets/piercing_nose.png

# Webcam
python app.py webcam --camera 0 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png
```

---

## 🎨 Customize Accessories

Replace PNG files in `assets/` with your own:
- **hat.png** - Must have transparent background (RGBA)
- **earring_left.png, earring_right.png** - Small, hook at top
- **piercing_nose.png** - Small stud
- **tattoo_face.png** - Semi-transparent design

Adjust positioning in `assets/overlay_config.json`:
```json
{
  "hat": {
    "scale_factor": 1.5,      // Make hat bigger
    "y_offset_factor": -0.3   // Position higher
  }
}
```

---

## ⚡ Performance Tuning

### Faster Inference
```bash
# Disable SVM validation
--no-svm

# Use fewer ORB features (during training)
--orb-features 300

# Smaller BoVW vocabulary
--k 128
```

### Better Accuracy
```bash
# More visual words
--k 512

# RBF kernel (slower but more flexible)
--svm rbf

# More training data (1000+ positive samples)
```

---

## 🐛 Troubleshooting

### "No module named 'pipelines'"
```bash
# Make sure you're in the project directory
cd cv_accessory_overlay
python app.py ...
```

### "Cascade file not found"
```bash
# Download cascades first
python app.py fetch-cascades
```

### "No faces detected"
```bash
# Try different cascade or disable SVM
python app.py infer --image input.jpg --out output.jpg --hat assets/hat.png --no-svm
```

### Low FPS on webcam
```bash
# Disable SVM for real-time performance
python app.py webcam --camera 0 --hat assets/hat.png --no-svm
```

---

## 📊 Recommended Datasets

### Public Face Datasets
- **WIDER FACE**: http://shuoyang1213.me/WIDERFACE/
- **LFW (Labeled Faces in the Wild)**: http://vis-www.cs.umass.edu/lfw/
- **CelebA**: https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html

### Background/Negative Samples
- **SUN Database**: https://groups.csail.mit.edu/vision/SUN/
- **COCO Dataset** (non-person images): https://cocodataset.org/

### Minimum Requirements
- ✅ 100 positive (face) samples
- ✅ 200 negative (non-face) samples
- ✅ Diverse lighting, poses, ages, ethnicities

---

## 🎯 Expected Performance

### Speed
- **Haar only** (--no-svm): 25-35 FPS (720p webcam)
- **Haar + SVM**: 15-22 FPS (720p webcam)
- **Single image (1920×1080)**: ~100-200ms

### Accuracy (with 1000+ training samples)
- **Accuracy**: 90-95%
- **F1 Score**: 88-92%
- **ROC-AUC**: 0.90-0.95

---

## 📝 Next Steps

1. ✅ Test with Haar-only mode (`--no-svm`)
2. ✅ Collect or download face dataset
3. ✅ Train SVM classifier
4. ✅ Evaluate on test set
5. ✅ Customize accessories
6. ✅ Deploy to production

For detailed documentation, see [README.md](README.md)

For interactive examples, see [notebooks/EDA.ipynb](notebooks/EDA.ipynb)
