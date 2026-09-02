    import random
    import time

    from bubble import bubble_sort_brute_force
    from selection import selection_sort

    def generar_aleatorios(inicio, incremento, maximo):
        datos = {}

        for tamaño in range(inicio, maximo + 1, incremento):
            datos[tamaño] = [random.randint(1, maximo) for _ in range(tamaño)]

        return datos

    def ejecutar_analisis1(datos):
        
        tamaños = []
        tiempos = []

        for tamaño in sorted(datos.keys()):

            copia = datos[tamaño].copy()

            print(f"\n--- Ordenando {tamaño} elementos ---")

            inicio = time.time()
            selection_sort(copia)
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
            bubble_sort_brute_force(copia)
            fin = time.time()

            tiempo_transcurrido = fin - inicio
            tamaños.append(tamaño)
            tiempos.append(tiempo_transcurrido)

            print(f"Lista ordenada: {copia[:5]}... (primeros 5)")
            print(f"Tiempo: {tiempo_transcurrido:.6f} segundos")
            print("--------------------------------")

        return tamaños, tiempos
