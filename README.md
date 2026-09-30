# 📱 iOS WebCam Bridge

> Turn your iPhone or Android into a wireless webcam for Windows — no app install needed.

[![Version](https://img.shields.io/badge/version-v1.0.1-brightgreen)](https://github.com/vicky-2005-18/IOSWebCam/releases/tag/v1.0.1)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-SocketIO-green?logo=flask)](https://flask-socketio.readthedocs.io)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)](https://github.com/vicky-2005-18/IOSWebCam)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ✨ What It Does

Uses your phone's browser as a wireless camera and streams it to your PC as a **virtual webcam** — instantly available in Zoom, Teams, Meet, OBS, and any other app.

- **Zero app install** on your phone — just open a link in Safari/Chrome
- **Works on any phone** — iPhone, Android, any browser
- **Works from anywhere** — auto HTTPS tunnel, no same-WiFi required
- **Virtual camera output** — appears as a real webcam in all apps

---

## 🚀 Quick Start

### Option 1 — Run directly (easiest)

```bash
# Clone the repo
git clone https://github.com/vicky-2005-18/IOSWebCam.git
cd IOSWebCam

# Create virtual environment & install
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# Start!
run.bat        # Double-click this, OR:
# venv\Scripts\python.exe app.py
```

**That's it.** The terminal will show a **QR code** — scan it with your phone.

### Option 2 — Download EXE (no Python needed)

1. Download `ioswebcam.exe` from [Releases](https://github.com/vicky-2005-18/IOSWebCam/releases)
2. Double-click to run
3. Scan the QR code shown in terminal

---

## 📡 How Connection Works (Auto)

The server automatically finds the best way to connect your phone:

```
1. 🌐 Cloudflare Tunnel  →  https://xxx.trycloudflare.com   (any phone, any network)
2. 🔗 ngrok Tunnel       →  https://xxx.ngrok-free.app      (if ngrok running)
3. 📶 Local WiFi HTTPS   →  https://192.168.x.x:5000        (same network only)
```

No manual setup needed — just run and scan the QR code.

---

## 📱 Connecting Your Phone

1. Scan the **QR code** shown in terminal (or open the URL)
2. Tap **"Visit Site"** on any warning page
3. Tap **"Allow"** for camera permission
4. Tap **▶ Start Camera & Stream**
5. ✅ Your phone camera is now a webcam on your PC!

---

## 🎮 Phone Controls

| Button | Action |
|---|---|
| 📷 Switch Camera | Toggle front/back camera |
| 🪞 Flip / Mirror | Mirror the image |
| 🔦 Flashlight | Toggle torch (rear camera) |
| 30 / 60 FPS | Change frame rate |
| 480p / 720p / 1080p | Change resolution |

---

## 🖥️ Architecture

```
📱 Phone (Browser)                    💻 PC (Windows)
┌─────────────────┐                  ┌──────────────────────────┐
│  HTML5 Camera   │  WebSocket JPEG  │  Flask-SocketIO Server   │
│  MediaDevices   │ ───────────────► │  OpenCV frame processor  │
│  getUserMedia() │                  │  PyVirtualCam output     │
└─────────────────┘                  └────────────┬─────────────┘
                                                  │
                                     ┌────────────▼─────────────┐
                                     │   Virtual Webcam Driver   │
                                     │  (OBS / Unity Capture)   │
                                     └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Server | Python 3.9+, Flask, Flask-SocketIO |
| Video Processing | OpenCV, NumPy |
| Virtual Camera | PyVirtualCam (OBS / Unity Capture) |
| Tunnel | Cloudflare cloudflared, pyngrok |
| Client | HTML5, CSS3, Vanilla JavaScript |
| Transport | WebSocket binary (JPEG frames) |
| Packaging | PyInstaller (single EXE) |

---

## ⚙️ Requirements

- **OS:** Windows 10/11 (64-bit)
- **Python:** 3.9+ (only for source run)
- **Virtual Camera Driver:** [OBS Virtual Camera](https://obsproject.com) **or** [Unity Capture](https://github.com/schellingb/UnityCapture)
- **Phone:** Any modern browser (Safari on iOS, Chrome on Android)

---

## 📁 Project Structure

```
IOSWebCam/
├── app.py              # Main server (Flask + SocketIO + tunnel auto-start)
├── run.bat             # One-click Windows launcher
├── cloudflared.exe     # Cloudflare tunnel binary (Git LFS)
├── requirements.txt    # Python dependencies
├── ioswebcam.spec      # PyInstaller build config
├── templates/
│   └── index.html      # Phone web interface
├── static/
│   └── css/style.css   # Styles
└── dist/
    └── ioswebcam.exe   # Compiled standalone executable
```

---

## 📝 Documentation

- [User Guide](USER_GUIDE.md) — Full setup and usage instructions
- [Troubleshooting](TROUBLESHOOTING.md) — Common issues & fixes
- [Distribution Guide](DISTRIBUTION.md) — EXE packaging details
- [Changelog](CHANGELOG.md) — Version history and release notes

---

## 🤝 Contributing

Pull requests welcome! Feel free to open issues for bugs or feature requests.

---

## 📄 License

MIT License — free to use, modify and distribute.