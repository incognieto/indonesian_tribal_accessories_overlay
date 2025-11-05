# Quick Reference: Cascade Selection

## Available Cascades

1. **Custom Trained** - `my_custom_face_cascade.xml` (Default)
2. **Bad Face** - `bad_face_cascade.xml` (Testing)
3. **OpenCV Default** - `haarcascade_frontalface_default.xml`

## How to Switch Cascade

### Via Godot GUI:
1. Start server: `python udp_webcam_overlay_server.py --load-samples`
2. Open Godot → Start UDP Receiver
3. Click **"⚙️ Settings"**
4. Select cascade from **"Face Detection Model"** dropdown
5. Done! Cascade changes instantly

## UDP Command

```
CASCADE:my_custom_face_cascade.xml
CASCADE:bad_face_cascade.xml
CASCADE:haarcascade_frontalface_default.xml
```

## Testing Cascade Quality

**Good Cascade** (my_custom, default):
- ✅ Detects faces accurately
- ✅ Few false positives
- ✅ Stable tracking

**Bad Cascade** (bad_face):
- ❌ Many false positives
- ❌ Detects non-faces
- ✅ Good for testing/debugging

## Quick Test

```bash
# Terminal 1
cd example_gui_godot
python udp_webcam_overlay_server.py --load-samples

# Godot: Launch scene → Connect → Settings → Change cascade
```

Compare detection quality in real-time!
