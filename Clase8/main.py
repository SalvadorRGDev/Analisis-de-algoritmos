from benchmark import (
    generador_aleatorios,
    medir_rendimiento,
    grafica_solo_dp,
    grafica_comparativa
)

min_val = 4
max_val = 40
inc = 2

datos_aleatorios = generador_aleatorios(min_val, max_val, inc)
tamaños, tiempos, memorias = medir_rendimiento(datos_aleatorios)

grafica_solo_dp(tamaños, tiempos["fibonacci_dp"], memorias["fibonacci_dp"])

grafica_comparativa(tamaños, tiempos, memorias)