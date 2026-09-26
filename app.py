import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('video_frame')
def handle_video_frame(data):
    # Decode binary JPEG buffer directly
    np_arr = np.frombuffer(data, dtype=np.uint8)
    frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if frame_bgr is not None:
        # Display frame in debug window
        cv2.imshow('iOS Camera', frame_bgr)
        cv2.waitKey(33)  # Display for ~33ms (30 FPS)

if __name__ == '__main__':
    print("Starting WebCam Bridge Server on port 5000...")
    print("Server binding to 0.0.0.0 for local network access")
    socketio.run(app, host='0.0.0.0', port=5000)