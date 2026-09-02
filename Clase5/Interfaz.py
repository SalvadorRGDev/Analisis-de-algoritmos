import tkinter as tk
import matplotlib.pyplot as plt
import backend

ventana = tk.Tk()
ventana.title("Analisis de algoritmos")


# --- Widgets ---

titulo = tk.Label(
    ventana,
    text="Analisis de algoritmos",
    font=("Arial", 20),
    bg="#FF6B35",
    fg="white",
    padx=20,
    pady=20
)
titulo.pack(fill="x")

#-----------------------------------------------------------------------------------------------#

# Datos para el Algoritmo 1

subtitulo1 = tk.Label(ventana, text="Algoritmo 1", font=("Arial", 15))
subtitulo1.pack()

contenedor_algoritmo1 = tk.Frame(ventana)
contenedor_algoritmo1.pack()

tk.Label(contenedor_algoritmo1, text="Cantidad inicial de elementos:").grid(row=0, column=0)
entry_inicio1 = tk.Entry(contenedor_algoritmo1)
entry_inicio1.grid(row=0, column=1)

tk.Label(contenedor_algoritmo1, text="Incremento por ciclo:").grid(row=0, column=2)
entry_incremento1 = tk.Entry(contenedor_algoritmo1)
entry_incremento1.grid(row=0, column=3)

tk.Label(contenedor_algoritmo1, text="Máximo de elementos:").grid(row=0, column=4)
entry_maximo1 = tk.Entry(contenedor_algoritmo1)
entry_maximo1.grid(row=0, column=5)

#-----------------------------------------------------------------------------------------------#

# Datos para el Algoritmo 2

subtitulo2 = tk.Label(ventana, text="Algoritmo 2", font=("Arial", 15))
subtitulo2.pack()

contenedor_algoritmo2 = tk.Frame(ventana)
contenedor_algoritmo2.pack()

tk.Label(contenedor_algoritmo2, text="Cantidad inicial de elementos:").grid(row=0, column=0)
entry_inicio2 = tk.Entry(contenedor_algoritmo2)
entry_inicio2.grid(row=0, column=1)

tk.Label(contenedor_algoritmo2, text="Incremento por ciclo:").grid(row=0, column=2)
entry_incremento2 = tk.Entry(contenedor_algoritmo2)
entry_incremento2.grid(row=0, column=3)

tk.Label(contenedor_algoritmo2, text="Máximo de elementos:").grid(row=0, column=4)
entry_maximo2 = tk.Entry(contenedor_algoritmo2)
entry_maximo2.grid(row=0, column=5)

#-----------------------------------------------------------------------------------------------#

aleatorios1 = {}
aleatorios2 = {}

def generar_click():
    global aleatorios1, aleatorios2

    aleatorios1 = backend.generar_aleatorios(
        int(entry_inicio1.get()),
        int(entry_incremento1.get()),
        int(entry_maximo1.get())
    )

    aleatorios2 = backend.generar_aleatorios(
        int(entry_inicio2.get()),
        int(entry_incremento2.get()),
        int(entry_maximo2.get())
    )

    print(aleatorios1)
    print(aleatorios2)

boton_generar = tk.Button(ventana, text="Generar", command=generar_click)
boton_generar.pack()

def analizar_click():
    tamaños1, tiempos1 = backend.ejecutar_analisis1(aleatorios1)
    tamaños2, tiempos2 = backend.ejecutar_analisis2(aleatorios2)

    plt.plot(tamaños1, tiempos1, marker="o", label="Algoritmo 1")
    plt.plot(tamaños2, tiempos2, marker="o", label="Algoritmo 2")
    plt.xlabel("Tamaño")
    plt.ylabel("Tiempo (s)")
    plt.title("Comparación de algoritmos")
    plt.legend()
    plt.show()

boton_analizar = tk.Button(ventana, text="Analizar", command=analizar_click)
boton_analizar.pack()

#-----------------------------------------------------------------------------------------------#


ventana.mainloop()
