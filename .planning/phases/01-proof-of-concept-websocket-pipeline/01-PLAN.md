# Phase 1: Proof of Concept & WebSocket Pipeline - Plan

**Phase:** 1 - Proof of Concept & WebSocket Pipeline
**Status:** Ready for execution
**Created:** 2026-09-26
**Mode:** mvp

## Phase Goal

Establish basic camera capture, WebSocket binary transmission, and OpenCV frame decoding pipeline with debug visualization. This phase delivers a working end-to-end video stream from iOS device to Windows host, displaying received frames in an OpenCV debug window.

## User Story

As a developer, I want to see a live video stream from my iOS device displayed on my Windows computer, so that I can verify the core streaming pipeline works before adding virtual camera integration and performance optimizations.

## Success Criteria

1. User can open web page on iOS device and grant camera permissions
2. Video frames are captured at 720p @ 30 FPS and transmitted as binary WebSocket messages
3. Server receives and decodes frames, displaying them in OpenCV debug window
4. End-to-end pipeline demonstrates working video stream from iOS to Windows host

## Requirements Coverage

- CAM-01: User can grant camera permissions on iOS device via browser prompt
- CAM-03: System captures video at 720p resolution @ 30 FPS by default
- CAM-04: System extracts video frames from HTML5 Canvas at fixed 33ms intervals
- VID-01: System transmits video frames as binary ArrayBuffers over WebSocket (not Base64)
- VID-02: WebSocket connection establishes bidirectional communication between iOS and Windows host
- VID-03: Server receives binary frame data and decodes using OpenCV
- UI-01: Mobile web interface displays connection status and controls

## Implementation Decisions

From CONTEXT.md:
- Error handling: Clear error message with retry button for camera permission denial
- Debug display: cv2.imshow window always visible for Phase 1 (removed in later phases)
- Mobile UI: Simple status indicator (Connected/Disconnected) with frame counter
- Technical: Flask-SocketIO with Eventlet, binary WebSocket transmission, canvas extraction at 33ms intervals

## Tasks

### 01-01: Set up Python virtual environment and Flask-SocketIO server on Windows host

**Type:** infrastructure
**Description:** Create Python development environment with required dependencies and basic Flask-SocketIO server structure.

**Steps:**
1. Create Python virtual environment: `python -m venv venv`
2. Activate virtual environment and install dependencies:
   - `pip install flask==2.3.3`
   - `pip install flask-socketio==5.3.6`
   - `pip install eventlet==0.33.3`
   - `pip install opencv-python==4.8.1.78`
   - `pip install numpy==1.24.3`
3. Create basic app.py structure:
   - Import Flask, Flask-SocketIO
   - Configure app with async_mode='eventlet'
   - Bind to 0.0.0.0:5000 for local network access
4. Create requirements.txt for dependency tracking
5. Test server startup: `python app.py` should start without errors

**Verification:**
- Virtual environment activates successfully
- All dependencies install without conflicts
- Server starts and binds to port 5000
- Server logs indicate Flask-SocketIO running with Eventlet

**Files created/modified:**
- `venv/` (virtual environment directory)
- `requirements.txt`
- `app.py` (basic Flask-SocketIO server skeleton)

---

### 01-02: Develop mobile web client with HTML5 camera capture and canvas frame extraction

**Type:** client
**Description:** Create HTML5 web interface that captures camera feed, extracts frames via Canvas, and handles permission errors.

**Steps:**
1. Create `templates/index.html` with:
   - HTML5 video element for camera preview
   - Offscreen canvas element for frame extraction
   - Connection status indicator (Connected/Disconnected)
   - Frame counter display
   - Error message display with retry button
2. Implement camera permission request:
   - Use `navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720, facingMode: 'environment' } })`
   - Handle permission denial with clear error message and retry button
   - Handle camera access errors with helpful messages
3. Implement canvas frame extraction:
   - Use `requestAnimationFrame` for timing control
   - Extract frames at fixed 33ms intervals (~30 FPS)
   - Draw video frame to canvas using `drawImage()`
   - Convert canvas to JPEG blob using `toBlob()` with quality 0.8
4. Add basic CSS for mobile-friendly layout:
   - Responsive design for iOS Safari
   - Full-screen video preview
   - Status indicator positioning
5. Test camera capture on iOS Safari:
   - Verify permission prompt appears
   - Verify video preview displays
   - Verify frame extraction timing

