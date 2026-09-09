from benchmark import generador_aleatorios, ordenamientos_aleatorios, grafica

min = 20
max = 100
inc = 20

datos_aleatorios = generador_aleatorios(min, max, inc)

tamaños, tiempos = ordenamientos_aleatorios(datos_aleatorios.keys())

grafica(tamaños, tiempos)