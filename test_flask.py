#!/usr/bin/env python3
"""
Simple test script to verify Flask is working
"""

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/test', methods=['GET'])
    def test():
        return jsonify({'status': 'ok', 'message': 'Flask is working!'})
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})
    
    import socket
    
    # Check if port is available
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
    except OSError:
        print(f"Port {port} is in use, trying 5001...")
        port = 5001
    
    print("="*60)
    print("Flask Test Server")
    print("="*60)
    print(f"Starting test server on http://localhost:{port}")
    print(f"Visit http://localhost:{port}/test to test")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=port, debug=True)
    
except ImportError as e:
    print("="*60)
    print("ERROR: Flask is not installed!")
    print("="*60)
    print("\nTo install Flask, run:")
    print("  pip install flask flask-cors")
    print("\nOr install all requirements:")
    print("  pip install -r requirements_detector.txt")
    print("\n" + "="*60)
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

