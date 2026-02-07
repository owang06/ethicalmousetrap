#!/usr/bin/env python3
"""
YOLOv8 COCO Center Detector
Detects if objects are in the center of the webcam feed
"""

import cv2
from ultralytics import YOLO
import numpy as np

class CenterDetector:
    def __init__(self, center_threshold=0.2):
        """
        Initialize detector
        center_threshold: percentage of screen (0.2 = center 20% of screen)
        """
        self.model = YOLO("yolov8n.pt")  # Load COCO model
        self.center_threshold = center_threshold
        self.cap = None
        self.init_camera()
        
    def init_camera(self):
        """Initialize webcam"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            print("✓ Camera initialized")
            print(f"✓ Center detection threshold: {self.center_threshold*100}%")
        except Exception as e:
            print(f"✗ Camera error: {e}")
            exit(1)
    
    def is_in_center(self, bbox, frame_width, frame_height):
        """
        Check if bounding box is in the center of frame
        bbox: [x1, y1, x2, y2] - top-left and bottom-right corners
        Returns: True if object center is in center zone
        """
        x1, y1, x2, y2 = bbox
        
        # Calculate object center
        obj_center_x = (x1 + x2) / 2
        obj_center_y = (y1 + y2) / 2
        
        # Frame center
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2
        
        # Define center zone
        zone_width = frame_width * self.center_threshold
        zone_height = frame_height * self.center_threshold
        
        left = frame_center_x - zone_width / 2
        right = frame_center_x + zone_width / 2
        top = frame_center_y - zone_height / 2
        bottom = frame_center_y + zone_height / 2
        
        # Check if object center is in zone
        in_center = left <= obj_center_x <= right and top <= obj_center_y <= bottom
        
        return in_center, (left, top, right, bottom)
    
    def draw_center_zone(self, frame):
        """Draw center detection zone on frame"""
        h, w = frame.shape[:2]
        zone_width = w * self.center_threshold
        zone_height = h * self.center_threshold
        
        center_x = w / 2
        center_y = h / 2
        
        left = int(center_x - zone_width / 2)
        top = int(center_y - zone_height / 2)
        right = int(center_x + zone_width / 2)
        bottom = int(center_y + zone_height / 2)
        
        # Draw center zone (green rectangle)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, "Center Zone", (left, top - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw crosshair in center
        cv2.line(frame, (int(center_x) - 20, int(center_y)), 
                (int(center_x) + 20, int(center_y)), (0, 255, 0), 2)
        cv2.line(frame, (int(center_x), int(center_y) - 20), 
                (int(center_x), int(center_y) + 20), (0, 255, 0), 2)
    
    def run(self):
        """Main detection loop"""
        print("\nRunning center detection...")
        print("Press 'q' to quit\n")
        
        center_objects = []
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error reading frame")
                break
            
            h, w = frame.shape[:2]
            
            # Run YOLOv8 detection
            results = self.model(frame, conf=0.5, verbose=False)
            
            center_objects = []
            center_count = 0
            
            # Process detections
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[cls]
                    
                    # Check if in center
                    in_center, zone = self.is_in_center([x1, y1, x2, y2], w, h)
                    
                    # Draw bounding box
                    color = (0, 0, 255) if in_center else (0, 255, 0)  # Red if in center, green if not
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    # Draw label
                    label = f"{class_name}: {conf:.2f}"
                    if in_center:
                        label += " (CENTER)"
                        center_count += 1
                    
                    cv2.putText(frame, label, (int(x1), int(y1) - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    if in_center:
                        center_objects.append((class_name, conf))
            
            # Draw center zone
            self.draw_center_zone(frame)
            
            # Display stats
            stats_text = f"Objects in center: {center_count}"
            cv2.putText(frame, stats_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display FPS
            cv2.putText(frame, "Press 'q' to quit", (10, h - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow("YOLOv8 Center Detector", frame)
            
            # Print center objects
            if center_objects:
                print(f"Objects in CENTER: {[obj[0] for obj in center_objects]}")
            
            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n✓ Detector closed")

def main():
    # center_threshold: percentage of screen width/height that defines center zone
    # 0.2 = center 20% of screen (10% on each side from center)
    # 0.5 = center 50% of screen (25% on each side from center)
    detector = CenterDetector(center_threshold=0.6)
    detector.run()

if __name__ == "__main__":
    main()
