import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend import generar_datos_aleatorios, ejecutar_analisis


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Algoritmos - Bubble Sort")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e2e")

        self.datos = None  # Aquí se guardan los datos generados

        self._crear_interfaz()

    def _crear_interfaz(self):
        # --- Título ---
        tk.Label(
            self.root,
            text="Análisis de Algoritmos",
            font=("Arial", 18, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4",
        ).pack(pady=(15, 5))

        tk.Label(
            self.root,
            text="Bubble Sort — O(n²)",
            font=("Arial", 12),
            bg="#1e1e2e",
            fg="#a6adc8",
        ).pack(pady=(0, 15))

        # --- Frame de inputs ---
        frame_inputs = tk.Frame(self.root, bg="#313244", padx=20, pady=15)
        frame_inputs.pack(padx=20, fill="x")

        # Input 1: Inicio
        tk.Label(
            frame_inputs,
            text="Cantidad inicial de elementos:",
            font=("Arial", 11),
            bg="#313244",
            fg="#cdd6f4",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.entry_inicio = tk.Entry(
            frame_inputs, font=("Arial", 11), width=15, bg="#45475a", fg="#cdd6f4",
            insertbackground="#cdd6f4"
        )
        self.entry_inicio.grid(row=0, column=1, padx=10, pady=5)
        self.entry_inicio.insert(0, "20")

        # Input 2: Incremento
        tk.Label(
            frame_inputs,
            text="Incremento por ciclo:",
            font=("Arial", 11),
            bg="#313244",
            fg="#cdd6f4",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.entry_incremento = tk.Entry(
            frame_inputs, font=("Arial", 11), width=15, bg="#45475a", fg="#cdd6f4",
            insertbackground="#cdd6f4"
        )
        self.entry_incremento.grid(row=1, column=1, padx=10, pady=5)
        self.entry_incremento.insert(0, "10")

        # Input 3: Máximo
        tk.Label(
            frame_inputs,
            text="Máximo de elementos:",
            font=("Arial", 11),
            bg="#313244",
            fg="#cdd6f4",
            anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=5)

        self.entry_maximo = tk.Entry(
            frame_inputs, font=("Arial", 11), width=15, bg="#45475a", fg="#cdd6f4",
            insertbackground="#cdd6f4"
        )
        self.entry_maximo.grid(row=2, column=1, padx=10, pady=5)
        self.entry_maximo.insert(0, "100")

        # --- Frame de botones ---
        frame_botones = tk.Frame(self.root, bg="#1e1e2e")
        frame_botones.pack(pady=15)

        self.btn_generar = tk.Button(
            frame_botones,
            text="1. Generar Datos Aleatorios",
            font=("Arial", 11, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#74c7ec",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._generar_datos,
        )
        self.btn_generar.grid(row=0, column=0, padx=10)

        self.btn_analizar = tk.Button(
            frame_botones,
            text="2. Iniciar Análisis",
            font=("Arial", 11, "bold"),
            bg="#a6e3a1",
            fg="#1e1e2e",
            activebackground="#94e2d5",
            padx=15,
            pady=8,
            cursor="hand2",
            state="disabled",
            command=self._iniciar_analisis,
        )
        self.btn_analizar.grid(row=0, column=1, padx=10)

        # --- Label de estado ---
        self.label_estado = tk.Label(
            self.root,
            text="Ingresa los parámetros y genera los datos.",
            font=("Arial", 10),
            bg="#1e1e2e",
            fg="#a6adc8",
        )
        self.label_estado.pack(pady=(0, 10))

        # --- Frame para la gráfica ---
        self.frame_grafica = tk.Frame(self.root, bg="#1e1e2e")
        self.frame_grafica.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _validar_inputs(self):
        """Valida que los 3 inputs sean números enteros positivos y lógicos."""
        try:
            inicio = int(self.entry_inicio.get())
            incremento = int(self.entry_incremento.get())
            maximo = int(self.entry_maximo.get())
        except ValueError:
            messagebox.showerror("Error", "Todos los campos deben ser números enteros.")
            return None

        if inicio <= 0 or incremento <= 0 or maximo <= 0:
            messagebox.showerror("Error", "Todos los valores deben ser mayores a 0.")
            return None

        if inicio > maximo:
            messagebox.showerror(
                "Error", "La cantidad inicial no puede ser mayor al máximo."
            )
            return None

        return inicio, incremento, maximo

    def _generar_datos(self):
        """Genera los datos aleatorios usando el backend."""
        valores = self._validar_inputs()
        if valores is None:
            return

        inicio, incremento, maximo = valores
        self.datos = generar_datos_aleatorios(inicio, incremento, maximo)

        cantidades = sorted(self.datos.keys())
        self.label_estado.config(
            text=f"✅ Datos generados: {len(cantidades)} listas — "
                 f"tamaños: {cantidades[0]} a {cantidades[-1]}",
            fg="#a6e3a1",
        )

        # Habilitar el botón de análisis
        self.btn_analizar.config(state="normal")

    def _iniciar_analisis(self):
        """Ejecuta el análisis de bubble sort y muestra la gráfica."""
        if self.datos is None:
            messagebox.showwarning("Aviso", "Primero genera los datos aleatorios.")
            return

        self.label_estado.config(text="⏳ Ejecutando análisis...", fg="#f9e2af")
        self.root.update()

        # Ejecutar análisis desde el backend
        tamaños, tiempos = ejecutar_analisis(self.datos)

        self.label_estado.config(
            text=f"✅ Análisis completado — {len(tamaños)} pruebas realizadas.",
            fg="#a6e3a1",
        )

        # Mostrar gráfica
        self._mostrar_grafica(tamaños, tiempos)

    def _mostrar_grafica(self, tamaños, tiempos):
        """Dibuja la gráfica de rendimiento dentro de la ventana."""
        # Limpiar gráfica anterior si existe
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 4), dpi=100, facecolor="#1e1e2e")
        ax = fig.add_subplot(111)

        # Estilo oscuro para la gráfica
        ax.set_facecolor("#313244")
        ax.plot(tamaños, tiempos, "o-", color="#89b4fa", linewidth=2, markersize=6)
        ax.set_xlabel("Cantidad de elementos (n)", color="#cdd6f4", fontsize=11)
        ax.set_ylabel("Tiempo (segundos)", color="#cdd6f4", fontsize=11)
        ax.set_title("Bubble Sort — O(n²)", color="#cdd6f4", fontsize=13, fontweight="bold")
        ax.tick_params(colors="#a6adc8")
        ax.grid(True, color="#45475a", linestyle="--", alpha=0.5)

        for spine in ax.spines.values():
            spine.set_color("#45475a")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()