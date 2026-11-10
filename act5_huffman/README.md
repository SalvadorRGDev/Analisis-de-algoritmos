# HADA · Compresor Huffman y árbol de expansión mínima

Actividad 5 de **Análisis de Algoritmos** (2026B). Aplicación de escritorio en
Python (Tkinter + matplotlib) que comprime textos con el **algoritmo de Huffman**
(técnica voraz), los guarda en un formato propio `.hada`, permite inspeccionar ese
archivo sin el `.txt` original, lo descomprime y verifica que el resultado sea
idéntico. Incluye una segunda parte con el **árbol de expansión mínima**
(Kruskal y Prim), otro algoritmo voraz.

```
BUSCAR LIBRO / SUBIR TXT → ANALIZAR → CONSTRUIR HUFFMAN → COMPRIMIR → INSPECCIONAR → DESCOMPRIMIR
```

## Integrante

Actividad individual: Salvador ([@SalvadorRGDev](https://github.com/SalvadorRGDev)).

Reporte técnico: [docs/reporte_actividad5.pdf](docs/reporte_actividad5.pdf).

## Cómo ejecutar

Requisitos: Python 3.10 o superior con Tkinter, y matplotlib.

```bash
pip install -r requirements.txt   # solo matplotlib
python3 main.py
```

Si falta Tkinter: `sudo pacman -S tk` (Arch/CachyOS), `sudo apt install python3-tk`
(Debian/Ubuntu). En Windows y macOS viene con el instalador de python.org.

Pruebas y evidencias:

```bash
python3 -m unittest discover -s tests -v
python3 evidencias/generar_evidencias.py --nuevo <ID de Gutenberg o ruta a un .txt>
```

## Qué hace cada pestaña

| Pestaña | Contenido |
|---|---|
| **1 · Texto de entrada** | Abrir un `.txt` local, escribir un texto corto, o **buscar en Project Gutenberg** por título, autor o palabras clave y descargar el libro elegido. |
| **2 · Frecuencias y códigos** | Tabla ordenable (símbolo, Unicode, frecuencia, %, código, bits) y gráfica de frecuencia contra longitud del código. Muestra la entropía y los bits promedio por símbolo. |
| **3 · Árbol de Huffman** | Árbol dibujado con zoom y desplazamiento. Se puede **reproducir la construcción voraz** paso a paso: en cada paso se resaltan los dos nodos que se unen y se muestra el estado de la cola de prioridad. Al hacer clic en una hoja se marca su camino y su código. |
| **4 · Compresión** | Tamaño original y comprimido (bytes y KB/MB), ahorro, % de reducción, razón de compresión, símbolos, bits codificados, tiempos. Compara con un código de longitud fija. Guarda el `.hada`. |
| **5 · Inspector .hada** | Abre **solo** un `.hada`: nombre y extensión, versión, tamaños, ahorro, símbolos, estructura del archivo con offsets, tabla de frecuencias, códigos y árbol reconstruidos, volcado hexadecimal por secciones, primeros bits separados por código y bits de relleno. Después, **DESCOMPRIMIR**: verifica SHA-256 (y byte a byte si el original está cargado), muestra el texto y lo guarda como `.txt`. |
| **6 · Expansión mínima** | Grafo de ejemplo o aleatorio, editable como texto. Ejecuta Kruskal o Prim paso a paso (aristas aceptadas en verde y rechazadas en rojo) y compara el peso de ambos. |

## El algoritmo

1. **Frecuencias** (`huffman.calcular_frecuencias`): se recorre el texto una vez. **O(n)**.
2. **Árbol voraz** (`huffman.construir_arbol`): cada carácter es una hoja dentro de un
   *min-heap*. Mientras quede más de un nodo, se sacan los **dos de menor frecuencia**
   y se unen en un nodo cuya frecuencia es la suma. Con `k` símbolos se hacen `k − 1`
   uniones de costo O(log k): **O(k log k)**.
3. **Códigos** (`huffman.generar_codigos`): recorrido del árbol; izquierda = `0`, derecha = `1`.
   Ningún código es prefijo de otro porque los símbolos solo están en las hojas.
4. **Codificar** (`huffman.codificar`): se concatenan los códigos y se empaquetan de 8 en 8
   bits; el último byte se rellena con ceros. **O(n + B)**, con `B` = bits de salida.
5. **Archivo `.hada`** (`formato.empaquetar`): cabecera + tabla de frecuencias + datos. Ver
   [docs/FORMATO.md](docs/FORMATO.md).
6. **Descomprimir** (`formato.leer` + `formato.descomprimir`): se reconstruye el árbol con la
   tabla, se recorre bit por bit desde la raíz y, al llegar a una hoja, se emite el símbolo.
   Se ignoran los bits de relleno. **O(B)**.
7. **Verificar**: SHA-256 del resultado contra el guardado en la cabecera.

**¿Por qué funciona la elección voraz?** Los dos símbolos menos frecuentes pueden ser
hermanos en el nivel más profundo de algún árbol óptimo (intercambiarlos con otros nodos
no aumenta el costo). Al unirlos, el problema se reduce a uno con `k − 1` símbolos que
tiene la misma estructura (subestructura óptima). La prueba
`test_optimo_contra_fuerza_bruta` lo confirma comparando contra todas las longitudes de
código posibles en alfabetos pequeños.

**Árbol de expansión mínima** (`expansion_minima.py`):
- **Kruskal**: ordena las aristas por peso y acepta cada una si une dos componentes
  distintas (Union-Find con compresión de camino y unión por rango). **O(E log E)**.
- **Prim**: crece un solo árbol desde un nodo inicial tomando siempre la arista más barata
  que sale del árbol (*min-heap*). **O(E log V)**.

Ambos se apoyan en la propiedad del corte: la arista más ligera que cruza un corte
siempre pertenece a algún MST.

## Resultados

Salida de `evidencias/generar_evidencias.py` (tabla completa e integridad en
[evidencias/resultados.md](evidencias/resultados.md)):

| Caso | Original | `.hada` | Reducción | Razón | Símbolos | Bits/símbolo | Entropía | Íntegro |
|---|---:|---:|---:|---:|---:|---:|---:|:-:|
| Texto pequeño `abracadabra` | 11 B | 137 B | −1145 % | 0.08 | 5 | 2.091 | 2.040 | ✔ |
| Don Quijote (#2000, español) | 2.12 MB | 1.16 MB | **45.48 %** | 1.834 | 111 | 4.474 | 4.438 | ✔ |
| Frankenstein (#84, inglés) | 438.36 KB | 246.33 KB | **43.81 %** | 1.780 | 94 | 4.504 | 4.469 | ✔ |
| Los pazos de Ulloa (#18005, no usado en el desarrollo) | 522.63 KB | 292.50 KB | **44.03 %** | 1.787 | 105 | 4.571 | 4.537 | ✔ |

- En los libros, Huffman queda a menos de 0.04 bits/símbolo de la entropía (el mínimo teórico).
- Un código de longitud fija necesitaría 7 bits por carácter para 111 símbolos; Huffman usa 4.47.
- En textos muy cortos el archivo **crece**: la cabecera y la tabla (79 + n + 8k bytes)
  pesan más que lo que se ahorra.

## Pruebas

`tests/test_huffman.py` (32 pruebas, todas pasan):

| Prueba pedida | Dónde |
|---|---|
| 1. Texto pequeño comprobable a mano | `TextoPequeno`: frecuencias, las 4 uniones, códigos y los 23 bits exactos de `abracadabra`. |
| 2. Libro de Project Gutenberg | `LibroGutenberg.test_quijote` y `generar_evidencias.py` (#2000 y #84). |
| 3. Integridad | Todas las pruebas de ida y vuelta comparan SHA-256 y byte a byte; `FormatoHada` altera bits y la tabla para comprobar que se detecta. |
| 4. Archivo no usado durante el desarrollo | `generar_evidencias.py --nuevo 18005`; acepta cualquier ID o `.txt`. |

También hay casos límite (archivo vacío, un solo símbolo, emojis y CJK, `\r\n`, BOM,
Latin-1, bytes aleatorios), la propiedad de prefijo, el determinismo del árbol y, para el
MST, el grafo clásico de Cormen (peso 37), Kruskal = Prim en 100 grafos aleatorios y una
comparación contra fuerza bruta.

Las capturas del funcionamiento están en [evidencias/capturas/](evidencias/capturas/).

## Estructura

```
act5_huffman/
├── main.py                 punto de entrada
├── interfaz.py             GUI (Tkinter + matplotlib)
├── huffman.py              frecuencias, árbol voraz, códigos, codificar/decodificar
├── formato.py              formato .hada: empaquetar, leer, descomprimir, verificar
├── gutenberg.py            búsqueda (OPDS de gutenberg.org, Gutendex de respaldo) y descarga
├── expansion_minima.py     Kruskal, Prim, Union-Find, generador de grafos
├── docs/FORMATO.md         especificación del formato .hada
├── docs/reporte_actividad5.pdf  reporte técnico
├── tests/test_huffman.py   pruebas unitarias
├── evidencias/             resultados.md, abracadabra.hada, capturas/ y el script que los genera
└── libros/                 copias de los libros descargados (ignorada por git)
```

## Tecnologías

- Python 3.14 (compatible con 3.10 o superior): `heapq`, `collections.Counter`, `struct`, `hashlib`, `urllib`, `xml.etree`.
- Tkinter / ttk para la interfaz, matplotlib para las gráficas.
- Project Gutenberg: catálogo OPDS (`gutenberg.org/ebooks/search.opds`) y Gutendex como respaldo.
- No se usa ninguna biblioteca de compresión (zip, gzip, zlib, etc.).

## Uso de IA

| Herramienta | Para qué | Cómo se validó |
|---|---|---|
| Claude Code (Claude Opus 5.5) | Apoyo para escribir el código, las pruebas, la documentación del formato y el README a partir de los requerimientos. | Pruebas unitarias (incluye comparación contra fuerza bruta para Huffman y MST), ida y vuelta con SHA-256 en tres libros, revisión manual de `abracadabra` bit por bit y revisión de las capturas de la interfaz. |

Revisé cada módulo y puedo explicar su funcionamiento.

## Limitaciones conocidas

- Es una aplicación de escritorio: no tiene URL pública (se eligió GUI en Python según las instrucciones de la actividad).
- Todo el archivo se procesa en memoria; está pensado para libros (unos pocos MB), no para archivos de cientos de MB.
- La decodificación recorre el árbol bit por bit en Python puro (≈0.7 s para el Quijote).
- La tabla usa 4 bytes por frecuencia: un símbolo no puede repetirse más de 4,294,967,295 veces.
- Huffman estático, de un solo pase por símbolo: no aprovecha repeticiones de palabras como LZ77; por eso la reducción ronda el 44–45 % y no más.
- La búsqueda en Gutenberg necesita internet. Los libros descargados quedan en `libros/` y se reutilizan.
- Con alfabetos enormes (por ejemplo, miles de ideogramas) el árbol se vuelve muy ancho para dibujarlo cómodamente.
