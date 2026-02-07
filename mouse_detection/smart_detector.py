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
from center_detector import CenterDetector
from mice_identifier import MouseDetector

class SmartMouseDetector:
    def __init__(self, center_threshold=0.6):
        """Initialize by combining center detector and mouse identifier"""
        print("Initializing Smart Mouse Detector...")
        
        # Import center detection from center_detector
        self.center_detector = CenterDetector(center_threshold=center_threshold)
        
        # Import mouse identification from mice_identifier
        self.mouse_identifier = MouseDetector()
        
        # Tracking
        self.tracked_objects = {}
        self.object_history_timeout = 5
        self.last_detection_time = 0
        # 0.5 Hz = one Gemini check every 2 seconds
        self.detection_cooldown = 5.0
        self.last_detection_result = None  # Store last detection result
        self.display_text = None  # Store text to display
        self.display_color = None  # Store display color
        self.rodent_detected = False  # Stop Gemini checks once a rodent is confirmed
    
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
    
    def run(self):
        """Main loop combining both detectors"""
        print("\nRunning Smart Mouse Detector...")
        print("YOLOv8: Detects if object is in center")
        print("Gemini: Identifies if it's a mouse")
        print("Press 'q' to quit\n")
        
        while True:
            ret, frame = self.center_detector.cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            
            # Use YOLOv8 detection from center_detector
            results = self.center_detector.model(frame, conf=0.5, verbose=False)
            
            objects_in_center = []
            
            # Check for objects in center
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    
                    # Use is_in_center from center_detector
                    in_center = self.center_detector.is_in_center([x1, y1, x2, y2], w, h)
                    
                    # Draw box
                    color = (0, 0, 255) if in_center else (0, 255, 0)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    label = f"Object {conf:.2f}"
                    if in_center:
                        label += " (CENTER)"
                        objects_in_center.append((x1, y1, x2, y2, conf))
                    
                    cv2.putText(frame, label, (int(x1), int(y1) - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # If object in center, use mice_identifier to analyze
            current_time = time.time()
            if (not self.rodent_detected and objects_in_center and
                    (current_time - self.last_detection_time > self.detection_cooldown)):
                obj = objects_in_center[0]
                center_x = (obj[0] + obj[2]) / 2
                center_y = (obj[1] + obj[3]) / 2
                
                if self.is_new_object(center_x, center_y):
                    print(f"Object detected in center")
                    print("Asking Gemini: Is this a mouse?")
                    
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
                else:
                    cv2.putText(frame, "⟳ Tracking same object...", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
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
                    last_result_text = f"Last Detection: MOUSE/RAT DETECTED ⚠"
                    result_color = (0, 0, 255)  # Red
                else:
                    last_result_text = f"Last Detection: {self.last_detection_result}"
                    result_color = (0, 255, 0)  # Green
                
                cv2.putText(frame, last_result_text, (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, result_color, 2)
            
            # Show frame
            cv2.imshow("Smart Mouse Detector", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.center_detector.cap:
            self.center_detector.cap.release()
        cv2.destroyAllWindows()
        print("\n✓ Detector stopped")

if __name__ == "__main__":
    detector = SmartMouseDetector(center_threshold=0.6)
    detector.run()
