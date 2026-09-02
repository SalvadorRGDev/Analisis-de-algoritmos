import random
import time

def generar_aleatorios(entry_inicio, entry_incremento, entry_maximo, elementos):
    entradas_algoritmos = []
    for i in range(elementos):
        valores_algoritmo = [
            int(entry_inicio[i].get()),
            int(entry_incremento[i].get()),
            int(entry_maximo[i].get())
        ]
        entradas_algoritmos.append(valores_algoritmo)

    datos = []

    for campos in entradas_algoritmos:
        inicio = campos[0]
        incremento = campos[1]
        maximo = campos[2]

        for tamaño in range(inicio, maximo + 1, incremento):
            datos.append([random.randint(1, maximo) for _ in range(tamaño)])

    return datos
        
        

    
    

