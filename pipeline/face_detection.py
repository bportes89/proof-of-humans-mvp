import cv2
import numpy as np

class ThermalFaceDetector:
    def __init__(self, min_temp=30.0, min_area=5000):
        self.min_temp = min_temp
        self.min_area = min_area

    def detect(self, frame):
        """
        Detects a face in a thermal frame.
        Returns:
            found (bool): True if face detected
            bbox (tuple): (x, y, w, h)
            score (float): Confidence score based on thermal properties
        """
        if frame is None:
            return False, None, 0.0

        # Simple thresholding: Humans are warm (usually > 30C in typical indoor)
        # Normalize frame to 0-255 for OpenCV processing if needed, 
        # but we can work with the raw float data for thresholding.
        
        # Create a binary mask for warm regions
        mask = (frame > self.min_temp).astype(np.uint8) * 255
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_cnt = None
        max_area = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.min_area:
                if area > max_area:
                    max_area = area
                    best_cnt = cnt
        
        if best_cnt is not None:
            x, y, w, h = cv2.boundingRect(best_cnt)
            
            # Basic geometric check (aspect ratio of a face is roughly 1:1.3 or so)
            aspect_ratio = h / w
            if 0.8 < aspect_ratio < 1.6:
                # Check internal thermal distribution (simple check: center warmer than edges?)
                # For MVP, just return True if we found a big warm blob.
                score = min(1.0, max_area / (self.min_area * 5)) # Normalize score somewhat
                return True, (x, y, w, h), score
            
        return False, None, 0.0
