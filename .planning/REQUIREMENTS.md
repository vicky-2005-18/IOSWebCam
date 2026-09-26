# Requirements: iOS WebCam Bridge

**Defined:** September 26, 2026
**Core Value:** Sub-100ms motion-to-photon latency at 720p @ 30 FPS with zero iOS app installation required.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Camera Capture

- [ ] **CAM-01**: User can grant camera permissions on iOS device via browser prompt
- [ ] **CAM-02**: User can select between front and rear camera on mobile device
- [ ] **CAM-03**: System captures video at 720p resolution @ 30 FPS by default
- [ ] **CAM-04**: System extracts video frames from HTML5 Canvas at fixed 33ms intervals

### Video Transmission

- [ ] **VID-01**: System transmits video frames as binary ArrayBuffers over WebSocket (not Base64)
- [ ] **VID-02**: WebSocket connection establishes bidirectional communication between iOS and Windows host
- [ ] **VID-03**: Server receives binary frame data and decodes using OpenCV
- [ ] **VID-04**: System converts frame color space from BGR (OpenCV) to RGB (PyVirtualCam)
- [ ] **VID-05**: End-to-end latency remains below 100ms on 5 GHz Wi-Fi network

### Virtual Camera Integration

- [ ] **VIR-01**: Server detects OBS Virtual Camera driver installation on startup
- [ ] **VIR-02**: System initializes PyVirtualCam at 1280x720 resolution @ 30 FPS
- [ ] **VIR-03**: Decoded RGB frames are injected into virtual camera loopback driver
- [ ] **VIR-04**: Virtual camera appears as standard DirectShow device in Windows
- [ ] **VIR-05**: Third-party applications (Zoom, Teams, Meet, OBS) can select virtual camera as input

### Mobile UI Controls

- [ ] **UI-01**: Mobile web interface displays connection status and controls
- [ ] **UI-02**: User can toggle between front and rear camera via UI button
- [ ] **UI-03**: User can toggle torch/flashlight on rear camera via UI button
- [ ] **UI-04**: User can select video resolution (480p, 720p, 1080p) via UI dropdown
- [ ] **UI-05**: iOS device screen remains awake during active streaming sessions

### Performance Optimization

- [ ] **PERF-01**: Server uses Eventlet async greenlets for non-blocking frame processing
- [ ] **PERF-02**: Frame rate is throttled to consistent 30 FPS on client canvas
- [ ] **PERF-03**: System adapts JPEG quality based on network conditions
- [ ] **PERF-04**: System falls back to lower resolution (480p) under high packet loss
- [ ] **PERF-05**: Performance telemetry overlay displays latency, FPS, and bandwidth usage

### Utility Features

- [ ] **UTIL-01**: Server automatically detects local IPv4 address for mobile pairing
- [ ] **UTIL-02**: Server generates QR code containing server URL for mobile scanning
- [ ] **UTIL-03**: Mobile device can scan QR code to connect to server automatically
- [ ] **UTIL-04**: System provides clear error messages for common issues (driver missing, permission denied)

### Packaging

- [ ] **PKG-01**: Entire Python project is packaged as standalone Windows executable
- [ ] **PKG-02**: Executable includes all dependencies (Flask, OpenCV, PyVirtualCam, etc.)
- [ ] **PKG-03**: User can run application without Python installation
- [ ] **PKG-04**: Comprehensive user documentation and troubleshooting guide included
- [ ] **PKG-05**: Installation process includes OBS Virtual Camera driver setup instructions

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Audio Streaming

- **AUD-01**: System captures and transmits audio alongside video
- **AUD-02**: Audio synchronization with video frames is maintained
- **AUD-03**: User can select audio input source on iOS device

### Multi-Device Support

- **MULT-01**: System supports multiple iOS devices connecting to single host
- **MULT-02**: Each device appears as separate virtual camera instance
- **MULT-03**: System handles driver conflicts between multiple virtual cameras

### Cross-Platform Support

- **CROSS-01**: System supports macOS host with v4l2loopback driver
- **CROSS-02**: System supports Linux host with v4l2loopback driver
- **CROSS-03**: Packaging provides executables for all supported platforms

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

|| Feature | Reason |
||---------|--------|
|| Native iOS app development | Web-based approach eliminates Apple Developer Account and App Store requirements |
|| App Store distribution | Not required for web-based solution |
|| Cloud-based streaming | Local network only processing ensures privacy and low latency |
|| Recording on host | Users can use OBS Studio for recording functionality |
|| Authentication and security | Local network only, no cloud services requiring authentication |
|| Multi-user collaboration | Single device to single host model for v1 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

|| Requirement | Phase | Status |
||-------------|-------|--------|
|| CAM-01 | Phase 1 | Pending |
|| CAM-02 | Phase 4 | Pending |
|| CAM-03 | Phase 1 | Pending |
|| CAM-04 | Phase 1 | Pending |
|| VID-01 | Phase 1 | Pending |
|| VID-02 | Phase 1 | Pending |
|| VID-03 | Phase 1 | Pending |
|| VID-04 | Phase 2 | Pending |
|| VID-05 | Phase 3 | Pending |
|| VIR-01 | Phase 2 | Pending |
|| VIR-02 | Phase 2 | Pending |
|| VIR-03 | Phase 2 | Pending |
|| VIR-04 | Phase 2 | Pending |
|| VIR-05 | Phase 2 | Pending |
|| UI-01 | Phase 1 | Pending |
|| UI-02 | Phase 4 | Pending |
|| UI-03 | Phase 4 | Pending |
|| UI-04 | Phase 4 | Pending |
|| UI-05 | Phase 4 | Pending |
|| PERF-01 | Phase 3 | Pending |
|| PERF-02 | Phase 3 | Pending |
|| PERF-03 | Phase 3 | Pending |
|| PERF-04 | Phase 3 | Pending |
|| PERF-05 | Phase 3 | Pending |
|| UTIL-01 | Phase 5 | Pending |
|| UTIL-02 | Phase 5 | Pending |
|| UTIL-03 | Phase 5 | Pending |
|| UTIL-04 | Phase 2 | Pending |
|| PKG-01 | Phase 5 | Pending |
|| PKG-02 | Phase 5 | Pending |
|| PKG-03 | Phase 5 | Pending |
|| PKG-04 | Phase 5 | Pending |
|| PKG-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0 ✓

---
*Requirements defined: September 26, 2026*
*Last updated: September 26, 2026 after initial definition*