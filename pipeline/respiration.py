import numpy as np
import time
from scipy.signal import find_peaks

class RespirationAnalyzer:
    def __init__(self, fps=30, buffer_seconds=20):
        self.fps = fps
        self.buffer_size = int(fps * buffer_seconds)
        self.signal_buffer = [] # Stores (timestamp, value) tuples
        self.timestamps = []
        self.values = []
        
    def add_sample(self, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
            
        self.timestamps.append(timestamp)
        self.values.append(value)
        
        # Maintain buffer size
        if len(self.values) > self.buffer_size:
            self.timestamps.pop(0)
            self.values.pop(0)
            
    def get_signal(self):
        return np.array(self.timestamps), np.array(self.values)
    
    def analyze_frequency(self):
        """
        Returns estimated RPM (Respirations Per Minute) and signal quality score.
        """
        if len(self.values) < self.fps * 5: # Need at least 5 seconds
            return 0.0, 0.0
            
        # Remove DC component (mean)
        signal = np.array(self.values)
        signal = signal - np.mean(signal)
        
        # Simple peak detection or zero crossings
        # For robustness, let's smooth it first (moving average)
        window_size = int(self.fps * 0.5) # 0.5s window
        if window_size > 0:
            signal_smooth = np.convolve(signal, np.ones(window_size)/window_size, mode='valid')
        else:
            signal_smooth = signal
            
        # Find peaks
        peaks, _ = find_peaks(signal_smooth, distance=self.fps*1.5) # Minimum 1.5s between breaths (~40 rpm max)
        
        num_peaks = len(peaks)
        duration_seconds = (self.timestamps[-1] - self.timestamps[0])
        if duration_seconds <= 0:
            return 0.0, 0.0

        rpm = (num_peaks / duration_seconds) * 60
        
        # Quality score based on regularity (variance of peak intervals)
        if num_peaks > 2:
            intervals = np.diff(peaks)
            regularity = 1.0 - (np.std(intervals) / np.mean(intervals))
            quality_score = max(0.0, min(1.0, regularity))
        else:
            quality_score = 0.5 # Not enough data for regularity check
            
        return rpm, quality_score

    def check_challenge(self, challenge_type="deep_breath", expected_duration=5.0):
        """
        Checks if the signal matches a specific pattern in the last N seconds.
        """
        # Placeholder for challenge logic
        # Real implementation would use DTW (Dynamic Time Warping) or simple heuristic on amplitude/duration
        if len(self.values) < self.fps * expected_duration:
            return False
            
        # Get recent signal
        recent_signal = np.array(self.values)[-int(self.fps*expected_duration):]
        amplitude = np.max(recent_signal) - np.min(recent_signal)
        
        # Heuristic: Deep breath has higher amplitude than normal breathing
        # We need a baseline amplitude to compare against.
        # For MVP, let's just check if amplitude is > threshold.
        
        # In mock camera: normal variation is ~1.5C (sin wave) + noise.
        # Deep breath might be > 2.0C variation.
        
        if challenge_type == "deep_breath":
            return amplitude > 2.0 # Threshold based on mock camera logic
            
        return False
