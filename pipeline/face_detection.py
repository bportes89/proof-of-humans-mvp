import cv2
import numpy as np
import os

class ThermalFaceDetector:
    def __init__(self, min_temp=25.0, min_area=5000):
        self.min_temp = min_temp
        self.min_area = min_area
        
        # Carregar Haar Cascade para detecção de face padrão (fallback para webcam simulada)
        # O arquivo haarcascade_frontalface_default.xml geralmente vem com o cv2
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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

        # --- ESTRATÉGIA 1: Detecção Padrão (Haar Cascade) ---
        # Como estamos usando uma webcam simulada que converte luz em "temperatura",
        # a imagem ainda tem características visuais fortes (olhos, nariz, boca).
        # O Haar Cascade é MUITO mais robusto que limiar de temperatura simples para isso.
        
        # Converter frame float (20.0-38.0) de volta para uint8 (0-255) para o detector
        # Mapeamento inverso aproximado: 20->0, 38->255
        frame_norm = np.clip((frame - 20.0) * (255.0 / 18.0), 0, 255).astype(np.uint8)
        
        # Equalizar histograma para melhorar contraste (ajuda muito em webcam ruim)
        frame_eq = cv2.equalizeHist(frame_norm)
        
        faces = self.face_cascade.detectMultiScale(
            frame_eq,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60) # Rosto não pode ser muito pequeno
        )
        
        if len(faces) > 0:
            # Pegar o maior rosto encontrado
            best_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = best_face
            # Converter tipos numpy para int nativo (evita erro de serialização JSON no FastAPI)
            return True, (int(x), int(y), int(w), int(h)), 0.95 # Alta confiança

        # --- ESTRATÉGIA 2: Fallback Térmico (Blob Quente) ---
        # Se o Haar falhar (ex: imagem térmica real muito borrada ou sem detalhes visuais),
        # tentamos achar uma região quente.
        
        # Simple thresholding: Humans are warm (usually > min_temp)
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
            if 0.5 < aspect_ratio < 2.0: # Relaxei um pouco os limites
                score = min(1.0, max_area / (self.min_area * 5))
                return True, (x, y, w, h), score
            
        return False, None, 0.0
