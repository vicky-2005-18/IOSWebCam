import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO
import pyvirtualcam
import atexit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

frame_count = 0
client_count = 0
cam = None

def cleanup():
    """Cleanup function to close virtual camera on shutdown."""
    global cam
    if cam is not None:
        print("\nClosing virtual camera...")
        cam.close()
        cam = None

atexit.register(cleanup)

def init_virtual_camera():
    """Initialize virtual camera with retry mechanism."""
    global cam
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cam = pyvirtualcam.Camera(width=1280, height=720, fps=30, device="OBS Virtual Camera")
            print(f"Virtual camera initialized: {cam.device}")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
    return False

def check_obs_driver():
    """Check if OBS Virtual Camera driver is available."""
    try:
        # Try to initialize virtual camera to detect driver
        test_cam = pyvirtualcam.Camera(width=1280, height=720, fps=30, device="OBS Virtual Camera")
        test_cam.close()
        print("[OK] OBS Virtual Camera driver detected")
        return True
    except Exception as e:
        print(f"[FAIL] OBS Virtual Camera driver not found")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global client_count
    client_count += 1
    print(f"Client connected. Total clients: {client_count}")
    return {'status': 'connected'}

@socketio.on('disconnect')
def handle_disconnect():
    global client_count
    client_count -= 1
    print("Client disconnected")

@socketio.on('video_frame')
def handle_video_frame(data):
    global frame_count

    # Decode binary JPEG buffer directly
    np_arr = np.frombuffer(data, dtype=np.uint8)
    frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame_bgr is not None:
        frame_count += 1

        # Convert BGR to RGB (required by PyVirtualCam)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        # Add frame counter and client count as overlay for testing
        frame_with_info = frame_rgb.copy()
        cv2.putText(frame_with_info, f"Frame: {frame_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame_with_info, f"Clients: {client_count}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Send frame to virtual camera if available
        if cam is not None:
            try:
                cam.send(frame_with_info)
                cam.sleep_until_next_frame()
            except Exception as e:
                print(f"Error sending frame to virtual camera: {e}")
        else:
            # Debug mode: print frame info to console
            if frame_count % 30 == 0:  # Print every 30 frames to avoid spam
                print(f"Received frame {frame_count} (debug mode - no virtual camera)")

if __name__ == '__main__':
    print("Starting WebCam Bridge Server on port 5000...")
    print("Server binding to 0.0.0.0 for local network access")

    # Check for OBS Virtual Camera driver
    print("\nChecking for OBS Virtual Camera driver...")
    if not check_obs_driver():
        print("\n" + "="*70)
        print("ERROR: OBS Virtual Camera driver not found!")
        print("="*70)
        print("\nTo use this application, you need to install OBS Studio")
        print("which includes the OBS Virtual Camera driver.")
        print("\nInstallation steps:")
        print("1. Download OBS Studio from: https://obsproject.com/")
        print("2. Install OBS Studio")
        print("3. Open OBS Studio and go to Tools > Virtual Camera")
        print("4. Click 'Start' to enable the Virtual Camera")
        print("5. Verify 'OBS Virtual Camera' appears in Windows Device Manager")
        print("\nAfter installation, restart this server.")
        print("="*70 + "\n")
        print("Starting server in debug mode (no virtual camera)...")
        socketio.run(app, host='0.0.0.0', port=5000)
    else:
        # Initialize virtual camera
        print("\nInitializing PyVirtualCam...")
        if init_virtual_camera():
            print(f"Virtual camera started: {cam.device}")
            print(f"Resolution: {cam.width}x{cam.height} @ {cam.fps} FPS")
            print(f"Backend: {cam.backend}")
            print("\nVirtual camera is now available in Windows as 'OBS Virtual Camera'")
            print("You can select it in Zoom, Teams, Meet, OBS Studio, etc.")
            print("\nPress CTRL+C to stop server")
            socketio.run(app, host='0.0.0.0', port=5000)
        else:
            print("Failed to initialize virtual camera after retries")
            print("Starting server in debug mode (no virtual camera)...")
            socketio.run(app, host='0.0.0.0', port=5000)