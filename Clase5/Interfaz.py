import tkinter as tk
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

#Estos Widgets tienen la finalidad de recibir cuantos algoritmos
#el usuario va a introducir, de esta forma se hara un programa
#que pueda analizar cualquier cantidad de algoritmos.
#Mejorando la experiencia del usuario.

mensaje_elementos = tk.Label(
    ventana,
    text="¿Cuantos elementos quieres analizar?",
    font=("Arial", 15)
)
mensaje_elementos.pack()

elementos = tk.IntVar(value=0)

entrada = tk.Entry(ventana, textvariable=elementos)
entrada.pack()

frame_campos = tk.Frame(ventana)

entry_inicio = []
entry_incremento = []  
entry_maximo = []  

def generar_campos():
    for i in range(elementos.get()):
        tk.Label(frame_campos, text="Cantidad inicial de elementos:").grid(row=i, column=0) 

        entry_inicio.append(tk.Entry(frame_campos))  
        entry_inicio[i].grid(row=i, column=1)  

        tk.Label(frame_campos, text="Incremento por ciclo:").grid(row=i, column=2)  

        entry_incremento.append(tk.Entry(frame_campos))  
        entry_incremento[i].grid(row=i, column=3)  

        tk.Label(frame_campos, text="Máximo de elementos:").grid(row=i, column=4)  

        entry_maximo.append(tk.Entry(frame_campos)) 
        entry_maximo[i].grid(row=i, column=5) 

boton_elementos = tk.Button(ventana, text="Confirmar", command=generar_campos)
boton_elementos.pack()

frame_campos.pack()

#-----------------------------------------------------------------------------------------------#

def analizar_click():
    resultados = backend.analizar(entry_inicio, entry_incremento, entry_maximo, elementos.get())  
    print(resultados)  

boton_analizar = tk.Button(ventana, text="Analizar", command=analizar_click)  
boton_analizar.pack()  

#-----------------------------------------------------------------------------------------------#


ventana.mainloop()