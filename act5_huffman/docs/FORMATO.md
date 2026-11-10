# Formato `.hada` (versión 1)

**HADA** = *Huffman · Análisis De Algoritmos*. Es un archivo binario con todo lo
necesario para reconstruir el `.txt` original **sin tenerlo a la mano**: la tabla
de frecuencias (de la que sale otra vez el mismo árbol), los bits comprimidos,
cuántos de esos bits son válidos y un hash para comprobar la integridad.

El texto original **no** se guarda: solo se guardan los bits de Huffman.

## Estructura

Todos los enteros van en **big-endian** (el byte más significativo primero).

| Offset | Tamaño | Campo | Descripción |
|---:|---:|---|---|
| 0 | 4 | `MAGIC` | Firma ASCII `HADA` (`48 41 44 41`). Si no está, el archivo se rechaza. |
| 4 | 1 | `VERSION` | Versión del formato. Hoy es `1`. |
| 5 | 1 | `CODIF` | Cómo se interpretan los bytes del `.txt`: `0` = UTF-8, `1` = Latin-1. |
| 6 | 2 | `RESERVADO` | `0`. Espacio para banderas de versiones futuras. |
| 8 | 8 | `TAM_ORIG` | Tamaño del `.txt` original en bytes. |
| 16 | 8 | `CARACTERES` | Número de caracteres del texto (= suma de la tabla de frecuencias). |
| 24 | 8 | `BITS` | **Bits válidos** de los datos comprimidos. |
| 32 | 1 | `RELLENO` | Bits de relleno del último byte (0 a 7). Siempre `8·len(DATOS) − BITS`. |
| 33 | 32 | `SHA256` | SHA-256 del `.txt` original, para verificar la descompresión. |
| 65 | 8 | `FECHA` | Momento de la compresión (segundos Unix). |
| 73 | 2 | `LEN_NOMBRE` | Longitud en bytes del nombre original. |
| 75 | n | `NOMBRE` | Nombre del `.txt` original en UTF-8. |
| 75+n | 4 | `SIMBOLOS` | `k` = número de símbolos distintos. |
| 79+n | 8·k | `TABLA` | `k` entradas de 8 bytes: punto de código Unicode (4 B) y frecuencia (4 B). |
| 79+n+8k | resto | `DATOS` | Códigos de Huffman concatenados y empaquetados de 8 en 8 bits. |

Tamaño de la cabecera: `79 + n + 8k` bytes. Para el Quijote (`n = 10`, `k = 111`)
son 977 bytes, contra 1,212,541 bytes de datos.

## Decisiones

**¿Por qué se guardan frecuencias y no el árbol ni los códigos?**
Con la tabla de frecuencias el descompresor ejecuta *el mismo algoritmo voraz* y
obtiene el mismo árbol. Para que el árbol sea idéntico, compresor y descompresor
usan un orden canónico: las hojas entran a la cola de prioridad ordenadas por
`(frecuencia, código Unicode)`, y los empates en el *heap* se resuelven por orden
de llegada. Además, así el inspector puede mostrar la tabla de frecuencias real
del texto, no solo los códigos.

**¿Símbolos = bytes o caracteres?**
Caracteres. El `.txt` se decodifica como UTF-8 estricto; si no es UTF-8 válido se
usa Latin-1, que acepta cualquier byte. En los dos casos, volver a codificar el
texto produce exactamente los mismos bytes, así que la integridad se conserva
(incluyendo BOM y saltos de línea `\r\n`). Por eso letras como `ñ` o `á`
cuentan como un solo símbolo y no como dos bytes.

**¿Por qué `BITS` y también `RELLENO`?**
El último byte casi nunca se llena; el descompresor necesita saber dónde parar
para no traducir los ceros de relleno como símbolos. `BITS` basta para eso;
`RELLENO` es redundante a propósito: `leer()` comprueba que
`8·len(DATOS) − BITS == RELLENO` para detectar archivos truncados.

**Integridad.** Tras descomprimir se calcula el SHA-256 del resultado y se compara
con `SHA256`. Si además el `.txt` original está cargado en la aplicación, se hace
una comparación byte a byte e indica el primer byte distinto, si lo hay.

**Validaciones al leer:** firma, versión, codificación conocida, tabla completa,
que la tabla sume `CARACTERES`, y la relación entre `BITS`, `RELLENO` y el tamaño
de `DATOS`. Si los datos se dañan, el decodificador termina a la mitad de un
código (error) o el hash no coincide.

## Ejemplo completo: `abracadabra`

Frecuencias `a:5 b:2 r:2 c:1 d:1` → códigos `a=0 c=100 d=101 b=110 r=111`.

```
00000000: 4841 4441 0100 0000 0000 0000 0000 000b  HADA............
00000010: 0000 0000 0000 000b 0000 0000 0000 0017  ................
00000020: 0104 5bab dcd2 1189 60e8 c8b8 e0ec f65b  ..[.....`......[
00000030: 7346 86e1 b18f 5871 0c96 4677 9f49 e942  sF....Xq..Fw.I.B
00000040: ae00 0000 006a f2a0 7300 0f61 6272 6163  .....j..s..abrac
00000050: 6164 6162 7261 2e74 7874 0000 0005 0000  adabra.txt......
00000060: 0063 0000 0001 0000 0064 0000 0001 0000  .c.......d......
00000070: 0062 0000 0002 0000 0072 0000 0002 0000  .b.......r......
00000080: 0061 0000 0005 6e8a dc                   .a....n..
```

| Offset | Bytes | Campo | Valor |
|---:|---|---|---|
| 0 | `48 41 44 41` | MAGIC | `HADA` |
| 4 | `01` | VERSION | 1 |
| 5 | `00` | CODIF | UTF-8 |
| 6 | `00 00` | RESERVADO | 0 |
| 8 | `00…0b` | TAM_ORIG | 11 bytes |
| 16 | `00…0b` | CARACTERES | 11 |
| 24 | `00…17` | BITS | 23 |
| 32 | `01` | RELLENO | 1 |
| 33 | `5b ab … ae` | SHA256 | `045babdc…49e942ae` |
| 65 | `00…6a f2 a0 73` | FECHA | 2026-11-09 22:41:23 |
| 73 | `00 0f` | LEN_NOMBRE | 15 |
| 75 | `61 62 … 74` | NOMBRE | `abracadabra.txt` |
| 90 | `00 00 00 05` | SIMBOLOS | 5 |
| 94 | `00000063 00000001` … | TABLA | c:1, d:1, b:2, r:2, a:5 |
| 134 | `6e 8a dc` | DATOS | `01101110 10001010 1101110`**`0`** |

Los 23 bits válidos se leen `0 110 111 0 100 0 101 0 110 111 0` =
`a b r a c a d a b r a`. El último `0` (en negritas) es relleno.

En un texto tan corto el `.hada` (137 B) es más grande que el original (11 B):
la cabecera y la tabla cuestan más de lo que se ahorra. En un libro, la cabecera es
menos del 0.1 % del archivo.

## Lectura en código

`formato.leer(bytes)` devuelve un `ArchivoHada` con todos los campos, la lista de
secciones con su offset y tamaño (la que muestra el inspector), el árbol
reconstruido y los códigos. `formato.descomprimir(hada)` recorre el árbol bit
por bit y devuelve el contenido, su SHA-256 y si coincide con la cabecera.
