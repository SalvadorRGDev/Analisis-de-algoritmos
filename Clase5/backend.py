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

