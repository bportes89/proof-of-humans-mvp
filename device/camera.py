import numpy as np
import time
import cv2

class ThermalCamera:
    """
    Simulates a thermal camera SDK wrapper.
    In a real scenario, this would wrap ctypes/cffi calls to the camera's DLL.
    """
    def __init__(self, width=640, height=480, fps=30, camera_index=None):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_running = False
        self.start_time = 0
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        self.is_running = True
        self.start_time = time.time()
        
        if self.camera_index is not None:
            print(f"Opening Real Camera (Index: {self.camera_index})...")
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW) # CAP_DSHOW for Windows usually faster
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_index}. Falling back to simulation.")
                self.cap = None
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                print("Real Camera started successfully.")
        
        if self.cap is None:
            print("Thermal Camera started (simulated)")

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        print("Thermal Camera stopped")

    def get_frame(self):
        """
        Returns a thermal frame (numpy array).
        If real camera is connected, returns grayscale frame converted to float.
        Otherwise, returns simulated thermal data.
        """
        if not self.is_running:
            return None

        # Real Camera Path
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Convert to grayscale (thermal cameras usually output 1 channel or grayscale RGB)
                if len(frame.shape) == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Normalize 0-255 to approx 20-38°C for compatibility with our algorithm
                # This is a naive mapping! Real radiometric data needs SDK.
                frame_float = frame.astype(np.float32)
                
                # Mapping: 0 -> 20°C, 255 -> 40°C
                frame_temp = 20.0 + (frame_float / 255.0) * 20.0
                return frame_temp
            else:
                print("Warning: Failed to read frame from camera.")
        
        # Simulation Path (Fallback)
        # Create a base background temperature (e.g., 20-25°C)
        frame = np.full((self.height, self.width), 22.0, dtype=np.float32)
        
        # Add some noise
        noise = np.random.normal(0, 0.5, (self.height, self.width))
        frame += noise

        # Simulate a "face" in the center (warmer, e.g., 34-36°C)
        # Simple Gaussian blob to represent a face
        y, x = np.ogrid[:self.height, :self.width]
        center_y, center_x = self.height // 2, self.width // 2
        
        # Head
        mask = ((x - center_x)**2 + (y - center_y)**2) < (100**2)
        frame[mask] = 34.0 + np.random.normal(0, 0.2, np.sum(mask))

        # Nose area (warmer/cooler based on breathing)
        # Breathing simulation: 12-15 breaths per minute => ~0.2-0.25 Hz
        t = time.time() - self.start_time
        breath_freq = 0.25 # Hz
        breath_phase = np.sin(2 * np.pi * breath_freq * t)
        
        # Expiration (warmer) / Inspiration (cooler) relative to core body temp? 
        # Actually, usually expiration is warmer than inspiration (ambient air).
        # Let's say nose temp fluctuates between 32°C (inspire) and 35°C (expire).
        nose_temp = 33.5 + 1.5 * breath_phase
        
        nose_mask = ((x - center_x)**2 + (y - (center_y + 20))**2) < (15**2)
        frame[nose_mask] = nose_temp + np.random.normal(0, 0.1, np.sum(nose_mask))

        return frame

    def get_resolution(self):
        return self.width, self.height
