import cv2
import tkinter as tk
from tkinter import Label, Button, Entry, ttk
from tkinter import *
from PIL import Image, ImageTk
#from networkx.utils.configs import config

from platedetec import ocr_plate, clear_gpu_memory
from crud import inc_not_seen_all, exist_auto, liquidar_auto, up_fecha_liquidar
from util import crea_image
# Reemplaza con la URL de tu cámara IP
camera_url = "http://192.168.1.172"


class CameraApp:
    def __init__(self, master):
        self.frame = None
        self.master = master
        self.master.title("Cámara IP")

        self.video_source = camera_url

        self.label = Label(master, text="Retirar manualmente un auto: ", font=("Arial",23))
        self.label.grid(row=10, column=10)

        self.tx_placa = Entry(master,width=10,font=("Arial", 25))
        self.tx_placa.place(x=50,y=50)

        bt_retirar = tk.Button(master, text="Retirar Auto", width=16, font=("Arial", 23))
        bt_retirar.place(x=220, y=50)
        bt_retirar.bind("<Button-1>", lambda _: self.win_pago())

        self.lb_pago = tk.Label(master, text="", width=52, font=("Arial", 23))
        self.lb_pago.place(x=10,y=120)

        self.update()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)




    def update(self):
        #self.win_pago()
        self.vid = cv2.VideoCapture(self.video_source)
        ret, self.frame = self.vid.read()
        foto = self.frame
        if ret:

            # Convertir el frame a formato RGB
            frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            # Convertir a imagen de PIL
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            #self.label.imgtk = imgtk
            #self.label.configure(image=imgtk)
            print("llamo a la funcion ocr_plate")
            plate = ocr_plate(frame)
            #type(f"tipo objeto plate {plate}")
            #int(plate)
            #print(f"plate retornada por ocr_plate: {plate}")
            crea_image(self.frame, f"in")
            if plate == 0:
                inc_not_seen_all()
        # Llamar a la función de actualización cada 10 ms
        self.label.after(10, self.update)
        #self.win_pago(100, self.update)

    def btpago_click(self):
        placa = self.tx_placa.get()
        print(f"se va a liquidar el auto {placa}")

    def on_closing(self):
        self.vid.release()
        self.master.destroy()

    def win_pago(self):
        placa_retirar = self.tx_placa.get()
        placa_retirar = placa_retirar.upper().replace(' ','').replace('-','')
        print(f"Busco la placa {placa_retirar} en la bd.")
        r, idauto = exist_auto(placa_retirar)
        r = int(r)
        idauto = int(idauto)

        if r==0:
           print(f"La placa {placa_retirar} no existe en la base de datos o ya fue retirado por el sistema, por favor verifique los datos ingresados.")
           self.lb_pago.config(text = f"No exite esa placa {placa_retirar}. Es posible que ya haya sido retirado.")
        else:
           print(f"Se retira la placa {placa_retirar} con id {idauto}")
           up_fecha_liquidar(idauto)
           total_pago, totalhoras, date_in,date_out = liquidar_auto(idauto)
           print(f"El auto paga ${total_pago}")
           self.lb_pago.config(text=f"Se retira la placa {placa_retirar}, total a pagar ${total_pago}.\n Ingreso: {date_in} \n salida: {date_out} \n horas:{totalhoras}")
           my_frame = self.frame






if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.geometry("1200x300")
    root.mainloop()
