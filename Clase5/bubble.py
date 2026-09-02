def bubble_sort_brute_force(arr):
    n = len(arr)
    # Ciclo externo corre n veces de forma fija
    for i in range(n):
        # Ciclo interno compara elementos adyacentes
        for j in range(0, n - 1):
            if arr[j] > arr[j + 1]:
                # Intercambio de elementos
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
