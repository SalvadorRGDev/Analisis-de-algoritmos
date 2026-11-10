"""Formato propio .hada (Huffman · Análisis De Algoritmos).

Todos los enteros van en big-endian. La estructura completa está documentada
en docs/FORMATO.md.

    MAGIC       4 B   b"HADA"
    VERSION     1 B   1
    CODIF       1 B   0 = UTF-8, 1 = Latin-1
    RESERVADO   2 B   0
    TAM_ORIG    8 B   tamaño del .txt original en bytes
    CARACTERES  8 B   número de caracteres del texto
    BITS        8 B   bits válidos de los datos comprimidos
    RELLENO     1 B   bits de relleno en el último byte (0-7)
    SHA256     32 B   hash del archivo original (integridad)
    FECHA       8 B   segundos Unix en que se comprimió
    LEN_NOMBRE  2 B   longitud del nombre original en bytes
    NOMBRE      n B   nombre original en UTF-8
    SIMBOLOS    4 B   k = número de símbolos distintos
    TABLA    8k B     k pares (código Unicode 4 B, frecuencia 4 B)
    DATOS       resto bits de Huffman empaquetados
"""

import hashlib
import struct
import time
from dataclasses import dataclass, field

import huffman

EXTENSION = ".hada"
MAGIC = b"HADA"
VERSION = 1
CODIFICACIONES = {0: "utf-8", 1: "latin-1"}

_CABECERA_FIJA = struct.Struct(">4sBBHQQQB32sQH")  # hasta LEN_NOMBRE
_ENTRADA = struct.Struct(">II")


@dataclass
class Seccion:
    nombre: str
    inicio: int
    tamano: int
    valor: str


@dataclass
class ArchivoHada:
    """Todo lo que se puede saber de un .hada sin tener el .txt original."""
    version: int
    codificacion: str
    tamano_original: int
    caracteres: int
    bits_validos: int
    relleno: int
    sha256: bytes
    fecha: int
    nombre_original: str
    frecuencias: dict
    datos: bytes
    tamano_archivo: int
    secciones: list = field(default_factory=list)
    raiz: huffman.Nodo | None = None
    pasos: list = field(default_factory=list)
    codigos: dict = field(default_factory=dict)

    @property
    def tamano_cabecera(self):
        return self.tamano_archivo - len(self.datos)


@dataclass
class Analisis:
    """Pasos 1 a 3: frecuencias, árbol voraz y códigos."""
    texto: str
    codificacion: int
    frecuencias: dict
    raiz: huffman.Nodo | None
    pasos: list
    codigos: dict
    tiempos: dict


@dataclass
class Resultado:
    """Pasos 4 y 5: el texto codificado y el archivo .hada generado."""
    analisis: Analisis
    original: bytes
    archivo: bytes
    hada: ArchivoHada
    tiempos: dict


def decodificar_texto(contenido):
    """Bytes del .txt -> (texto, id de codificación).

    Se intenta UTF-8 estricto; si falla se usa Latin-1, que acepta cualquier
    byte. En ambos casos volver a codificar da exactamente los mismos bytes.
    """
    try:
        return contenido.decode("utf-8"), 0
    except UnicodeDecodeError:
        return contenido.decode("latin-1"), 1


def empaquetar(frecuencias, datos, bits_validos, original, codificacion, nombre, caracteres, fecha=None):
    nombre_bytes = nombre.encode("utf-8")[:65535]
    relleno = len(datos) * 8 - bits_validos
    partes = [
        _CABECERA_FIJA.pack(
            MAGIC, VERSION, codificacion, 0, len(original), caracteres,
            bits_validos, relleno, hashlib.sha256(original).digest(),
            int(time.time()) if fecha is None else fecha, len(nombre_bytes),
        ),
        nombre_bytes,
        struct.pack(">I", len(frecuencias)),
    ]
    for simbolo, frecuencia in huffman.ordenar_frecuencias(frecuencias):
        partes.append(_ENTRADA.pack(ord(simbolo), frecuencia))
    partes.append(datos)
    return b"".join(partes)


def analizar(original):
    """original.txt (bytes) -> frecuencias, árbol y códigos."""
    tiempos = {}
    inicio = time.perf_counter()
    texto, codificacion = decodificar_texto(original)
    frecuencias = huffman.calcular_frecuencias(texto)
    tiempos["frecuencias"] = time.perf_counter() - inicio

    inicio = time.perf_counter()
    raiz, pasos = huffman.construir_arbol(frecuencias)
    codigos = huffman.generar_codigos(raiz)
    tiempos["arbol"] = time.perf_counter() - inicio
    return Analisis(texto, codificacion, frecuencias, raiz, pasos, codigos, tiempos)


def comprimir(original, nombre="texto.txt", analisis=None, fecha=None):
    """original.txt (bytes) -> Resultado con el archivo .hada listo para guardar."""
    analisis = analisis or analizar(original)
    tiempos = dict(analisis.tiempos)
    inicio = time.perf_counter()
    datos, bits_validos = huffman.codificar(analisis.texto, analisis.codigos)
    archivo = empaquetar(analisis.frecuencias, datos, bits_validos, original,
                         analisis.codificacion, nombre, len(analisis.texto), fecha)
    tiempos["codificar"] = time.perf_counter() - inicio

    return Resultado(analisis, original, archivo, leer(archivo), tiempos)


