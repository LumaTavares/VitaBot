import customtkinter as ctk
import threading
import cv2
from PIL import Image
from webcam import Webcam
from thermalcamera import ThermalCam
import webcam
import thermalcamera
import os
import time
from datetime import datetime

# Variáveis globais da câmera normal
camera = None
url = "http://192.168.1.114:81/stream"

# teste de integração codigo paralelo
camera_rgb = Webcam(id_camera=url, largura=640, altura=480)
camera_term = ThermalCam(porta="COM3", baud_rate=115200)

def salvar_frames(button):
    global camera_rgb, camera_term
    if camera_rgb.running:
        ret, frame_rgb = camera_rgb.read()
        if ret:
            pasta_destino = "capturas_rgb"
            os.makedirs(pasta_destino, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"rgb_{timestamp}.png"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            cv2.imwrite(caminho_completo, cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
            print(f"[{timestamp}] Frame RGB salvo!")

    if camera_term.running:
        resultado = camera_term.read()
        if resultado is not None:
            ok, frame_termico, matriz_termica = resultado
            if ok:
                pasta_destino = "capturas_termicas"
                os.makedirs(pasta_destino, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"termica_{timestamp}.png"
                caminho_completo = os.path.join(pasta_destino, nome_arquivo)
                cv2.imwrite(caminho_completo, cv2.cvtColor(frame_termico, cv2.COLOR_RGB2BGR))
                print(f"[{timestamp}] Frame Térmico salvo!")

def atualizar_cameras():
    global camera_rgb, camera_term
    while True:
        if camera_rgb.running:
            ret, frame_rgb = camera_rgb.read()
            if ret:
                frame_rgb = webcam.process_frame(frame_rgb)
                img_rgb = Image.fromarray(frame_rgb)
                img_rgb = img_rgb.resize((600, 500))
                ctk_img_rgb = ctk.CTkImage(light_image=img_rgb, size=(600, 500))
                camera_label.configure(image=ctk_img_rgb)
                camera_label.image = ctk_img_rgb
        
        if camera_term.running:
            resultado = camera_term.read()
            if resultado is not None:
                ok ,frame_termico, matriz_termica = resultado
                ultimo_frame_termico = frame_termico
                ultima_matriz_termica = matriz_termica
                
                img_termico = Image.fromarray(frame_termico)
                ctk_img_termico = ctk.CTkImage(light_image=img_termico, size=(600, 500))
                camera_termica_label.configure(image=ctk_img_termico)
                camera_termica_label.image = ctk_img_termico

        time.sleep(0.1)  # Pequena pausa para evitar sobrecarga da CPU

threading.Thread(target=atualizar_cameras, daemon=True).start()



# start camera parlelo
def ligar_camera_rgb(button):
    global camera_rgb
    if not camera_rgb.running:
        camera_rgb.start()
        button.configure(text="Desligar Câmera", command=lambda: desligar_camera_rgb(button))

def desligar_camera_rgb(button):
    global camera_rgb
    if camera_rgb.running:
        camera_rgb.stop()
        button.configure(text="Ligar Câmera", command=lambda: ligar_camera_rgb(button))

def ligar_camera_term(button):
    global camera_term
    if not camera_term.running:
        camera_term.start()
        button.configure(text="Desligar Câmera Térmica", command=lambda: desligar_camera_term(button))

def desligar_camera_term(button):
    global camera_term
    if camera_term.running:
        camera_term.stop()
        button.configure(text="Visualizar informações térmicas", command=lambda: ligar_camera_term(button))



# ================= CONFIGURAÇÃO DA INTERFACE =================
root = ctk.CTk()
root.attributes('-fullscreen', True)
root.bind('<Escape>', lambda e: root.destroy())
ctk.set_appearance_mode("dark")
root.configure(fg_color="#1b1b1e")

# --- Divisão da Câmera Normal ---
Camera_Div = ctk.CTkFrame(root, bg_color='black')
Camera_Div.pack(side="left", padx=150, pady=50, anchor="n")

frame1 = ctk.CTkFrame(Camera_Div, corner_radius=20, fg_color='#3a3a3f')
frame1.pack()

camera_label = ctk.CTkLabel(frame1, text="", width=600, height=500)
camera_label.pack()

Botao_Camera = ctk.CTkButton(Camera_Div, text="Ligar Câmera", font=('Arial', 20), 
                    bg_color='gray', hover_color='darkgray', text_color='white', 
                    command=lambda: ligar_camera_rgb(Botao_Camera))
Botao_Camera.pack(pady=10)

# --- Divisão da Câmera Térmica ---
Camera_Termica_Div = ctk.CTkFrame(root, bg_color='black')
Camera_Termica_Div.pack(side="right", padx=150, pady=50, anchor="n")

Frame2 = ctk.CTkFrame(Camera_Termica_Div, width=600, height=500, corner_radius=20, fg_color='#3a3a3f')
Frame2.pack()

camera_termica_label = ctk.CTkLabel(Frame2, text="", width=600, height=500)
camera_termica_label.pack()

# ---> VÍNCULO DO EVENTO DE CLIQUE DO MOUSE <---
camera_termica_label.bind("<Button-1>", ao_clicar_termica)

# ---> NOVO LABEL PARA EXIBIR A TEMPERATURA <---
label_temperatura = ctk.CTkLabel(Camera_Termica_Div, 
                                 text="Clique na imagem térmica para medir a temperatura", 
                                 font=('Arial', 18, 'bold'), 
                                 text_color="#00FF00")
label_temperatura.pack(pady=5)

Botao_Camera_Termica = ctk.CTkButton(Camera_Termica_Div, text="Visualizar informações térmicas",
                            font=('Arial', 20), bg_color='gray', hover_color='darkgray',
                            text_color='white', 
                            command=lambda: ligar_camera_term(Botao_Camera_Termica))
Botao_Camera_Termica.pack(pady=10)

# Botão para alternar o salvamento automático
Botao_Salvar = ctk.CTkButton(Camera_Termica_Div, text="Iniciar Salvamento Automático (2s)",
                            font=('Arial', 20), fg_color='#228B22', hover_color='#006400',
                            text_color='white', command=lambda: salvar_frames(Botao_Salvar))
Botao_Salvar.pack(pady=10)

root.mainloop()