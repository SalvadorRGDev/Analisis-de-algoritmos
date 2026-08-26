import time

def bubble_sort(arr):
    # Complejidad temporal
    #print(type(arr))
    #print(len(arr))

    #time.sleep(100)

    n = len(arr)  # O(1)

    # Bucle exterior:
    for i in range(n):  # O(n)

        # Bucle interior:
        for j in range(0, n - i - 1):  # O(n)

            # Comparación: O(1)
            if arr[j] > arr[j + 1]:  # O(1)

                # Intercambio: O(1)
                arr[j], arr[j + 1] = arr[j + 1], arr[j]  # O(1)


array = [6, 5, 3, 1, 8, 7, 2, 4]  # O(1)

bubble_sort(array)  # O(n^2)

print("\n")  # O(1)
print("Lista ordenada:", array, "\n")  # O(n)
print("--------------------------------")  # O(1)