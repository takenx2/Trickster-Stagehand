import tkinter as tk
from PIL import ImageTk,Image
import os
root = tk.Tk()
root.title("Stagehand")
root.geometry("600x400")
img = Image.open("res/circle_48.png")
ico = Image.open("res/icon.png")
root.iconphoto(False,ImageTk.PhotoImage(ico.resize((64,64),Image.Resampling.NEAREST)))
size = (256,256)

sprite = ImageTk.PhotoImage(img.resize(size,Image.Resampling.NEAREST))
canvas = tk.Canvas(root,width=600,height=400,bg="#070707")
x = canvas.create_image(0,0,image=sprite,anchor=tk.CENTER)
def update(z: tk.Event):
    canvas.coords(x,(z.width/2,z.height/2))
canvas.pack(fill="both",expand=True)
canvas.bind("<Configure>",update)
root.mainloop()