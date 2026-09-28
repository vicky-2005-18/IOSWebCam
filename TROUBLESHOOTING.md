# iOS WebCam Bridge - Troubleshooting Guide

## Camera Access Issues

### "Camera API requires HTTPS or localhost"

**Problem:** iOS Safari blocks camera access on HTTP URLs for security.

**Solutions:**
1. **Use localhost:** On the host computer, use `http://127.0.0.1:5000` instead of the IP address
2. **Use ngrok:** Set up ngrok for HTTPS tunneling (see USER_GUIDE.md)
3. **Enable HTTPS:** Configure Flask with SSL certificates (advanced)

### Camera Permission Denied

**Problem:** Safari denies camera permission when prompted.

**Solutions:**
1. Go to iOS Settings → Safari → Camera
2. Change setting to "Ask" or "Allow"
3. Restart Safari and try again
4. Clear Safari cache: Settings → Safari → Clear History and Website Data

### "No camera found on this device"

**Problem:** Device has no camera or camera is disabled.

**Solutions:**
1. Ensure your device has a working camera
2. Check iOS Settings → Privacy → Camera
3. Ensure Safari has camera access
4. Restart your iOS device

### Camera is already in use

**Problem:** Another application is using the camera.

**Solutions:**
1. Close other camera applications
2. Restart Safari
3. Restart your iOS device

## Unity Capture Issues

### "Unity Video Capture driver not found"

**Problem:** Unity Capture driver is not installed.

**Solutions:**
1. Download Unity Capture from: https://github.com/schellingb/UnityCapture/releases
2. Download and run the UnityCaptureSetup.exe installer
3. Complete the installation wizard
4. Verify "Unity Video Capture" appears in Windows Device Manager

### Virtual camera not appearing in Zoom/Teams/Meet

**Problem:** Unity Video Capture is not listed as a camera option.

**Solutions:**
1. Restart the video conferencing application
2. Check Windows Device Manager → Camera
3. Reinstall Unity Capture driver

### Virtual camera shows black screen

**Problem:** Unity Video Capture is selected but shows no video.

**Solutions:**
1. Ensure the iOS WebCam Bridge server is running
2. Ensure your iOS device is connected and streaming
3. Restart the iOS WebCam Bridge server
4. Check server logs for errors

## Network Issues

### Cannot connect to server from iOS device

**Problem:** iOS device cannot reach the server URL.

**Solutions:**
1. Ensure both devices are on the same Wi-Fi network
2. Check the IP address displayed in the server terminal
3. Try pinging the IP address from your iOS device (using a network app)
4. Disable VPN on both devices
5. Check Windows Firewall settings
6. Ensure the server is running (check terminal)

### High latency or poor video quality

**Problem:** Video is laggy or pixelated.

**Solutions:**
1. Check Wi-Fi signal strength
2. Switch to 5 GHz Wi-Fi instead of 2.4 GHz
3. Reduce resolution to 480p
4. Move closer to your Wi-Fi router
5. Close other applications using bandwidth
6. Check ping value in mobile UI (should be < 100ms)

### Connection drops frequently

**Problem:** Video stream disconnects intermittently.

**Solutions:**
1. Check Wi-Fi stability
2. Restart your Wi-Fi router
3. Ensure iOS device doesn't go to sleep (screen lock prevention is enabled)
4. Check server logs for errors
5. Ensure no other devices are hogging bandwidth

## Performance Issues

### High CPU usage on Windows

**Problem:** Server process uses excessive CPU.

**Solutions:**
1. Reduce resolution to 480p or 720p
2. Close other applications
3. Ensure your computer meets system requirements
4. Check for malware or background processes
5. Restart the server

### Low frame rate (< 30 FPS)

**Problem:** Video is choppy or not smooth.

**Solutions:**
1. Check network conditions (ping, bandwidth)
2. Reduce resolution
3. Close other applications
4. Ensure iOS device has good battery
5. Restart the server
6. Check "Dropped frames" counter in mobile UI

### High bandwidth usage

**Problem:** Using too much network bandwidth.

**Solutions:**
1. Reduce resolution
2. Check if quality scaling is working (should adapt to network)
3. Close other network applications
4. Check "BW" metric in mobile UI

