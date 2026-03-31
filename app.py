from flask import Flask, render_template, Response, jsonify
import cv2
from crowd_monitor_core import CrowdMonitor
import time
import os
import threading

app = Flask(__name__)

# Use inbuilt webcam
VIDEO_SOURCE = 0

model_path = os.path.join(os.path.dirname(__file__), "venv", "yolov8n.pt")
if not os.path.exists(model_path):
    model_path = "yolov8n.pt"

monitor = CrowdMonitor(model_path=model_path, video_source=VIDEO_SOURCE, export_csv="crowd_data.csv")

latest_data = {
    "total_count": 0,
    "zone_counts": {"Zone A": 0, "Zone B": 0, "Zone C": 0},
    "zone_densities": {"Zone A": 0.0, "Zone B": 0.0, "Zone C": 0.0},
    "alerts": {"Zone A": "SAFE", "Zone B": "SAFE", "Zone C": "SAFE"},
    "cumulative": {"Zone A": 0, "Zone B": 0, "Zone C": 0}
}
last_log_time = time.time()

# Initialize camera once globally to avoid exclusive-lock errors on page refresh!
cap = cv2.VideoCapture(VIDEO_SOURCE)
cap_lock = threading.Lock()

def generate_frames():
    global latest_data, last_log_time
    
    while True:
        with cap_lock:
            success, frame = cap.read()
            
        if not success:
            # If camera disconnects temporarily
            time.sleep(0.1)
            continue
            
        processed_frame, total, zc, zd, al = monitor.process_frame(frame)
        
        # Update global data
        latest_data["total_count"] = total
        latest_data["zone_counts"] = zc
        latest_data["zone_densities"] = zd
        latest_data["alerts"] = al
        latest_data["cumulative"] = monitor.cumulative_entries
        
        current_time = time.time()
        if current_time - last_log_time >= 1.0:
            monitor.log_to_csv(total, zc, zd, al)
            last_log_time = current_time
        
        # Encode for web streaming
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/metrics')
def metrics():
    return jsonify(latest_data)

if __name__ == '__main__':
    print("Starting AI Crowd Monitor Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
