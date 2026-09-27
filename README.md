# iOS WebCam Bridge

A high-performance, low-latency streaming utility that repurposes an iOS device (iPhone/iPad) into a full-featured virtual USB/system webcam for Windows desktop operating systems.

## Overview

This project leverages modern HTML5 web APIs on the client side and an asynchronous Python receiving pipeline on the host PC to eliminate the need for native iOS app compilation, Apple Developer Account provisioning, or App Store distribution.

## Core Value

Sub-100ms motion-to-photon latency at 720p @ 30 FPS with zero iOS app installation required.

## Architecture

The system follows a three-layer architecture:
- **Client Layer:** Mobile web frontend using HTML5 MediaDevices API
- **Transport Layer:** WebSocket protocol for low-latency binary transmission
- **Server Layer:** Python engine with Flask-SocketIO, OpenCV, and PyVirtualCam integration

## Technology Stack

- **Server:** Python 3.10+, Flask-SocketIO, Eventlet, OpenCV, NumPy
- **Virtual Camera:** PyVirtualCam with OBS Virtual Camera Driver
- **Client:** HTML5, CSS3, JavaScript (no framework dependencies)
- **Transport:** WebSocket binary transmission (not Base64)

## Project Status

**Current Phase:** ✅ All 5 Phases Complete

The project has been fully implemented:
1. ✅ Project initialization and planning complete
2. ✅ Phase 1: Proof of Concept & WebSocket Pipeline
3. ✅ Phase 2: Virtual Camera Driver Integration
4. ✅ Phase 3: Performance & Latency Optimization
5. ✅ Phase 4: Mobile UI Controls & Utility Features
6. ✅ Phase 5: Packaging & Single-Executable Build

## Development

### Prerequisites

- Windows 10/11 (64-bit)
- Python 3.9+
- OBS Virtual Camera Driver
- iOS 14.0+ device with Safari

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000` and display the local IPv4 address for mobile device connection.

## Documentation

- [Distribution Guide](DISTRIBUTION.md) - Download and install the standalone executable
- [User Guide](USER_GUIDE.md) - Installation and usage instructions
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Engineering Specification](iOS_WebCam_Bridge_Engineering_Doc.docx) - Complete technical specification
- [Project Planning](.planning/) - GSD workflow artifacts (PROJECT.md, REQUIREMENTS.md, ROADMAP.md)
- [Research](.planning/research/) - Technical research (STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md)

## Quick Start (Executable)

1. Download `ioswebcam.exe` from the [GitHub Releases](https://github.com/vicky-2005-18/IOSWebCam/releases) page
2. Install [OBS Studio](https://obsproject.com/) and enable the Virtual Camera
3. Double-click `ioswebcam.exe` to run
4. Open Safari on your iOS device and navigate to the displayed URL
5. Select "OBS Virtual Camera" in your video conferencing application

See [DISTRIBUTION.md](DISTRIBUTION.md) for detailed instructions.

## License

[License to be determined]

## Contributing

This is a personal project currently in development.