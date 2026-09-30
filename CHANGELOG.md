# Changelog

All notable changes to iOS WebCam Bridge are documented here.

---

## [v1.0.1] — 2026-09-30

### Fixed
- Enhanced camera error handling on iOS Safari (better HTTPS detection, clearer user messages)
- HTTPS self-signed certificate now regenerates automatically when the local IP changes
- Improved SSL compatibility for Safari's strict certificate requirements (SAN + sub-825-day validity)

### Improved
- Documentation refresh: README, TROUBLESHOOTING, USER_GUIDE, and DISTRIBUTION guides all updated
- QR code display is now more resilient to console encoding issues on Windows

---

## [v1.0.0] — 2026-09-28

### Initial Public Release

#### Core Features
- **Zero-install phone client** — open a URL in Safari or Chrome, no app download needed
- **Auto HTTPS tunnel** — priority order: Cloudflare named tunnel → Cloudflare quick tunnel → ngrok → local HTTPS (self-signed cert)
- **QR code** printed in terminal at startup for easy phone scanning
- **Virtual webcam output** — frames pumped to OBS Virtual Camera or Unity Capture via PyVirtualCam
- **Real-time WebSocket streaming** — binary JPEG frames over Socket.IO, low-latency queue (maxsize=2, drops stale frames)
- **Frame telemetry** — FPS, bandwidth (Mbps), frame count, and client count broadcast every second

#### Phone Controls
- Switch front/back camera
- Mirror / flip image
- Flashlight (torch) toggle (rear camera only)
- Frame rate selection: 30 FPS / 60 FPS
- Resolution selection: 480p / 720p / 1080p

#### Architecture
- Flask + Flask-SocketIO server (threading async mode)
- OpenCV frame decode and resize pipeline
- Dedicated frame worker thread for async processing
- Self-signed SSL cert generation via `cryptography` library
- Single-file EXE packaging via PyInstaller

#### Documentation
- `README.md` — Quick start, architecture diagram, tech stack
- `USER_GUIDE.md` — Full setup and usage walkthrough
- `TROUBLESHOOTING.md` — Common issues and fixes
- `DISTRIBUTION.md` — EXE packaging and distribution guide

---

## Release Highlights by Development Phase

| Phase | Focus | Key Commits |
|-------|-------|-------------|
| Phase 1 | Server + mobile client foundation | `c1c69b9`, `ea98991` |
| Phase 2 | Virtual camera driver integration | `dc151e9` |
| Phase 3 | Performance and latency optimization | `b07f8c7` |
| Phase 4 | Mobile UI controls (camera switch, torch, mirror, FPS/res) | `207d14f` |
| Phase 5 | PyInstaller single-EXE packaging | `46d2e89` |
| Post | Auto HTTPS tunnel, Cloudflare/ngrok, SSL cert | `abd84f7` |
| Post | Docs overhaul | `ba88f44` |
| Post | Camera error handling improvements | `4f0cad9` |
