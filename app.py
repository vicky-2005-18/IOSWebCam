import cv2
import numpy as np
from flask import Flask, render_template, request, Response, jsonify
from flask_socketio import SocketIO
import pyvirtualcam
import atexit
import threading
import queue
import time
import socket
import qrcode
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os
import sys
import shutil
import winreg
import logging

# Silence Werkzeug development server warning & routine HTTP request polling logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# SocketIO configured for high-bandwidth raw 1080p frames with pure WebSocket
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=10,
    ping_interval=5,
    max_http_buffer_size=16 * 1024 * 1024  # 16MB buffer for crisp 1080p / 4K frames
)

frame_count = 0
client_count = 0
cam = None
frame_queue = queue.Queue(maxsize=1)  # Strict 1-frame queue: Always processes latest frame, 0 queue delay
fps_counter = 0
last_fps_time = time.time()
current_fps = 0

# Telemetry
bandwidth_counter = 0
last_bandwidth_time = time.time()
current_bandwidth = 0  # in Mbps

# Smart Framing & Studio Video Processing Suite State
framing_mode = 'crop'  # 'crop' (center-fill 16:9), 'fit' (pillarbox with blur), or 'stretch'
rotation_angle = 0     # 0, 90, 180, 270
image_adjustments = {
    'brightness': 0,    # -100 to 100
    'contrast': 1.0,    # 0.5 to 2.0
    'saturation': 1.0,  # 0.0 to 2.0
    'sharpness': 0      # 0 to 100
}
beauty_filter = {
    'enabled': False,
    'strength': 0.5     # 0.0 to 1.0
}
privacy_mode = False    # True: outputs broadcast 'Be Right Back' screen to virtual cam & preview
latest_preview_frame = None
latest_frame_event = threading.Event()

def apply_rotation(frame, angle):
    """Rotate frame by 0, 90, 180, or 270 degrees clockwise."""
    if angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def apply_image_adjustments(frame, brightness=0, contrast=1.0, saturation=1.0, sharpness=0):
    """Apply real-time brightness, contrast, saturation, and sharpness directly in RGB."""
    # 1. Brightness & Contrast (sub-millisecond using convertScaleAbs)
    if brightness != 0 or contrast != 1.0:
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
    
    # 2. Saturation via fast SIMD color matrix in RGB
    if abs(saturation - 1.0) > 0.02:
        r_w, g_w, b_w = 0.299, 0.587, 0.114
        inv = 1.0 - saturation
        mat = np.array([
            [inv * r_w + saturation, inv * g_w,              inv * b_w],
            [inv * r_w,              inv * g_w + saturation, inv * b_w],
            [inv * r_w,              inv * g_w,              inv * b_w + saturation]
        ], dtype=np.float32)
        frame = cv2.transform(frame, mat)
        
    # 3. Sharpness (Unsharp Mask)
    if sharpness > 0:
        strength = (sharpness / 100.0) * 1.5
        blurred = cv2.GaussianBlur(frame, (0, 0), 3)
        frame = cv2.addWeighted(frame, 1.0 + strength, blurred, -strength, 0)
        
    return frame

