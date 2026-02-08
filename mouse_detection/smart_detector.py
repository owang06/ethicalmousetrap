#!/usr/bin/env python3
"""
Smart Mouse Detector
Combines:
- center_detector.py: Detects objects in center zone (YOLOv8)
- mice_identifier.py: Identifies if object is a mouse (Gemini AI)
"""

import cv2
import os
import time
import threading
from flask import Flask, Response
from flask_cors import CORS
from center_detector import CenterDetector
from mice_identifier import MouseDetector

class SmartMouseDetector:
    def __init__(self, center_threshold=0.4, persistence_time=1.0):
        """Initialize by combining center detector and mouse identifier"""
        print("Initializing Smart Mouse Detector...")
        
        # Import center detection from center_detector
        self.center_detector = CenterDetector(center_threshold=center_threshold, persistence_time=persistence_time)
        
        # Import mouse identification from mice_identifier
        self.mouse_identifier = MouseDetector()
        
        # Tracking
        self.tracked_objects = {}
        self.object_history_timeout = 5
        self.last_detection_time = 0
        # Increase cooldown to 60 seconds to avoid quota limits
        self.detection_cooldown = 60.0
        self.last_detection_result = None  # Store last detection result
        self.display_text = None  # Store text to display
        self.display_color = None  # Store display color
        self.rodent_detected = False  # Stop Gemini checks once a rodent is confirmed
        self.quota_exceeded = False  # Track if we hit quota limits
        
        # Frame buffering for streaming
        self.current_frame = None
        self.current_frame_clean = None
        self.frame_lock = threading.Lock()
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
    
    def is_new_object(self, center_x, center_y):
        """Check if object is new or already analyzed"""
        current_time = time.time()
        min_distance = 100  # pixels
        
        # Clean up old tracked objects
        self.tracked_objects = {
            obj_id: (x, y, t) for obj_id, (x, y, t) in self.tracked_objects.items()
            if current_time - t < self.object_history_timeout
        }
        
        # Check if this object is close to a recently tracked one
        for obj_id, (tracked_x, tracked_y, tracked_time) in self.tracked_objects.items():
            distance = ((center_x - tracked_x) ** 2 + (center_y - tracked_y) ** 2) ** 0.5
            if distance < min_distance:
                return False  # Same object
        
        return True  # New object
    
    def add_tracked_object(self, center_x, center_y):
        """Add object to tracking history"""
        obj_id = len(self.tracked_objects)
        self.tracked_objects[obj_id] = (center_x, center_y, time.time())
    
    def crop_to_center(self, frame):
        """Crop frame to center zone"""
        h, w = frame.shape[:2]
        center_threshold = self.center_detector.center_threshold
        zone_width = int(w * center_threshold)
        zone_height = int(h * center_threshold)
        
        center_x = w / 2
        center_y = h / 2
        
        left = int(center_x - zone_width / 2)
        top = int(center_y - zone_height / 2)
        right = int(center_x + zone_width / 2)
        bottom = int(center_y + zone_height / 2)
        
        return frame[top:bottom, left:right]
    
    def setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/health')
        def health():
            return {'status': 'ok'}, 200
        
        @self.app.route('/stream')
        def stream():
            return Response(self.generate_frames(clean=False), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/stream-clean')
        def stream_clean():
            return Response(self.generate_frames(clean=True), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def generate_frames(self, clean=False):
        """Generate MJPEG frames
        clean=True: frames without bounding boxes
        clean=False: frames with bounding boxes
        """
        while True:
            with self.frame_lock:
                frame_to_send = self.current_frame_clean if clean else self.current_frame
                if frame_to_send is not None:
                    ret, buffer = cv2.imencode('.jpg', frame_to_send)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n'
                           b'Content-Length: ' + f'{len(frame_bytes)}'.encode() + b'\r\n\r\n'
                           + frame_bytes + b'\r\n')
            time.sleep(0.03)  # ~30 FPS
    
    def run_detection_loop(self):
        """Main detection loop (runs in background thread)"""
        print("\nRunning Smart Mouse Detector detection loop...")
        
        while True:
            ret, frame = self.center_detector.cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            
            # Use YOLOv8 detection from center_detector
            results = self.center_detector.model(frame, conf=0.5, verbose=False)
            
            objects_in_center = []
            current_time = time.time()
            detected_objects = set()
            
            # Check for objects in center
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = self.center_detector.model.names[cls]
                    
                    # Calculate object center for stable tracking
                    obj_center_x = (x1 + x2) / 2
                    obj_center_y = (y1 + y2) / 2
                    
                    # Bin coordinates to 50-pixel grid to handle small movements
                    binned_x = int(obj_center_x / 50) * 50
                    binned_y = int(obj_center_y / 50) * 50
                    
                    # Use is_in_center from center_detector (returns tuple)
                    in_center, zone = self.center_detector.is_in_center([x1, y1, x2, y2], w, h)
                    
                    # Track persistence time using binned center coordinates
                    obj_key = f"{class_name}_{binned_x}_{binned_y}"
                    detected_objects.add(obj_key)
                    
                    time_in_center = 0
                    confirmed_center = False
                    
                    if in_center:
                        if obj_key not in self.center_detector.center_start_time:
                            self.center_detector.center_start_time[obj_key] = current_time
                        time_in_center = current_time - self.center_detector.center_start_time[obj_key]
                        confirmed_center = time_in_center >= self.center_detector.persistence_time
                    else:
                        # Remove from tracking if not in center
                        if obj_key in self.center_detector.center_start_time:
                            del self.center_detector.center_start_time[obj_key]
                    
                    # Draw box with color based on confirmation status
                    if confirmed_center:
                        color = (0, 0, 255)  # Red if confirmed in center
                        objects_in_center.append((x1, y1, x2, y2, conf))
                    elif in_center:
                        color = (0, 165, 255)  # Orange if in center but not yet confirmed
                    else:
                        color = (0, 255, 0)  # Green if not in center
                    
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    label = f"{class_name}: {conf:.2f}"
                    if in_center:
                        if confirmed_center:
                            label += f" (DETECTED {time_in_center:.1f}s)"
                        else:
                            label += f" ({time_in_center:.1f}s/{self.center_detector.persistence_time}s)"
                    
                    cv2.putText(frame, label, (int(x1), int(y1) - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Clean up old tracking entries  
            keys_to_remove = [k for k in self.center_detector.center_start_time.keys() if k not in detected_objects]
            for key in keys_to_remove:
                del self.center_detector.center_start_time[key]
            
            # If object confirmed in center for full duration, use mice_identifier to analyze
            if (not self.quota_exceeded and not self.rodent_detected and objects_in_center and
                    (current_time - self.last_detection_time > self.detection_cooldown)):
                obj = objects_in_center[0]
                center_x = (obj[0] + obj[2]) / 2
                center_y = (obj[1] + obj[3]) / 2
                
                if self.is_new_object(center_x, center_y):
                    print(f"Object detected in center, analyzing with Gemini...")
                    
                    try:
                        # Crop frame and use mice_identifier's Gemini model
                        cropped = self.crop_to_center(frame)
                        temp_path = "temp_frame.jpg"
                        cv2.imwrite(temp_path, cropped)
                        result = self.mouse_identifier.detect_with_gemini(temp_path)
                        
                        print(f"GEMINI RESULT: {result}")
                        
                        # Store last detection result
                        self.last_detection_result = result
                        
                        # Store display for persistent showing
                        if 'NO MOUSE' in result.upper():
                            self.display_text = "Not a mouse"
                            self.display_color = (0, 255, 0)
                        else:
                            self.display_text = "MOUSE DETECTED!"
                            self.display_color = (0, 0, 255)
                            self.rodent_detected = True
                            self.add_tracked_object(center_x, center_y)
                        
                        self.last_detection_time = current_time
                    except Exception as e:
                        error_msg = str(e)
                        if '429' in error_msg or 'quota' in error_msg.lower():
                            print("[WARNING] Gemini API quota exceeded. Pausing detections...")
                            self.quota_exceeded = True
                            self.display_text = "API Quota Exceeded"
                            self.display_color = (0, 165, 255)  # Orange
                            # Reset after 60 seconds
                            if current_time - self.last_detection_time > 60:
                                self.quota_exceeded = False
                                self.last_detection_time = current_time
                        else:
                            print(f"[ERROR] Detection failed: {error_msg}")
                            self.display_text = "Detection Error"
                            self.display_color = (0, 165, 255)
            
            # Use draw_center_zone from center_detector
            self.center_detector.draw_center_zone(frame)
            
            # Status
            status = f"Objects in center: {len(objects_in_center)}"
            cv2.putText(frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display current detection result (persists until it changes)
            if self.display_text and self.display_color:
                cv2.putText(frame, self.display_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.display_color, 3)
            
            # Display last detection result at top
            if self.last_detection_result:
                if 'MOUSE' in self.last_detection_result.upper() or 'RAT' in self.last_detection_result.upper():
                    last_result_text = f"Last Detection: MOUSE/RAT DETECTED"
                    result_color = (0, 0, 255)  # Red
                else:
                    last_result_text = f"Last Detection: {self.last_detection_result}"
                    result_color = (0, 255, 0)  # Green
                
                cv2.putText(frame, last_result_text, (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, result_color, 2)
            
            # Store frame for MJPEG streaming
            with self.frame_lock:
                self.current_frame = frame.copy()
            
            time.sleep(0.033)  # ~30 FPS
    
    def run(self):
        """Start detector and Flask server"""
        # Start detection loop in background thread
        detection_thread = threading.Thread(target=self.run_detection_loop, daemon=True)
        detection_thread.start()
        
        # Start Flask server
        print("\nFlask server starting on port 5001...")
        self.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.center_detector.cap:
            self.center_detector.cap.release()
        print("\n✓ Detector stopped")

if __name__ == "__main__":
    detector = SmartMouseDetector(center_threshold=0.4, persistence_time=1.0)
    detector.run()
