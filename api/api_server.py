from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add parent directory to path to import process_manager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from process_manager import ProcessManager

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize process manager
process_manager = ProcessManager()

# Path to the main.py script
MAIN_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'main.py')
MAIN_SCRIPT_PATH = os.path.abspath(MAIN_SCRIPT_PATH)

@app.route('/api/conversation/start', methods=['POST'])
def start_conversation():
    """
    Start the voice assistant conversation.
    """
    try:
        if process_manager.is_running():
            return jsonify({
                'success': False,
                'message': 'Conversation is already running'
            }), 400
        
        success = process_manager.start_process(MAIN_SCRIPT_PATH)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation started successfully',
                'status': process_manager.get_status()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start conversation'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/conversation/stop', methods=['POST'])
def stop_conversation():
    """
    Stop the voice assistant conversation.
    """
    try:
        if not process_manager.is_running():
            return jsonify({
                'success': False,
                'message': 'No conversation is running'
            }), 400
        
        success = process_manager.stop_process()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation stopped successfully',
                'status': 'idle'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to stop conversation'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get the current status of the voice assistant.
    """
    try:
        status = process_manager.get_status()
        is_running = process_manager.is_running()
        
        return jsonify({
            'success': True,
            'status': status,
            'is_running': is_running
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'success': True,
        'message': 'API server is running'
    }), 200

if __name__ == '__main__':
    print(f"Starting Flask API server...")
    print(f"Main script path: {MAIN_SCRIPT_PATH}")
    print(f"Script exists: {os.path.exists(MAIN_SCRIPT_PATH)}")
    print(f"Working directory will be: {os.path.dirname(MAIN_SCRIPT_PATH)}")
    print(f"API will be available at: http://localhost:5000")
    print(f"CORS enabled for React frontend")
    
    if not os.path.exists(MAIN_SCRIPT_PATH):
        print(f"\n⚠️  WARNING: Main script not found at {MAIN_SCRIPT_PATH}")
        print(f"Please verify the path is correct before starting conversations.\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
