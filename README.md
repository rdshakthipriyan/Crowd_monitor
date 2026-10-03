# AI Crowd Monitoring System

> Real-time AI-powered crowd detection, tracking, zone-wise density analysis, and alert monitoring using YOLOv8, ByteTrack, OpenCV, and Flask.

---

## 📌 Overview

The **AI Crowd Monitoring System** is a computer-vision-based application designed to monitor people in real time from a webcam feed.

The system uses **YOLOv8** for person detection and **ByteTrack** for multi-object tracking. The monitored video frame is divided into three predefined zones, allowing the system to calculate zone-wise crowd counts and density values.

Based on the calculated density, each zone is classified into:

- 🟢 **SAFE**
- 🟡 **WARNING**
- 🔴 **DANGER**

The system also provides a real-time web dashboard using Flask, displays the processed video stream, maintains cumulative zone-entry counts, generates a visual heatmap, and periodically stores monitoring data in a CSV file.

---

## 🎯 Objectives

The main objectives of the project are:

- Detect people automatically from live video.
- Track detected individuals across video frames.
- Reduce duplicate counting using multi-object tracking.
- Divide the monitored area into multiple zones.
- Calculate crowd density independently for each zone.
- Classify crowd conditions as SAFE, WARNING, or DANGER.
- Reduce alert fluctuations using sustained-alert logic.
- Visualize crowd concentration using a heatmap.
- Provide real-time monitoring through a web dashboard.
- Store crowd monitoring data for historical analysis.

---

## ✨ Key Features

### 👤 Real-Time Person Detection

Uses **YOLOv8** to detect people from the camera feed.

Only the `person` class is processed by the detection pipeline.

### 🎯 Multi-Object Tracking

**ByteTrack** is used to maintain tracking IDs across consecutive frames.

This allows the system to distinguish individuals across frames instead of treating every detection as a new person.

### 🗺️ Three-Zone Analysis

The video frame is divided into three vertical zones:

```text
┌──────────────────────────────────────────────┐
│                  VIDEO FRAME                 │
├────────────────┬────────────────┬────────────┤
│    ZONE A      │     ZONE B     │   ZONE C   │
│                │                │            │
│                │                │            │
│                │                │            │
└────────────────┴────────────────┴────────────┘
