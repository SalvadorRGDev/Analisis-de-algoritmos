import random
import time
import matplotlib.pyplot as plt

from ordenamientos import insertion_sort
from ordenamientos import gnome_sort
from ordenamientos import stooge_sort
from ordenamientos import exchange_sort

datos = {}

def generador_aleatorios(minimo, maximo, incremento):

    for i in range(minimo, maximo+1, incremento):
        datos[i] = [random.randint(1, maximo) for _ in range(i)]

    return datos

def ordenamientos_aleatorios(arreglo):
    tiempos = {"insertion_sort": [], "gnome_sort": [], "exchange_sort": [], "stooge_sort": []}
    tamaños = []

    for i in arreglo:
        tamaños.append(i)
        copy_insertion = datos[i].copy()
        copy_gnome = datos[i].copy()
        copy_exchange = datos[i].copy()
        copy_stooge = datos[i].copy()

        #Insertion Sort
        time_inicio = time.time()
        insertion_sort(copy_insertion)
        time_fin = time.time()
        tiempos["insertion_sort"].append(time_fin - time_inicio)

        #Gnome Sort
        time_inicio = time.time()
        gnome_sort(copy_gnome)
        time_fin = time.time()
        tiempos["gnome_sort"].append(time_fin - time_inicio)

        #Exchange Sort
        time_inicio = time.time()
        exchange_sort(copy_exchange)
        time_fin = time.time()
        tiempos["exchange_sort"].append(time_fin - time_inicio)

        #Stooge Sort
        time_inicio = time.time()
        stooge_sort(copy_stooge)
        time_fin = time.time()
        tiempos["stooge_sort"].append(time_fin - time_inicio)

    return tamaños, [tiempos["insertion_sort"], tiempos["gnome_sort"], tiempos["exchange_sort"], tiempos["stooge_sort"]]



def grafica(tamaños, tiempos):

    plt.plot(tamaños, tiempos[0], label="Insertion Sort")
    plt.plot(tamaños, tiempos[1], label="Gnome Sort")
    plt.plot(tamaños, tiempos[2], label="Exchange Sort")
    #plt.plot(tamaños, tiempos[3], label="Stooge Sort")
    plt.legend()
    plt.xlabel("Tamaño del arreglo")
    plt.ylabel("Tiempo")
    plt.title("Tiempo de ejecución de los algoritmos")
    plt.show()