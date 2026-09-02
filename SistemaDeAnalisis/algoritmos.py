import time

def bubble_sort(arr):
    # Complejidad temporal
    print(type(arr))
    print(len(arr))

    n = len(arr)  # O(1)

    # Bucle exterior:
    for i in range(n):  # O(n)

        # Bucle interior:
        for j in range(0, n - i - 1):  # O(n)

            # Comparación: O(1)
            if arr[j] > arr[j + 1]:  # O(1)

                # Intercambio: O(1)
                arr[j], arr[j + 1] = arr[j + 1], arr[j]  # O(1)
