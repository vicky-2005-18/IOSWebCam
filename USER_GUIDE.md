# iOS WebCam Bridge - User Guide

## Overview

iOS WebCam Bridge is a Windows application that turns your iPhone or iPad into a virtual webcam for video conferencing applications like Zoom, Microsoft Teams, Google Meet, and OBS Studio. No native iOS app installation required - just use Safari!

## System Requirements

- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **OBS Virtual Camera:** Required for virtual camera functionality
- **iOS Device:** iPhone or iPad running iOS 14+ with Safari
- **Network:** Local Wi-Fi network (5 GHz recommended for best performance)
- **Browser:** Safari on iOS (for camera access)

## Installation

### Step 1: Download the Application

1. Download `ioswebcam.exe` from the project repository
2. Place the executable in a folder of your choice (e.g., `C:\Program Files\iOSWebCam`)

### Step 2: Install OBS Virtual Camera Driver

The OBS Virtual Camera driver is required to expose the video stream as a system camera device.

1. Download OBS Studio from: https://obsproject.com/
2. Install OBS Studio (free, open-source)
3. Open OBS Studio
4. Go to **Tools** → **Virtual Camera**
5. Click **Start** to enable the Virtual Camera
6. Verify "OBS Virtual Camera" appears in Windows Device Manager under "Camera"

**Note:** You only need OBS Studio for the Virtual Camera driver. You don't need to use OBS Studio itself for this application.

## Quick Start

### 1. Start the Server

1. Double-click `ioswebcam.exe` to launch the application
2. The server will start and display:
   - Detected local IP address
   - Server URL (e.g., `http://192.168.1.101:5000`)
   - QR code for easy mobile scanning

### 2. Connect Your iOS Device

**Option A: Scan QR Code (Recommended)**
1. Open Camera app on your iPhone/iPad
2. Point at the QR code displayed in the terminal
3. Tap the Safari notification that appears
4. The web interface will open automatically

**Option B: Manual URL Entry**
1. Open Safari on your iPhone/iPad
2. Type the server URL shown in the terminal (e.g., `http://192.168.1.101:5000`)
3. Navigate to the URL

### 3. Grant Camera Permission

1. Safari will prompt for camera permission
2. Tap **Allow** to grant access
3. The camera preview will appear

### 4. Use in Video Conferencing

1. Open your video conferencing app (Zoom, Teams, Meet, OBS Studio, etc.)
2. Go to camera settings
3. Select **"OBS Virtual Camera"** as your video input
4. Your iOS device's camera feed will appear!

## Features

### Camera Controls

**Switch Camera**
- Tap the **📷 Switch Camera** button to toggle between front and rear cameras
- Use front camera for selfies
- Use rear camera for better quality

**Flashlight/Torch**
- Tap the **🔦 Flashlight** button to toggle the rear camera flashlight
- Only available when rear camera is selected
- Useful for low-light environments

**Resolution Selector**
- Choose from **480p**, **720p**, or **1080p**
- 720p is recommended for best balance of quality and performance
- 1080p may be too heavy for some devices

### Performance Metrics

The mobile interface displays real-time performance metrics:
- **Frames:** Total frames sent
- **FPS:** Current frame rate (target: 30 FPS)
- **Dropped:** Frames dropped due to network conditions
- **Server FPS:** Server-side processing FPS
- **BW:** Current bandwidth usage (Mbps)
- **Ping:** Network round-trip time (ms)

### Screen Lock Prevention

The application automatically keeps your iOS device awake during streaming to prevent sleep interruption. This preserves battery when not streaming.

## Network Setup

### Local Network (Recommended)

1. Ensure your Windows computer and iOS device are on the same Wi-Fi network
2. Start the server
3. Connect your iOS device using the provided URL or QR code
4. No additional setup required

### Remote Network (Requires HTTPS)

iOS Safari blocks camera access on HTTP URLs for security. To use the application over the internet or on different networks:

**Option A: Use ngrok (Easiest)**
1. Download ngrok from: https://ngrok.com/download
2. Extract and run ngrok
3. Sign up for free at https://ngrok.com/signup
4. Run: `ngrok http 5000`
5. ngrok will provide an HTTPS URL (e.g., `https://xxxx.ngrok-free.app`)
6. Use this URL on your iOS device

**Option B: Self-Signed SSL (Advanced)**
- Generate SSL certificates
- Configure Flask to use HTTPS
- Requires technical knowledge

## Troubleshooting

### Common Issues

**"Camera API requires HTTPS" error**
- iOS Safari requires HTTPS for camera access (except localhost)
- Use ngrok for HTTPS tunneling (see above)
- Or test on the host computer using `http://127.0.0.1:5000`

**"OBS Virtual Camera driver not found" error**
- Install OBS Studio from https://obsproject.com/
- Open OBS Studio → Tools → Virtual Camera → Start
- Verify driver appears in Windows Device Manager

**Camera permission denied**
- Go to iOS Settings → Safari → Camera
- Ensure "Ask" or "Allow" is selected
- Restart Safari and try again

**Video not appearing in Zoom/Teams**
- Ensure OBS Virtual Camera is enabled in OBS Studio
- Verify "OBS Virtual Camera" appears in Windows Device Manager
- Restart the video conferencing application
- Check camera settings in the application

**Poor video quality or lag**
- Check your Wi-Fi signal strength
- Try 5 GHz Wi-Fi instead of 2.4 GHz
- Reduce resolution to 480p
- Move closer to your Wi-Fi router

**High CPU usage**
- Reduce resolution to 480p or 720p
- Close other applications
- Ensure your computer meets system requirements

For more troubleshooting information, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Performance Tips

- **Best Performance:** 5 GHz Wi-Fi, 720p resolution, < 100ms ping
- **Battery Saving:** Use front camera, 480p resolution, disable flashlight
- **Low Light:** Use rear camera with flashlight, 720p resolution
- **Multiple Devices:** The server supports multiple concurrent connections

## Security Notes

- The application uses local network communication only
- No data is sent to external servers
- Camera stream is transmitted only to your local network
- For remote access, use ngrok or set up HTTPS with proper SSL certificates

## Support

For issues, questions, or contributions:
- GitHub Repository: https://github.com/vicky-2005-18/IOSWebCam
- Report bugs: https://github.com/vicky-2005-18/IOSWebCam/issues

## License

This project is open-source. See LICENSE file for details.
