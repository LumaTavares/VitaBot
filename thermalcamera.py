import serial
import numpy as np
import cv2

def conectar_serial():
    porta = "COM8"  # porta serial pode ajustar se precisar
    baud_rate = 115200

    try:
        ser = serial.Serial(porta, baud_rate, timeout=1) #canal de comunicação serial
        print("comunicação estabelecida com a porta", porta)
        ler_frame(ser)
    except serial.SerialException as e:
        print(f"Erro ao conectar à porta serial: {e}")
        return None

def ler_frame(ser):
    height= 24
    width = 32
    frame_linhas=[]
    while True:
        data = ser.readline().decode('utf-8', errors='ignore').strip()
        if data != "FRAME_END":
            for n in data.split(","):
                i=0
                while i < width:
                    i+=1
                    linha=[]
                    linha.append(float(n))
            frame_linhas.append(linha)
                    
        print(frame_linhas)
        frame = np.array(frame_linhas, dtype=np.float32)
        min_val = np.min(frame)
        max_val = np.max(frame)

        norm = ((frame - min_val)/(max_val - min_val)) * 255 #precisa transformar a imagem em cinza pro colormap funcionar
        norm = norm.astype(np.uint8)

        resized= cv2.resize(norm,(640,480),interpolation=cv2.INTER_CUBIC)
        thermal = cv2.applyColorMap(resized, cv2.COLORMAP_INFERNO)

        return thermal
        


conectar_serial()