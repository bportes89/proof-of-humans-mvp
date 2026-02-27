import time
import cv2
import numpy as np
import threading
import json
import base64
import uuid
from datetime import datetime

from device.camera import ThermalCamera
from pipeline.face_detection import ThermalFaceDetector
from pipeline.respiration import RespirationAnalyzer
from pipeline.biometrics import BiometricEngine

class PipelineManager:
    def __init__(self, camera_index=None):
        self.camera = ThermalCamera(camera_index=camera_index)
        self.detector = ThermalFaceDetector()
        self.biometrics = BiometricEngine()
        
        # Session state
        self.current_session_id = None
        self.session_start_time = 0
        self.session_state = "IDLE" # IDLE, ENROLLING, VERIFYING, COMPLETED, FAILED
        self.user_id = None
        
        self.respiration_analyzer = None
        self.last_frame = None
        self.last_detection = (False, None, 0.0)
        
        self.proof = None
        
        # Background thread for processing
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            print("Pipeline: Already running")
            return
        print("Pipeline: Starting camera...")
        self.camera.start()
        self.running = True
        print("Pipeline: Starting thread...")
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        print("Pipeline: Start complete")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.camera.stop()

    def _process_loop(self):
        print("Pipeline: Thread started")
        while self.running:
            try:
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                with self.lock:
                    self.last_frame = frame.copy()
                
                # Detect Face
                found, bbox, score = self.detector.detect(frame)
                with self.lock:
                    self.last_detection = (found, bbox, score)
                
                if found and self.session_state in ["ENROLLING", "VERIFYING"]:
                    x, y, w, h = bbox
                    
                    # Extract ROI for respiration (e.g., center of face/nose)
                    # Simple approximation: center of bbox
                    cx, cy = int(x + w//2), int(y + h//2)
                    # Ensure within bounds
                    cy = min(max(cy, 0), frame.shape[0]-1)
                    cx = min(max(cx, 0), frame.shape[1]-1)
                    
                    roi_val = frame[cy, cx] 
                    
                    if self.respiration_analyzer:
                        self.respiration_analyzer.add_sample(roi_val)
                        
                        # Analyze signal
                        rpm, quality = self.respiration_analyzer.analyze_frequency()
                        
                        # Check challenge (e.g., deep breath in last 5s)
                        passed_challenge = self.respiration_analyzer.check_challenge(
                            challenge_type="deep_breath", 
                            expected_duration=5.0
                        )
                        
                        elapsed = time.time() - self.session_start_time
                        
                        if self.session_state == "ENROLLING":
                            # Auto-enroll after stable signal (e.g. > 5s)
                            if elapsed > 5.0 and quality > 0.3:
                                face_roi = frame[int(y):int(y+h), int(x):int(x+w)]
                                self.biometrics.enroll(self.user_id, face_roi)
                                self.proof = self._generate_proof(liveness_score=quality, matched=True, match_score=1.0)
                                self.session_state = "COMPLETED"
                                
                        elif self.session_state == "VERIFYING":
                            # Verify identity
                            if elapsed > 3.0: # Wait a bit for signal
                                face_roi = frame[int(y):int(y+h), int(x):int(x+w)]
                                match, match_score = self.biometrics.verify(self.user_id, face_roi)
                                
                                # Logic: If face matches AND liveness/challenge passed
                                if match:
                                    # For MVP, let's be lenient on challenge if liveness quality is high
                                    if passed_challenge or (quality > 0.6):
                                        self.proof = self._generate_proof(liveness_score=quality, matched=True, match_score=match_score)
                                        self.session_state = "COMPLETED"
                                    elif elapsed > 15.0:
                                        # Timeout
                                        self.session_state = "FAILED"
                                else:
                                    if elapsed > 10.0:
                                        self.session_state = "FAILED" # Identity mismatch

                time.sleep(1/30.0) # ~30 FPS
            except Exception as e:
                print(f"Pipeline Error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1.0)
        print("Pipeline: Thread stopped")

    def start_session(self, user_id, mode="VERIFY"):
        with self.lock:
            self.current_session_id = str(uuid.uuid4())
            self.user_id = user_id
            self.session_start_time = time.time()
            if mode == "ENROLL":
                self.session_state = "ENROLLING"
            else:
                self.session_state = "VERIFYING"
            
            self.respiration_analyzer = RespirationAnalyzer(fps=30)
            self.proof = None
            
        return self.current_session_id

    def get_status(self):
        """Returns current status for UI"""
        rpm = 0.0
        quality = 0.0
        proof_data = None
        
        with self.lock:
            if self.respiration_analyzer:
                rpm, quality = self.respiration_analyzer.analyze_frequency()
            
            state = self.session_state
            detected = self.last_detection[0]
            bbox = self.last_detection[1]
            sid = self.current_session_id
            if self.proof:
                proof_data = self.proof.copy()

        return {
            "session_id": sid,
            "state": state,
            "face_detected": detected,
            "bbox": bbox,
            "rpm": rpm,
            "signal_quality": quality,
            "proof": proof_data
        }

    def get_latest_frame_b64(self):
        """Returns base64 encoded frame for UI preview (heatmap)"""
        with self.lock:
            if self.last_frame is None:
                return None
            frame_copy = self.last_frame.copy()
            detection = self.last_detection
        
        # Normalize to 0-255 uint8
        # Mock camera produces floats around 20-40.
        # Normalize dynamically or statically
        # Static normalization for consistency: 15C to 40C mapped to 0-255
        norm_frame = np.clip((frame_copy - 15) * (255 / (40 - 15)), 0, 255).astype(np.uint8)
        
        # Apply colormap
        color_frame = cv2.applyColorMap(norm_frame, cv2.COLORMAP_JET)
        
        # Draw bbox if detected
        if detection and detection[0]:
            x, y, w, h = detection[1]
            cv2.rectangle(color_frame, (int(x), int(y)), (int(x+w), int(y+h)), (0, 255, 0), 2)
            
        _, buffer = cv2.imencode('.jpg', color_frame)
        return base64.b64encode(buffer).decode('utf-8')

    def _generate_proof(self, liveness_score, matched, match_score=1.0):
        return {
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "liveness_score": float(liveness_score),
            "identity_match": bool(matched),
            "identity_score": float(match_score),
            "signature": f"signed_by_server_{self.current_session_id}" 
        }

# Global instance
pipeline = PipelineManager()
