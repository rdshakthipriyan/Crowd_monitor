# AI Crowd Monitoring System

<p align="center">
  <b>Real-Time AI-Based Crowd Detection, Tracking, Density Analysis and Alert Monitoring</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20Dashboard-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/YOLOv8-Object%20Detection-purple" alt="YOLOv8">
  <img src="https://img.shields.io/badge/ByteTrack-Multi--Object%20Tracking-orange" alt="ByteTrack">
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-red?logo=opencv" alt="OpenCV">
  <img src="https://img.shields.io/badge/Status-Prototype-success" alt="Status">
</p>

---

## 📌 Overview

The **AI Crowd Monitoring System** is a real-time computer vision application designed to automatically detect, track, and analyze people in a monitored video stream.

The system uses **YOLOv8** for person detection and **ByteTrack** for multi-object tracking. The video frame is divided into three predefined zones, allowing the system to calculate crowd counts and density values independently for each zone.

Based on the calculated density, each zone is assigned one of three alert states:

- 🟢 **SAFE**
- 🟡 **WARNING**
- 🔴 **DANGER**

The processed video is streamed through a **Flask web dashboard**, while real-time crowd statistics are exposed through a JSON API. The system also generates a heatmap of tracked activity and periodically logs crowd statistics to a CSV file.

The current implementation is designed for **single-camera monitoring using a webcam**.

---

## 🎯 Objectives

The main objectives of the project are:

- Detect people automatically from a live video stream.
- Track detected individuals across consecutive frames.
- Reduce duplicate counting using multi-object tracking.
- Divide the monitored area into predefined zones.
- Calculate crowd density for each zone.
- Classify crowd conditions into SAFE, WARNING, and DANGER.
- Reduce temporary alert fluctuations using sustained-alert logic.
- Visualize crowd concentration through a heatmap.
- Provide a real-time browser-based monitoring dashboard.
- Store crowd monitoring information for historical analysis.

---

## ✨ Features

### 👤 Real-Time Person Detection

The system uses **YOLOv8** to detect people in each processed video frame.

Only the `person` class is considered during the detection process.

---

### 🎯 Multi-Object Tracking

**ByteTrack** is used to track detected people across frames.

Each tracked person receives a tracking ID that allows the system to maintain identity information between consecutive frames.

---

### 🗺️ Zone-Based Crowd Monitoring

The monitored video frame is divided into three vertical zones:

