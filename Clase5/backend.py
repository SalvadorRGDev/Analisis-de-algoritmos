import random
import time

def generar_aleatorios(inicio, incremento, maximo):
    datos = {}

    for tamaño in range(inicio, maximo + 1, incremento):
        datos[tamaño] = [random.randint(1, maximo) for _ in range(tamaño)]

    return datos


def bubble_sort(lista):
    n = len(lista)
    for i in range(n):
        for j in range(n - i - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]


def insert_sort(lista):
    for i in range(1, len(lista)):
        key = lista[i]
        j = i - 1
        while j >= 0 and key < lista[j]:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = key


def ejecutar_analisis1(datos):
    
    tamaños = []
    tiempos = []

    for tamaño in sorted(datos.keys()):

        copia = datos[tamaño].copy()

        print(f"\n--- Ordenando {tamaño} elementos ---")

        inicio = time.time()
        bubble_sort(copia)
        fin = time.time()

        tiempo_transcurrido = fin - inicio
        tamaños.append(tamaño)
        tiempos.append(tiempo_transcurrido)

        print(f"Lista ordenada: {copia[:5]}... (primeros 5)")
        print(f"Tiempo: {tiempo_transcurrido:.6f} segundos")
        print("--------------------------------")

    return tamaños, tiempos

def ejecutar_analisis2(datos):
    
    tamaños = []
    tiempos = []

    for tamaño in sorted(datos.keys()):
        
        copia = datos[tamaño].copy()

        print(f"\n--- Ordenando {tamaño} elementos ---")

        inicio = time.time()
        bubble_sort(copia)
        fin = time.time()

        tiempo_transcurrido = fin - inicio
        tamaños.append(tamaño)
        tiempos.append(tiempo_transcurrido)

        print(f"Lista ordenada: {copia[:5]}... (primeros 5)")
        print(f"Tiempo: {tiempo_transcurrido:.6f} segundos")
        print("--------------------------------")

    return tamaños, tiempos
