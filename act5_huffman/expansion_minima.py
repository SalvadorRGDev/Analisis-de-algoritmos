"""Árbol de expansión mínima (MST) con dos algoritmos voraces: Kruskal y Prim.

Igual que Huffman, ambos toman en cada paso la mejor opción local (la arista
más barata permitida) y esa elección lleva al óptimo global.
"""

import heapq
import itertools
import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Arista:
    u: str
    v: str
    peso: float

    def __str__(self):
        return f"{self.u}–{self.v} ({self.peso:g})"


@dataclass
class PasoMST:
    numero: int
    arista: Arista
    aceptada: bool
    motivo: str


class UnionFind:
    """Conjuntos disjuntos con compresión de camino y unión por rango."""

    def __init__(self, elementos):
        self.padre = {e: e for e in elementos}
        self.rango = {e: 0 for e in elementos}

    def buscar(self, x):
        while self.padre[x] != x:
            self.padre[x] = self.padre[self.padre[x]]
            x = self.padre[x]
        return x

    def unir(self, a, b):
        ra, rb = self.buscar(a), self.buscar(b)
        if ra == rb:
            return False
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        return True


def kruskal(nodos, aristas):
    """Ordena las aristas por peso y acepta cada una si no forma ciclo.

    O(E log E) por el ordenamiento; Union-Find detecta ciclos en casi O(1).
    Si el grafo no es conexo devuelve un bosque de expansión mínima.
    """
    conjuntos = UnionFind(nodos)
    arbol, pasos = [], []
    for arista in sorted(aristas, key=lambda a: (a.peso, a.u, a.v)):
        if conjuntos.unir(arista.u, arista.v):
            arbol.append(arista)
            pasos.append(PasoMST(len(pasos) + 1, arista, True, "une dos componentes"))
        else:
            pasos.append(PasoMST(len(pasos) + 1, arista, False, "formaría un ciclo"))
        if len(arbol) == len(nodos) - 1:
            break
    return arbol, pasos


def prim(nodos, aristas, inicio=None):
    """Crece un solo árbol desde `inicio` tomando siempre la arista más barata
    que sale del árbol. O(E log V) con un min-heap."""
    if not nodos:
        return [], []
    vecinos = {n: [] for n in nodos}
    for a in aristas:
        vecinos[a.u].append((a.v, a))
        vecinos[a.v].append((a.u, a))

    inicio = inicio if inicio in vecinos else nodos[0]
    visitados = {inicio}
    contador = itertools.count()  # desempate para no comparar objetos Arista
    cola = [(a.peso, next(contador), destino, a) for destino, a in vecinos[inicio]]
    heapq.heapify(cola)
    arbol, pasos = [], []
    while cola and len(visitados) < len(nodos):
        _, _, destino, arista = heapq.heappop(cola)
        if destino in visitados:
            pasos.append(PasoMST(len(pasos) + 1, arista, False, "ambos extremos ya están en el árbol"))
            continue
        visitados.add(destino)
        arbol.append(arista)
        pasos.append(PasoMST(len(pasos) + 1, arista, True, f"agrega el nodo {destino}"))
        for siguiente, a in vecinos[destino]:
            if siguiente not in visitados:
                heapq.heappush(cola, (a.peso, next(contador), siguiente, a))
    return arbol, pasos


def peso_total(arbol):
    return sum(a.peso for a in arbol)


def leer_grafo(texto):
    """Lee aristas, una por línea: "A B 4". Las líneas con # son comentarios."""
    nodos, aristas = [], []
    for numero, linea in enumerate(texto.splitlines(), 1):
        linea = linea.split("#", 1)[0].strip()
        if not linea:
            continue
        partes = linea.replace(",", " ").split()
        if len(partes) != 3:
            raise ValueError(f"Línea {numero}: se esperaba 'origen destino peso'")
        u, v, peso = partes
        try:
            peso = float(peso)
        except ValueError:
            raise ValueError(f"Línea {numero}: el peso '{peso}' no es un número") from None
        for n in (u, v):
            if n not in nodos:
                nodos.append(n)
        aristas.append(Arista(u, v, peso))
    return nodos, aristas


def grafo_a_texto(aristas):
    return "\n".join(f"{a.u} {a.v} {a.peso:g}" for a in aristas)


def es_conexo(nodos, aristas):
    conjuntos = UnionFind(nodos)
    for a in aristas:
        conjuntos.unir(a.u, a.v)
    return len({conjuntos.buscar(n) for n in nodos}) <= 1


def generar_grafo(n=10, vecinos=3, semilla=None):
    """Grafo aleatorio en el plano: cada nodo se une con sus `vecinos` más
    cercanos y el peso es la distancia redondeada. Siempre es conexo.

    Devuelve (nodos, aristas, posiciones).
    """
    azar = random.Random(semilla)
    nombres = [_nombre(i) for i in range(n)]
    posiciones = {m: (azar.uniform(0, 100), azar.uniform(0, 100)) for m in nombres}

    def distancia(a, b):
        (x1, y1), (x2, y2) = posiciones[a], posiciones[b]
        return max(1, round(math.hypot(x1 - x2, y1 - y2)))

    pares = set()
    for a in nombres:
        cercanos = sorted((m for m in nombres if m != a), key=lambda m: distancia(a, m))
        for b in cercanos[:vecinos]:
            pares.add(tuple(sorted((a, b))))

    # Si quedaron componentes separadas, se unen por el par más cercano.
    conjuntos = UnionFind(nombres)
    for a, b in pares:
        conjuntos.unir(a, b)
    while len({conjuntos.buscar(m) for m in nombres}) > 1:
        a, b = min(
            ((a, b) for a in nombres for b in nombres
             if conjuntos.buscar(a) != conjuntos.buscar(b)),
            key=lambda par: distancia(*par),
        )
        pares.add(tuple(sorted((a, b))))
        conjuntos.unir(a, b)

    aristas = [Arista(a, b, distancia(a, b)) for a, b in sorted(pares)]
    return nombres, aristas, posiciones


def posiciones_circulares(nodos):
    k = max(len(nodos), 1)
    return {n: (50 + 45 * math.cos(2 * math.pi * i / k), 50 + 45 * math.sin(2 * math.pi * i / k))
            for i, n in enumerate(nodos)}


def _nombre(i):
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return letras[i % 26] + (str(i // 26) if i >= 26 else "")