```text
┌─────────────────────────────────────────────┐
│                  VIDEO FRAME                │
├────────────────┬────────────────┬───────────┤
│                │                │           │
│    ZONE A      │     ZONE B     │   ZONE C  │
│                │                │           │
│                │                │           │
│                │                │           │
└────────────────┴────────────────┴───────────┘

The current implementation uses:

Zone	Horizontal Range
Zone A	0% – 33%
Zone B	33% – 66%
Zone C	66% – 100%

For each zone, the system maintains:

Current people count
Cumulative entries
Density value
Alert status
📊 Crowd Density Estimation

The system calculates a zone-specific density metric based on the number of detected people and the pixel area of the zone.

Density = (Number of People × Density Weight) / Zone Area

The current implementation uses:

Density Weight = 10000.0

Note: This is an image-space/empirical density metric. It is not a calibrated real-world measurement such as people per square metre.

🚨 Crowd Alert Classification

The system classifies each zone according to its calculated density.

Density	Alert Status
< 3.0	🟢 SAFE
3.0 – 5.0	🟡 WARNING
> 5.0	🔴 DANGER

The alert system also uses temporal smoothing.

Each zone maintains a history of the most recent alert states. An alert condition is accepted when it appears in at least 70% of the most recent 15 states.

This helps prevent rapid status changes caused by temporary detection fluctuations.

🔥 Heatmap Visualization

The system generates a heatmap using the tracked positions of detected people.

The heatmap pipeline is:

Tracked Person Position
          ↓
Heatmap Accumulator
          ↓
Temporal Decay
          ↓
Gaussian Blur
          ↓
Color Mapping
          ↓
Overlay on Video

Older activity gradually fades while recent activity contributes more strongly to the visualization.

🌐 Real-Time Web Dashboard

The project includes a Flask-based web dashboard.

The dashboard displays:

Live processed video
Current active people
Zone A statistics
Zone B statistics
Zone C statistics
Current zone count
Cumulative zone entries
Density values
Alert status

The dashboard automatically requests updated metrics every 500 milliseconds.

💾 CSV Data Logging

The application periodically stores monitoring data in:

crowd_data.csv

The logged information includes:

Timestamp
Total current people
Zone A current count
Zone B current count
Zone C current count
Zone A density
Zone B density
Zone C density
Zone A alert
Zone B alert
Zone C alert
⚡ Performance Optimization

The system includes frame skipping to reduce unnecessary YOLO inference.

The current implementation processes every second frame:

process_every_n_frames = 2

Previously processed detection and tracking results are reused for skipped frames.

The video frame is also resized while maintaining its aspect ratio, with a maximum dimension of:

640 pixels
🏗️ System Architecture
                     ┌───────────────────┐
                     │      Webcam       │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │      OpenCV       │
                     │   VideoCapture    │
                     └─────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │      YOLOv8        │
                    │  Person Detection  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │     ByteTrack      │
                    │  Object Tracking   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   Zone Analysis    │
                    │                    │
                    │ A │ B │ C          │
                    └─────────┬──────────┘
                              │
                ┌─────────────┼──────────────┐
                │             │              │
                ▼             ▼              ▼
        ┌──────────────┐ ┌──────────┐ ┌──────────────┐
        │    Density   │ │ Heatmap  │ │   Tracking   │
        │  Calculation │ │Generation│ │   Counters   │
        └──────┬───────┘ └──────────┘ └──────────────┘
               │
               ▼
       ┌────────────────────┐
       │   Alert Analysis   │
       │                    │
       │ SAFE / WARNING /   │
       │      DANGER        │
       └─────────┬──────────┘
                 │
          ┌──────┴───────┐
          │              │
          ▼              ▼
 ┌────────────────┐ ┌────────────────┐
 │ Flask Dashboard│ │  CSV Logging   │
 └────────────────┘ └────────────────┘
🔄 Processing Workflow
START
  │
  ▼
Initialize Flask Application
  │
  ▼
Load YOLOv8 Model
  │
  ▼
Initialize Webcam
  │
  ▼
Capture Video Frame
  │
  ▼
Resize Frame
  │
  ▼
Run YOLOv8 Detection
  │
  ▼
ByteTrack Tracking
  │
  ▼
Identify Person Positions
  │
  ▼
Assign People to Zones
  │
  ├──────────────┬──────────────┐
  ▼              ▼              ▼
Zone A         Zone B         Zone C
  │              │              │
  └──────────────┼──────────────┘
                 │
                 ▼
        Calculate Density
                 │
                 ▼
        Evaluate Alert State
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      SAFE    WARNING   DANGER
        │        │        │
        └────────┼────────┘
                 │
                 ▼
          Generate Heatmap
                 │
                 ▼
        Annotate Video Frame
                 │
                 ▼
        Update Flask Metrics
                 │
          ┌──────┴──────┐
          ▼             ▼
    Web Dashboard    CSV Logging
          │
          ▼
       Next Frame
🧠 Computer Vision Pipeline
1. Video Acquisition

The current application uses the default webcam as its video source.

VIDEO_SOURCE = 0

OpenCV's VideoCapture interface is used to obtain video frames.

2. Frame Preprocessing

The input frame is resized while maintaining its aspect ratio.

The maximum image dimension is limited to:

640 pixels

This reduces the computational load during real-time processing.

3. Person Detection

YOLOv8 Nano is used for object detection.

The model is loaded from:

yolov8n.pt

The tracking call is configured to process only:

Class 0 → Person
4. Multi-Object Tracking

The system uses ByteTrack through the Ultralytics tracking interface.

Tracking persistence is enabled so that object IDs can be maintained across frames.

Video Frame
     ↓
YOLO Detection
     ↓
Detected Person
     ↓
ByteTrack
     ↓
Tracking ID
5. Zone Assignment

The system calculates the bottom-center point of each person's bounding box.

That point is used to determine which zone contains the person.

Bounding Box
┌─────────────┐
│             │
│    Person   │
│             │
└──────●──────┘
       ↑
 Bottom-center

The detected person is assigned to the first matching zone.

🚨 Alert Processing

The alert pipeline consists of:

Current Zone Count
        ↓
Density Calculation
        ↓
Raw Alert
        ↓
Alert History
        ↓
70% Sustained Condition
        ↓
Final Alert

The system stores up to 15 alert states per zone.

Example:

SAFE
SAFE
SAFE
WARNING
SAFE
SAFE
SAFE
SAFE
SAFE
SAFE
SAFE
SAFE
SAFE
SAFE
SAFE

        ↓

     SAFE

This prevents a single temporary detection change from immediately changing the displayed status.

🔥 Heatmap Processing

The heatmap is generated from tracked person positions.

For every detected person, the system adds activity to the heatmap accumulator.

Older values are reduced using temporal decay:

Heatmap = Heatmap × 0.95

The accumulated map is then:

Normalized
Gaussian blurred
Converted into a color map
Blended with the original video

The final video therefore contains both detection information and crowd-concentration visualization.

🌐 Web Dashboard

The dashboard is implemented using:

HTML5
CSS3
JavaScript
Flask

The interface contains a live video panel and a monitoring panel.

┌─────────────────────────────────────────────────────┐
│              AI Crowd Monitoring Hub                │
├──────────────────────────┬──────────────────────────┤
│                          │ Current Active People     │
│                          │                          │
│       LIVE VIDEO         │            12            │
│                          │                          │
│  YOLOv8 + ByteTrack      ├──────────────────────────┤
│                          │ Zone A                    │
│                          │ Count | Density | Alert  │
│                          ├──────────────────────────┤
│                          │ Zone B                    │
│                          │ Count | Density | Alert  │
│                          ├──────────────────────────┤
│                          │ Zone C                    │
│                          │ Count | Density | Alert  │
└──────────────────────────┴──────────────────────────┘
🔌 Flask API

The current application exposes three main routes.

Method	Endpoint	Purpose
GET	/	Loads the dashboard
GET	/video_feed	Streams processed video
GET	/metrics	Returns live crowd metrics
/

Loads:

templates/index.html

This provides the monitoring dashboard.

/video_feed

Provides the processed video stream using:

multipart/x-mixed-replace

The browser displays the stream through an HTML <img> element.

/metrics

Returns the latest monitoring information as JSON.

Example:

{
  "total_count": 12,
  "zone_counts": {
    "Zone A": 4,
    "Zone B": 5,
    "Zone C": 3
  },
  "zone_densities": {
    "Zone A": 1.23,
    "Zone B": 2.41,
    "Zone C": 0.98
  },
  "alerts": {
    "Zone A": "SAFE",
    "Zone B": "SAFE",
    "Zone C": "SAFE"
  },
  "cumulative": {
    "Zone A": 17,
    "Zone B": 23,
    "Zone C": 11
  }
}
📁 Project Structure
Crowd_monitor/
│
├── app.py
│   └── Flask application
│       - Web server
│       - Webcam capture
│       - Video streaming
│       - Metrics API
│
├── crowd_monitor_core.py
│   └── Core monitoring engine
│       - YOLOv8 detection
│       - ByteTrack tracking
│       - Zone analysis
│       - Density calculation
│       - Alert processing
│       - Heatmap generation
│       - CSV logging
│
├── templates/
│   └── index.html
│       └── Web dashboard
│
├── crowd_data.csv
│   └── Crowd monitoring data
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│
├── fix_git.bat
│
└── reinit_git.bat
🛠️ Technology Stack
Technology	Purpose
Python	Core programming language
Flask	Web server and dashboard backend
OpenCV	Video capture and image processing
YOLOv8	Person detection
ByteTrack	Multi-object tracking
NumPy	Numerical processing
HTML5	Dashboard structure
CSS3	Dashboard styling
JavaScript	Live dashboard updates
CSV	Data logging
📦 Requirements

The project uses Python 3.x.

Major dependencies include:

Flask
OpenCV
NumPy
Ultralytics

The analyzed project specifies the following versions:

Flask       3.1.3
OpenCV      4.13.0.92
NumPy       2.2.3
Ultralytics 8.4.24

The repository's requirements.txt should be used as the dependency source when installing the project.

🚀 Installation
1. Clone the Repository
git clone https://github.com/rdshakthipriyan/Crowd_monitor.git

Enter the project directory:

cd Crowd_monitor
2. Create a Virtual Environment
Windows
python -m venv venv

Activate it:

venv\Scripts\activate
Linux / macOS
python3 -m venv venv

Activate it:

source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
🤖 YOLOv8 Model

The application expects the YOLOv8 Nano model:

yolov8n.pt

The application first checks for the model inside:

venv/yolov8n.pt

and then falls back to:

yolov8n.pt

in the project location.

Make sure the model file is available before starting the application.

▶️ Running the Application

Start the Flask application:

python app.py

The server runs on:

http://localhost:5000

Open a browser and visit:

http://localhost:5000

The AI Crowd Monitoring Hub dashboard should load.

🖥️ Standalone Monitoring Mode

The core monitoring module can also be executed directly:

python crowd_monitor_core.py

This runs the monitoring system using an OpenCV window rather than the Flask dashboard.

This mode is useful for direct testing and development.

📊 CSV Data Logging

The application stores monitoring data in:

crowd_data.csv

The CSV structure is:

Timestamp
Total_Current
Zone_A_Current
Zone_B_Current
Zone_C_Current
Density_A
Density_B
Density_C
Alert_A
Alert_B
Alert_C

Example:

Timestamp,Total_Current,Zone_A_Current,Zone_B_Current,Zone_C_Current,Density_A,Density_B,Density_C,Alert_A,Alert_B,Alert_C
2026-10-03 10:30:01,8,3,2,3,1.21,0.81,1.22,SAFE,SAFE,SAFE

The Flask application periodically appends new records to the CSV file.

📈 Monitoring Metrics

The system provides two types of counting information.

Current Count

The number of people currently detected in the frame.

Current Active People
Cumulative Entries

The number of unique tracking IDs that have been observed entering a particular zone during the monitoring session.

Zone A → Total Entries
Zone B → Total Entries
Zone C → Total Entries

These values are maintained independently for each zone.

⚡ Performance Optimization

The system includes several mechanisms intended to reduce processing overhead.

Frame Skipping

YOLO tracking is performed every second frame:

process_every_n_frames = 2
Frame Resizing

The maximum image dimension is:

640 pixels
Result Reuse

For skipped frames, the previously calculated detection and tracking results are reused.

Global Camera Capture

The Flask application initializes the camera once globally and uses a threading lock to coordinate camera access.

This avoids repeatedly opening the webcam when the dashboard is refreshed.

🎓 Academic Project

This project was developed as part of:

24ME411 – Product Development Lab-II

Department of:

Electronics and Communication Engineering

R.M.K. Engineering College

The project report identifies the project as:

AI Crowd Monitoring System

The report focuses on automated crowd detection, tracking, zone-based analysis, density estimation, alert generation, heatmap visualization, and data logging.

🌍 Potential Applications

The system can be adapted for research and prototype applications involving:

Railway stations
Shopping malls
Stadiums
Public events
Educational campuses
Public gathering areas
Smart-city research
Crowd-density analysis
Video surveillance research
⚠️ Current Limitations

The current implementation has several limitations that should be considered before production deployment.

Single Camera

The current application uses:

VIDEO_SOURCE = 0

Therefore, it currently processes one webcam/video source.

Approximate Density Metric

The density calculation uses pixel-based zone area and an empirical scaling factor.

It should not be interpreted as a calibrated physical measurement such as:

people / m²

without additional camera calibration and real-world scene measurement.

Dense Crowd Occlusion

When many people overlap heavily, object detection and tracking can become less reliable because individuals may partially or completely obscure one another.

No Authentication

The current dashboard does not implement authentication or user accounts.

No HTTPS Configuration

The current Flask application is configured for local/development usage and does not provide HTTPS configuration.

Hardcoded Configuration

Several settings are currently defined directly in the source code, including:

Camera source
Flask port
Density thresholds
Density scaling factor
Number of zones
Frame processing interval
Single-Process Architecture

The current implementation is designed as a relatively simple local monitoring application rather than a distributed production surveillance system.

🔮 Future Enhancements

Potential future improvements include:

Multi-camera monitoring
Camera calibration
Real-world density estimation
User authentication
Role-based access control
HTTPS deployment
Configurable camera sources
Configurable zones
Configurable alert thresholds
Database-backed storage
Historical analytics dashboard
Automated notifications
Mobile monitoring interface
Cloud deployment
Edge-device deployment
Advanced crowd behavior analysis
Long-term crowd trend analysis
🔐 Security Considerations

The current implementation is primarily intended as a local/development prototype.

For public or production deployment, additional security mechanisms should be implemented, including:

Authentication
Authorization
HTTPS
Secure configuration
Input validation
Rate limiting
Robust error handling
Production-grade application serving
Secure network configuration
📚 References

The project work is based on concepts related to:

YOLO-based object detection
Multi-object tracking
Crowd counting
Crowd density estimation
Computer vision
Real-time video analytics

The academic project report discusses research including:

MCNN
CSRNet
JHU-CROWD++
YOLO-based detection
YOLOv8
👥 Contributors
Shakthi Priyan R D

Electronics and Communication Engineering
R.M.K. Engineering College

Saktheeshwaran S

Electronics and Communication Engineering
R.M.K. Engineering College

Soorya Prakash B

Electronics and Communication Engineering
R.M.K. Engineering College

📄 Project Information
Item	Details
Project	AI Crowd Monitoring System
Course	24ME411 – Product Development Lab-II
Department	Electronics and Communication Engineering
Institution	R.M.K. Engineering College
Primary Language	Python
Detection	YOLOv8
Tracking	ByteTrack
Computer Vision	OpenCV
Backend	Flask
Frontend	HTML, CSS, JavaScript
Data Storage	CSV
Video Source	Webcam
Monitoring Zones	3
Alert Levels	SAFE / WARNING / DANGER
📌 Project Status

Status: Functional Prototype

The current implementation provides:

✅ Real-time person detection
✅ YOLOv8-based detection
✅ ByteTrack-based tracking
✅ Three-zone crowd analysis
✅ Current crowd counting
✅ Cumulative zone-entry counting
✅ Density calculation
✅ SAFE / WARNING / DANGER classification
✅ Sustained alert logic
✅ Heatmap generation
✅ Real-time Flask dashboard
✅ Live MJPEG video streaming
✅ Real-time metrics API
✅ CSV data logging
✅ Frame-skipping optimization
⭐ Summary
                 AI CROWD MONITORING SYSTEM
                            │
                            ▼
                       Webcam Input
                            │
                            ▼
                         OpenCV
                            │
                            ▼
                         YOLOv8
                            │
                      Person Detection
                            │
                            ▼
                       ByteTrack
                            │
                     Person Tracking
                            │
                            ▼
                    Three-Zone Analysis
                     │      │      │
                     ▼      ▼      ▼
                  Zone A  Zone B  Zone C
                     │      │      │
                     └──────┼──────┘
                            ▼
                    Density Calculation
                            │
                            ▼
                     Alert Classification
                     │       │       │
                   SAFE   WARNING   DANGER
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       Flask Dashboard               CSV Logging
              │
              ▼
       Real-Time Monitoring
🔗 Repository

GitHub Repository

<p align="center"> <b>AI • Computer Vision • Real-Time Monitoring • Crowd Analytics</b> </p> ```

One correction before you paste it: the example crowd_data.csv row is illustrative, not a real row from your repository. If you want the README to be strictly evidence-only, remove that example row and keep only the CSV column structure.