def leer(archivo):
    """Lee e interpreta un .hada y reconstruye el árbol a partir de la tabla."""
    if len(archivo) < _CABECERA_FIJA.size or archivo[:4] != MAGIC:
        raise ValueError("No es un archivo .hada (firma 'HADA' no encontrada)")
    (magic, version, codificacion, _reservado, tamano_original, caracteres,
     bits_validos, relleno, sha256, fecha, len_nombre) = _CABECERA_FIJA.unpack_from(archivo)
    if version != VERSION:
        raise ValueError(f"Versión {version} no soportada (se esperaba {VERSION})")
    if codificacion not in CODIFICACIONES:
        raise ValueError(f"Codificación desconocida: {codificacion}")

    secciones = []

    def seccion(nombre, inicio, tamano, valor):
        secciones.append(Seccion(nombre, inicio, tamano, str(valor)))

    seccion("Firma (magic)", 0, 4, magic.decode("ascii"))
    seccion("Versión", 4, 1, version)
    seccion("Codificación", 5, 1, f"{codificacion} = {CODIFICACIONES[codificacion]}")
    seccion("Reservado", 6, 2, 0)
    seccion("Tamaño original", 8, 8, f"{tamano_original:,} bytes")
    seccion("Caracteres", 16, 8, f"{caracteres:,}")
    seccion("Bits válidos", 24, 8, f"{bits_validos:,}")
    seccion("Bits de relleno", 32, 1, relleno)
    seccion("SHA-256 original", 33, 32, sha256.hex())
    seccion("Fecha", 65, 8, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fecha)))
    seccion("Longitud del nombre", 73, 2, len_nombre)

    pos = _CABECERA_FIJA.size
    nombre = archivo[pos:pos + len_nombre].decode("utf-8", errors="replace")
    seccion("Nombre original", pos, len_nombre, nombre)
    pos += len_nombre

    if pos + 4 > len(archivo):
        raise ValueError("Archivo truncado: falta la tabla de símbolos")
    (k,) = struct.unpack_from(">I", archivo, pos)
    seccion("Número de símbolos", pos, 4, k)
    pos += 4

    if pos + k * _ENTRADA.size > len(archivo):
        raise ValueError("Archivo truncado: la tabla de símbolos está incompleta")
    frecuencias = {}
    for i in range(k):
        punto, frecuencia = _ENTRADA.unpack_from(archivo, pos + i * _ENTRADA.size)
        frecuencias[chr(punto)] = frecuencia
    seccion("Tabla de frecuencias", pos, k * _ENTRADA.size, f"{k} × (Unicode 4 B + frecuencia 4 B)")
    pos += k * _ENTRADA.size

    datos = archivo[pos:]
    seccion("Datos comprimidos", pos, len(datos), f"{bits_validos:,} bits + {relleno} de relleno")

    if not 0 <= relleno < 8 or len(datos) * 8 - bits_validos != relleno:
        raise ValueError("Los bits válidos no coinciden con el tamaño de los datos")
    if sum(frecuencias.values()) != caracteres:
        raise ValueError("La tabla de frecuencias no suma el número de caracteres")

    raiz, pasos = huffman.construir_arbol(frecuencias)
    return ArchivoHada(
        version=version,
        codificacion=CODIFICACIONES[codificacion],
        tamano_original=tamano_original,
        caracteres=caracteres,
        bits_validos=bits_validos,
        relleno=relleno,
        sha256=sha256,
        fecha=fecha,
        nombre_original=nombre,
        frecuencias=frecuencias,
        datos=datos,
        tamano_archivo=len(archivo),
        secciones=secciones,
        raiz=raiz,
        pasos=pasos,
        codigos=huffman.generar_codigos(raiz),
    )


@dataclass
class Descompresion:
    contenido: bytes
    texto: str
    sha256: str
    integro: bool
    segundos: float


def descomprimir(hada):
    """Reconstruye el .txt original solo con la información del .hada."""
    inicio = time.perf_counter()
    texto = huffman.decodificar(hada.datos, hada.bits_validos, hada.raiz)
    contenido = texto.encode(hada.codificacion)
    segundos = time.perf_counter() - inicio
    digest = hashlib.sha256(contenido).digest()
    integro = digest == hada.sha256 and len(contenido) == hada.tamano_original
    return Descompresion(contenido, texto, digest.hex(), integro, segundos)


def comparar_bytes(a, b):
    """Comparación byte a byte. Devuelve None si son idénticos o la posición
    del primer byte distinto."""
    if a == b:
        return None
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def formato_tamano(n):
    """1234567 -> '1,234,567 B (1.18 MB)'."""
    if n >= 1024 * 1024:
        return f"{n:,} B ({n / 1024 / 1024:.2f} MB)"
    if n >= 1024:
        return f"{n:,} B ({n / 1024:.2f} KB)"
    return f"{n:,} B"
