#!/usr/bin/env python3
"""
Mouse/Rat Detector using Gemini AI
Takes a photo when you press Enter and uses Gemini to detect if it's a mouse/rat
"""

import cv2
import os
import time
import sys
import argparse
import json
import base64

# Check for Flask before importing
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("ERROR: Flask is not installed!")
    print("Please install Flask and flask-cors:")
    print("  pip install flask flask-cors")
    print("Or install all requirements:")
    print("  pip install -r requirements_detector.txt")

import google.generativeai as genai

class MouseDetector:
    def __init__(self, background_mode=False):
        self.background_mode = background_mode
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
            if not self.background_mode:
                print("Press ENTER to capture and detect, or 'q' to quit")
            else:
                print("Running in background mode - camera is active")
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
        
    def capture_frame(self):
        """Capture a frame from the camera"""
        if not self.cap or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def capture_and_detect(self, frame=None):
        """Detect mouse/rat in captured frame"""
        if frame is None:
            frame = self.capture_frame()
            if frame is None:
                return "Error: Could not capture frame from camera"
        
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
            if not os.path.exists(image_path):
                return f"Error: Image file not found: {image_path}"
            
            # Create prompt
            prompt = "Look at this image and determine if there is a mouse or rat visible. Respond with ONLY one of these options: 'MOUSE/RAT DETECTED' or 'NO MOUSE/RAT'. Be very specific - only respond if you can clearly see a mouse or rat in the image."
            
            # Prepare image
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            # Generate content
            if not self.model:
                return "Error: Gemini model not initialized"
            
            response = self.model.generate_content([prompt, img])
            
            if not response or not hasattr(response, 'text'):
                return "Error: Invalid response from Gemini API"
            
            return response.text.strip()
                
        except Exception as e:
            import traceback
            error_msg = f"Error in detect_with_gemini: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return error_msg
    
    def run(self):
        """Main loop"""
        if self.background_mode:
            self.run_background()
        else:
            self.run_interactive()
    
    def run_background(self):
        """Run in background mode with HTTP API server"""
        if not FLASK_AVAILABLE:
            print("\n" + "="*60)
            print("ERROR: Cannot run in background mode - Flask is not installed!")
            print("="*60)
            print("\nTo fix this, install Flask:")
            print("  pip install flask flask-cors")
            print("\nOr install all requirements:")
            print("  pip install -r requirements_detector.txt")
            print("\n" + "="*60)
            exit(1)
        
        # Determine port early so we can use it in messages
        # macOS often uses port 5000 for AirPlay, so start with 5001
        import socket
        self.port = 5001  # Default to 5001 to avoid macOS AirPlay conflict
        for test_port in [5001, 5000, 5002, 8000]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('127.0.0.1', test_port))
                sock.close()
                self.port = test_port
                break
            except OSError:
                continue
        
        app = Flask(__name__)
        CORS(app)  # Enable CORS for Next.js app
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok', 'camera': self.cap.isOpened() if self.cap else False})
        
        @app.route('/detect', methods=['POST'])
        def detect():
            try:
                print("Detection request received")
                # Capture frame from camera
                frame = self.capture_frame()
                if frame is None:
                    print("ERROR: Could not capture frame from camera")
                    return jsonify({'error': 'Could not capture frame from camera', 'status': 'error'}), 500
                
                print("Frame captured, starting detection...")
                # Detect mouse
                result = self.capture_and_detect(frame)
                print(f"Detection result: {result}")
                
                # Determine if mouse was detected
                detected = 'MOUSE/RAT DETECTED' in result.upper() or 'DETECTED' in result.upper()
                
                response_data = {
                    'detected': detected,
                    'result': result,
                    'status': 'success'
                }
                print(f"Returning response: {response_data}")
                return jsonify(response_data)
            except Exception as e:
                print(f"ERROR in detect route: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e), 'status': 'error'}), 500
        
        @app.route('/capture', methods=['GET'])
        def capture_image():
            """Capture and return image as base64"""
            try:
                frame = self.capture_frame()
                if frame is None:
                    return jsonify({'error': 'Could not capture frame'}), 500
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    return jsonify({'error': 'Could not encode image'}), 500
                
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                return jsonify({
                    'image': f'data:image/jpeg;base64,{img_base64}',
                    'status': 'success'
                })
            except Exception as e:
                return jsonify({'error': str(e), 'status': 'error'}), 500
        
        # Add error handler for all exceptions
        @app.errorhandler(Exception)
        def handle_exception(e):
            print(f"Error in Flask app: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e), 'status': 'error'}), 500
        
        print("Mouse detector running in background mode with API server...")
        print("Camera is active and ready for use")
        print(f"API server starting on http://127.0.0.1:{self.port}")
        print("  GET  /health - Check server and camera status")
        print("  POST /detect - Capture and detect mouse")
        print("  GET  /capture - Capture image")
        
        # Keep the camera stream active by reading frames periodically
        def keep_camera_alive():
            while True:
                try:
                    if self.cap and self.cap.isOpened():
                        ret, frame = self.cap.read()
                        if not ret:
                            print("Warning: Could not read from camera")
                            time.sleep(1)
                            continue
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error in camera thread: {e}")
                    time.sleep(1)
        
        import threading
        camera_thread = threading.Thread(target=keep_camera_alive, daemon=True)
        camera_thread.start()
        
        try:
            print("\n" + "="*60)
            print("Starting Flask server...")
            print("="*60 + "\n")
            print(f"Starting Flask server on http://127.0.0.1:{self.port}")
            print("="*60 + "\n")
            # Use 127.0.0.1 for better compatibility, threaded=True for concurrent requests
            app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False, threaded=True)
        except KeyboardInterrupt:
            print("\n\nShutting down Flask server...")
        except Exception as e:
            print(f"\nFATAL ERROR starting Flask server: {e}")
            import traceback
            traceback.print_exc()
            print("\n" + "="*60)
            print("Troubleshooting:")
            print("1. Make sure Flask is installed: pip install flask flask-cors")
            print("2. Check if port 5000 is already in use")
            print("3. Make sure you have the required permissions")
            print("="*60 + "\n")
        finally:
            print("Cleaning up...")
            self.cleanup()
    
    def run_interactive(self):
        """Run in interactive mode with GUI"""
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
        if not self.background_mode:
            cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Mouse/Rat Detector using Gemini AI')
    parser.add_argument('--background', action='store_true', 
                       help='Run in background mode without GUI windows')
    args = parser.parse_args()
    
    detector = MouseDetector(background_mode=args.background)
    detector.run()

if __name__ == "__main__":
    main()
