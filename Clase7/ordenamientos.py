def insertion_sort(lista):
    """
    Ordenamiento por Inserción.
    Complejidad: O(N^2)
    """
    arr = lista.copy()
    for i in range(1, len(arr)):
        clave = arr[i]
        j = i - 1
        # Compara la clave con los elementos anteriores y los desplaza
        while j >= 0 and arr[j] > clave:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = clave
    return arr


def gnome_sort(lista):
    arr = lista.copy()
    i = 0
    n = len(arr)
    
    while i < n:
        if i == 0 or arr[i] >= arr[i - 1]:
            i += 1  # Avanza si está en orden
        else:
            arr[i], arr[i - 1] = arr[i - 1], arr[i]  # Intercambia
            i -= 1  # Retrocede un paso
            
    return arr

def stooge_sort_rec(arr, l, h):
    if l >= h:
        return

    # Si el primer elemento es mayor que el último, intercambiar
    if arr[l] > arr[h]:
        arr[l], arr[h] = arr[h], arr[l]

    # Si hay 3 o más elementos en el rango
    if h - l + 1 > 2:
        t = (h - l + 1) // 3
        # Aplicar fuerza bruta a los 3 tercios superpuestos
        stooge_sort_rec(arr, l, h - t)       # Primeros 2/3
        stooge_sort_rec(arr, l + t, h)       # Últimos 2/3
        stooge_sort_rec(arr, l, h - t)       # Primeros 2/3 de nuevo

def stooge_sort(lista):
    arr = lista.copy()
    stooge_sort_rec(arr, 0, len(arr) - 1)
    return arr

def exchange_sort(lista):
    """
    Ordenamiento por Intercambio Directo (Exchange Sort).
    Complejidad: O(N^2)
    """
    arr = lista.copy()
    n = len(arr)
    for i in range(n - 1):
        for j in range(i + 1, n):
            # Si el elemento posterior es menor, intercambia de inmediato
            if arr[j] < arr[i]:
                arr[i], arr[j] = arr[j], arr[i]
    return arr