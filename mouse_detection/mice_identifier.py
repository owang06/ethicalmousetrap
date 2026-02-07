#!/usr/bin/env python3
"""
Mouse/Rat Detector using Gemini AI
Takes a photo when you press Enter and uses Gemini to detect if it's a mouse/rat
"""

import cv2
import os
import time
import google.generativeai as genai



class MouseDetector:
    def __init__(self):
        # Try to load from .env file manually
        self.api_key = None
        env_path = '.env'
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'GEMINI_API_KEY':
                                self.api_key = value.strip().strip('"').strip("'")
                                break
            except Exception as e:
                print(f"Warning: Could not read .env file: {e}")
        
        # Fallback to environment variable
        if not self.api_key:
            self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key or self.api_key == 'your-api-key-here':
            print("ERROR: Please set GEMINI_API_KEY in .env file")
            print("Create a .env file with: GEMINI_API_KEY=your-actual-key-here")
            exit(1)
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # First, list available models to see what we can use
        print("Checking available models for your API key...")
        available_models = []
        model_name_map = {}  # Map short names to full names
        try:
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    # Store both full name and short name
                    full_name = model.name
                    short_name = full_name.replace('models/', '')
                    available_models.append(short_name)
                    model_name_map[short_name] = full_name
                    print(f"  ✓ {short_name} (full: {full_name})")
        except Exception as e:
            print(f"  Warning: Could not list models: {e}")
        
        if not available_models:
            print("\nError: No models found with generateContent support.")
            print("Please check your API key and ensure it has access to Gemini models.")
            exit(1)
        
        # Initialize model - try available models first, then fallback to common names
        self.model = None
        # Try available models first (these are guaranteed to exist)
        # Then try common free tier model names
        model_names = available_models + ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro-vision']
        # Remove duplicates while preserving order
        model_names = list(dict.fromkeys(model_names))
        
        print("\nAttempting to initialize Gemini model...")
        for model_name in model_names:
            try:
                # Try both short name and full name formats
                # GenerativeModel usually accepts short names, but let's try both
                model_to_try = [model_name]
                if model_name in model_name_map:
                    model_to_try.insert(0, model_name_map[model_name])
                
                model_initialized = False
                for model_id in model_to_try:
                    try:
                        self.model = genai.GenerativeModel(model_id)
                        print(f"✓ Model object created with {model_name}")
                        model_initialized = True
                        break
                    except Exception as init_e:
                        continue
                
                if not model_initialized:
                    print(f"✗ Could not create model object for {model_name}")
                    continue
                
                # Test the model with a simple text+image call to verify it actually works
                # This will catch 404 errors and other API issues
                try:
                    import PIL.Image
                    test_img = PIL.Image.new('RGB', (1, 1), color='white')
                    test_response = self.model.generate_content(["Say 'test'", test_img])
                    print(f"✓ Gemini AI initialized and verified with {model_name}!")
                    break
                except Exception as test_e:
                    error_msg = str(test_e)
                    # If it's a 404, this model definitely doesn't work
                    if '404' in error_msg or 'not found' in error_msg.lower():
                        print(f"  ✗ This model is not available for your API key")
                        print(f"  Error: {error_msg}")
                        print(f"  Trying next model...")
                    else:
                        # For other errors, log but still try next model
                        print(f"  ⚠ Test failed (might be temporary): {error_msg}")
                        print(f"  Trying next model...")
                    self.model = None
                    continue
                    
            except Exception as e:
                print(f"✗ Trying {model_name}... failed: {e}")
                continue
        
        if not self.model:
            print("\nError: Could not initialize any working Gemini model")
            print("Available models were:")
            for m in available_models:
                print(f"  - {m}")
            print("\nNote: Some models may be listed but not actually available for your API key tier.")
            exit(1)
        
        self.cap = None
        self.init_camera()
        
    def init_camera(self):
        """Initialize camera"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            print("Camera initialized successfully!")
            print("Press ENTER to capture and detect, or 'q' to quit")
        except Exception as e:
            print(f"Camera error: {str(e)}")
            print("Make sure your camera is connected and permissions are granted")
            exit(1)
    
    def show_preview(self):
        """Show camera preview"""
        print("\nShowing camera preview...")
        print("Press ENTER to capture, or 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read from camera")
                break
            
            # Show preview
            cv2.imshow('Mouse Detector - Press ENTER to capture, Q to quit', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('\n') or key == ord('\r'):  # Enter key
                return frame
            elif key == ord('q'):
                return None
        
    def capture_and_detect(self, frame):
        """Detect mouse/rat in captured frame"""
        # Save captured image temporarily
        cv2.imwrite("temp_capture.jpg", frame)
        print("\nImage captured! Sending to Gemini AI...")
        
        # Detect using Gemini
        result = self.detect_with_gemini("temp_capture.jpg")
        
        # Clean up temp file
        try:
            os.remove("temp_capture.jpg")
        except:
            pass
        
        return result
    
    def detect_with_gemini(self, image_path):
        """Send image to Gemini API for detection"""
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Create prompt
            prompt = "Look at this image and determine if there is a mouse or rat visible. Respond with ONLY one of these options: 'MOUSE/RAT DETECTED' or 'NO MOUSE/RAT'. Be very specific - only respond if you can clearly see a mouse or rat in the image."
            
            # Prepare image
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            # Generate content
            response = self.model.generate_content([prompt, img])
            
            return response.text.strip()
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run(self):
        """Main loop"""
        try:
            while True:
                frame = self.show_preview()
                
                if frame is None:
                    break
                
                result = self.capture_and_detect(frame)
                print(f"\n{'='*60}")
                print(f"RESULT: {result}")
                print(f"{'='*60}\n")
                
                # Show result for 3 seconds
                cv2.putText(frame, result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2)
                cv2.imshow('Result - Press any key to continue', frame)
                cv2.waitKey(3000)
                cv2.destroyWindow('Result - Press any key to continue')
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    detector = MouseDetector()
    detector.run()

if __name__ == "__main__":
    main()
