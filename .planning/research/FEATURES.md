# Feature Research

**Domain:** iOS WebCam Bridge - Real-time video streaming from iOS to Windows
**Researched:** September 26, 2026
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

|| Feature | Why Expected | Complexity | Notes |
||---------|--------------|------------|-------|
|| Camera capture (front/rear) | Users expect to choose between cameras | MEDIUM | HTML5 MediaDevices API provides this natively |
|| Real-time video transmission | Core function - without this, product doesn't work | HIGH | WebSocket binary transmission for low latency |
|| Virtual camera integration | Must appear as system camera in video apps | HIGH | PyVirtualCam + OBS Driver integration |
|| Basic mobile UI | Users need to control camera and see connection status | MEDIUM | Simple HTML5 interface with controls |
|| Resolution selection | Users expect quality options based on network conditions | MEDIUM | Dynamic stream renegotiation |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

|| Feature | Value Proposition | Complexity | Notes |
||---------|-------------------|------------|-------|
|| Zero iOS app installation | No App Store, no compilation, instant use | LOW | Web-based approach is unique advantage |
|| Sub-100ms latency | Professional-grade performance for streaming | HIGH | Binary WebSocket transmission + async optimization |
|| Auto-discovery with QR code | Effortless pairing without typing URLs | MEDIUM | Local IPv4 detection + QR code generation |
|| Screen lock prevention | iOS devices don't sleep during streaming | LOW | NoSleep.js library integration |
|| Standalone Windows executable | No Python installation required for end users | HIGH | PyInstaller packaging for distribution |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

|| Feature | Why Requested | Why Problematic | Alternative |
||---------|---------------|-----------------|-------------|
|| Native iOS app | More control over hardware | Requires Apple Developer Account, App Store approval, compilation | Web-based HTML5 approach |
|| Cloud streaming | Access from anywhere | Adds latency, requires internet, privacy concerns | Local network only |
|| Multi-device support | Use multiple phones as cameras | Increases complexity significantly, potential driver conflicts | Single device v1, defer to v2 |
|| Audio streaming | Complete webcam experience | Adds complexity to WebSocket protocol, audio sync challenges | Video-only v1, defer audio to v2 |
|| Recording on host | Save streams locally | Adds storage management, complexity beyond virtual camera | Use OBS Studio for recording |

## Feature Dependencies

```
[Camera capture]
    └──requires──> [WebSocket transmission]
                       └──requires──> [Frame decoding]
                          └──requires──> [Virtual camera integration]

[Screen lock prevention] ──enhances──> [Camera capture]

[Auto-discovery with QR code] ──enhances──> [Mobile UI usability]

[Resolution selection] ──conflicts──> [Sub-100ms latency] (higher resolution = higher latency)
```

### Dependency Notes

- **Camera capture requires WebSocket transmission:** Video frames must be transmitted to host for processing
- **WebSocket transmission requires Frame decoding:** Host must decode received binary frames before processing
- **Frame decoding requires Virtual camera integration:** Decoded frames must be fed into virtual camera driver
- **Screen lock prevention enhances Camera capture:** Ensures continuous streaming without iOS sleep interruption
- **Auto-discovery with QR code enhances Mobile UI usability:** Eliminates manual URL entry for better UX
- **Resolution selection conflicts with Sub-100ms latency:** Higher resolutions increase bandwidth and processing time, potentially violating latency constraints

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] Camera capture (front/rear) — Core functionality, without this nothing works
- [ ] Real-time video transmission — Essential for streaming, must achieve sub-100ms latency
- [ ] Virtual camera integration — Required for Zoom/Teams/OBS integration
- [ ] Basic mobile UI — Minimal controls for camera toggling and connection status
- [ ] Screen lock prevention — Critical for continuous streaming sessions

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Resolution selection — Once core streaming is stable, add quality options
- [ ] Torch/flashlight control — Enhances usability in low-light conditions
- [ ] Performance telemetry overlay — Helps users monitor latency and bandwidth
- [ ] Auto-discovery with QR code — Improves initial setup experience

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Audio streaming — Adds complexity to protocol and sync challenges
- [ ] Multi-device support — Requires driver-level changes and conflict resolution
- [ ] macOS/Linux support — Different virtual camera drivers required
- [ ] Recording on host — Use OBS Studio instead for this functionality
- [ ] Cloud streaming — Violates local-only privacy model

## Feature Prioritization Matrix

|| Feature | User Value | Implementation Cost | Priority |
||---------|------------|---------------------|----------|
|| Camera capture (front/rear) | HIGH | MEDIUM | P1 |
|| Real-time video transmission | HIGH | HIGH | P1 |
|| Virtual camera integration | HIGH | HIGH | P1 |
|| Basic mobile UI | HIGH | MEDIUM | P1 |
|| Screen lock prevention | HIGH | LOW | P1 |
|| Resolution selection | MEDIUM | MEDIUM | P2 |
|| Torch/flashlight control | MEDIUM | LOW | P2 |
|| Performance telemetry overlay | LOW | MEDIUM | P2 |
|| Auto-discovery with QR code | MEDIUM | MEDIUM | P2 |
|| Audio streaming | MEDIUM | HIGH | P3 |
|| Multi-device support | LOW | HIGH | P3 |
|| macOS/Linux support | MEDIUM | HIGH | P3 |
|| Recording on host | LOW | MEDIUM | P3 |
|| Cloud streaming | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

|| Feature | Competitor A (Native Apps) | Competitor B (Hardware Webcams) | Our Approach |
||---------|---------------------------|----------------------------------|--------------|
|| Installation | App Store download | Hardware purchase | Web-based, no installation |
|| Platform support | iOS only | Cross-platform hardware | iOS to Windows only v1 |
|| Latency | Variable (depends on app) | Native USB speed | Sub-100ms optimized |
|| Cost | Free or paid | Hardware cost | Free software |
|| Portability | Requires iOS device | Physical device | Uses existing iOS device |
|| Flexibility | App-dependent | Fixed hardware | Software-configurable |

## Sources

- iOS WebCam Bridge Engineering Document (provided) — Complete feature specification
- Competitor analysis: EpocCam, iVCam, DroidCam — Native iOS webcam apps
- Competitor analysis: Logitech, Razer webcams — Hardware webcam solutions
- Video conferencing requirements: Zoom, Teams, Meet, OBS integration patterns
- Mobile web limitations: iOS Safari MediaDevices API constraints

---
*Feature research for: iOS WebCam Bridge*
*Researched: September 26, 2026*