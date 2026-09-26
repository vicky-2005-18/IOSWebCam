# Architecture Research

**Domain:** iOS WebCam Bridge - Real-time video streaming from iOS to Windows
**Researched:** September 26, 2026
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT: iOS Device                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │ MediaDevices API │  │    HTML5 Canvas Frame Extraction  │  │
│  │ (Camera Hardware) │──→│  (JPEG Compression / ArrayBuffer) │  │
│  └──────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ WebSocket Stream (Binary ArrayBuffer)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   RECEIVER: Windows Host PC                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │ Flask-SocketIO   │  │   NumPy / OpenCV Decoding Pipeline  │  │
│  │ Server (Async)   │──→│  (Color Space BGR → RGB Convert)   │  │
│  └──────────────────┘  └──────────────────────────────────┘  │
│                           │                                    │
│                           ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           PyVirtualCam Loopback Driver                   │  │
│  │         (DirectShow Kernel Interface)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Third-Party Desktop Applications                │
│         (Zoom / MS Teams / Google Meet / OBS Studio)         │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

|| Component | Responsibility | Typical Implementation |
||-----------|----------------|------------------------|
|| MediaDevices API | Camera hardware access and permission handling | navigator.mediaDevices.getUserMedia() |
|| HTML5 Canvas | Frame extraction at fixed intervals, JPEG compression | Offscreen canvas with drawImage() and toBlob() |
|| WebSocket Client | Binary frame transmission, bidirectional control messages | Socket.IO client with binary transmission |
|| Flask-SocketIO Server | WebSocket connection handling, frame reception | Flask app with SocketIO async mode |
|| OpenCV Decoder | Binary JPEG to NumPy array conversion, color space transformation | cv2.imdecode() and cv2.cvtColor() |
|| PyVirtualCam | Frame injection into DirectShow virtual camera loopback | Camera.send() with RGB frames |
|| OBS Virtual Camera Driver | Kernel-level DirectShow device implementation | Windows driver installed separately |

## Recommended Project Structure

```
ioswebcam/
├── app.py                    # Main Flask-SocketIO server application
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Mobile web client interface
├── static/
│   ├── css/
│   │   └── style.css        # Mobile UI styling
│   └── js/
│       └── client.js        # WebSocket client and camera logic
├── README.md                # User documentation
└── .planning/               # GSD planning artifacts
```

### Structure Rationale

- **app.py:** Single-file server for simplicity, all WebSocket and camera logic in one place
- **templates/index.html:** Mobile web client served by Flask, contains camera capture and UI controls
- **static/css/style.css:** Separate styling for mobile-first responsive design
- **static/js/client.js:** JavaScript logic for WebSocket communication and camera handling
- **requirements.txt:** Standard Python dependency management for easy installation

## Architectural Patterns

### Pattern 1: Event-Driven Asynchronous Architecture

**What:** Server uses async greenlets (Eventlet) to handle concurrent WebSocket connections without blocking
**When to use:** Real-time bidirectional communication with multiple concurrent clients
**Trade-offs:** Pros: Non-blocking, high concurrency; Cons: Debugging complexity, requires async-aware code

**Example:**
```python
from flask_socketio import SocketIO
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

@socketio.on('video_frame')
def handle_video_frame(data):
    # Process frame asynchronously
    frame = decode_frame(data)
    send_to_virtual_camera(frame)
```

### Pattern 2: Binary WebSocket Transmission

**What:** Transmit raw binary ArrayBuffers instead of Base64-encoded strings to reduce payload by 33%
**When to use:** Low-latency real-time data transmission where CPU encoding overhead matters
**Trade-offs:** Pros: Lower bandwidth, faster processing; Cons: Requires binary handling on both ends

**Example:**
```javascript
// Client side
canvas.toBlob((blob) => {
    socket.emit('video_frame', blob); // Binary transmission
}, 'image/jpeg', 0.8);
```

### Pattern 3: Kernel-Level Loopback Integration

**What:** Use virtual camera driver to inject frames directly into OS camera pipeline
**When to use:** Need to appear as native camera device to third-party applications
**Trade-offs:** Pros: Native integration, works with all video apps; Cons: Platform-specific driver dependency

