# Stack Research

**Domain:** iOS WebCam Bridge - Real-time video streaming from iOS to Windows
**Researched:** September 26, 2026
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

|| Technology | Version | Purpose | Why Recommended |
||------------|---------|---------|-----------------|
|| Python | 3.10+ | Server runtime engine | Latest stable with best async support, matches engineering spec requirements |
|| Flask-SocketIO | 5.3+ | WebSocket server framework | Eventlet async engine provides light multi-threading with minimal latency |
|| Flask | 2.3+ | Web framework foundation | Minimal overhead, integrates seamlessly with SocketIO |
|| Eventlet | 0.33+ | Async greenlet engine | Provides concurrent WebSocket handling without blocking main thread |
|| OpenCV (opencv-python) | 4.8+ | Image processing and decoding | High-performance C++ backend for rapid image decoding and matrix transformations |
|| NumPy | 1.24+ | Numerical computing for frame data | Efficient array operations for video frame manipulation |
|| PyVirtualCam | 0.6+ | Virtual camera driver interface | Direct kernel-level DirectShow integration on Windows |
|| OBS Virtual Camera Driver | Latest | System-level virtual camera | Recognized natively by Zoom, Teams, Meet, OBS Studio |

### Supporting Libraries

|| Library | Version | Purpose | When to Use |
||---------|---------|---------|-------------|
|| qrcode-terminal | 0.17+ | QR code generation for pairing | Auto-discovery and instant mobile device connection |
|| NoSleep.js | 0.12+ | iOS screen lock prevention | Prevents iOS device from sleeping during active streaming |
|| HTML5 Canvas API | Native | Frame extraction from video stream | Built-in browser API, no external dependency needed |
|| WebSocket API | Native | Real-time bidirectional communication | Built-in browser API, no external dependency needed |
|| MediaDevices API | Native | Camera hardware access | Built-in browser API, no external dependency needed |

### Development Tools

|| Tool | Purpose | Notes |
||------|---------|-------|
|| PyInstaller | 5.13+ | Package Python as standalone Windows executable | Bundles all dependencies into single .exe file |
|| venv | Native | Python virtual environment | Isolates project dependencies from system Python |
|| pip | Native | Python package manager | Install and manage Python dependencies |

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Core dependencies
pip install flask==2.3.3
pip install flask-socketio==5.3.6
pip install eventlet==0.33.3
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pyvirtualcam==0.6.1
pip install qrcode-terminal==0.17.0

# Packaging (for Phase 5)
pip install pyinstaller==5.13.2
```

**OBS Virtual Camera Driver:**
- Download from OBS Project website
- Install on Windows host system
- Required for pyvirtualcam to function

## Alternatives Considered

|| Recommended | Alternative | When to Use Alternative |
||-------------|-------------|-------------------------|
|| Flask-SocketIO + Eventlet | Tornado + Tornado-WebSocket | If you need more complex async patterns beyond WebSocket |
|| PyVirtualCam + OBS Driver | DirectShow custom driver | If you need custom driver implementation (requires C++ expertise) |
|| Binary WebSocket transmission | Base64 encoded strings | Never - adds 33% payload overhead, violates latency requirements |
|| HTML5 Canvas | WebCodecs API | When WebCodecs has broader iOS Safari support (currently experimental) |

## What NOT to Use

|| Avoid | Why | Use Instead |
||-------|-----|-------------|
|| Base64 encoding for video frames | Adds 33% payload overhead, violates sub-100ms latency requirement | Binary ArrayBuffer transmission over WebSocket |
|| Native iOS app development | Requires Apple Developer Account, App Store approval, compilation | Web-based HTML5 approach |
|| HTTP polling for video frames | High latency, inefficient network usage | WebSocket for real-time bidirectional communication |
|| Cloud-based streaming services | Adds network hops, increases latency, requires internet connectivity | Local network only processing |
|| RTP/RTSP protocols | More complex setup, not needed for local network use case | WebSocket for simplicity and low overhead |

## Stack Patterns by Variant

**If building for macOS/Linux host:**
- Use v4l2loopback instead of OBS Virtual Camera
- PyVirtualCam supports both DirectShow (Windows) and v4l2 (Linux)
- Architecture remains identical, only driver layer changes

**If requiring multiple camera sources:**
- Extend PyVirtualCam to support multiple virtual camera instances
- Requires host system with multiple OBS Virtual Camera installations
- Increases complexity significantly (defer to v2)

**If network conditions are poor (high packet loss):**
- Implement dynamic JPEG quality scaling
- Fallback to lower resolution (480p) under high latency conditions
- Add network quality monitoring and adaptive streaming

## Version Compatibility

|| Package A | Compatible With | Notes |
||-----------|-----------------|-------|
|| Python 3.10+ | All listed packages | Python 3.9+ minimum per engineering spec |
|| Flask-SocketIO 5.3+ | Flask 2.3+ | Flask 2.0+ required for async mode support |
|| PyVirtualCam 0.6+ | OBS Virtual Camera Driver | Must install OBS driver first |
|| OpenCV 4.8+ | NumPy 1.24+ | OpenCV depends on compatible NumPy version |

## Sources

- iOS WebCam Bridge Engineering Document (provided) — Complete technical specification
- OBS Project Documentation — Virtual Camera driver requirements
- Flask-SocketIO Documentation — WebSocket implementation patterns
- PyVirtualCam GitHub Repository — DirectShow integration details
- HTML5 MediaDevices API (MDN) — Browser camera access standards
- WebSocket API (MDN) — Real-time communication standards

---
*Stack research for: iOS WebCam Bridge*
*Researched: September 26, 2026*