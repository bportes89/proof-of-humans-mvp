import numpy as np
import hashlib
import uuid
import cv2

class BiometricEngine:
    def __init__(self):
        self.enrolled_users = {} # {user_id: template}
        
    def enroll(self, user_id, face_roi_thermal):
        """
        Generates a template from thermal face ROI and stores it.
        For MVP, we just hash the ROI as a placeholder for embedding.
        """
        # Resize ROI to standard size (e.g., 64x64)
        roi_resized = cv2.resize(face_roi_thermal, (64, 64))
        
        # Mock embedding generation:
        # In reality, this would be a deep learning model inference.
        # Here we just compute a hash of the pixel values (very brittle, but okay for mock).
        # Or better: random vector if we can't do real matching.
        
        # To make it slightly more "real", let's use a PCA-like projection or just raw pixels flattened.
        template = roi_resized.flatten()
        
        self.enrolled_users[user_id] = template
        return True

    def verify(self, user_id, face_roi_thermal):
        """
        Verifies if the current face matches the enrolled user.
        """
        if user_id not in self.enrolled_users:
            return False, 0.0
            
        stored_template = self.enrolled_users[user_id]
        
        roi_resized = cv2.resize(face_roi_thermal, (64, 64))
        current_template = roi_resized.flatten()
        
        # Cosine similarity or Euclidean distance
        # Since these are raw pixels, correlation might be better?
        # Let's use correlation coefficient for robustness to absolute temperature differences.
        
        correlation = np.corrcoef(stored_template, current_template)[0, 1]
        
        # Threshold: 0.8 correlation seems reasonable for same object same pose
        is_match = correlation > 0.8
        
        return is_match, correlation
