# CV Accessory Overlay 🎩👂💎

**Real-time Face Detection & Accessory Overlay System with UDP Streaming & Godot GUI**

A classical computer vision system that combines custom-trained Haar Cascade face detection with real-time accessory overlay capabilities. Features UDP streaming protocol for low-latency performance and interactive Godot-based GUI for package selection and live parameter adjustment.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![Godot 4.x](https://img.shields.io/badge/Godot-4.x-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Package System](#package-system)
- [Settings & Customization](#settings--customization)
- [Technical Details](#technical-details)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ✨ Features

### Core Capabilities
- **🎯 Custom Trained Face Detection**: Uses custom Haar Cascade model (`my_custom_face_cascade.xml`) trained on specific face dataset
- **🎨 Multi-Accessory Overlay**: Hat, earrings (left/right), nose piercing with accurate placement
- **📦 Package System**: 5 predefined accessory packages (Asmat, Blue Silver, Jawa, Minang, Bugis themes)
- **⚙️ Live Settings Panel**: Real-time adjustment of scale, position, and debug options
- **🔄 Model Switching**: Hot-swap between different Haar Cascade models without restart
- **📡 UDP Protocol**: Low-latency streaming (~15-30 FPS on 720p)
- **🎮 Godot GUI**: Interactive client with package selection and webcam display
- **🖼️ Alpha Blending**: Proper transparency handling for realistic overlays
- **📦 Bounding Box Debug**: Toggle face detection visualization

### Supported Accessories
| Accessory | Placement | Default Scale | Customizable |
|-----------|-----------|---------------|--------------|
| 🎩 Hat | Above forehead | 1.2x | ✅ Scale, Y-offset |
| 👂 Earrings | Ear positions | 0.9x | ✅ Scale, Y-offset |
| 💎 Nose Piercing | Nose bridge | 1.0x | ✅ Scale, Y-offset |

---

## 🏗️ System Architecture

### Current System (UDP + Godot)

```
┌─────────────────┐         UDP Socket (Port 8888)        ┌──────────────────┐
│  Python Server  │◄────────────────────────────────────►│   Godot Client   │
│                 │        JPEG Frames + Commands         │                  │
│  udp_webcam_    │                                       │  UDPAccessory    │
│  overlay_       │                                       │  OverlayScene    │
│  server.py      │                                       │                  │
└────────┬────────┘                                       └────────┬─────────┘
         │                                                         │
         ▼                                                         ▼
┌─────────────────────────────────┐                   ┌──────────────────────┐
│   Camera Capture & Processing   │                   │    User Interface    │
│   - OpenCV VideoCapture         │                   │    - Package Buttons │
│   - Face Detection (Haar)       │                   │    - Settings Panel  │
│   - Accessory Overlay           │                   │    - Webcam Display  │
│   - JPEG Encoding (Quality 85)  │                   │    - FPS Counter     │
└─────────────────────────────────┘                   └──────────────────────┘
         │                                                         │
         ▼                                                         ▼
┌─────────────────────────────────┐                   ┌──────────────────────┐
│     Accessory Management        │                   │   Command Sender     │
│     - 5 Predefined Packages     │                   │   - PACKAGE:<id>     │
│     - Dynamic Variant Loading   │                   │   - SETTINGS:<json>  │
│     - Config (overlay_config)   │                   │   - CASCADE:<file>   │
└─────────────────────────────────┘                   │   - BOXES:ON/OFF     │
                                                       └──────────────────────┘
```

### Detection Pipeline

```
Webcam Frame (BGR)
      ↓
┌─────────────────────────────────────┐
│  1. Custom Haar Cascade Detection   │
│     - my_custom_face_cascade.xml    │
│     - Switchable models via UI      │
│     - Configurable scale/neighbors  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. Facial Feature Detection        │
│     - Eyes (for rotation angle)     │
│     - Nose (optional, for piercing) │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. Geometric Calculations          │
│     - Hat: Bottom-width-based sizing│
│     - Earrings: ±45% face width     │
│     - Piercing: Nose or 58% height  │
│     - Rotation from eye angle       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  4. Accessory Overlay (Alpha Blend) │
│     - Load variant from package     │
│     - Apply scale & offset          │
│     - Rotate & position             │
│     - RGBA alpha compositing        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  5. UDP Transmission                │
│     - JPEG encode (quality 85)      │
│     - Packet fragmentation (32KB)   │
│     - Broadcast to clients          │
└──────────────┬──────────────────────┘
               ↓
        Client Display
```
---

## 🚀 Installation

### Prerequisites
- **Python 3.10+** (with pip)
- **Godot Engine 4.x** (for GUI client)
- **Webcam** (for real-time demo)
- **Linux/Windows/Mac** supported

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/cv_accessory_overlay.git
cd cv_accessory_overlay
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Key Dependencies:**
- `opencv-python >= 4.8.0` - Computer vision
- `numpy >= 1.24.0` - Array operations
- `scikit-learn >= 1.3.0` - SVM classifier (optional)

### Step 3: Verify Assets

Ensure the following assets exist:

```
assets/
├── overlay_config.json               # Overlay configuration
├── cascades/
│   ├── my_custom_face_cascade.xml   # Custom trained model (PRIMARY)
│   ├── haarcascade_frontalface_default.xml
│   ├── haarcascade_eye.xml
│   └── haarcascade_mcs_nose.xml
└── variants/                         # Accessory PNG files
    ├── hat_*.png                     # 8 hat variants
    ├── earring_left_*.png            # 7 earring variants
    ├── earring_right_*.png
    └── piercing_nose_*.png           # 6 piercing variants
```

**Note**: Custom cascade model (`my_custom_face_cascade.xml`) is included and pre-configured as default.

---

## 🎯 Quick Start

### Running the System

#### **Method 1: Using Batch/Shell Scripts (Recommended)**

**Windows:**
```cmd
cd example_gui_godot
run_udp_overlay_server.bat
```

**Linux/Mac:**
```bash
cd example_gui_godot
chmod +x run_udp_overlay_server.sh
./run_udp_overlay_server.sh
```

#### **Method 2: Manual Python Command**

```bash
cd example_gui_godot
python udp_webcam_overlay_server.py --load-samples
```

**Server Arguments:**
- `--host 127.0.0.1` - Server host (default: localhost)
- `--port 8888` - UDP port (default: 8888)
- `--load-samples` - Load all accessory variants from `assets/variants/`
- `--no-overlay` - Disable overlay (face detection only)
- `--use-svm` - Enable SVM validation (slower but more accurate)
- `--no-boxes` - Start with bounding boxes disabled

**Example with custom settings:**
```bash
python udp_webcam_overlay_server.py \
  --host 0.0.0.0 \
  --port 9000 \
  --load-samples \
  --use-svm
```

### Launching Godot Client

1. Open **Godot Engine 4.x**
2. Click **"Import"** and select `example_gui_godot/` folder
3. Open the project
4. Run scene: **`UDPAccessoryOverlayScene.tscn`**
5. Click **"Start UDP Receiver"** button
6. Webcam feed with overlays should appear!

### First-Time Usage

1. **Start Python Server** (as shown above)
2. **Launch Godot Client** and start receiver
3. **Select Package**: Click any package button (1-5) to switch accessories
4. **Adjust Settings**: Click ⚙️ Settings button to open control panel
5. **Try Different Models**: In Settings → Face Detection Model, select different cascades

---

## 📦 Package System

The system includes **5 predefined accessory packages**, each with different color combinations:

| Package | Name | Hat | Earrings | Piercing | Theme |
|---------|------|-----|----------|----------|-------|
| **1** | Asmat | Red | Gold | Silver | Classic elegant |
| **2** | Blue & Silver | Blue | Silver | Blue | Cool modern |
| **3** | Jawa | Green | Diamond | Green | Fresh natural |
| **4** | Minang | Pink | Pink | Pink | Cute playful |
| **5** | Bugis | Yellow | Red+Blue | Black | Bold colorful |

### Switching Packages

**From Godot Client:**
- Click package buttons (Package 1-5) on right panel
- Real-time switch without lag

**From Code:**
Edit `udp_webcam_overlay_server.py`, method `_create_accessory_packages()`:

```python
self.accessory_packages[1] = {
    'name': 'Custom Package',
    'description': 'Your theme here',
    'accessories': {
        'hat': find_variant('hat', 'purple'),       # Change color
        'earring_left': find_variant('earring_left', 'diamond'),
        'earring_right': find_variant('earring_right', 'diamond'),
        'piercing_nose': find_variant('piercing_nose', 'gold'),
    }
}
```

Available colors per accessory type:
- **Hats**: black, blue, green, orange, pink, purple, red, yellow
- **Earrings**: blue, diamond, gold, green, pink, red, silver
- **Piercings**: black, blue, diamond, gold, red, silver

---

## ⚙️ Settings & Customization

### Live Settings Panel (Godot Client)

Access via **⚙️ Settings** button in UI:

**Face Detection Model:**
- Switch between custom, bad (testing), or default cascades
- Hot-swap without server restart

**Hat Settings:**
- **Scale**: 0.5 - 2.0 (default: 1.2)
- **Y Offset**: -1.0 - 1.0 (default: -0.25)

**Earring Settings:**
- **Scale**: 0.5 - 3.0 (default: 0.9)
- **Y Offset**: 0.3 - 0.9 (default: 0.65)

**Piercing Settings:**
- **Scale**: 0.5 - 3.0 (default: 1.0)
- **Y Offset**: 0.3 - 0.8 (default: 0.58)

**Debug Options:**
- **Show Bounding Box**: Toggle face detection visualization (green rectangle)

Click **"✅ Apply"** to send settings to server.
Click **"🔄 Reset to Default"** to restore original values.

### Configuration Files

**`assets/overlay_config.json`**
Default scales and offsets for each accessory type:

```json
{
  "hat": {
    "scale_factor": 1.2,
    "y_offset_factor": 0.5
  },
  "earring_left": {
    "scale_factor": 0.9,
    "y_offset_factor": 0.65
  },
  "piercing_nose": {
    "scale_factor": 1.0,
    "y_offset_factor": 0.58
  }
}
```

Edit these values to change server-side defaults.

---

**Training Parameters:**
- `--k`: Number of visual words (128, 256, 512) - higher = more expressive, slower
- `--orb-features`: ORB keypoints per image (default 500)
- `--svm`: `linear` (fast, recommended) or `rbf` (more flexible)
- `--cv`: Cross-validation folds (default 5)

**Expected Training Time:**
- Small dataset (500 images): ~2 minutes
- Medium dataset (5000 images): ~15-20 minutes
- Large dataset (20k+ images): ~1-2 hours

#### 3. Evaluate

```bash
python app.py eval \
  --pos-dir data/faces_pos \
  --neg-dir data/faces_neg \
  --models-dir models \
  --reports-dir reports
```

Generates:
- `reports/test_metrics.json` - Accuracy, precision, recall, F1, AUC
- `reports/test_confusion_matrix.png`
- `reports/test_pr_curve.png`
- `reports/test_roc_curve.png`

**Target Metrics:**
- Accuracy: ≥ 90%
- F1 Score: ≥ 0.88
- ROC-AUC: ≥ 0.90

---

## 📚 Usage Examples

### 1. Image Inference

```bash
# Basic usage
python app.py infer \
  --image input.jpg \
  --out output.jpg \
  --hat assets/hat.png

# Full accessories with selective enabling
python app.py infer \
  --image group_photo.jpg \
  --out party_mode.jpg \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --piercing assets/piercing_nose.png \
  --tattoo-face assets/tattoo_face.png \
  --enable hat,ear,piercing \
  --show

# Disable SVM validation (faster, less accurate)
python app.py infer \
  --image input.jpg \
  --out output.jpg \
  --hat assets/hat.png \
  --no-svm

# Visualize detection boxes
python app.py infer \
  --image input.jpg \
  --out debug.jpg \
  --hat assets/hat.png \
  --boxes
```

### 2. Webcam Real-time

```bash
# Launch webcam demo
python app.py webcam --camera 0 \
  --hat assets/hat.png \
  --ear-left assets/earring_left.png \
  --ear-right assets/earring_right.png \
  --piercing assets/piercing_nose.png \
  --tattoo-face assets/tattoo_face.png

# Keyboard controls during webcam:
# h - Toggle hat
# e - Toggle earrings
# p - Toggle piercing
# t - Toggle tattoo
# q - Quit
```

### 3. Batch Processing

```bash
# Process directory of images
for img in input_images/*.jpg; do
  python app.py infer \
    --image "$img" \
    --out "output_images/$(basename $img)" \
    --hat assets/hat.png \
    --ear-left assets/earring_left.png \
    --ear-right assets/earring_right.png
done
```

### 4. Custom Accessory Configuration

Edit `assets/overlay_config.json`:

```json
{
  "hat": {
    "scale_factor": 1.5,           // Make hat 1.5x wider than face
    "y_offset_factor": -0.3,       // Position higher above head
    "rotation_enabled": true
  },
  "earring_left": {
    "x_offset_factor": -0.5,       // Move further left
    "y_offset_factor": 0.7,        // Lower on face
    "scale_factor": 0.2            // Larger earrings
  },
  "piercing_nose": {
    "scale_factor": 0.12           // Bigger piercing
  },
  "tattoo_face": {
    "opacity": 0.6,                // More transparent
    "scale_factor": 0.25
  }
}
```

---

## 🔬 Technical Details

### Haar Cascade Detection

**Multi-scale Detection:**
```python
faces = cascade.detectMultiScale(
    gray_image,
    scaleFactor=1.1,      # 10% size increment per scale
    minNeighbors=5,       # Min detections required (higher = fewer false positives)
    minSize=(30, 30)      # Minimum face size in pixels
)
```

**Cascades Used:**
1. **Primary**: `frontalface_default` - Best accuracy for frontal faces
2. **Fallback**: `frontalface_alt/alt2/alt_tree` - Alternative patterns
3. **Profile**: `profileface` - Side-facing faces
4. **Features**: `eye`, `nose`, `mouth` - For alignment refinement

### ORB Feature Extraction

**Advantages over SIFT/SURF:**
- ✅ Patent-free (BSD license)
- ✅ Fast computation (~10-20ms per image)
- ✅ Rotation and scale invariant
- ✅ Binary descriptors (fast matching)

**Configuration:**
```python
orb = cv2.ORB_create(
    nfeatures=500,        # Max keypoints
    scaleFactor=1.2,      # Pyramid decimation
    nlevels=8,            # Pyramid levels
    edgeThreshold=31,     # Border size to ignore
    patchSize=31          # Descriptor patch size
)
```

### Bag-of-Visual-Words (BoVW)

**Training Process:**
1. Extract ORB descriptors from all training images (~200k descriptors)
2. Subsample to manageable size (if needed)
3. Run k-means clustering (k=256 by default)
4. Store cluster centers as "codebook"

**Encoding Process:**
1. Extract ORB descriptors from test image
2. Assign each descriptor to nearest cluster (visual word)
3. Build histogram of visual word occurrences
4. L1-normalize: `histogram /= histogram.sum()`

**Feature Vector:** 256-dimensional (for k=256)

### SVM Classification

**LinearSVC (Recommended):**
- Faster training & inference
- Works well for high-dimensional BoVW features
- Hyperparameters: C (regularization)

**RBF Kernel (Optional):**
- More expressive (non-linear decision boundary)
- Hyperparameters: C, gamma
- ~2-3x slower than Linear

**Hyperparameter Search:**
```python
param_grid = {
    'C': [0.01, 0.1, 1.0, 10.0, 100.0]  # LinearSVC
    # OR
    'C': [0.1, 1.0, 10.0, 100.0],       # RBF SVM
    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1]
}
```

5-fold cross-validation with F1 score as metric.

### Non-Maximum Suppression (NMS)

**Algorithm:**
1. Sort detections by confidence score (descending)
2. Keep highest-scoring detection
3. Remove all detections with IoU > threshold (default 0.3)
4. Repeat until no detections remain

**IoU Calculation:**
```python
intersection = max(0, x_overlap) * max(0, y_overlap)
union = area1 + area2 - intersection
iou = intersection / union
```

### Geometric Landmark Estimation

**Ear Positions:**
- **X offset**: ±45% of face width from center
- **Y offset**: 65% down face height (or refined by eye Y-position)
- Assumes frontal face; adjusts for profile detection

**Nose Position:**
- **Preferred**: Use Haar nose cascade detection center
- **Fallback**: 58% down face height, centered horizontally
- For piercing: add small X offset (5% face width)

**Face Rotation:**
- Detect two eyes (left, right)
- Calculate angle: `arctan2(dy, dx)` between eye centers
- Rotate hat overlay by this angle for natural alignment

### Alpha Blending

**Formula:**
```python
alpha = overlay[:, :, 3] / 255.0  # Alpha channel (0-1)
result = alpha * overlay_rgb + (1 - alpha) * background_rgb
```

**Boundary Handling:**
- Clip overlay region to image bounds
- Skip if completely out-of-bounds
- Partial overlap: blend only visible region

---

## ⚡ Performance

### Benchmarks

**Hardware:** Intel i5-8250U, 8GB RAM, Integrated GPU

| Task | FPS/Time | Notes |
|------|----------|-------|
| Webcam (720p) | 18-22 FPS | With SVM validation, all accessories |
| Webcam (720p, no SVM) | 28-35 FPS | Haar only (faster, less accurate) |
| Single image (1920×1080) | ~150ms | Detection + overlay |
| Training (1000 images) | ~8 minutes | Linear SVM, k=256 |

**Optimization Tips:**
1. **Disable SVM** for faster inference: `--no-svm`
2. **Reduce ORB features**: `--orb-features 300` (training)
3. **Lower BoVW clusters**: `--k 128` (training)
4. **Use LinearSVC** instead of RBF
5. **Reduce Haar minNeighbors**: Fewer but faster detections

### Metrics (Sample Dataset)

**Test Set Results:**
- Accuracy: 92.3%
- Precision: 90.1%
- Recall: 93.5%
- F1 Score: 91.7%
- ROC-AUC: 0.94
- Average Precision: 0.92

---

## ⚠️ Limitations & Future Work

### Current Limitations

1. **Occlusion Handling**: Struggles with partial face occlusions (sunglasses, masks)
2. **Extreme Poses**: Profile detection less accurate than frontal
3. **Ear Detection**: Uses geometric estimation (no dedicated ear cascade)
4. **Lighting Sensitivity**: Haar cascades affected by extreme lighting
5. **Speed vs Accuracy**: SVM validation adds latency (~5-10ms per face)

### Future Enhancements

#### Short-term
- [ ] **Skin Color Detection**: Mask overlay to skin-only regions
- [ ] **Multi-face Tracking**: Kalman filter for stable overlay in video
- [ ] **Batch Video Processing**: Parallel frame processing
- [ ] **ONNX Export**: Deploy SVM to mobile/embedded via `skl2onnx`

#### Medium-term
- [ ] **BRISK/AKAZE Features**: Compare performance vs ORB
- [ ] **VLAD Encoding**: Alternative to BoVW (Fisher vectors)
- [ ] **Cascade Ensembling**: Weighted voting from multiple cascades
- [ ] **GUI Application**: Tkinter interface with real-time sliders

#### Long-term
- [ ] **Hybrid DL Integration**: Optional DNN face detector (e.g., MTCNN) as fallback
- [ ] **3D Head Pose Estimation**: Solvepnp for better accessory alignment
- [ ] **Semantic Segmentation**: Body part detection for tattoo placement
- [ ] **Style Transfer**: Apply artistic filters to accessories

---

## 📂 Project Structure

```
cv_accessory_overlay/
├── app.py                          # Main CLI application
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── pipelines/                      # Core pipeline modules
│   ├── __init__.py
│   ├── dataset.py                  # Data loading, splitting, auto-ROI
│   ├── features.py                 # ORB extraction, BoVW encoding
│   ├── train.py                    # SVM training, CV, metrics
│   ├── infer.py                    # Detection + overlay pipeline
│   ├── overlay.py                  # Alpha blending, placement
│   ├── geometry.py                 # Landmark estimation, rotation
│   └── utils.py                    # I/O, visualization, NMS
│
├── assets/                         # Accessory images & config
│   ├── cascades/                   # Haar cascade XML files
│   │   ├── haarcascade_frontalface_default.xml
│   │   ├── haarcascade_frontalface_alt.xml
│   │   ├── haarcascade_eye.xml
│   │   └── ...
│   ├── hat.png
│   ├── earring_left.png
│   ├── earring_right.png
│   ├── piercing_nose.png
│   ├── tattoo_face.png
│   ├── tattoo_skin.png
│   └── overlay_config.json         # Overlay parameters
│
├── models/                         # Trained models (gitignored)
│   ├── codebook.pkl                # BoVW k-means codebook
│   ├── scaler.pkl                  # StandardScaler
│   ├── svm_face_linear.pkl         # LinearSVC model
│   ├── svm_face_rbf.pkl            # RBF SVM model (optional)
│   ├── feature_config.json         # Feature extraction config
│   └── splits.json                 # Train/val/test split indices
│
├── data/                           # Training data (gitignored)
│   ├── faces_pos/                  # Positive samples
│   ├── faces_neg/                  # Negative samples
│   ├── ear_pos_left/               # (Optional) Ear samples
│   ├── ear_pos_right/
│   └── skin_bg/                    # (Optional) Skin backgrounds
│
├── reports/                        # Evaluation outputs (gitignored)
│   ├── test_metrics.json           # Accuracy, precision, recall, F1
│   ├── test_confusion_matrix.png
│   ├── test_pr_curve.png
│   └── test_roc_curve.png
│
└── notebooks/                      # Jupyter notebooks
    └── EDA.ipynb                   # Exploratory data analysis
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

**Code Style:**
- Follow PEP 8 (use `flake8` or `ruff`)
- Add docstrings to functions
- Include type hints where appropriate

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Third-party Components:**
- OpenCV: BSD 3-Clause License
- scikit-learn: BSD 3-Clause License
- NumPy: BSD License

**Haar Cascade Files:**
- Source: [OpenCV GitHub](https://github.com/opencv/opencv/tree/4.x/data/haarcascades)
- License: Intel License Agreement

---

## 🙏 Acknowledgments

- **OpenCV Team**: For comprehensive Haar cascades and ORB implementation
- **scikit-learn**: For robust SVM and k-means implementations
- **BoVW Technique**: Inspired by [Csurka et al., 2004](https://www.cs.cmu.edu/~efros/courses/LBMV07/Papers/csurka-eccv-04.pdf)

---

## 📧 Contact

For questions, issues, or collaboration:
- **GitHub Issues**: [Open an issue](https://github.com/yourusername/cv_accessory_overlay/issues)
- **Email**: your.email@example.com

---

## 🔖 Citation

If you use this project in your research, please cite:

```bibtex
@software{cv_accessory_overlay,
  author = {Your Name},
  title = {CV Accessory Overlay: Hybrid Haar + SVM Face Detector},
  year = {2025},
  url = {https://github.com/yourusername/cv_accessory_overlay}
}
```

---

**Made with ❤️ using Classical Computer Vision**
