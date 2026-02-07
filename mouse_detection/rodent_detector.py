#!/usr/bin/env python3
"""
YOLOv8 Rodent Detector
Uses pre-trained YOLOv8 model specialized for rodent detection
"""

import cv2
from ultralytics import YOLO
import time

class RodentDetector:
    def __init__(self, model_variant="yolov8n"):
        """
        Initialize rodent detector with pre-trained model
        
        Options:
        - yolov8n: Nano (fastest, least accurate)
        - yolov8s: Small
        - yolov8m: Medium
        - yolov8l: Large
        - yolov8x: XLarge (slowest, most accurate)
        
        Or use a custom rodent model from Hugging Face:
        - keremberke/yolov8n-rodent
        - keremberke/yolov8m-rodent
        """
        print("Initializing YOLOv8 Rodent Detector...")
        print(f"Model: {model_variant}\n")
        
        try:
            # Try to load rodent-specific model from Hugging Face
            if "rodent" in model_variant.lower():
                print(f"Loading rodent-specific model: {model_variant}")
                self.model = YOLO(f"https://huggingface.co/keremberke/{model_variant}/resolve/main/weights/best.pt")
            else:
                # Use standard COCO model
                self.model = YOLO(f"{model_variant}.pt")
            
            print("✓ Model loaded successfully\n")
        except Exception as e:
            print(f"⚠ Could not load rodent model: {e}")
            print("Falling back to YOLOv8 Nano COCO model...")
            self.model = YOLO("yolov8n.pt")
        
        # Initialize camera
        self.cap = None
        self.init_camera()
        
        # Stats
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
    
    def init_camera(self):
        """Initialize webcam"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            print("✓ Camera initialized")
        except Exception as e:
            print(f"✗ Camera error: {e}")
            exit(1)
    
    def draw_stats(self, frame, detections_count):
        """Draw FPS and detection count"""
        h, w = frame.shape[:2]
        
        # Calculate FPS
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.fps = self.frame_count / elapsed
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw detection count
        status = "🐭 RODENT DETECTED!" if detections_count > 0 else "No rodents"
        color = (0, 0, 255) if detections_count > 0 else (0, 255, 0)
        cv2.putText(frame, status, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw detection count
        cv2.putText(frame, f"Detections: {detections_count}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    def run(self):
        """Main detection loop"""
        print("Running rodent detection...")
        print("Press 'q' to quit\n")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            
            # Run detection
            results = self.model(frame, conf=0.5)
            
            rodent_count = 0
            
            # Draw detections
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[cls]
                    
                    # Check if detection is likely a rodent
                    if "mouse" in class_name.lower() or "rat" in class_name.lower() or "rodent" in class_name.lower():
                        rodent_count += 1
                        color = (0, 0, 255)  # Red for rodents
                    else:
                        color = (0, 255, 0)  # Green for other objects
                    
                    # Draw box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    # Draw label
                    label = f"{class_name} {conf:.2f}"
                    cv2.putText(frame, label, (int(x1), int(y1) - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw stats
            self.draw_stats(frame, rodent_count)
            
            # Draw instructions
            cv2.putText(frame, "Press 'q' to quit", (10, h - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow("YOLOv8 Rodent Detector", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n✓ Detector stopped")

def main():
    # Try different rodent models in order
    models_to_try = [
        "keremberke/yolov8n-rodent",  # Rodent-specific nano
        "keremberke/yolov8m-rodent",  # Rodent-specific medium
        "yolov8m",                     # Fallback to standard medium
    ]
    
    detector = RodentDetector(model_variant=models_to_try[0])
    detector.run()

if __name__ == "__main__":
    main()
