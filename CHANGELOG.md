# Changelog

All notable changes to iOS WebCam Bridge are documented here.

---

## [v1.1.0] — 2026-09-30

### Added
- **Interactive Connection Mode Menu**: Direct selection between High-Speed Local Wi-Fi / USB (0 delay, 60 FPS) and Cloudflare Tunnel (Remote networks).
- **Latency Preset Selector in Web UI**: Real-time choice between Zero Delay (Realtime), Balanced, and Ultra Sharp modes.
- **Root Certificate Download Endpoint (`/cert`)**: Enables easy one-tap certificate profile installation for iOS devices.
- **Native 1080p @ 60 FPS Virtual Camera Engine**: High-definition DirectShow output with sharp resampling.

### Fixed
- **3–5 Second Delay Eliminated**: Removed artificial sleep delays, reduced frame queue to 1, and enabled low-latency local Wi-Fi / USB streaming.
- **Dropped Frames Fix**: Eliminated the artificial interval drop-guard and upgraded to `requestVideoFrameCallback` for synchronized capture.
- **iOS Safari SSL Setup**: Simplified the setup instructions to just 2 taps inside Safari.

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
