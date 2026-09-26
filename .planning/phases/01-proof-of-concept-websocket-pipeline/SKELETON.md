# Walking Skeleton — iOS WebCam Bridge

**Phase:** 1
**Generated:** 2026-09-26

## Capability Proven End-to-End

A user can open a web page on their iOS device, grant camera permissions, and see the live video stream displayed in an OpenCV debug window on their Windows host computer.

## Architectural Decisions

|| Decision | Choice | Rationale |
||---|---|---|
|| Server framework | Flask 2.3 + Flask-SocketIO 5.3 + Eventlet 0.33 | Lightweight async WebSocket server with minimal latency, proven for real-time applications |
|| Frame processing | OpenCV 4.8 + NumPy 1.24 | High-performance C++ backend for rapid image decoding and matrix transformations |
|| Client runtime | HTML5 + JavaScript (no framework) | Zero dependencies ensures instant web page load and minimal CPU usage on iOS |
|| Data transmission | Binary WebSocket (Socket.IO) | Reduces payload by 33% compared to Base64, critical for sub-100ms latency goal |
|| Virtual camera | Deferred to Phase 2 | Phase 1 focuses on proving streaming pipeline works before adding system integration |
|| Project structure | Single-file app.py + templates/ + static/ | Simple structure for MVP, can evolve to modular structure in later phases |

## Stack Touched in Phase 1

- [x] Project scaffold (Python virtual environment, requirements.txt, basic Flask app)
- [x] Routing — Flask route serving index.html at root URL
- [x] Data flow — Camera capture → Canvas extraction → WebSocket transmission → OpenCV decoding → Debug display
- [x] UI — Mobile web page with camera permission request and connection status indicator
- [x] Deployment — Local development server (flask run on 0.0.0.0:5000)

## Out of Scope (Deferred to Later Slices)

- Virtual camera driver integration (PyVirtualCam + OBS Driver) — Phase 2
- Performance optimization (async queues, frame throttling, adaptive quality) — Phase 3
- Mobile UI controls (camera toggle, torch, resolution selector) — Phase 4
- Screen lock prevention (NoSleep.js) — Phase 4
- Auto-discovery and QR code pairing — Phase 5
- Packaging as standalone Windows executable — Phase 5
- Audio streaming — v2 requirement
- Multi-device support — v2 requirement
- Cross-platform support (macOS/Linux) — v2 requirement

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: Virtual camera integration — Expose stream as DirectShow device for third-party apps
- Phase 3: Performance optimization — Achieve sub-100ms latency with async processing and adaptive quality
- Phase 4: Mobile UI controls — Add camera toggles, torch control, resolution selection, screen lock prevention
- Phase 5: Packaging and distribution — Bundle as standalone executable with auto-discovery and documentation