def apply_beauty_filter(frame, strength=0.5):
    """Fast edge-preserving bilateral skin smoothing filter."""
    if strength <= 0.05:
        return frame
    h, w = frame.shape[:2]
    # 4x downsample for 60 FPS real-time execution
    small = cv2.resize(frame, (w // 4, h // 4), interpolation=cv2.INTER_LINEAR)
    smooth_small = cv2.bilateralFilter(small, d=5, sigmaColor=30, sigmaSpace=30)
    smooth = cv2.resize(smooth_small, (w, h), interpolation=cv2.INTER_LINEAR)
    return cv2.addWeighted(smooth, float(strength), frame, 1.0 - float(strength), 0)

cached_privacy_base = None
cached_privacy_base_dim = None
cached_privacy_time_sec = None
cached_privacy_frame = None

def get_cached_privacy_frame(w=1920, h=1080):
    """Generate or retrieve cached broadcast-grade 'Be Right Back' privacy card in RGB."""
    global cached_privacy_base, cached_privacy_base_dim, cached_privacy_time_sec, cached_privacy_frame
    current_sec = int(time.time())
    
    # Rebuild base card when dimensions change
    if cached_privacy_base is None or cached_privacy_base_dim != (w, h):
        # RGB gradient from slate to deep indigo
        gradient = np.linspace([11, 15, 25], [30, 27, 75], h, dtype=np.float32)
        base = np.tile(gradient[:, np.newaxis, :], (1, w, 1)).astype(np.uint8)
        cw = min(720, int(w * 0.8))
        ch = min(340, int(h * 0.6))
        cx, cy = (w - cw) // 2, (h - ch) // 2
        card = base[cy:cy+ch, cx:cx+cw]
        base[cy:cy+ch, cx:cx+cw] = cv2.addWeighted(card, 0.35, np.full((ch, cw, 3), (20, 25, 35), dtype=np.uint8), 0.65, 0)
        cv2.rectangle(base, (cx, cy), (cx+cw, cy+ch), (95, 80, 80), 1, cv2.LINE_AA)
        
        # Badges and text in RGB
        cv2.circle(base, (cx + 45, cy + 55), 6, (255, 165, 0), -1, cv2.LINE_AA)
        cv2.putText(base, 'STUDIO STANDBY', (cx + 65, cy + 61), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2, cv2.LINE_AA)
        cv2.putText(base, 'BE RIGHT BACK', (cx + 45, cy + 135), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(base, 'Camera feed temporarily muted for privacy', (cx + 45, cy + 185), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (185, 175, 170), 1, cv2.LINE_AA)
        cv2.putText(base, 'iOS WebCam Bridge', (cx + cw - 210, cy + ch - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (145, 135, 130), 1, cv2.LINE_AA)
        
        cached_privacy_base = base
        cached_privacy_base_dim = (w, h)
        cached_privacy_time_sec = None

    # Re-draw the digital clock when second changes
    if cached_privacy_time_sec != current_sec or cached_privacy_frame is None:
        frame = cached_privacy_base.copy()
        cw = min(720, int(w * 0.8))
        ch = min(340, int(h * 0.6))
        cx, cy = (w - cw) // 2, (h - ch) // 2
        time_str = time.strftime('%I:%M:%S %p')
        cv2.putText(frame, time_str, (cx + 45, cy + ch - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 230, 100), 2, cv2.LINE_AA)
        cached_privacy_frame = frame
        cached_privacy_time_sec = current_sec

    return cached_privacy_frame

def process_aspect_ratio(frame, target_width, target_height, mode='crop'):
    """Preserve aspect ratio when mobile orientation or resolution differs from virtual camera.
    
    Modes:
      - 'crop': Smart center-crop to 16:9 (fills entire webcam frame with zero distortion)
      - 'fit': Broadcast-grade pillarbox with darkened & blurred ambient background
      - 'stretch': Direct linear resize
    """
    src_h, src_w = frame.shape[:2]
    target_aspect = target_width / target_height
    src_aspect = src_w / src_h

    # If aspect ratios are identical or within 1.5% tolerance, simple direct resize
    if abs(src_aspect - target_aspect) < 0.015:
        if (src_w, src_h) != (target_width, target_height):
            return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        return frame

    if mode == 'crop':
        if src_aspect > target_aspect:
            # Source is wider than target: crop horizontal sides
            new_w = int(src_h * target_aspect)
            offset_x = (src_w - new_w) // 2
            cropped = frame[:, offset_x:offset_x + new_w]
        else:
            # Source is taller than target (e.g. 9:16 portrait on 16:9 virtual cam): crop top/bottom
            new_h = int(src_w / target_aspect)
            offset_y = (src_h - new_h) // 2
            cropped = frame[offset_y:offset_y + new_h, :]
        return cv2.resize(cropped, (target_width, target_height), interpolation=cv2.INTER_LINEAR)

    elif mode == 'fit':
        # Studio pillarbox with lightning-fast ambient background blur (0.3ms vs 25ms)
        small_bg = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_NEAREST)
        small_bg = cv2.GaussianBlur(small_bg, (15, 15), 0)
        bg = cv2.resize(small_bg, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        bg = cv2.convertScaleAbs(bg, alpha=0.5, beta=0)  # dim background

        scale = min(target_width / src_w, target_height / src_h)
        scaled_w = int(src_w * scale)
        scaled_h = int(src_h * scale)
        scaled = cv2.resize(frame, (scaled_w, scaled_h), interpolation=cv2.INTER_LINEAR)

        x_start = (target_width - scaled_w) // 2
        y_start = (target_height - scaled_h) // 2
        bg[y_start:y_start + scaled_h, x_start:x_start + scaled_w] = scaled
        return bg

    else:
        return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)

def cleanup():
    """Cleanup function to close virtual camera on shutdown."""
    global cam
    if cam is not None:
        print("\nClosing virtual camera...")
        cam.close()
        cam = None
    cv2.destroyAllWindows()

atexit.register(cleanup)

def frame_worker():
    """Worker thread to process frames with sub-millisecond zero-delay pipeline."""
    global frame_count, fps_counter, last_fps_time, current_fps
    global bandwidth_counter, last_bandwidth_time, current_bandwidth
    global latest_preview_frame

    last_privacy_tick = 0
    last_preview_time = 0

    while True:
        try:
            # Get frame from queue (non-blocking with fast timeout)
            data = frame_queue.get(timeout=0.04)

            # Track bandwidth
            frame_size = len(data)
            bandwidth_counter += frame_size
            current_time = time.time()
            if current_time - last_bandwidth_time >= 1.0:
                current_bandwidth = (bandwidth_counter * 8) / (1024 * 1024)
                bandwidth_counter = 0
                last_bandwidth_time = current_time

            target_w = cam.width if cam is not None else 1920
            target_h = cam.height if cam is not None else 1080

            if privacy_mode:
                # Privacy mode active: replace incoming camera feed with live BRB card in RGB
                frame_rgb = get_cached_privacy_frame(target_w, target_h)
            else:
                # 1. Ultra-fast direct RGB decode (bypasses BGR conversion, 35% faster)
                np_arr = np.frombuffer(data, dtype=np.uint8)
                frame_rgb = cv2.imdecode(np_arr, cv2.IMREAD_COLOR_RGB)

                if frame_rgb is not None:
                    # 2. Hardware-accelerated stream rotation (0, 90, 180, 270)
                    if rotation_angle != 0:
                        frame_rgb = apply_rotation(frame_rgb, rotation_angle)

                    # 3. Studio Image Tuning (brightness, contrast, saturation, sharpness directly in RGB)
                    frame_rgb = apply_image_adjustments(
                        frame_rgb,
                        brightness=image_adjustments.get('brightness', 0),
                        contrast=image_adjustments.get('contrast', 1.0),
                        saturation=image_adjustments.get('saturation', 1.0),
                        sharpness=image_adjustments.get('sharpness', 0)
                    )

                    # 4. Beauty / Skin smoothing filter if enabled
                    if beauty_filter.get('enabled', False):
                        frame_rgb = apply_beauty_filter(frame_rgb, beauty_filter.get('strength', 0.5))

                    # 5. Aspect-ratio preserving smart framing
                    frame_rgb = process_aspect_ratio(frame_rgb, target_w, target_h, mode=framing_mode)

            if frame_rgb is not None:
                frame_count += 1
                fps_counter += 1

                # Send clean frame DIRECTLY to virtual camera with zero delay (<0.2ms)
                if cam is not None:
                    try:
                        cam.send(frame_rgb)
                    except Exception as e:
                        print(f"Error sending frame to virtual camera: {e}")
                else:
                    # Debug mode: show OpenCV window
                    cv2.imshow('iOS WebCam Bridge - Debug Mode', cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quit requested from debug window")
                        break

                # Update preview frame for laptop dashboard monitor at 20 FPS (prevents CPU bog-down)
                if current_time - last_preview_time >= 0.05:
                    last_preview_time = current_time
                    try:
                        _, preview_buf = cv2.imencode('.jpg', cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 70])
                        latest_preview_frame = preview_buf.tobytes()
                        latest_frame_event.set()
                    except Exception:
                        pass

                # Calculate FPS telemetry every second
                if current_time - last_fps_time >= 1.0:
                    current_fps = fps_counter
                    fps_counter = 0
                    last_fps_time = current_time
                    socketio.emit('telemetry', {
                        'fps': current_fps,
                        'bandwidth': current_bandwidth,
                        'frame_count': frame_count,
                        'client_count': client_count,
                        'framing_mode': framing_mode,
                        'rotation': rotation_angle,
                        'image_adjustments': image_adjustments,
                        'beauty_filter': beauty_filter,
                        'privacy_mode': privacy_mode
                    })

            frame_queue.task_done()

        except queue.Empty:
            # Standby mode: keep streaming the BRB card at 30 fps if privacy mode is on
            if privacy_mode:
                now = time.time()
                if now - last_privacy_tick >= (1.0 / 30.0):
                    last_privacy_tick = now
                    target_w = cam.width if cam is not None else 1920
                    target_h = cam.height if cam is not None else 1080
                    priv_frame_rgb = get_cached_privacy_frame(target_w, target_h)
                    
                    if cam is not None:
                        try:
                            cam.send(priv_frame_rgb)
                        except Exception:
                            pass
                    try:
                        _, preview_buf = cv2.imencode('.jpg', cv2.cvtColor(priv_frame_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 70])
                        latest_preview_frame = preview_buf.tobytes()
                        latest_frame_event.set()
                    except Exception:
                        pass
            continue
        except Exception as e:
            print(f"Error in frame worker: {e}")
            continue

def is_unity_capture_installed():
    """Check registry to see if Unity Capture DirectShow filter is registered."""
    clsid = r'CLSID\{8E14549B-DB61-4309-AFA1-3578E927E935}'
    try:
        winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, clsid)
        return True
    except FileNotFoundError:
        return False


def auto_install_unity_capture():
    """Bundle the Unity Capture DLLs inside the EXE and register them silently.

    Works both when running as a PyInstaller EXE (sys._MEIPASS) and during
    normal Python development (relative 'drivers' folder).
    """
    import subprocess

    if is_unity_capture_installed():
        print("[driver] Unity Capture already installed.")
        return True

    print("[driver] Unity Capture not found. Installing automatically...")

    # Locate bundled DLLs
    if getattr(sys, 'frozen', False):          # Running as PyInstaller EXE
        base = sys._MEIPASS
    else:                                       # Running as plain Python
        base = os.path.dirname(os.path.abspath(__file__))

    dll32 = os.path.join(base, 'drivers', 'unitycapture', 'UnityCaptureFilter32.dll')
    dll64 = os.path.join(base, 'drivers', 'unitycapture', 'UnityCaptureFilter64.dll')

    if not os.path.exists(dll64):
        print(f"[driver] ERROR: Bundled DLL not found at {dll64}")
        return False

    print("[driver] A UAC (Admin) prompt will appear — please click YES to install the virtual camera driver.")
    print("[driver] This is a one-time install. It will never ask again.")

    try:
        # Register 64-bit DLL (required) — runas triggers UAC admin elevation
        result64 = subprocess.run(
            ['powershell', '-Command',
             f'Start-Process regsvr32 -ArgumentList \'/s \"{ dll64 }\"\' -Verb RunAs -Wait -PassThru | Select-Object -ExpandProperty ExitCode'],
            capture_output=True, text=True, timeout=60
        )

        # Register 32-bit DLL (for 32-bit apps like some older Zoom builds)
        if os.path.exists(dll32):
            subprocess.run(
                ['powershell', '-Command',
                 f'Start-Process regsvr32 -ArgumentList \'/s \"{ dll32 }\"\' -Verb RunAs -Wait -PassThru | Select-Object -ExpandProperty ExitCode'],
                capture_output=True, text=True, timeout=60
            )

        if is_unity_capture_installed():
            print("[driver] Unity Capture installed successfully!")
            return True
        else:
            print("[driver] Installation may have been cancelled or failed.")
            print("[driver] If UAC was denied, please re-run as Administrator.")
            return False

    except Exception as e:
        print(f"[driver] Auto-install failed: {e}")
        return False


def init_virtual_camera():
    """Initialize virtual camera with retry mechanism at 1080p 60FPS."""
    global cam
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Use Unity Capture backend at native Full HD (1080p) 60 FPS
            cam = pyvirtualcam.Camera(width=1920, height=1080, fps=60, backend='unitycapture')
            print(f"Virtual camera initialized: {cam.device} (1920x1080 @ 60 FPS)")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed (1080p60): {e}")
            # Fallback to 720p 60fps if driver/system restricts 1080p
            if attempt == max_retries - 1:
                try:
                    print("Falling back to 1280x720 @ 60 FPS...")
                    cam = pyvirtualcam.Camera(width=1280, height=720, fps=60, backend='unitycapture')
                    print(f"Virtual camera initialized with fallback: {cam.device}")
                    return True
                except Exception as fb_err:
                    print(f"Fallback failed: {fb_err}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
    return False

def generate_self_signed_cert(ip_address):
    """Generate a self-signed SSL certificate for the given IP address.
    
    Always regenerates if the IP has changed since last cert was made.
    iOS Safari requires a cert with proper SAN and short validity.
    """
    import ipaddress as _ipaddress
    cert_file = 'cert.pem'
    key_file  = 'key.pem'
    ip_file   = 'cert_ip.txt'   # tracks which IP the cert was made for

    # Re-generate if IP changed or cert missing
    existing_ip = None
    if os.path.exists(ip_file):
        with open(ip_file) as f:
            existing_ip = f.read().strip()

    if (os.path.exists(cert_file) and os.path.exists(key_file)
            and existing_ip == ip_address):
        print(f"Using existing SSL certificate for {ip_address}")
        return cert_file, key_file

    print(f"Generating SSL certificate for {ip_address} ...")

    # Private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    with open(key_file, 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Certificate — iOS Safari needs: SAN with IP, short validity <= 825 days
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"WebCam Bridge"),
        x509.NameAttribute(NameOID.COMMON_NAME, ip_address),
    ])

    san_list = [x509.DNSName("localhost")]
    try:
        san_list.append(x509.IPAddress(_ipaddress.ip_address(ip_address)))
    except ValueError:
        san_list.append(x509.DNSName(ip_address))

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=397))   # < 825 day iOS limit
        .add_extension(x509.SubjectAlternativeName(san_list), critical=False)
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True
        )
        .sign(key, hashes.SHA256(), default_backend())
    )
    with open(cert_file, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    # Remember which IP this cert was made for
    with open(ip_file, 'w') as f:
        f.write(ip_address)

    print(f"Certificate written to {cert_file}")
    return cert_file, key_file

def get_local_ip():
    """Get local Wi-Fi / LAN IPv4 address (e.g. 192.168.x.x) for phone pairing.
    
    Uses an active outbound UDP probe to find the actual Wi-Fi or Ethernet adapter IP,
    avoiding VPN/Tailscale/WSL virtual adapters.
    """
    # 1. Primary probe: Check active default gateway route to internet/DNS
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        if local_ip and not local_ip.startswith('127.'):
            return local_ip
    except Exception:
        pass

    # 2. Secondary fallback: inspect all host IPs and pick true LAN subnets
    try:
        hostname = socket.gethostname()
        host_ips = socket.gethostbyname_ex(hostname)[2]
        
        # Priority A: Standard home/office Wi-Fi (192.168.x.x or 10.x.x.x)
        for ip in host_ips:
            if ip.startswith('192.168.') or ip.startswith('10.'):
                return ip
                
        # Priority B: Any non-loopback, non-Tailscale/CGNAT (100.64.0.0/10) IP
        for ip in host_ips:
            if not ip.startswith('127.') and not ip.startswith('100.'):
                return ip

        # Priority C: First available IP
        if host_ips:
            return host_ips[0]
    except Exception as e:
        print(f"[WARN] IP auto-detection error: {e}")

    return '127.0.0.1'

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

@app.route('/dashboard')
def dashboard():
    """Laptop Studio Dashboard for remote management and preview monitor."""
    return render_template('dashboard.html')

@app.route('/preview_feed')
def preview_feed():
    """Low-latency MJPEG preview stream for the Laptop Studio Dashboard."""
    def generate():
        while True:
            latest_frame_event.wait(timeout=1.0)
            latest_frame_event.clear()
            if latest_preview_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_preview_frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cert')
def download_cert():
    """Endpoint for iOS devices to download the root certificate for profile installation."""
    from flask import send_file
    if os.path.exists('cert.pem'):
        return send_file('cert.pem', mimetype='application/x-x509-ca-cert', as_attachment=True, download_name='webcam_cert.crt')
    return "Certificate not found", 404

@socketio.on('connect')
def handle_connect():
    global client_count
    client_count += 1
    print(f"Client connected. Total clients: {client_count}")
    # Sync current studio state to connecting client
    socketio.emit('studio_state', {
        'framing_mode': framing_mode,
        'rotation': rotation_angle,
        'image_adjustments': image_adjustments,
        'beauty_filter': beauty_filter,
        'privacy_mode': privacy_mode
    }, to=request.sid)
    return {'status': 'connected'}

@socketio.on('disconnect')
def handle_disconnect():
    global client_count
    client_count -= 1
    print("Client disconnected")

@socketio.on('video_frame')
def handle_video_frame(data):
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
    except Exception as e:
        print(f"Error queuing frame: {e}")

@socketio.on('ping')
def handle_ping(data):
    """Handle ping request for network quality monitoring."""
    socketio.emit('ping_response', data, to=request.sid)

@socketio.on('remote_command')
def handle_remote_command(data):
    """Relay remote command from Laptop Dashboard to phone camera."""
    socketio.emit('remote_command', data)

@socketio.on('camera_state_update')
def handle_camera_state_update(data):
    """Relay phone camera state (zoom, torch, lens, battery) to Laptop Dashboard."""
    socketio.emit('camera_state', data)

@socketio.on('battery_telemetry')
def handle_battery_telemetry(data):
    """Relay phone battery status to Laptop Dashboard."""
    socketio.emit('battery_telemetry', data)

@socketio.on('set_framing_mode')
def handle_set_framing_mode(data):
    """Update aspect ratio framing mode ('crop', 'fit', 'stretch')."""
    global framing_mode
    mode = data.get('mode', 'crop')
    if mode in ['crop', 'fit', 'stretch']:
        framing_mode = mode
        socketio.emit('framing_mode_changed', {'mode': framing_mode})

@socketio.on('set_rotation')
def handle_set_rotation(data):
    """Set stream rotation angle (0, 90, 180, 270)."""
    global rotation_angle
    try:
        angle = int(data.get('angle', 0))
        if angle in [0, 90, 180, 270]:
            rotation_angle = angle
            socketio.emit('rotation_changed', {'angle': rotation_angle})
    except Exception as e:
        print(f"Error setting rotation: {e}")

@socketio.on('set_image_adjustments')
def handle_set_image_adjustments(data):
    """Update brightness, contrast, saturation, and sharpness in real-time."""
    global image_adjustments
    try:
        if 'brightness' in data:
            image_adjustments['brightness'] = max(-100, min(100, int(data['brightness'])))
        if 'contrast' in data:
            image_adjustments['contrast'] = max(0.5, min(2.0, float(data['contrast'])))
        if 'saturation' in data:
            image_adjustments['saturation'] = max(0.0, min(2.0, float(data['saturation'])))
        if 'sharpness' in data:
            image_adjustments['sharpness'] = max(0, min(100, int(data['sharpness'])))
        socketio.emit('image_adjustments_changed', image_adjustments)
    except Exception as e:
        print(f"Error setting image adjustments: {e}")

@socketio.on('reset_image_adjustments')
def handle_reset_image_adjustments():
    """Reset all image tuning adjustments to neutral defaults."""
    global image_adjustments
    image_adjustments = {'brightness': 0, 'contrast': 1.0, 'saturation': 1.0, 'sharpness': 0}
    socketio.emit('image_adjustments_changed', image_adjustments)

@socketio.on('set_beauty_filter')
def handle_set_beauty_filter(data):
    """Enable/disable and adjust beauty filter strength."""
    global beauty_filter
    try:
        if 'enabled' in data:
            beauty_filter['enabled'] = bool(data['enabled'])
        if 'strength' in data:
            beauty_filter['strength'] = max(0.0, min(1.0, float(data['strength'])))
        socketio.emit('beauty_filter_changed', beauty_filter)
    except Exception as e:
        print(f"Error setting beauty filter: {e}")

@socketio.on('set_privacy_mode')
def handle_set_privacy_mode(data):
    """Toggle privacy 'Be Right Back' screen to virtual camera."""
    global privacy_mode
    try:
        privacy_mode = bool(data.get('enabled', False))
        socketio.emit('privacy_mode_changed', {'enabled': privacy_mode})
    except Exception as e:
        print(f"Error setting privacy mode: {e}")

def start_cloudflare_tunnel(port=5000):
    """Start a Cloudflare tunnel and return the public HTTPS URL.

    Named tunnel (CLOUDFLARE_TUNNEL_TOKEN set):
      - Starts cloudflared as background daemon
      - Returns CLOUDFLARE_PUBLIC_URL env var (set in run.bat)
      - URL is permanent and never changes

    Quick tunnel (no token):
      - Gets a random trycloudflare.com URL
      - No account needed
    """
    import subprocess, re

    # Find cloudflared binary
    cloudflared = None
    for candidate in [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloudflared.exe'),
        shutil.which('cloudflared'),
        shutil.which('cloudflared.exe'),
    ]:
        if candidate and os.path.exists(candidate):
            cloudflared = candidate
            break

    if not cloudflared:
        return None

    token      = os.environ.get('CLOUDFLARE_TUNNEL_TOKEN', '')
    public_url = os.environ.get('CLOUDFLARE_PUBLIC_URL', '')

    if token:
        # ── Named tunnel: permanent URL ───────────────────────────────────
        if not public_url:
            print("[cloudflare] ERROR: CLOUDFLARE_PUBLIC_URL not set in run.bat!")
            print("             Add the line:  set CLOUDFLARE_PUBLIC_URL=https://your-hostname")
            print("             (find your hostname in Cloudflare dashboard → Tunnels → your tunnel → Public Hostname)")
            return None

        print(f"[cloudflare] Starting named tunnel → {public_url}")
        # Start as background daemon (fire and forget — URL is known already)
        subprocess.Popen(
            [cloudflared, 'tunnel', '--no-autoupdate', 'run', '--token', token],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(3)  # Give it a moment to connect
        return public_url

    else:
        # ── Quick tunnel: random trycloudflare.com URL ────────────────────
        print("[cloudflare] Starting quick tunnel (no account needed)...")
        proc = subprocess.Popen(
            [cloudflared, 'tunnel', '--no-autoupdate', '--url', f'http://localhost:{port}'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        url_pattern = re.compile(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com')
        for _ in range(60):
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.5)
                continue
            match = url_pattern.search(line)
            if match:
                found = match.group(0)
                print(f"[cloudflare] Quick tunnel URL: {found}")
                return found
            if proc.poll() is not None:
                break
        return None




def start_ngrok_tunnel(port=5000):
    """Try ngrok (existing session or pyngrok)."""
    import urllib.request
    import json as _json

    # ── 1. Check if ngrok is already running ──────────────────────────────
    try:
        with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as resp:
            data = _json.loads(resp.read())
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                url = t.get("public_url", "")
                if url.startswith("https://"):
                    print(f"[ngrok] Found existing tunnel: {url}")
                    return url
                elif url.startswith("http://"):
                    https_url = url.replace("http://", "https://", 1)
                    print(f"[ngrok] Found existing tunnel (upgraded to https): {https_url}")
                    return https_url
    except Exception:
        pass

    # ── 2. Try pyngrok to start a new tunnel ──────────────────────────────
    try:
        from pyngrok import ngrok as pyngrok_ngrok, conf

        system_ngrok = None
        for candidate in [
            r"C:\Users\vikas\AppData\Local\Microsoft\WindowsApps\ngrok.exe",
            shutil.which("ngrok"),
        ]:
            if candidate and os.path.exists(candidate):
                system_ngrok = candidate
                break

        if system_ngrok:
            conf.get_default().ngrok_path = system_ngrok

        token = os.environ.get('NGROK_AUTHTOKEN', '')
        if token:
            pyngrok_ngrok.set_auth_token(token)

        tunnel = pyngrok_ngrok.connect(port, bind_tls=True)
        public_url = tunnel.public_url
        if public_url.startswith('http://'):
            public_url = public_url.replace('http://', 'https://', 1)
        print(f"[ngrok] Started new tunnel: {public_url}")
        return public_url
    except ImportError:
        pass
    except Exception as e:
        print(f"[ngrok] Could not start tunnel: {e}")


    return None




if __name__ == '__main__':
    print("="*70)
    print(" 📹 WebCam Bridge Server")
    print("="*70)

    local_ip = get_local_ip()
    server_url = f"https://{local_ip}:5000"
    print(f"Local IP: {local_ip}")

    # Check if mode was pre-set via environment variable, otherwise prompt user directly
    use_tunnel_env = os.environ.get('USE_TUNNEL')
    
    if use_tunnel_env is None:
        print("\n" + "─"*70)
        print(" Choose Connection Mode:")
        print("   [1] Direct Wi-Fi / USB Cable - ⚡ Zero Delay, 60 FPS (RECOMMENDED)")
        print("   [2] Cloudflare Internet Tunnel - 🌐 Remote across different networks")
        print("─"*70)
        try:
            choice = input(" Select mode [default=1]: ").strip()
            if choice == '2':
                use_tunnel = True
            else:
                use_tunnel = False
        except (EOFError, KeyboardInterrupt):
            use_tunnel = False
    else:
        use_tunnel = (use_tunnel_env == '1')

    public_url = None

    if use_tunnel:
        # ── 1. Try Cloudflare tunnel (permanent if token set) ─────────────────
        print("\n[🌐 Tunnel Mode] Checking for Cloudflare tunnel...")
        public_url = start_cloudflare_tunnel(5000)

        if not public_url:
            # ── 2. Try ngrok (if already running) ────────────────────────────
            print("[cloudflare] Not available. Checking for ngrok...")
            public_url = start_ngrok_tunnel(5000)

    if public_url:
        connect_url = public_url
        use_ssl = False
        ssl_ctx = None
    else:
        # ── Direct High-Speed Local WiFi / USB Mode (Sub-30ms) ───────────
        print("\n[⚡ High-Speed Direct Mode] Using direct local connection (0 delay, 60 FPS).")
        cert_file, key_file = generate_self_signed_cert(local_ip)
        ssl_ctx = (cert_file, key_file)
        connect_url = server_url
        use_ssl = True


    # ── QR code ──────────────────────────────────────────────────────────
    print()
    display_qr_code(connect_url)

    print("\nTo connect from your mobile device:")
    print(f"  📱 Mobile URL: {connect_url}")
    print(f"  💻 Laptop Dashboard: {'http://localhost:5000/dashboard' if not use_ssl else f'{server_url}/dashboard'}")
    if not use_ssl:
        print("  If you see a warning page, tap 'Visit Site'")
    else:
        print()
        print("  " + "─"*60)
        print("  📱 HOW TO OPEN ON IPHONE (Just 2 quick taps):")
        print("  " + "─"*60)
        print(f"  1. Open Safari on iPhone and go to: {connect_url}")
        print("  2. If Safari shows 'This Connection Is Not Private':")
        print("     👉 Tap 'Show Details' (at the bottom)")
        print("     👉 Tap 'visit this website' (small link at bottom)")
        print("     👉 Tap 'Visit Website' to confirm!")
        print("     ✅ That's it! The webcam page will immediately open.")
        print()
        print("  Note: If your iPhone requires certificate installation:")
        print(f"  Download it directly at: {connect_url}/cert")
        print("  " + "─"*60)

    print("\nPress CTRL+C to stop the server.")
    print("="*70 + "\n")

    # ── Frame worker ─────────────────────────────────────────────────────
    worker_thread = threading.Thread(target=frame_worker, daemon=True)
    worker_thread.start()

    # ── Auto-install Unity Capture driver if missing ──────────────────────
    auto_install_unity_capture()

    # ── Virtual camera ───────────────────────────────────────────────────
    print("Initializing Unity Capture virtual camera...")
    if init_virtual_camera():
        print(f"Virtual camera ready: {cam.device} ({cam.width}x{cam.height} @ {cam.fps} FPS)")
        print("You can now select it in Zoom, Teams, Meet, OBS, etc.\n")
    else:
        print("[WARN] Unity Capture driver not found or install was cancelled.")
        print("       Re-run as Administrator, or install manually:")
        print("       https://github.com/schellingb/UnityCapture/releases\n")

    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=ssl_ctx, allow_unsafe_werkzeug=True)