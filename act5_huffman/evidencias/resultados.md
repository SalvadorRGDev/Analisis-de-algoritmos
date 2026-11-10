# Resultados de compresión e integridad

Generado con `evidencias/generar_evidencias.py` el 2026-11-09 23:05 (Python 3.14.7, Linux).

Cada caso sigue el flujo `original.txt → .sypher → recuperado.txt`. El `.sypher` se vuelve a leer desde sus bytes, sin el `.txt`, antes de descomprimir.

| Caso | Archivo | Original | .sypher | Ahorro | Reducción | Razón | Símbolos | Bits/símbolo | Entropía | Comprimir | Descomprimir |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 · Texto pequeño (comprobación manual) | `abracadabra.txt` | 11 B (11 B) | 137 B (137 B) | -126 B | -1145.45 % | 0.080 | 5 | 2.091 | 2.040 | 0 ms | 0 ms |
| 2 · Gutenberg #2000 (Don Quijote (español)) | `pg2000.txt` | 2,225,777 B (2.12 MB) | 1,213,518 B (1.16 MB) | 1,012,259 B | 45.48 % | 1.834 | 111 | 4.474 | 4.438 | 214 ms | 747 ms |
| 2 · Gutenberg #84 (Frankenstein (inglés)) | `pg84.txt` | 448,885 B (438.36 KB) | 252,247 B (246.33 KB) | 196,638 B | 43.81 % | 1.780 | 94 | 4.504 | 4.469 | 40 ms | 151 ms |
| 4 · Archivo nuevo (no usado durante el desarrollo) | `pg18005.txt` | 535,176 B (522.63 KB) | 299,519 B (292.50 KB) | 235,657 B | 44.03 % | 1.787 | 105 | 4.571 | 4.537 | 57 ms | 228 ms |

## 3 · Integridad

| Archivo | SHA-256 original | SHA-256 recuperado | Hash | Byte a byte |
|---|---|---|:-:|:-:|
| `abracadabra.txt` | `045babdcd2118960…` | `045babdcd2118960…` | ✔ | ✔ idénticos |
| `pg2000.txt` | `8a3738c61aa507f2…` | `8a3738c61aa507f2…` | ✔ | ✔ idénticos |
| `pg84.txt` | `2b97b7f8aad50864…` | `2b97b7f8aad50864…` | ✔ | ✔ idénticos |
| `pg18005.txt` | `c42f30054c6389bc…` | `c42f30054c6389bc…` | ✔ | ✔ idénticos |

## 1 · Texto pequeño a mano: `abracadabra`

| Símbolo | Frecuencia | Código | Bits |
|:-:|--:|:-:|--:|
| `a` | 5 | `0` | 5 |
| `b` | 2 | `110` | 6 |
| `r` | 2 | `111` | 6 |
| `c` | 1 | `100` | 3 |
| `d` | 1 | `101` | 3 |

Uniones voraces (siempre los dos nodos de menor frecuencia):

1. 1 + 1 = 2
2. 2 + 2 = 4
3. 2 + 4 = 6
4. 5 + 6 = 11

Bits: `0 110 111 0 100 0 101 0 110 111 0` = 23 bits → `01101110100010101101110` + 1 bit de relleno = 3 bytes de datos.
El `.sypher` completo mide 137 bytes porque la cabecera y la tabla pesan más que el texto: en textos muy cortos el archivo crece. Ver `abracadabra.sypher`.
