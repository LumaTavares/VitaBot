import serial
import numpy as np
import cv2

def conectar_serial():
    porta = "COM3"  # porta serial pode ajustar se precisar
    baud_rate = 115200

    try:
        ser = serial.Serial(porta, baud_rate, timeout=1) # canal de comunicação serial
        print("Comunicação estabelecida com a porta", porta)
        return ser
    except serial.SerialException as e:
        print(f"Erro ao conectar à porta serial: {e}")
        return None

def ler_frame(ser):
    frame_linhas = []
    
    while True:
        data = ser.readline().decode('utf-8', errors='ignore').strip()
        
        # Quando a câmera disser que o frame acabou, saímos do loop
        if data == "FRAME_END":
            if len(frame_linhas) == 24: # Garante que leu as 24 linhas corretamente
                break
            else:
                frame_linhas = [] # Se vier quebrado, descarta e tenta de novo
                continue
        
        # Se tiver dados, converte a linha de texto para uma lista de floats
        if data:
            try:
                linha = [float(n) for n in data.split(",") if n]
                if len(linha) == 32:
                    frame_linhas.append(linha)
            except ValueError:
                pass # Ignora lixo na serial

    # Converte para array Numpy
    frame = np.array(frame_linhas, dtype=np.float32)
    min_val = np.min(frame)
    max_val = np.max(frame)

    # Evita erro de divisão por zero caso a imagem venha toda de uma cor só
    if max_val == min_val:
        norm = np.zeros_like(frame, dtype=np.uint8)
    else:
        norm = ((frame - min_val) / (max_val - min_val)) * 255
        norm = norm.astype(np.uint8)

    # Redimensiona e aplica o mapa de calor
    resized = cv2.resize(norm, (600, 500), interpolation=cv2.INTER_CUBIC)
    thermal_bgr = cv2.applyColorMap(resized, cv2.COLORMAP_INFERNO)
    
    # IMPORTANTE: OpenCV usa BGR, mas o Tkinter/Pillow usa RGB. Precisamos converter!
    thermal_rgb = cv2.cvtColor(thermal_bgr, cv2.COLOR_BGR2RGB)

    # Retorna a imagem RGB para exibição E a matriz original com as temperaturas reais
    return thermal_rgb, frame