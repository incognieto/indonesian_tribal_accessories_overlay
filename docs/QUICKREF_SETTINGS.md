# Quick Guide: Manual Accessory Settings

## 🎯 Quick Start (3 Steps)

### 1️⃣ Start Server
```bash
python udp_webcam_overlay_server.py --overlay --mirror
```

### 2️⃣ Connect Client
- Run Godot scene
- Click "Start UDP Receiver"

### 3️⃣ Open Settings
- Click "⚙️ Settings" button
- Adjust sliders
- Click "✅ Apply"

---

## 🎚️ Parameter Ranges

| Accessory | Parameter | Min | Max | Default |
|-----------|-----------|-----|-----|---------|
| 🎩 Hat | Scale | 0.5 | 2.0 | 1.2 |
| 🎩 Hat | Y Offset | -1.0 | 1.0 | -0.25 |
| 💎 Earring | Scale | 0.05 | 0.5 | 0.15 |
| 💎 Earring | Y Offset | 0.3 | 0.9 | 0.65 |
| 👃 Piercing | Scale | 0.03 | 0.2 | 0.08 |
| 👃 Piercing | Y Offset | 0.3 | 0.8 | 0.58 |

---

## 🔧 Common Adjustments

### **Topi Terlalu Tinggi/Rendah:**
```
Adjust: Hat Y Offset
• Lebih negatif (-) = naik ke atas
• Lebih positif (+) = turun ke bawah
```

### **Topi Terlalu Besar/Kecil:**
```
Adjust: Hat Scale
• Increase = topi lebih besar
• Decrease = topi lebih kecil
```

### **Anting Tidak Pas di Telinga:**
```
Adjust: Earring Y Offset
• Nilai lebih besar = turun
• Nilai lebih kecil = naik
```

### **Piercing Tidak Tepat di Hidung:**
```
Adjust: Piercing Y Offset
• Fine-tune posisi vertikal
• Range 0.3 - 0.8 untuk variasi wajah
```

---

## ⌨️ Controls

| Button | Action |
|--------|--------|
| ⚙️ Settings | Toggle settings panel |
| ✅ Apply | Send settings to server |
| 🔄 Reset | Reset to default values |
| ✖️ Close | Hide settings panel |

---

## 💡 Tips

✅ **Adjust while webcam running** - See changes in real-time  
✅ **Use Reset button** - Quick way back to defaults  
✅ **Combine with Packages** - Settings + package = custom look  
✅ **Small increments** - Use step 0.01 for precision  

---

## 🚨 Troubleshooting

**Q: Settings not applying?**
A: Make sure UDP is connected (click "Start UDP Receiver")

**Q: Panel not showing?**
A: Click "⚙️ Settings" button again

**Q: Want to undo changes?**
A: Click "🔄 Reset" button

---

## 📝 Notes

- Settings are **temporary** (reset when restart server)
- Changes apply to **current package** only
- Switching package will **override** manual settings
- All changes are **real-time** (instant feedback)

---

**Happy Customizing! 🎨✨**
