# iOS WebCam Bridge

## What This Is

A high-performance, low-latency streaming utility that repurposes an iOS device (iPhone/iPad) into a full-featured virtual USB/system webcam for Windows desktop operating systems. By leveraging modern HTML5 web APIs on the client side and an asynchronous Python receiving pipeline on the host PC, the system eliminates the need for native iOS app compilation, Apple Developer Account provisioning, or App Store distribution.

## Core Value

Sub-100ms motion-to-photon latency at 720p @ 30 FPS with zero iOS app installation required.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] iOS device camera capture via HTML5 MediaDevices API (front/rear camera selection)
- [ ] Real-time video frame transmission over WebSocket to host PC
- [ ] Host Python server receives and decodes frames using OpenCV
- [ ] Virtual camera driver integration exposing stream as DirectShow device
- [ ] Mobile UI controls for camera toggling, torch/flashlight, resolution selection
- [ ] Low-latency optimization (binary transmission, frame throttling, async queues)
- [ ] iOS screen lock prevention during streaming
- [ ] Auto-discovery and QR code pairing for mobile connection
- [ ] Packaging as standalone Windows executable

### Out of Scope

- Native iOS app development — eliminated by web-based approach
- App Store distribution — not required for web-based solution
- Cloud-based streaming — all processing is local network only
- Multi-device support — single iOS device to single Windows host
- Audio streaming — video-only implementation

## Context

**Technical Environment:**
- Host: Windows 10/11 (64-bit) with Python 3.9+
- Client: iOS 14.0+ running Mobile Safari (WebKit with WebRTC & Media Device support)
- Network: Shared local Wi-Fi (802.11n/ac/ax) or USB network tethering
- Target Applications: Zoom, Microsoft Teams, Google Meet, OBS Studio

**Architecture Pattern:**
Client-Server event-driven architecture using asynchronous WebSocket communication and kernel-level loopback drivers. The system follows a three-layer architecture: Client Layer (mobile web frontend), Transport Layer (WebSocket protocol), and Server Layer (Python engine with virtual camera driver interface).

**Performance Requirements:**
- Sub-100ms end-to-end latency on 5 GHz wireless network
- Host CPU usage below 15% on mid-tier quad-core processors
- Mobile battery drain not exceeding 20% per hour
- 720p @ 30 FPS default resolution

## Constraints

- **Platform**: Windows 10/11 host only — Linux/macOS not supported in v1
- **Browser**: iOS Safari only — requires WebKit Media Device API support
- **Network**: Local network only — no internet/cloud streaming support
- **Dependencies**: Requires OBS Virtual Camera driver on Windows host
- **Latency**: Hard constraint of 100ms maximum end-to-end latency
- **Performance**: CPU and battery constraints limit resolution options

## Key Decisions

|| Decision | Rationale | Outcome |
||----------|-----------|---------|
|| Web-based iOS client | Eliminates native app compilation, Apple Developer Account, and App Store distribution | — Pending |
|| Binary WebSocket transmission | Reduces payload size by ~33% compared to Base64 encoding, critical for sub-100ms latency | — Pending |
|| Flask-SocketIO with Eventlet | Provides light multi-threading with minimal WebSocket connection latency | — Pending |
|| PyVirtualCam with OBS driver | Direct kernel-level DirectShow integration recognized natively by video software | — Pending |
|| 5-phase implementation approach | Gradual complexity from proof-of-concept to production-ready packaging | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: September 26, 2026 after initialization*