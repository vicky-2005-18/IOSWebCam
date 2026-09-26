import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

frame_count = 0
client_count = 0

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
        
        # Add frame counter and connection status to debug window
        frame_with_info = frame_bgr.copy()
        cv2.putText(frame_with_info, f"Frame: {frame_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame_with_info, f"Clients: {client_count}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display frame in debug window
        cv2.imshow('iOS Camera', frame_with_info)
        
        # Display for ~33ms (30 FPS) and handle quit key
        key = cv2.waitKey(33)
        if key == 27 or key == ord('q'):  # ESC or 'q' to quit
            socketio.stop()
            return

if __name__ == '__main__':
    print("Starting WebCam Bridge Server on port 5000...")
    print("Server binding to 0.0.0.0 for local network access")
    print("Press ESC or 'q' in debug window to stop server")
    socketio.run(app, host='0.0.0.0', port=5000)