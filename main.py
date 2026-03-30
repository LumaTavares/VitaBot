import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from thermalcamera import conectar_serial

camera = None

#acho que nao precisava passar button como parametro
def ligar_camera(button):
    global camera 
    if camera is None:
        button.configure(text="Desligar Camera", command=lambda: desligar_camera(button))
        camera = cv2.VideoCapture(0)
    atualizar_camera()

def desligar_camera(button):
    global camera
    if camera is not None:
        camera.release()
        camera = None
    camera_label.configure(image=None)
    camera_label.image = None
    button.configure(text="Ligar Camera",command=lambda: ligar_camera(button))

def ligar_camera_termica():

def atualizar_camera():
    if camera is not None:
        ret, frame = camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)#converter a imagem de BGR para RGB porque o OpenCV usa BGR 
            img = Image.fromarray(frame) #converte a imagem para o formato PIL
            img= img.resize((600, 500))
            ctk_img = ctk.CTkImage(light_image=img, size=(600, 500)) #converte a imagem para o formato CTkImage
            camera_label.configure(image=ctk_img) #atualiza o label com a nova imagem 
            camera_label.image = ctk_img #atualiza o label com a nova imagem 

        camera_label.after(10, atualizar_camera)    

root = ctk.CTk()
root.attributes('-fullscreen', True)
root.bind('<Escape>', lambda e: root.destroy())
ctk.set_appearance_mode("dark")
root.configure(fg_color="#1b1b1e")

"frame para area da camera"
Camera_Div=ctk.CTkFrame(root,bg_color='black')
Camera_Div.pack(side="left", padx=150, pady=50,anchor="n")

frame1= ctk.CTkFrame(Camera_Div,corner_radius=20, fg_color='#3a3a3f')
frame1.pack()

camera_label = ctk.CTkLabel(frame1, text="",width=600, height=500)
camera_label.pack()

Botao_Camera=ctk.CTkButton(Camera_Div,text="Ligar Camera", font=('Arial', 20), 
                    bg_color='gray',hover_color='darkgray', text_color='white', command=lambda: ligar_camera(Botao_Camera))
Botao_Camera.pack(pady=10)

"frame para camera termica"
Camera_Termica_Div=ctk.CTkFrame(root,bg_color='black')
Camera_Termica_Div.pack(side="right", padx=150, pady=50,anchor="n")

Frame2 = ctk.CTkFrame(Camera_Termica_Div, 
                      width=600,height=500,corner_radius=20, fg_color='#3a3a3f')
Frame2.pack()

Botao_Camera_Termica=ctk.CTkButton(Camera_Termica_Div,text="Vizualizar informações térmicas",
                            font=('Arial', 20), bg_color='gray',hover_color='darkgray',
                            text_color='white')
Botao_Camera_Termica.pack(pady=10)

root.mainloop()