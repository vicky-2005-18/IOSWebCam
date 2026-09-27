import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO
import pyvirtualcam
import atexit
import threading
import queue
import time
import socket
import qrcode

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

frame_count = 0
client_count = 0
cam = None
frame_queue = queue.Queue(maxsize=30)  # Limit queue to prevent memory overflow
fps_counter = 0
last_fps_time = time.time()
current_fps = 0

# Telemetry
bandwidth_counter = 0
last_bandwidth_time = time.time()
current_bandwidth = 0  # in Mbps

def cleanup():
    """Cleanup function to close virtual camera on shutdown."""
    global cam
    if cam is not None:
        print("\nClosing virtual camera...")
        cam.close()
        cam = None

atexit.register(cleanup)

def frame_worker():
    """Worker thread to process frames asynchronously."""
    global frame_count, fps_counter, last_fps_time, current_fps
    global bandwidth_counter, last_bandwidth_time, current_bandwidth

    while True:
        try:
            # Get frame from queue (non-blocking with timeout)
            data = frame_queue.get(timeout=0.1)

            # Track bandwidth
            frame_size = len(data)
            bandwidth_counter += frame_size
            current_time = time.time()
            if current_time - last_bandwidth_time >= 1.0:
                # Calculate bandwidth in Mbps
                current_bandwidth = (bandwidth_counter * 8) / (1024 * 1024)
                bandwidth_counter = 0
                last_bandwidth_time = current_time

            # Decode binary JPEG buffer
            np_arr = np.frombuffer(data, dtype=np.uint8)
            frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame_bgr is not None:
                frame_count += 1
                fps_counter += 1

                # Calculate FPS every second
                if current_time - last_fps_time >= 1.0:
                    current_fps = fps_counter
                    fps_counter = 0
                    last_fps_time = current_time
                    # Send telemetry to all clients
                    socketio.emit('telemetry', {
                        'fps': current_fps,
                        'bandwidth': current_bandwidth,
                        'frame_count': frame_count,
                        'client_count': client_count
                    }, broadcast=True)

                # Convert BGR to RGB (required by PyVirtualCam)
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                # Add telemetry overlay
                frame_with_info = frame_rgb.copy()
                cv2.putText(frame_with_info, f"FPS: {current_fps}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame_with_info, f"Frame: {frame_count}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame_with_info, f"Clients: {client_count}", (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame_with_info, f"Bandwidth: {current_bandwidth:.1f} Mbps", (10, 150),
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
                    if frame_count % 30 == 0:
                        print(f"Processed frame {frame_count} (debug mode - no virtual camera)")

            frame_queue.task_done()

        except queue.Empty:
            # No frames in queue, continue
            continue
        except Exception as e:
            print(f"Error in frame worker: {e}")
            continue

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
        print("[FAIL] OBS Virtual Camera driver not found")
        return False

def get_local_ip():
    """Get local IPv4 address for auto-discovery."""
    try:
        # Get hostname and resolve to IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Verify it's an IPv4 address
        if local_ip.startswith('127.') or local_ip == '::1':
            # Fallback to 0.0.0.0 if localhost
            return '0.0.0.0'

        return local_ip
    except Exception as e:
        print(f"[WARN] Could not detect local IP: {e}")
        return '0.0.0.0'

def display_qr_code(url):
    """Generate and display QR code for the given URL."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        print("\n" + "="*70)
        print("Scan this QR code with your mobile device:")
        print("="*70)
        qr.print_ascii(invert=True)
        print("="*70)
        print(f"Or navigate to: {url}")
        print("="*70 + "\n")
    except Exception as e:
        # QR code generation failed (likely console encoding issue)
        print("\n" + "="*70)
        print("QR Code Display")
        print("="*70)
        print(f"Navigate to: {url}")
        print("="*70 + "\n")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect(sid):
    global client_count
    client_count += 1
    print(f"Client connected. Total clients: {client_count}")
    return {'status': 'connected'}

@socketio.on('disconnect')
def handle_disconnect(sid):
    global client_count
    client_count -= 1
    print("Client disconnected")

@socketio.on('video_frame')
def handle_video_frame(data, sid):
    """Queue incoming frame for async processing."""
    try:
        # Put frame in queue (non-blocking)
        if frame_queue.full():
            # Drop oldest frame if queue is full
            try:
                frame_queue.get_nowait()
                frame_queue.task_done()
            except queue.Empty:
                pass

        frame_queue.put_nowait(data)
        # Send acknowledgment for packet loss tracking
        socketio.emit('frame_ack', to=sid)
    except Exception as e:
        print(f"Error queuing frame: {e}")

@socketio.on('ping')
def handle_ping(data, sid):
    """Handle ping request for network quality monitoring."""
    socketio.emit('ping_response', data, to=sid)

if __name__ == '__main__':
    print("Starting WebCam Bridge Server on port 5000...")

    # Detect local IP address
    local_ip = get_local_ip()
    server_url = f"http://{local_ip}:5000"
    print(f"\nDetected local IP address: {local_ip}")
    print(f"Server URL: {server_url}")
    print("\nTo connect from your mobile device:")
    print(f"1. Ensure your device is on the same Wi-Fi network")
    print(f"2. Open Safari and navigate to: {server_url}")
    print(f"3. Grant camera permission when prompted")
    print(f"Note: iOS requires HTTPS for camera access. Use ngrok for remote testing.")

    # Display QR code for easy mobile connection
    display_qr_code(server_url)

    print("\nServer binding to 0.0.0.0 for local network access")

    # Start frame worker thread
    print("\nStarting frame processing worker...")
    worker_thread = threading.Thread(target=frame_worker, daemon=True)
    worker_thread.start()
    print("Frame worker started")

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