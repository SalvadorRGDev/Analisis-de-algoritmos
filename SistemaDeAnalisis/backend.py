import random
import time

from algoritmos import bubble_sort 


def generar_datos_aleatorios(inicio, incremento, maximo):
    """
    Genera un diccionario de listas aleatorias.
    Las claves son el tamaño de cada lista.
    
    Ejemplo: inicio=20, incremento=10, maximo=100
    Genera listas de tamaños: 20, 30, 40, 50, 60, 70, 80, 90, 100
    """
    datos = {}

    for tamaño in range(inicio, maximo + 1, incremento):
        datos[tamaño] = [random.randint(1, maximo) for _ in range(tamaño)]

    return datos


def ejecutar_analisis(datos):
    """
    Ejecuta bubble sort sobre cada lista de datos y mide el tiempo.
    Retorna dos listas: tamaños (X) y tiempos (Y) para graficar.
    """
    tamaños = []
    tiempos = []

    for tamaño in sorted(datos.keys()):
        # Se hace una copia para no modificar los datos originales
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
