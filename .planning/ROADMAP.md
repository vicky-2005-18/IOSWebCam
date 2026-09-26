# Roadmap: iOS WebCam Bridge

## Overview

Build a complete iOS-to-Windows webcam bridge system through 5 phases: establish basic streaming pipeline (Phase 1), integrate virtual camera driver (Phase 2), optimize for sub-100ms latency (Phase 3), enhance mobile UI with controls (Phase 4), and package as standalone executable (Phase 5). Each phase delivers working functionality, from debug stream to distributable product.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Proof of Concept & WebSocket Pipeline** - Establish basic camera capture, WebSocket transmission, and frame decoding pipeline
- [ ] **Phase 2: Virtual Camera Driver Integration** - Integrate PyVirtualCam and OBS driver for system camera exposure
- [ ] **Phase 3: Performance & Latency Optimization** - Optimize for sub-100ms latency with async processing and adaptive quality
- [ ] **Phase 4: Mobile UI Controls & Utility Features** - Add camera controls, screen lock prevention, and QR code pairing
- [ ] **Phase 5: Packaging & Single-Executable Build** - Package as standalone Windows executable with documentation

## Phase Details

### Phase 1: Proof of Concept & WebSocket Pipeline
**Goal**: Establish basic camera capture, WebSocket binary transmission, and OpenCV frame decoding pipeline with debug visualization
**Mode**: mvp
**Depends on**: Nothing (first phase)
**Requirements**: CAM-01, CAM-03, CAM-04, VID-01, VID-02, VID-03, UI-01
**Success Criteria** (what must be TRUE):
  1. User can open web page on iOS device and grant camera permissions
  2. Video frames are captured at 720p @ 30 FPS and transmitted as binary WebSocket messages
  3. Server receives and decodes frames, displaying them in OpenCV debug window
  4. End-to-end pipeline demonstrates working video stream from iOS to Windows host
**Plans**: 3 plans

Plans:
- [ ] 01-01: Set up Python virtual environment and Flask-SocketIO server on Windows host
- [ ] 01-02: Develop mobile web client with HTML5 camera capture and canvas frame extraction
- [ ] 01-03: Implement WebSocket binary transmission and OpenCV frame decoding with debug display

### Phase 2: Virtual Camera Driver Integration
**Goal**: Integrate PyVirtualCam with OBS Virtual Camera driver to expose stream as system camera device
**Mode**: mvp
**Depends on**: Phase 1
**Requirements**: VID-04, VIR-01, VIR-02, VIR-03, VIR-04, VIR-05, UTIL-04
**Success Criteria** (what must be TRUE):
  1. Server detects OBS Virtual Camera driver installation and provides helpful error messages if missing
  2. PyVirtualCam initializes at 1280x720 @ 30 FPS and accepts RGB frames
  3. Decoded frames are converted from BGR to RGB and injected into virtual camera loopback
  4. Virtual camera appears as selectable input in Zoom, Teams, Meet, and OBS Studio
  5. Third-party applications display video stream from virtual camera correctly
**Plans**: 3 plans

Plans:
- [ ] 02-01: Install OBS Virtual Camera driver and implement driver detection on server startup
- [ ] 02-02: Integrate PyVirtualCam library and configure virtual camera parameters
- [ ] 02-03: Implement BGR to RGB color space conversion and frame injection into virtual camera

### Phase 3: Performance & Latency Optimization
**Goal**: Optimize system for sub-100ms end-to-end latency with async processing, frame rate control, and adaptive quality scaling
**Mode**: mvp
**Depends on**: Phase 2
**Requirements**: VID-05, PERF-01, PERF-02, PERF-03, PERF-04, PERF-05
**Success Criteria** (what must be TRUE):
  1. Server uses Eventlet async greenlets for non-blocking frame processing under load
  2. Client canvas throttles frame rate to consistent 30 FPS without jitter
  3. End-to-end latency remains below 100ms on standard 5 GHz Wi-Fi network
  4. System adapts JPEG quality dynamically based on network ping metrics
  5. System falls back to 480p resolution automatically under high packet loss conditions
  6. Performance telemetry overlay displays real-time latency, FPS, and bandwidth usage
**Plans**: 4 plans

Plans:
- [ ] 03-01: Refactor server to use Eventlet async mode and implement frame processing queues
- [ ] 03-02: Implement frame rate throttling on client canvas for consistent 30 FPS output
- [ ] 03-03: Add dynamic JPEG quality scaling and resolution fallback based on network conditions
- [ ] 03-04: Implement performance telemetry overlay with latency, FPS, and bandwidth metrics

### Phase 4: Mobile UI Controls & Utility Features
**Goal**: Enhance mobile web interface with camera controls, screen lock prevention, and QR code auto-discovery for improved usability
**Mode**: mvp
**Depends on**: Phase 3
**Requirements**: CAM-02, UI-02, UI-03, UI-04, UI-05
**Success Criteria** (what must be TRUE):
  1. User can toggle between front and rear camera via mobile UI button
  2. User can toggle torch/flashlight on rear camera via mobile UI button
  3. User can select video resolution (480p, 720p, 1080p) via mobile UI dropdown
  4. iOS device screen remains awake during active streaming sessions (prevents sleep interruption)
  5. Mobile UI displays clear connection status and control indicators
**Plans**: 4 plans

Plans:
- [ ] 04-01: Integrate NoSleep.js library with silent audio loop for iOS screen lock prevention
- [ ] 04-02: Implement camera toggle button (front/rear) with MediaStreamTrack constraint changes
- [ ] 04-03: Implement torch/flashlight toggle using WebKit ImageCapture constraint API
- [ ] 04-04: Build dynamic resolution selector with on-the-fly stream renegotiation

### Phase 5: Packaging & Single-Executable Build
**Goal**: Package entire Python project as standalone Windows executable with auto-discovery, QR code generation, and comprehensive documentation
**Mode**: mvp
**Depends on**: Phase 4
**Requirements**: UTIL-01, UTIL-02, UTIL-03, PKG-01, PKG-02, PKG-03, PKG-04, PKG-05
**Success Criteria** (what must be TRUE):
  1. Server automatically detects local IPv4 address and displays in terminal
  2. Server generates QR code containing server URL for mobile device scanning
  3. Mobile device can scan QR code to automatically connect to server
  4. PyInstaller packages entire project as standalone Windows executable
  5. Executable includes all dependencies (Flask, OpenCV, PyVirtualCam, etc.)
  6. User can run application without Python installation
  7. Comprehensive user documentation and troubleshooting guide are included
  8. Installation process includes OBS Virtual Camera driver setup instructions
**Plans**: 4 plans

Plans:
- [ ] 05-01: Implement auto-discovery routine using socket.gethostbyname for local IPv4 detection
- [ ] 05-02: Integrate qrcode-terminal library for QR code generation and display
- [ ] 05-03: Configure PyInstaller to package project as standalone Windows executable
- [ ] 05-04: Write comprehensive user documentation, deployment manual, and troubleshooting guide

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

|| Phase | Plans Complete | Status | Completed |
||-------|----------------|--------|-----------|
|| 1. Proof of Concept & WebSocket Pipeline | 0/3 | Not started | - |
|| 2. Virtual Camera Driver Integration | 0/3 | Not started | - |
|| 3. Performance & Latency Optimization | 0/4 | Not started | - |
|| 4. Mobile UI Controls & Utility Features | 0/4 | Not started | - |
|| 5. Packaging & Single-Executable Build | 0/4 | Not started | - |