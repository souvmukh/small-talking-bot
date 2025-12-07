import subprocess
import threading
import time
import os
import sys
from typing import Optional

class ProcessManager:
    """
    Manages the voice assistant subprocess lifecycle.
    Handles starting, stopping, and monitoring the Python chatbot process.
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.status = 'idle'  # idle, listening, speaking, processing
        self.lock = threading.Lock()
    
    def start_process(self, script_path: str) -> bool:
        """
        Start the voice assistant process.
        
        Args:
            script_path: Path to the main.py script
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        with self.lock:
            if self.process and self.process.poll() is None:
                print("Process is already running")
                return False
            
            # Validate script path exists
            if not os.path.exists(script_path):
                print(f"Error: Script not found at {script_path}")
                return False
            
            try:
                # Get the directory containing the script (src/)
                script_dir = os.path.dirname(os.path.abspath(script_path))
                
                print(f"Starting process: {script_path}")
                print(f"Working directory: {script_dir}")
                print(f"Python executable: {sys.executable}")
                
                # Start the Python script as a subprocess with correct working directory
                # Use sys.executable to ensure we use the same Python (with venv) as the API server
                self.process = subprocess.Popen(
                    [sys.executable, os.path.basename(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    cwd=script_dir  # Set working directory to src/
                )
                self.status = 'listening'
                print(f"Started process with PID: {self.process.pid}")
                
                # Give the process a moment to start and check for immediate errors
                time.sleep(0.5)
                if self.process.poll() is not None:
                    # Process already terminated - capture error
                    stderr = self.process.stderr.read()
                    print(f"Process terminated immediately with error:\n{stderr}")
                    self.process = None
                    self.status = 'idle'
                    return False
                
                # Start a thread to monitor the process
                monitor_thread = threading.Thread(target=self._monitor_process, daemon=True)
                monitor_thread.start()
                
                return True
            except Exception as e:
                print(f"Error starting process: {e}")
                self.status = 'idle'
                return False
    
    def stop_process(self) -> bool:
        """
        Stop the voice assistant process.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        with self.lock:
            if not self.process or self.process.poll() is not None:
                print("No process is running")
                self.status = 'idle'
                return False
            
            try:
                # Terminate the process
                self.process.terminate()
                
                # Wait for process to terminate (with timeout)
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    self.process.kill()
                    self.process.wait()
                
                print(f"Stopped process with PID: {self.process.pid}")
                self.process = None
                self.status = 'idle'
                return True
            except Exception as e:
                print(f"Error stopping process: {e}")
                return False
    
    def get_status(self) -> str:
        """
        Get the current status of the voice assistant.
        
        Returns:
            str: Current status (idle, listening, speaking, processing)
        """
        with self.lock:
            # Check if process is still running
            if self.process and self.process.poll() is not None:
                # Process has ended
                self.status = 'idle'
                self.process = None
            
            return self.status
    
    def is_running(self) -> bool:
        """
        Check if the process is currently running.
        
        Returns:
            bool: True if running, False otherwise
        """
        with self.lock:
            return self.process is not None and self.process.poll() is None
    
    def _monitor_process(self):
        """
        Monitor the process output and update status accordingly.
        This runs in a separate thread.
        """
        if not self.process:
            return
        
        try:
            # Read output line by line
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.strip()
                print(f"Process output: {line}")
                
                # Update status based on output
                # You can customize this based on your main.py log messages
                if 'Listening' in line:
                    self.status = 'listening'
                elif 'Speaking' in line or 'Output' in line:
                    self.status = 'speaking'
                elif 'Processing' in line or 'Generating' in line:
                    self.status = 'processing'
        except Exception as e:
            print(f"Error monitoring process: {e}")
        finally:
            # Process has ended
            with self.lock:
                self.status = 'idle'
                if self.process:
                    self.process = None
