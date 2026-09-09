import matplotlib.pyplot as plt

def grafica(tamaños, tiempos):

    plt.plot(tamaños, tiempos[0], label="Insertion Sort")
    plt.plot(tamaños, tiempos[1], label="Gnome Sort")
    plt.plot(tamaños, tiempos[2], label="Exchange Sort")
    plt.plot(tamaños, tiempos[3], label="Stooge Sort")
    plt.legend()
    plt.xlabel("Tamaño del arreglo")
    plt.ylabel("Tiempo")
    plt.title("Tiempo de ejecución de los algoritmos")
    plt.show()