**Example:**
```python
import pyvirtualcam
cam = pyvirtualcam.Camera(width=1280, height=720, fps=30, fmt=pyvirtualcam.PixelFormat.RGB)
cam.send(frame_rgb)  # Inject frame into virtual camera
cam.sleep_until_next_frame()
```

## Data Flow

### Request Flow

```
[iOS Camera Hardware]
    ↓
[MediaDevices API] → [Canvas Frame Extraction] → [JPEG Compression]
    ↓                    ↓                         ↓
[WebSocket Binary Transmission] → [Flask-SocketIO Server]
    ↓                                              ↓
[OpenCV Decoder] → [BGR to RGB Conversion] → [PyVirtualCam]
    ↓                                              ↓
[DirectShow Virtual Camera] → [Third-Party Video Apps]
```

### State Management

```
[Server State]
    ↓ (WebSocket events)
[Connection Status] ←→ [Frame Queue] → [Processing Status]
    ↓
[Virtual Camera State]
```

### Key Data Flows

1. **Video Frame Flow:** iOS camera → Canvas extraction → JPEG compression → WebSocket binary transmission → OpenCV decode → Color conversion → Virtual camera injection
2. **Control Message Flow:** Mobile UI controls → WebSocket commands → Server parameter updates → Camera stream adjustments
3. **Connection Management:** QR code scan → HTTP request → WebSocket connection → Handshake confirmation → Streaming active

## Scaling Considerations

|| Scale | Architecture Adjustments |
||-------|--------------------------|
|| 1-5 concurrent users | Single-threaded Eventlet async handles easily |
|| 5-20 concurrent users | May need connection pooling, but single process still sufficient |
|| 20+ concurrent users | Consider multiple worker processes with load balancer |

### Scaling Priorities

1. **First bottleneck:** Network bandwidth on local Wi-Fi router, not server CPU
2. **Second bottleneck:** Virtual camera driver conflicts with multiple instances (OBS limitation)

## Anti-Patterns

### Anti-Pattern 1: Base64 Encoding for Video Frames

**What people do:** Encode video frames as Base64 strings for WebSocket transmission
**Why it's wrong:** Adds 33% payload overhead, increases CPU encoding time on iOS, violates sub-100ms latency requirement
**Do this instead:** Transmit raw binary ArrayBuffers directly over WebSocket

### Anti-Pattern 2: Synchronous Frame Processing

**What people do:** Process video frames synchronously in the main thread
**Why it's wrong:** Blocks WebSocket connection handling, causes frame drops and latency spikes
**Do this instead:** Use Eventlet async greenlets for non-blocking concurrent processing

### Anti-Pattern 3: Polling for Frame Updates

**What people do:** Use HTTP polling or setInterval to check for new frames
**Why it's wrong:** High latency, inefficient network usage, poor real-time performance
**Do this instead:** Use WebSocket push-based real-time communication

## Integration Points

### External Services

|| Service | Integration Pattern | Notes |
||---------|---------------------|-------|
|| OBS Virtual Camera Driver | PyVirtualCam library | Must install driver separately, Windows-only |
|| iOS Safari Browser | HTML5 MediaDevices API | No external integration needed, browser-native |
|| Local Network Router | Wi-Fi/USB tethering | Standard network connectivity, no special config |

### Internal Boundaries

|| Boundary | Communication | Notes |
||----------|---------------|-------|
|| Client ↔ Server | WebSocket binary frames | Low-framing overhead, bidirectional control messages |
|| Server ↔ Virtual Camera | PyVirtualCam API | Direct kernel-level interface, high-performance C-types bindings |
|| UI ↔ Camera Logic | JavaScript event handlers | Tightly coupled in single HTML file for simplicity |

## Sources

- iOS WebCam Bridge Engineering Document (provided) — Complete architecture specification
- Flask-SocketIO Documentation — Async WebSocket patterns
- PyVirtualCam GitHub Repository — DirectShow integration details
- HTML5 MediaDevices API (MDN) — Browser camera access patterns
- WebSocket API (MDN) — Real-time communication best practices
- Eventlet Documentation — Async greenlet patterns for Python

---
*Architecture research for: iOS WebCam Bridge*
*Researched: September 26, 2026*