**Verification:**
- iOS Safari displays camera permission prompt
- Video preview shows live camera feed
- Canvas extraction runs at ~30 FPS
- Error messages display correctly for permission denial
- Mobile layout works on iOS device screen sizes

**Files created/modified:**
- `templates/index.html` (mobile web client)
- `static/css/style.css` (mobile-friendly styling)

---

### 01-03: Implement WebSocket binary transmission and OpenCV frame decoding with debug display

**Type:** tracer (end-to-end slice)
**Description:** Connect mobile client to server via WebSocket, transmit binary frames, decode with OpenCV, and display in debug window.

**Steps:**
1. Implement WebSocket client in index.html:
   - Include Socket.IO client library
   - Connect to server WebSocket endpoint
   - Implement connection status updates (Connected/Disconnected)
   - Update frame counter on successful transmission
2. Implement binary frame transmission:
   - Emit canvas blob as binary data: `socket.emit('video_frame', blob, { binary: true })`
   - Ensure transmission uses binary mode (not Base64)
   - Add transmission error handling
3. Implement server WebSocket handler in app.py:
   - Create `@socketio.on('video_frame')` event handler
   - Receive binary data directly (no Base64 decoding)
   - Add error handling for malformed frames
4. Implement OpenCV frame decoding:
   - Convert binary data to NumPy array: `np.frombuffer(data, dtype=np.uint8)`
   - Decode JPEG to image: `cv2.imdecode(np_arr, cv2.IMREAD_COLOR)`
   - Handle decode errors gracefully
5. Implement debug display:
   - Create OpenCV window: `cv2.imshow('iOS Camera', frame_bgr)`
   - Display frame counter and connection status in window
   - Add key press handling to quit (ESC or 'q')
   - Update window at 30 FPS using `cv2.waitKey(33)`
6. Test end-to-end pipeline:
   - Connect iOS device to server
   - Verify video stream displays in OpenCV window
   - Verify frame counter updates on mobile UI
   - Verify connection status indicators work
   - Measure approximate latency (should be < 200ms for PoC)

**Verification:**
- WebSocket connection establishes successfully
- Binary frames transmit without Base64 encoding
- OpenCV decodes frames correctly
- Debug window displays live video stream
- Frame counter increments on mobile UI
- Connection status updates on both client and server
- End-to-end latency is acceptable for PoC (< 200ms)

**Files created/modified:**
- `templates/index.html` (add Socket.IO client and transmission logic)
- `app.py` (add WebSocket handler, OpenCV decoding, debug display)

---

## Execution Order

1. **01-01:** Set up Python virtual environment and Flask-SocketIO server (infrastructure)
2. **01-02:** Develop mobile web client with HTML5 camera capture (client)
3. **01-03:** Implement WebSocket binary transmission and OpenCV frame decoding (tracer)

## Dependencies

- 01-02 depends on 01-01 (server must exist before client can connect)
- 01-03 depends on 01-01 and 01-02 (both client and server needed for end-to-end test)

## Risks

- **iOS Safari camera permission complexity:** iOS Safari has strict camera permission handling. Mitigation: Test on actual iOS device, implement clear error messages.
- **WebSocket binary transmission compatibility:** Ensure Socket.IO client and server both support binary mode. Mitigation: Use Socket.IO library which handles binary data natively.
- **OpenCV decoding performance:** JPEG decoding may be CPU-intensive. Mitigation: Use appropriate JPEG quality (0.8) to balance quality and performance.
- **Network connectivity:** iOS device and Windows host must be on same network. Mitigation: Document network requirements clearly, provide troubleshooting steps.

## Out of Scope

- Virtual camera integration (Phase 2)
- Performance optimization (Phase 3)
- Camera controls (front/rear toggle, torch) (Phase 4)
- Resolution selection (Phase 4)
- Screen lock prevention (Phase 4)
- QR code pairing (Phase 5)
- Packaging as executable (Phase 5)

## Definition of Done

- [ ] All 3 tasks completed and verified
- [ ] End-to-end video stream works from iOS to Windows
- [ ] OpenCV debug window displays live video
- [ ] Mobile UI shows connection status and frame counter
- [ ] Error handling works for camera permission denial
- [ ] Code committed to git
- [ ] Phase marked as complete in ROADMAP.md

---
*Plan created: 2026-09-26*
*Mode: mvp (vertical slicing)*