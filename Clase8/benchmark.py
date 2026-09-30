import time
import tracemalloc
import matplotlib.pyplot as plt
from ordenamientos import fibonacci, fibonacci_dp

datos = []

def generador_aleatorios(minimo, maximo, incremento):
    datos.clear()
    for i in range(minimo, maximo + 1, incremento):
        datos.append(i)
    return datos

def medir_rendimiento(arreglo):
    tiempos = {"fibonacci": [], "fibonacci_dp": []}
    memorias = {"fibonacci": [], "fibonacci_dp": []}
    tamaños = []

    for n in arreglo:
        tamaños.append(n)

        tracemalloc.start()
        t0 = time.perf_counter()
        fibonacci(n)
        t1 = time.perf_counter()
        _, peak_rec = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tiempos["fibonacci"].append(t1 - t0)
        memorias["fibonacci"].append(peak_rec / 1024)  # KB

        tracemalloc.start()
        t0 = time.perf_counter()
        fibonacci_dp(n)
        t1 = time.perf_counter()
        _, peak_dp = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tiempos["fibonacci_dp"].append(t1 - t0)
        memorias["fibonacci_dp"].append(peak_dp / 1024)  # KB

    return tamaños, tiempos, memorias

def grafica_solo_dp(tamaños, tiempos_dp, memorias_dp):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(tamaños, tiempos_dp, label="Fibonacci DP", marker='o', color='blue')
    ax1.set_xlabel("Valor de N")
    ax1.set_ylabel("Tiempo (segundos)")
    ax1.set_title("Punto 2: Tiempo - Fibonacci P. Dinámica")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(tamaños, memorias_dp, label="Fibonacci DP", marker='s', color='green')
    ax2.set_xlabel("Valor de N")
    ax2.set_ylabel("Memoria Pico (KB)")
    ax2.set_title("Punto 2: Espacio (Memoria) - Fibonacci P. Dinámica")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def grafica_comparativa(tamaños, tiempos, memorias):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(tamaños, tiempos["fibonacci"], label="Fibonacci (Sin P. Dinámica)", marker='o', color='red')
    ax1.plot(tamaños, tiempos["fibonacci_dp"], label="Fibonacci (Con P. Dinámica)", marker='s', color='blue')
    ax1.set_xlabel("Valor de N")
    ax1.set_ylabel("Tiempo (segundos)")
    ax1.set_title("Punto 3: Comparativa de Tiempo")
    ax1.legend()
    ax1.grid(True)

    ax2.plot(tamaños, memorias["fibonacci"], label="Fibonacci (Sin P. Dinámica)", marker='o', color='red')
    ax2.plot(tamaños, memorias["fibonacci_dp"], label="Fibonacci (Con P. Dinámica)", marker='s', color='blue')
    ax2.set_xlabel("Valor de N")
    ax2.set_ylabel("Memoria Pico (KB)")
    ax2.set_title("Punto 3: Comparativa de Espacio (Memoria)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()