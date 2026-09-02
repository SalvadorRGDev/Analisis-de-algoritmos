def analizar(entry_inicio, entry_incremento, entry_maximo, elementos):
    resultados = []
    for i in range(elementos):
        valores_algoritmo = [
            int(entry_inicio[i].get()),
            int(entry_incremento[i].get()),
            int(entry_maximo[i].get())
        ]
        resultados.append(valores_algoritmo)
    return resultados
