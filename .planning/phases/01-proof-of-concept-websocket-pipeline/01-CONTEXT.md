# Phase 1: Proof of Concept & WebSocket Pipeline - Context

**Gathered:** September 26, 2026
**Status:** Ready for planning

## Phase Boundary

Establish basic camera capture, WebSocket binary transmission, and OpenCV frame decoding pipeline with debug visualization. This phase delivers a working end-to-end video stream from iOS device to Windows host, displaying received frames in an OpenCV debug window. The focus is on proving the core streaming pipeline works before adding virtual camera integration or performance optimizations.

## Implementation Decisions

### Error Handling
- **D-01:** Mobile client shows clear error message with retry button when camera permission is denied — **Reversibility:** reversible — Simple UI change, no architectural impact
- **D-02:** Server logs connection errors and provides helpful error messages in terminal for debugging

### Debug Display
- **D-03:** cv2.imshow debug window is always visible during Phase 1 for pipeline verification — **Reversibility:** reversible — Will be removed in Phase 2 when virtual camera integration replaces debug display
- **D-04:** Debug window displays frame counter and basic connection status alongside video feed

### Mobile UI (Phase 1 Minimal)
- **D-05:** Mobile interface displays simple status indicator (Connected/Disconnected) with frame counter — **Reversibility:** reversible — Will be enhanced in Phase 4 with full controls
- **D-06:** No camera controls or resolution selection in Phase 1 (deferred to Phase 4)

### Technical Implementation
- **D-07:** Use Flask-SocketIO with Eventlet async mode for WebSocket server (carried forward from PROJECT.md)
- **D-08:** Transmit video frames as binary ArrayBuffers, not Base64 (carried forward from PROJECT.md)
- **D-09:** Canvas frame extraction at fixed 33ms intervals (~30 FPS) using requestAnimationFrame
- **D-10:** OpenCV cv2.imdecode for binary JPEG to NumPy array conversion
- **D-11:** Server binds to 0.0.0.0 on port 5000 for local network access

### Claude's Discretion
None — all decisions captured via auto-selection based on engineering document specifications

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Engineering Specification
- `iOS_WebCam_Bridge_Engineering_Doc.docx` — Complete technical specification with architecture, stack, and implementation details (extracted text available)

### Project Context
- `.planning/PROJECT.md` — Core value, constraints, and key technical decisions
- `.planning/REQUIREMENTS.md` — Phase 1 requirements: CAM-01, CAM-03, CAM-04, VID-01, VID-02, VID-03, UI-01
- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, and plan structure

### Research Findings
- `.planning/research/STACK.md` — Recommended Python stack (Flask-SocketIO, Eventlet, OpenCV, NumPy)
- `.planning/research/ARCHITECTURE.md` — Three-layer architecture and component responsibilities
- `.planning/research/PITFALLS.md` — Critical pitfalls to avoid (Base64 encoding, synchronous processing)

## Existing Code Insights

### Reusable Assets
None — greenfield project with no existing code

### Established Patterns
None — first implementation phase

### Integration Points
None — building foundation for subsequent phases

## Specific Ideas

No specific requirements — open to standard approaches based on engineering document specifications. The document provides clear implementation patterns for Flask-SocketIO server setup, HTML5 camera capture, and WebSocket binary transmission.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 1-Proof of Concept & WebSocket Pipeline*
*Context gathered: September 26, 2026*