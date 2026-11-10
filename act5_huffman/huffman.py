"""Algoritmo de Huffman con la técnica voraz.

Flujo: texto -> frecuencias -> árbol -> códigos -> bits -> bytes empaquetados,
y de regreso: bytes + árbol -> texto.
"""

import heapq
import math
from collections import Counter
from dataclasses import dataclass


@dataclass(eq=False)
class Nodo:
    frecuencia: int
    simbolo: str | None = None   # solo las hojas tienen símbolo
    izquierdo: "Nodo | None" = None
    derecho: "Nodo | None" = None
    paso: int = 0                # paso voraz en que se creó (0 = hoja inicial)

    @property
    def es_hoja(self):
        return self.simbolo is not None


@dataclass
class Paso:
    """Una decisión voraz: se unen los dos nodos de menor frecuencia."""
    numero: int
    izquierdo: Nodo
    derecho: Nodo
    nuevo: Nodo
    restantes: int  # nodos que quedan en la cola después de unir


def calcular_frecuencias(texto):
    """Cuenta cuántas veces aparece cada carácter. O(n)."""
    return dict(Counter(texto))


def ordenar_frecuencias(frecuencias):
    """Orden canónico: frecuencia ascendente y, en empate, por código Unicode.

    El compresor y el descompresor usan este mismo orden, así que los dos
    construyen exactamente el mismo árbol a partir de la tabla guardada.
    """
    return sorted(frecuencias.items(), key=lambda par: (par[1], ord(par[0])))


def construir_arbol(frecuencias):
    """Construye el árbol de Huffman con una cola de prioridad (min-heap).

    En cada paso se toma la decisión voraz: sacar los dos nodos de menor
    frecuencia y unirlos en uno nuevo cuya frecuencia es la suma.
    Con k símbolos hay k - 1 uniones, cada una O(log k): O(k log k).

    Devuelve (raiz, pasos). Si no hay símbolos, la raíz es None.
    """
    if not frecuencias:
        return None, []

    # El contador "orden" desempata nodos con igual frecuencia (FIFO), así el
    # heap nunca compara objetos Nodo y el resultado es determinista.
    cola = []
    orden = 0
    for simbolo, frecuencia in ordenar_frecuencias(frecuencias):
        heapq.heappush(cola, (frecuencia, orden, Nodo(frecuencia, simbolo)))
        orden += 1

    if len(cola) == 1:
        # Un solo símbolo distinto: se le asigna el código "0".
        hoja = cola[0][2]
        return Nodo(hoja.frecuencia, izquierdo=hoja, paso=1), []

    pasos = []
    while len(cola) > 1:
        f1, _, menor = heapq.heappop(cola)
        f2, _, segundo = heapq.heappop(cola)
        nuevo = Nodo(f1 + f2, izquierdo=menor, derecho=segundo, paso=len(pasos) + 1)
        heapq.heappush(cola, (nuevo.frecuencia, orden, nuevo))
        orden += 1
        pasos.append(Paso(len(pasos) + 1, menor, segundo, nuevo, len(cola)))

    return cola[0][2], pasos


def generar_codigos(raiz):
    """Recorre el árbol: izquierda agrega '0' y derecha agrega '1'."""
    codigos = {}
    if raiz is None:
        return codigos
    pila = [(raiz, "")]
    while pila:
        nodo, prefijo = pila.pop()
        if nodo.es_hoja:
            codigos[nodo.simbolo] = prefijo or "0"
            continue
        if nodo.derecho:
            pila.append((nodo.derecho, prefijo + "1"))
        if nodo.izquierdo:
            pila.append((nodo.izquierdo, prefijo + "0"))
    return codigos


def codificar(texto, codigos):
    """Sustituye cada carácter por su código y empaqueta los bits en bytes.

    Devuelve (datos, bits_validos). El último byte se rellena con ceros; los
    bits de relleno son 8 * len(datos) - bits_validos.
    """
    bits = "".join(map(codigos.__getitem__, texto))
    bits_validos = len(bits)
    if bits_validos == 0:
        return b"", 0
    relleno = -bits_validos % 8
    numero = int(bits, 2) << relleno
    return numero.to_bytes((bits_validos + relleno) // 8, "big"), bits_validos


def bytes_a_bits(datos, bits_validos=None):
    """Convierte bytes a una cadena de '0' y '1' (sin los bits de relleno)."""
    if not datos:
        return ""
    bits = bin(int.from_bytes(datos, "big"))[2:].zfill(len(datos) * 8)
    return bits if bits_validos is None else bits[:bits_validos]


def decodificar(datos, bits_validos, raiz):
    """Recorre el árbol bit por bit; al llegar a una hoja emite su símbolo."""
    if raiz is None or bits_validos == 0:
        return ""
    salida = []
    nodo = raiz
    for bit in bytes_a_bits(datos, bits_validos):
        nodo = nodo.derecho if bit == "1" else nodo.izquierdo
        if nodo is None:
            raise ValueError("Secuencia de bits inválida para este árbol")
        if nodo.simbolo is not None:
            salida.append(nodo.simbolo)
            nodo = raiz
    if nodo is not raiz:
        raise ValueError("Los datos terminan a la mitad de un código")
    return "".join(salida)


def longitud_media(frecuencias, codigos):
    """Bits promedio por símbolo: sum(f * len(código)) / total."""
    total = sum(frecuencias.values())
    if total == 0:
        return 0.0
    return sum(f * len(codigos[s]) for s, f in frecuencias.items()) / total


def entropia(frecuencias):
    """Entropía de Shannon en bits/símbolo: el límite inferior teórico."""
    total = sum(frecuencias.values())
    if total == 0:
        return 0.0
    return -sum(f / total * math.log2(f / total) for f in frecuencias.values())


def recorrer(raiz):
    """Todos los nodos del árbol en preorden."""
    if raiz is None:
        return []
    nodos, pila = [], [raiz]
    while pila:
        nodo = pila.pop()
        nodos.append(nodo)
        for hijo in (nodo.derecho, nodo.izquierdo):
            if hijo:
                pila.append(hijo)
    return nodos


def mostrar_simbolo(simbolo):
    """Versión legible de un carácter para tablas y para el árbol."""
    especiales = {"\n": "\\n", "\r": "\\r", "\t": "\\t", " ": "␣"}
    if simbolo in especiales:
        return especiales[simbolo]
    punto = ord(simbolo)
    if punto < 32 or punto == 127 or 0x80 <= punto < 0xA0 or punto > 0xFFFF or not simbolo.isprintable():
        return f"U+{punto:04X}"
    return simbolo
