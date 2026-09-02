import tkinter as tk


def saludar():
    nombre = entrada.get()
    etiqueta_saludo.config(text=f"HOLA {nombre}")


ventana = tk.Tk()
ventana.title("Saludo")

titulo = tk.Label(ventana, text="Programa de saludo")
titulo.pack()

entrada = tk.Entry(ventana)
entrada.pack()

boton = tk.Button(ventana, text="Saludar", command=saludar)
boton.pack()

etiqueta_saludo = tk.Label(ventana, text="")
etiqueta_saludo.pack()

ventana.mainloop()
