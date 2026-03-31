import cv2
import numpy as np
import csv
import time
from ultralytics import YOLO
import os
from collections import deque

class CrowdMonitor:
    def __init__(self, model_path="yolov8n.pt", video_source=0, export_csv="crowd_data.csv"):
        self.model = YOLO(model_path)
        self.video_source = video_source
        self.csv_file = export_csv
        
        # Scaling and skipping
        self.target_width = None
        self.target_height = None
        self.max_dimension = 640
        self.frame_count = 0
        self.process_every_n_frames = 2 # Frame skipping for performance
        
        # Define 3 Zones based on relative coordinates [0, 1]
        self.zone_ratios = {
            "Zone A": [(0.0, 0.0), (0.33, 0.0), (0.33, 1.0), (0.0, 1.0)],
            "Zone B": [(0.33, 0.0), (0.66, 0.0), (0.66, 1.0), (0.33, 1.0)],
            "Zone C": [(0.66, 0.0), (1.0, 0.0), (1.0, 1.0), (0.66, 1.0)]
        }
        
        self.zones = {}
        self.zone_areas = {}
        self.heatmap_accum = None
        
        # Tracking memory
        self.tracked_ids_memory = { "Zone A": set(), "Zone B": set(), "Zone C": set() }
        self.cumulative_entries = { "Zone A": 0, "Zone B": 0, "Zone C": 0 }
        
        # Density and Alerts
        self.density_weight = 10000.0
        self.alert_history = { "Zone A": deque(maxlen=15), "Zone B": deque(maxlen=15), "Zone C": deque(maxlen=15) } 
        self.current_alerts = { "Zone A": "SAFE", "Zone B": "SAFE", "Zone C": "SAFE" }
        
        # Init CSV File
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Total_Current", "Zone_A_Current", "Zone_B_Current", "Zone_C_Current", "Density_A", "Density_B", "Density_C", "Alert_A", "Alert_B", "Alert_C"])

        # Cache for skipped frames
        self.last_processed_results = None

    def _initialize_dimensions(self, frame):
        h, w = frame.shape[:2]
        
        # Scale preserving aspect ratio
        if w > h:
            self.target_width = self.max_dimension
            self.target_height = int((h / w) * self.max_dimension)
        else:
            self.target_height = self.max_dimension
            self.target_width = int((w / h) * self.max_dimension)
            
        self.heatmap_accum = np.zeros((self.target_height, self.target_width), dtype=np.float32)
        
        # Init Zones
        for name, ratios in self.zone_ratios.items():
            pts = np.array([ [int(x*self.target_width), int(y*self.target_height)] for x, y in ratios ], np.int32)
            self.zones[name] = pts
            self.zone_areas[name] = cv2.contourArea(pts)

    def get_sustained_alert(self, zone_name, new_alert):
        """ Returns an alert only if it has been sustained for a duration. """
        self.alert_history[zone_name].append(new_alert)
        
        history = list(self.alert_history[zone_name])
        if len(history) == self.alert_history[zone_name].maxlen:
            if history.count("DANGER") >= len(history) * 0.7:
                return "DANGER"
            elif history.count("WARNING") >= len(history) * 0.7:
                return "WARNING"
            elif history.count("SAFE") >= len(history) * 0.7:
                return "SAFE"
                
        return self.current_alerts[zone_name]

    def process_frame(self, frame):
        # 1. Initialize dimensions lazily & Resolve Resolution
        if self.target_width is None or self.target_height is None:
            self._initialize_dimensions(frame)
            
        frame = cv2.resize(frame, (self.target_width, self.target_height))
        self.frame_count += 1
        
        # 2. Frame Skipping
        if self.frame_count % self.process_every_n_frames != 0 and self.last_processed_results is not None:
            results, boxes, track_ids = self.last_processed_results
        else:
            # Run YOLO with tracking, strictly using ByteTrack
            results = self.model.track(frame, persist=True, classes=[0], tracker="bytetrack.yaml", verbose=False)
            boxes, track_ids = [], []
            if results and results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
            self.last_processed_results = (results, boxes, track_ids)
            
        current_zone_counts = { "Zone A": 0, "Zone B": 0, "Zone C": 0 }
        current_frame_ids = { "Zone A": set(), "Zone B": set(), "Zone C": set() }
        total_current = 0
        
        # 3. Heatmap Temporal Decay
        if self.heatmap_accum is not None:
            self.heatmap_accum = self.heatmap_accum * 0.95
        
        # 4. Process Detections & Tracking
        for box, track_id in zip(boxes, track_ids):
            total_current += 1
            x1, y1, x2, y2 = map(int, box)
            cx, cy = int((x1 + x2) / 2), int(y2) 
            
            # Add to heatmap
            if self.heatmap_accum is not None and 0 <= cx < self.target_width and 0 <= cy < self.target_height:
                self.heatmap_accum[cy, cx] += 2.0
                
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Check zones
            for z_name, z_pts in self.zones.items():
                if cv2.pointPolygonTest(z_pts, (cx, cy), False) >= 0:
                    current_zone_counts[z_name] += 1
                    current_frame_ids[z_name].add(track_id)
                    
                    if track_id not in self.tracked_ids_memory[z_name]:
                        self.tracked_ids_memory[z_name].add(track_id)
                        self.cumulative_entries[z_name] += 1
                    break
                    
        for z_name in self.tracked_ids_memory:
            if len(self.tracked_ids_memory[z_name]) > 1000:
                self.tracked_ids_memory[z_name] = set(list(self.tracked_ids_memory[z_name])[-500:])
                
        # 5. Density and Alert Logic
        zone_densities = {}
        for z_name, z_pts in self.zones.items():
            count = current_zone_counts[z_name]
            area = self.zone_areas[z_name]
            
            density = (count * self.density_weight) / area if area > 0 else 0
            zone_densities[z_name] = density
            
            if density < 3.0:
                raw_alert = "SAFE"
            elif density <= 5.0:
                raw_alert = "WARNING"
            else:
                raw_alert = "DANGER"
                
            sustained_alert = self.get_sustained_alert(z_name, raw_alert)
            self.current_alerts[z_name] = sustained_alert
            
            if sustained_alert == "SAFE":
                color = (0, 255, 0)
            elif sustained_alert == "WARNING":
                color = (0, 255, 255) # Yellow
            else:
                color = (0, 0, 255) # Red
                
            cv2.polylines(frame, [z_pts], True, color, 2)
            
            txt_x, txt_y = z_pts[0][0] + 10, 30
            cv2.putText(frame, f"{z_name}: {count} (Tot: {self.cumulative_entries[z_name]})", (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, f"Den: {density:.2f}", (txt_x, txt_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(frame, sustained_alert, (txt_x, txt_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # 6. Heatmap Overlay
        if self.heatmap_accum is not None:
            heatmap_norm = cv2.normalize(self.heatmap_accum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap_norm = cv2.GaussianBlur(heatmap_norm, (15, 15), 0)
            heatmap_colored = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
            frame = cv2.addWeighted(frame, 0.7, heatmap_colored, 0.3, 0)
        
        # Display Total Count
        cv2.putText(frame, f"Current Total: {total_current}", (10, self.target_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame, total_current, current_zone_counts, zone_densities, self.current_alerts

    def log_to_csv(self, total_count, zone_counts, zone_densities, alerts):
        with open(self.csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                total_count,
                zone_counts["Zone A"], zone_counts["Zone B"], zone_counts["Zone C"],
                f"{zone_densities['Zone A']:.2f}", f"{zone_densities['Zone B']:.2f}", f"{zone_densities['Zone C']:.2f}",
                alerts["Zone A"], alerts["Zone B"], alerts["Zone C"]
            ])

if __name__ == "__main__":
    monitor = CrowdMonitor(model_path="yolov8n.pt", video_source=0)
    cap = cv2.VideoCapture(monitor.video_source)
    
    last_log_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        processed_frame, total, zc, zd, al = monitor.process_frame(frame)
        
        current_time = time.time()
        if current_time - last_log_time >= 1.0:
            monitor.log_to_csv(total, zc, zd, al)
            last_log_time = current_time
            
        cv2.imshow("AI Crowd Monitor Live", processed_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
            
    cap.release()
    cv2.destroyAllWindows()
