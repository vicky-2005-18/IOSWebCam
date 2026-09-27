# iOS WebCam Bridge - Distribution Guide

## Executable Distribution

The standalone Windows executable is located at:
```
dist/ioswebcam.exe
```

### Executable Size
Approximately 66 MB (includes all dependencies)

### System Requirements
- Windows 10 or Windows 11 (64-bit)
- OBS Studio (required for virtual camera functionality)
- Wi-Fi network for iOS device connection
- iOS device with Safari browser

### Installation Instructions for Users

#### Option 1: Direct Download (Recommended)
1. Download `ioswebcam.exe` from the GitHub Releases page
2. Place the executable in any folder on your Windows computer
3. Double-click `ioswebcam.exe` to run
4. No Python installation required!

#### Option 2: Source Code Installation
For users who prefer to run from source:
1. Install Python 3.14 or later from https://python.org
2. Clone the repository: `git clone https://github.com/vicky-2005-18/IOSWebCam.git`
3. Navigate to the project directory: `cd IOSWebCam`
4. Create virtual environment: `python -m venv venv`
5. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Git Bash: `source venv/Scripts/activate`
6. Install dependencies: `pip install -r requirements.txt`
7. Run the server: `python app.py`

### OBS Virtual Camera Setup (Required)

The application requires OBS Studio to provide the virtual camera driver:

1. **Download OBS Studio**
   - Visit: https://obsproject.com/
   - Download and install OBS Studio (free)

2. **Enable Virtual Camera**
   - Open OBS Studio
   - Go to **Tools > Virtual Camera**
   - Click **Start** to enable the Virtual Camera
   - Verify "OBS Virtual Camera" appears in Windows Device Manager

3. **Use the Virtual Camera**
   - After starting the iOS WebCam Bridge, the stream will appear as "OBS Virtual Camera"
   - Select "OBS Virtual Camera" in Zoom, Teams, Google Meet, OBS, or other applications

### Quick Start Guide

1. **Install OBS Studio** and enable the Virtual Camera (see above)

2. **Run the Application**
   - Double-click `ioswebcam.exe`
   - The server will start and display:
     - Local IP address
     - Server URL
     - QR code (if console supports it)

3. **Connect iOS Device**
   - Ensure your iOS device is on the same Wi-Fi network
   - Open Safari on your iOS device
   - Navigate to the server URL displayed in the terminal
   - Grant camera permission when prompted
   - **Note:** iOS requires HTTPS for camera access. For remote testing, use ngrok (see USER_GUIDE.md)

4. **Start Streaming**
   - The video will appear in the virtual camera
   - Select "OBS Virtual Camera" in your video conferencing application

### Troubleshooting

See `TROUBLESHOOTING.md` for detailed troubleshooting guides covering:
- Camera access issues
- OBS Virtual Camera problems
- Network connectivity issues
- Performance optimization
- iOS device issues
- Windows firewall issues

### Security Notes

- The executable is not code-signed. Windows Defender may flag it as untrusted.
- Add an exception in Windows Defender if needed.
- The application only works on local networks by default.
- For remote access, use ngrok or set up HTTPS with SSL certificates.

### Updating

To update to the latest version:
1. Download the new `ioswebcam.exe` from GitHub Releases
2. Replace the old executable with the new one
3. No configuration changes required

### Building from Source

To build the executable yourself:
1. Install Python 3.14 or later
2. Install dependencies: `pip install -r requirements.txt`
3. Build executable: `pyinstaller ioswebcam.spec`
4. The executable will be created in `dist/ioswebcam.exe`

### Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/vicky-2005-18/IOSWebCam/issues
- Documentation: See `USER_GUIDE.md` and `TROUBLESHOOTING.md`

### License

This project is provided as-is for educational and personal use.
