import cv2
import numpy as np
from flask import Flask, render_template, request
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

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

frame_count = 0
client_count = 0
cam = None
frame_queue = queue.Queue(maxsize=2)  # Low buffer to ensure real-time zero delay
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
    cv2.destroyAllWindows()

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

                # Ensure frame matches virtual camera dimensions (1280x720)
                if cam is not None and (frame_bgr.shape[1] != cam.width or frame_bgr.shape[0] != cam.height):
                    frame_bgr = cv2.resize(frame_bgr, (cam.width, cam.height), interpolation=cv2.INTER_LINEAR)

                # Convert BGR to RGB (required by PyVirtualCam)
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                # Send clean frame directly to virtual camera without text overlay
                if cam is not None:
                    try:
                        cam.send(frame_rgb)
                    except Exception as e:
                        print(f"Error sending frame to virtual camera: {e}")
                else:
                    # Debug mode: show OpenCV window
                    cv2.imshow('iOS WebCam Bridge - Debug Mode', frame_bgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quit requested from debug window")
                        break

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
            # Use Unity Capture backend explicitly
            cam = pyvirtualcam.Camera(width=1280, height=720, fps=30, backend='unitycapture')
            print(f"Virtual camera initialized: {cam.device}")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
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
        socketio.emit('frame_ack', to=request.sid)
    except Exception as e:
        print(f"Error queuing frame: {e}")

@socketio.on('ping')
def handle_ping(data):
    """Handle ping request for network quality monitoring."""
    socketio.emit('ping_response', data, to=request.sid)

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
    print(" WebCam Bridge Server")
    print("="*70)

    local_ip = get_local_ip()
    server_url = f"https://{local_ip}:5000"
    print(f"Local IP: {local_ip}")

    # ── 1. Try Cloudflare tunnel (permanent if token set) ─────────────────
    print("\nChecking for Cloudflare tunnel...")
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
        # ── 3. Fallback: HTTPS on local WiFi with self-signed cert ────────
        print("\n[tunnel] No tunnel found. Using local HTTPS (self-signed cert).")
        cert_file, key_file = generate_self_signed_cert(local_ip)
        ssl_ctx = (cert_file, key_file)
        connect_url = server_url
        use_ssl = True


    # ── QR code ──────────────────────────────────────────────────────────
    print()
    display_qr_code(connect_url)

    print("\nTo connect from your mobile device:")
    print(f"  Open: {connect_url}")
    if not use_ssl:
        print("  If you see a warning page, tap 'Visit Site'")
    else:
        print()
        print("  *** FIRST TIME SETUP (one-time, 2 minutes) ***")
        print("  iOS Safari will say 'Not Secure' or 'Cannot Connect'.")
        print("  You need to TRUST the certificate on your iPhone:")
        print()
        print(f"  STEP 1: Open this URL in Safari: {connect_url}")
        print("  STEP 2: Tap 'Show Details' then 'visit this website'")
        print("  STEP 3: Tap 'Visit Website' to confirm")
        print("  STEP 4: Go to iPhone Settings > General > VPN & Device Management")
        print(f"  STEP 5: Tap 'WebCam Bridge' certificate → tap 'Trust'")
        print("  STEP 6: Go to Settings > General > About > Certificate Trust Settings")
        print("  STEP 7: Enable full trust for 'WebCam Bridge'")
        print("  STEP 8: Return to Safari and refresh — camera will work!")
        print()
        print("  Android phones: Just tap 'Advanced' → 'Proceed' — no extra steps!")

    print("\nPress CTRL+C to stop the server.")
    print("="*70 + "\n")

    # ── Frame worker ─────────────────────────────────────────────────────
    worker_thread = threading.Thread(target=frame_worker, daemon=True)
    worker_thread.start()

    # ── Virtual camera ───────────────────────────────────────────────────
    print("Initializing Unity Capture virtual camera...")
    if init_virtual_camera():
        print(f"Virtual camera ready: {cam.device} ({cam.width}x{cam.height} @ {cam.fps} FPS)")
        print("You can now select it in Zoom, Teams, Meet, OBS, etc.\n")
    else:
        print("[WARN] Unity Capture driver not found. Camera output disabled.")
        print("       Download from: https://github.com/schellingb/UnityCapture/releases\n")

    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=ssl_ctx, allow_unsafe_werkzeug=True)