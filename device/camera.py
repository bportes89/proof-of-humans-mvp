import numpy as np
import time
import cv2

class ThermalCamera:
    """
    Simulates a thermal camera SDK wrapper.
    In a real scenario, this would wrap ctypes/cffi calls to the camera's DLL.
    """
    def __init__(self, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_running = False
        self.start_time = 0
        
    def start(self):
        self.is_running = True
        self.start_time = time.time()
        print("Thermal Camera started (simulated)")

    def stop(self):
        self.is_running = False
        print("Thermal Camera stopped")

    def get_frame(self):
        """
        Returns a simulated thermal frame (numpy array).
        Values represent temperature in Celsius (approx).
        """
        if not self.is_running:
            return None
            
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
