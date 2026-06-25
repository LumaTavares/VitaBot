import customtkinter as ctk
import cv2
from PIL import Image
import webcam
import thermalcamera
import os
from datetime import datetime

# Variáveis globais da câmera normal
camera = None
url = "http://172.19.176.26:81/stream"

# Variáveis globais da câmera térmica
ser_termica = None
rodando_termica = False
ultimo_frame_termico = None

# Variável de controle do salvamento automático
auto_salvando = False

# ================= CÂMERA NORMAL =================
def ligar_camera(button):
    global camera 
    if camera is None:
        button.configure(text="Desligar Câmera", command=lambda: desligar_camera(button))
        camera = cv2.VideoCapture(url)
    atualizar_camera()

def desligar_camera(button):
    global camera
    if camera is not None:
        camera.release()
        camera = None
    camera_label.configure(image=None)
    camera_label.image = None
    button.configure(text="Ligar Câmera", command=lambda: ligar_camera(button))

def atualizar_camera():
    if camera is not None:
        ret, frame = camera.read()
        if ret:
            frame = webcam.process_frame(frame)
            img = Image.fromarray(frame)
            img = img.resize((600, 500))
            ctk_img = ctk.CTkImage(light_image=img, size=(600, 500))
            camera_label.configure(image=ctk_img)
            camera_label.image = ctk_img

        camera_label.after(10, atualizar_camera)    

# ================= CÂMERA TÉRMICA =================
def ligar_camera_termica(button):
    global ser_termica, rodando_termica
    if not rodando_termica:
        ser_termica = thermalcamera.conectar_serial()
        if ser_termica is not None:
            rodando_termica = True
            button.configure(text="Desligar Câmera Térmica", command=lambda: desligar_camera_termica(button))
            atualizar_camera_termica()

def desligar_camera_termica(button):
    global ser_termica, rodando_termica
    rodando_termica = False
    if ser_termica is not None:
        ser_termica.close()
        ser_termica = None
    
    camera_termica_label.configure(image=None)
    camera_termica_label.image = None
    button.configure(text="Visualizar informações térmicas", command=lambda: ligar_camera_termica(button))

def atualizar_camera_termica():
    global ser_termica, rodando_termica, ultimo_frame_termico
    if rodando_termica and ser_termica is not None:
        frame_termico = thermalcamera.ler_frame(ser_termica)
        
        if frame_termico is not None:
            ultimo_frame_termico = frame_termico
            img = Image.fromarray(frame_termico)
            ctk_img = ctk.CTkImage(light_image=img, size=(600, 500))
            camera_termica_label.configure(image=ctk_img)
            camera_termica_label.image = ctk_img
            
        camera_termica_label.after(10, atualizar_camera_termica)

# ================= SALVAMENTO AUTOMÁTICO =================
def toggle_auto_salvar():
    global auto_salvando
    
    # Inverte o estado atual
    auto_salvando = not auto_salvando
    
    if auto_salvando:
        Botao_Salvar.configure(text="Parar Salvamento Automático", fg_color='#8B0000', hover_color='#640000')
        print("Salvamento automático INICIADO.")
        loop_salvamento() # Inicia o ciclo de salvamento
    else:
        Botao_Salvar.configure(text="Iniciar Salvamento Automático (2s)", fg_color='#228B22', hover_color='#006400')
        print("Salvamento automático PARADO.")

def loop_salvamento():
    global auto_salvando, ultimo_frame_termico
    
    # Só executa se o modo de auto-salvamento ainda estiver ativado
    if auto_salvando:
        # Só salva se a câmera térmica estiver ligada e gerando frames
        if ultimo_frame_termico is not None and rodando_termica:
            pasta_destino = "capturas_termicas"
            os.makedirs(pasta_destino, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"termica_{timestamp}.png"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            
            frame_bgr = cv2.cvtColor(ultimo_frame_termico, cv2.COLOR_RGB2BGR)
            cv2.imwrite(caminho_completo, frame_bgr)
            print(f"[{timestamp}] Frame salvo automaticamente!")
            
        # Agenda a próxima execução dessa mesma função para daqui a 2000 milissegundos (2 segundos)
        root.after(2000, loop_salvamento)

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
                    command=lambda: ligar_camera(Botao_Camera))
Botao_Camera.pack(pady=10)

# --- Divisão da Câmera Térmica ---
Camera_Termica_Div = ctk.CTkFrame(root, bg_color='black')
Camera_Termica_Div.pack(side="right", padx=150, pady=50, anchor="n")

Frame2 = ctk.CTkFrame(Camera_Termica_Div, width=600, height=500, corner_radius=20, fg_color='#3a3a3f')
Frame2.pack()

camera_termica_label = ctk.CTkLabel(Frame2, text="", width=600, height=500)
camera_termica_label.pack()

Botao_Camera_Termica = ctk.CTkButton(Camera_Termica_Div, text="Visualizar informações térmicas",
                            font=('Arial', 20), bg_color='gray', hover_color='darkgray',
                            text_color='white', 
                            command=lambda: ligar_camera_termica(Botao_Camera_Termica))
Botao_Camera_Termica.pack(pady=10)

# Botão atualizado para alternar o salvamento automático
Botao_Salvar = ctk.CTkButton(Camera_Termica_Div, text="Iniciar Salvamento Automático (2s)",
                            font=('Arial', 20), fg_color='#228B22', hover_color='#006400',
                            text_color='white', command=toggle_auto_salvar)
Botao_Salvar.pack(pady=10)

root.mainloop()