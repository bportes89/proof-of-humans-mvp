import cv2

def list_cameras():
    print("=== Detectando Câmeras Disponíveis ===")
    available_cameras = []
    
    # Tentar abrir as 5 primeiras câmeras
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) # CAP_DSHOW é melhor para Windows
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    print(f"[OK] Câmera {i}: Resolução {width}x{height}")
                    available_cameras.append(i)
                else:
                    print(f"[FAIL] Câmera {i}: Aberta, mas não leu frame.")
                cap.release()
            else:
                pass # Câmera não existe ou ocupada
        except Exception as e:
            print(f"[ERROR] Erro ao checar câmera {i}: {e}")

    if not available_cameras:
        print("\n[AVISO] Nenhuma câmera detectada pelo OpenCV.")
        print("Dicas:")
        print("1. Verifique se a câmera está plugada.")
        print("2. Se for Thermal Master P3 Pro, use o OBS Studio 'Virtual Camera'.")
        print("3. Verifique se outro programa não está usando a câmera.")
    else:
        print(f"\n[SUCESSO] Câmeras encontradas nos índices: {available_cameras}")
        print("Para usar uma delas, configure a variável de ambiente CAMERA_INDEX.")

if __name__ == "__main__":
    list_cameras()
