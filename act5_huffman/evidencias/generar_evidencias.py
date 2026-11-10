"""Corre el flujo completo original.txt -> .hada -> recuperado.txt sobre varios
textos y escribe evidencias/resultados.md.

Uso:
    python3 evidencias/generar_evidencias.py                  # casos por defecto
    python3 evidencias/generar_evidencias.py --nuevo 1234      # agrega el libro #1234
    python3 evidencias/generar_evidencias.py --nuevo otro.txt  # agrega un .txt local
"""

import argparse
import hashlib
import platform
import sys
import time
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parent))

import formato  # noqa: E402
import gutenberg  # noqa: E402
import huffman  # noqa: E402

LIBROS_BASE = [(2000, "Don Quijote (español)"), (84, "Frankenstein (inglés)")]


def libro(id_libro, titulo):
    contenido, ruta = gutenberg.descargar(gutenberg.Libro(id_libro, titulo, ""))
    return contenido, ruta.name


def medir(etiqueta, tipo, contenido, nombre):
    inicio = time.perf_counter()
    resultado = formato.comprimir(contenido, nombre)
    t_comprimir = time.perf_counter() - inicio
    leido = formato.leer(resultado.archivo)       # solo el .hada, sin el .txt
    recuperado = formato.descomprimir(leido)
    diferencia = formato.comparar_bytes(contenido, recuperado.contenido)
    a = resultado.analisis
    return {
        "etiqueta": etiqueta, "tipo": tipo, "nombre": nombre,
        "original": len(contenido), "comprimido": len(resultado.archivo),
        "simbolos": len(a.frecuencias), "caracteres": len(a.texto),
        "bits": leido.bits_validos, "media": huffman.longitud_media(a.frecuencias, a.codigos),
        "entropia": huffman.entropia(a.frecuencias),
        "t_comprimir": t_comprimir, "t_descomprimir": recuperado.segundos,
        "sha_original": hashlib.sha256(contenido).hexdigest(), "sha_recuperado": recuperado.sha256,
        "integro": recuperado.integro, "identico": diferencia is None,
        "archivo": resultado.archivo, "analisis": a,
    }


def kb(n):
    return f"{n / 1024 / 1024:.2f} MB" if n >= 1024 * 1024 else f"{n / 1024:.2f} KB" if n >= 1024 else f"{n} B"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nuevo", action="append", default=[],
                        help="ID de Gutenberg o ruta a un .txt no usado durante el desarrollo")
    args = parser.parse_args()

    casos = [medir("1 · Texto pequeño", "comprobación manual", b"abracadabra", "abracadabra.txt")]
    for id_libro, titulo in LIBROS_BASE:
        casos.append(medir(f"2 · Gutenberg #{id_libro}", titulo, *libro(id_libro, titulo)))
    for nuevo in args.nuevo:
        if nuevo.isdigit():
            contenido, nombre = libro(int(nuevo), "")
        else:
            contenido, nombre = Path(nuevo).read_bytes(), Path(nuevo).name
        casos.append(medir("4 · Archivo nuevo", "no usado durante el desarrollo", contenido, nombre))

    pequeno = casos[0]
    (CARPETA / "abracadabra.hada").write_bytes(pequeno["archivo"])

    lineas = [
        "# Resultados de compresión e integridad",
        "",
        f"Generado con `evidencias/generar_evidencias.py` el {time.strftime('%Y-%m-%d %H:%M')} "
        f"(Python {platform.python_version()}, {platform.system()}).",
        "",
        "Cada caso sigue el flujo `original.txt → .hada → recuperado.txt`. El `.hada` se vuelve a leer "
        "desde sus bytes, sin el `.txt`, antes de descomprimir.",
        "",
        "| Caso | Archivo | Original | .hada | Ahorro | Reducción | Razón | Símbolos | Bits/símbolo | Entropía | Comprimir | Descomprimir |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in casos:
        ahorro = c["original"] - c["comprimido"]
        lineas.append(
            f"| {c['etiqueta']} ({c['tipo']}) | `{c['nombre']}` | {c['original']:,} B ({kb(c['original'])}) | "
            f"{c['comprimido']:,} B ({kb(c['comprimido'])}) | {ahorro:,} B | {ahorro / c['original'] * 100:.2f} % | "
            f"{c['original'] / c['comprimido']:.3f} | {c['simbolos']} | {c['media']:.3f} | {c['entropia']:.3f} | "
            f"{c['t_comprimir'] * 1000:.0f} ms | {c['t_descomprimir'] * 1000:.0f} ms |"
        )
    lineas += ["", "## 3 · Integridad", "",
               "| Archivo | SHA-256 original | SHA-256 recuperado | Hash | Byte a byte |", "|---|---|---|:-:|:-:|"]
    for c in casos:
        lineas.append(f"| `{c['nombre']}` | `{c['sha_original'][:16]}…` | `{c['sha_recuperado'][:16]}…` | "
                      f"{'✔' if c['integro'] else '✘'} | {'✔ idénticos' if c['identico'] else '✘ distintos'} |")

    a = pequeno["analisis"]
    lineas += [
        "", "## 1 · Texto pequeño a mano: `abracadabra`", "",
        "| Símbolo | Frecuencia | Código | Bits |", "|:-:|--:|:-:|--:|",
    ]
    for s in sorted(a.frecuencias, key=lambda s: (-a.frecuencias[s], s)):
        lineas.append(f"| `{s}` | {a.frecuencias[s]} | `{a.codigos[s]}` | {a.frecuencias[s] * len(a.codigos[s])} |")
    lineas += ["", "Uniones voraces (siempre los dos nodos de menor frecuencia):", ""]
    for p in a.pasos:
        lineas.append(f"{p.numero}. {p.izquierdo.frecuencia} + {p.derecho.frecuencia} = {p.nuevo.frecuencia}")
    bits = huffman.bytes_a_bits(formato.leer(pequeno["archivo"]).datos, pequeno["bits"])
    lineas += [
        "", f"Bits: `{' '.join(a.codigos[c] for c in a.texto)}` = {pequeno['bits']} bits "
        f"→ `{bits}` + 1 bit de relleno = 3 bytes de datos.",
        f"El `.hada` completo mide {pequeno['comprimido']} bytes porque la cabecera y la tabla pesan más que el "
        "texto: en textos muy cortos el archivo crece. Ver `abracadabra.hada`.",
    ]
    (CARPETA / "resultados.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    if not all(c["integro"] and c["identico"] for c in casos):
        sys.exit("¡Falló la integridad en algún caso!")


if __name__ == "__main__":
    main()