## iOS Device Issues

### Screen goes to sleep during streaming

**Problem:** iOS device screen turns off during streaming.

**Solutions:**
1. Screen lock prevention should be enabled automatically
2. Ensure NoSleep.js is working (check browser console)
3. Manually keep screen awake (Settings → Display & Brightness → Auto-Lock → Never)
4. Plug device into power

### Safari crashes or freezes

**Problem:** Safari becomes unresponsive.

**Solutions:**
1. Restart Safari
2. Clear Safari cache and cookies
3. Restart iOS device
4. Update iOS to latest version
5. Free up device storage

### Audio not working (if implemented in future)

**Problem:** Audio stream is not working.

**Solutions:**
1. Ensure audio permission is granted
2. Check iOS Settings → Safari → Microphone
3. Ensure device has working microphone
4. Restart Safari
5. Check server logs for audio errors

## Windows Issues

### Application won't start

**Problem:** `ioswebcam.exe` doesn't launch.

**Solutions:**
1. Right-click → Run as Administrator
2. Check Windows Defender or antivirus (may be blocking)
3. Verify executable is not corrupted (redownload)
4. Check Windows Event Viewer for errors
5. Ensure Windows 10/11 64-bit

### Port 5000 already in use

**Problem:** Server fails to start because port 5000 is in use.

**Solutions:**
1. Close other applications using port 5000
2. Use `netstat -ano | findstr :5000` to find the process
3. Kill the process using `taskkill /PID <pid> /F`
4. Or modify app.py to use a different port

### Firewall blocking connection

**Problem:** Windows Firewall blocks the server.

**Solutions:**
1. Allow Python in Windows Firewall
2. Allow `ioswebcam.exe` in Windows Firewall
3. Temporarily disable firewall for testing
4. Add firewall rule for port 5000

## PyInstaller Executable Issues

### Executable size is too large

**Problem:** The .exe file is very large (> 200MB).

**Solutions:**
1. This is normal due to OpenCV and NumPy dependencies
2. Use UPX compression (already enabled in .spec file)
3. Exclude unnecessary modules in .spec file
4. Accept the size as necessary for functionality

### Antivirus false positive

**Problem:** Antivirus flags the executable as malware.

**Solutions:**
1. This is a known issue with PyInstaller executables
2. Add exception in antivirus settings
3. Download from trusted source (GitHub)
4. Verify the file hash matches expected value
5. Consider code signing (requires certificate)

### Missing dependencies in executable

**Problem:** Executable fails with "Module not found" error.

**Solutions:**
1. Check hidden imports in .spec file
2. Rebuild the executable with PyInstaller
3. Ensure all dependencies are in requirements.txt
4. Test in virtual environment before building
5. Check PyInstaller documentation for missing modules

## Advanced Troubleshooting

### Enable Debug Logging

To see detailed error messages:

1. Open `app.py`
2. Change logging level to DEBUG
3. Add more print statements
4. Rebuild executable if needed

### Check Network Connectivity

Use these commands to diagnose network issues:

**On Windows:**
```bash
ping <ios-device-ip>
netstat -ano | findstr :5000
```

**On iOS:**
- Use a network analyzer app
- Check Wi-Fi signal strength
- Test with other network applications

### Monitor Performance

Use these tools to monitor performance:

**Windows:**
- Task Manager (CPU, memory, network)
- Resource Monitor
- Performance Monitor

**iOS:**
- Settings → Battery → Battery Usage
- Settings → Cellular → Cellular Data Options

## Getting Help

If you still have issues after trying these solutions:

1. Check the [GitHub Issues](https://github.com/vicky-2005-18/IOSWebCam/issues) for similar problems
2. Create a new issue with:
   - Windows version
   - iOS version
   - Exact error message
   - Steps to reproduce
   - Server logs (if applicable)
3. Include screenshots if relevant

## Known Limitations

- iOS Safari requires HTTPS for camera access (except localhost)
- Virtual camera requires Unity Capture driver
- Performance depends on network quality
- iOS device screen lock prevention may not work on all iOS versions
- Some antivirus software may flag the executable as false positive
