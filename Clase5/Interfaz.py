import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider,
    QPushButton, QVBoxLayout, QGridLayout, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
import backend

app = QApplication(sys.argv)

ventana = QWidget()
ventana.setWindowTitle("Analisis de algoritmos")

layout_principal = QVBoxLayout()
ventana.setLayout(layout_principal)

# --- Widgets ---

titulo = QLabel("Analisis de algoritmos")
titulo.setFont(QFont("Arial", 20))
titulo.setAlignment(Qt.AlignCenter)
titulo.setStyleSheet("background-color: #FF6B35; color: white; padding: 20px;")
layout_principal.addWidget(titulo)

#-----------------------------------------------------------------------------------------------#

# Datos para el Algoritmo 1

# Titulo el algoritmo
subtitulo1 = QLabel("Algoritmo 1")
subtitulo1.setFont(QFont("Arial", 15))
subtitulo1.setAlignment(Qt.AlignCenter)
layout_principal.addWidget(subtitulo1)

#Input que se encarga de recibir la cantidad de elementos maximos que puede tener la lista del algoritmo
contenedor_algoritmo1 = QFrame()
layout_principal.addWidget(contenedor_algoritmo1)
grid_algoritmo1 = QGridLayout()
contenedor_algoritmo1.setLayout(grid_algoritmo1)

#Input que se encarga de recibir la cantidad de elementos con el que iniciara el algoritmo
grid_algoritmo1.addWidget(QLabel("Cantidad inicial de elementos:"), 0, 0)
entry_inicio1 = QSlider(Qt.Horizontal)
entry_inicio1.setMinimum(0)
entry_inicio1.setMaximum(100)
grid_algoritmo1.addWidget(entry_inicio1, 0, 1)
valor_inicio1 = QLabel("0")
entry_inicio1.valueChanged.connect(lambda v: valor_inicio1.setText(str(v)))
grid_algoritmo1.addWidget(valor_inicio1, 1, 1)

#Input que se encarga de recibir la cantidad de elementos que se agregaran a la lista del algoritmo por ciclo
grid_algoritmo1.addWidget(QLabel("Incremento por ciclo:"), 0, 2)
entry_incremento1 = QSlider(Qt.Horizontal)
entry_incremento1.setMinimum(0)
entry_incremento1.setMaximum(100)
grid_algoritmo1.addWidget(entry_incremento1, 0, 3)
valor_incremento1 = QLabel("0")
entry_incremento1.valueChanged.connect(lambda v: valor_incremento1.setText(str(v)))
grid_algoritmo1.addWidget(valor_incremento1, 1, 3)

#Input que se encarga de recibir la cantidad de elementos maximos que puede tener la lista del algoritmo
grid_algoritmo1.addWidget(QLabel("Máximo de elementos:"), 0, 4)
entry_maximo1 = QSlider(Qt.Horizontal)
entry_maximo1.setMinimum(0)
entry_maximo1.setMaximum(100)
grid_algoritmo1.addWidget(entry_maximo1, 0, 5)
valor_maximo1 = QLabel("0")
entry_maximo1.valueChanged.connect(lambda v: valor_maximo1.setText(str(v)))
grid_algoritmo1.addWidget(valor_maximo1, 1, 5)

#-----------------------------------------------------------------------------------------------#

# Datos para el Algoritmo 2

# Titulo el algoritmo
subtitulo2 = QLabel("Algoritmo 2")
subtitulo2.setFont(QFont("Arial", 15))
subtitulo2.setAlignment(Qt.AlignCenter)
layout_principal.addWidget(subtitulo2)

#Contenedor que sirve para que se pueda usar grid, con el objetivo de que en esa linea esten los 3 inputs del usuario
contenedor_algoritmo2 = QFrame()
layout_principal.addWidget(contenedor_algoritmo2)
grid_algoritmo2 = QGridLayout()
contenedor_algoritmo2.setLayout(grid_algoritmo2)

#Input que se encarga de recibir la cantidad de elementos con el que iniciara el algoritmo
grid_algoritmo2.addWidget(QLabel("Cantidad inicial de elementos:"), 0, 0)
entry_inicio2 = QSlider(Qt.Horizontal)
entry_inicio2.setMinimum(0)
entry_inicio2.setMaximum(100)
grid_algoritmo2.addWidget(entry_inicio2, 0, 1)
valor_inicio2 = QLabel("0")
entry_inicio2.valueChanged.connect(lambda v: valor_inicio2.setText(str(v)))
grid_algoritmo2.addWidget(valor_inicio2, 1, 1)

#Input que se encarga de recibir la cantidad de elementos que se agregaran a la lista del algoritmo por ciclo
grid_algoritmo2.addWidget(QLabel("Incremento por ciclo:"), 0, 2)
entry_incremento2 = QSlider(Qt.Horizontal)
entry_incremento2.setMinimum(0)
entry_incremento2.setMaximum(100)
grid_algoritmo2.addWidget(entry_incremento2, 0, 3)
valor_incremento2 = QLabel("0")
entry_incremento2.valueChanged.connect(lambda v: valor_incremento2.setText(str(v)))
grid_algoritmo2.addWidget(valor_incremento2, 1, 3)

#Input que se encarga de recibir la cantidad de elementos maximos que puede tener la lista del algoritmo
grid_algoritmo2.addWidget(QLabel("Máximo de elementos:"), 0, 4)
entry_maximo2 = QSlider(Qt.Horizontal)
entry_maximo2.setMinimum(0)
entry_maximo2.setMaximum(100)
grid_algoritmo2.addWidget(entry_maximo2, 0, 5)
valor_maximo2 = QLabel("0")
entry_maximo2.valueChanged.connect(lambda v: valor_maximo2.setText(str(v)))
grid_algoritmo2.addWidget(valor_maximo2, 1, 5)

#-----------------------------------------------------------------------------------------------#

aleatorios1 = {}
aleatorios2 = {}

def generar_click():
    global aleatorios1, aleatorios2

    aleatorios1 = backend.generar_aleatorios(
        entry_inicio1.value(),
        entry_incremento1.value(),
        entry_maximo1.value()
    )

    aleatorios2 = backend.generar_aleatorios(
        entry_inicio2.value(),
        entry_incremento2.value(),
        entry_maximo2.value()
    )

    print(aleatorios1)
    print(aleatorios2)

boton_generar = QPushButton("Generar")
boton_generar.clicked.connect(generar_click)
layout_principal.addWidget(boton_generar)

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

boton_analizar = QPushButton("Analizar")
boton_analizar.clicked.connect(analizar_click)
layout_principal.addWidget(boton_analizar)

#-----------------------------------------------------------------------------------------------#

ventana.show()
sys.exit(app.exec())
