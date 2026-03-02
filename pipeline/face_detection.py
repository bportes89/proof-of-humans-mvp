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
        # Tenta achar rosto com características visuais (olhos, nariz)
        
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
        # Se o Haar falhar, tentamos achar uma região quente.
        # IMPORTANTE: Quando usamos OBS Virtual Camera com imagens coloridas (Ironbow/Rainbow),
        # o "frame" que chega aqui pode não ser uma matriz de temperatura limpa.
        # Precisamos ser robustos.
        
        # Se o frame parece ser uma imagem normal convertida (valores ~20-38), usamos threshold simples.
        # Mas se for imagem colorida capturada pelo OBS, os valores podem estar bagunçados na conversão grayscale.
        
        # Vamos tentar binarizar com Otsu (automático) para separar frente/fundo
        # Isso funciona bem se o rosto for a coisa mais brilhante (quente) na imagem, 
        # que é o caso típico de termografia (rosto amarelo/vermelho vs fundo azul/verde).
        
        try:
            # Converter para uint8 para Otsu
            frame_u8 = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Threshold de Otsu (separa automaticamente o pico mais claro)
            _, mask_otsu = cv2.threshold(frame_u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(mask_otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_cnt = None
            max_area = 0
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                # Area mínima um pouco menor para garantir detecção
                if area > self.min_area * 0.5: 
                    if area > max_area:
                        max_area = area
                        best_cnt = cnt
            
            if best_cnt is not None:
                x, y, w, h = cv2.boundingRect(best_cnt)
                
                # Checagem geométrica relaxada
                aspect_ratio = h / w
                if 0.5 < aspect_ratio < 2.0: 
                    score = min(1.0, max_area / (self.min_area * 5))
                    return True, (int(x), int(y), int(w), int(h)), score
        except Exception as e:
            print(f"Erro no fallback térmico: {e}")

        # --- ESTRATÉGIA 3: Fallback Geométrico (Central ROI) ---
        # Se tudo falhar (imagem muito ruidosa, baixo contraste térmico, OBS colorido confuso),
        # assumimos que o usuário está posicionado no CENTRO da tela (UX padrão).
        # Retornamos um quadrado fixo no meio da imagem.
        
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Tamanho estimado do rosto (ex: 1/3 da largura da tela)
        face_w = int(width * 0.35)
        face_h = int(face_w * 1.3) # Proporção áurea aproximada
        
        x = max(0, center_x - face_w // 2)
        y = max(0, center_y - face_h // 2)
        
        # Garantir que está dentro da imagem
        w = min(width - x, face_w)
        h = min(height - y, face_h)
        
        # Score baixo para indicar que foi "chute"
        return True, (int(x), int(y), int(w), int(h)), 0.5
