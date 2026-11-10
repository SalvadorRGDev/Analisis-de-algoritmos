"""Pruebas del algoritmo, del formato .sypher y del árbol de expansión mínima.

Ejecutar desde la carpeta del proyecto:  python3 -m unittest -v
"""

import hashlib
import random
import struct
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import expansion_minima as mst  # noqa: E402
import formato  # noqa: E402
import huffman  # noqa: E402


def ida_y_vuelta(contenido, nombre="prueba.txt"):
    resultado = formato.comprimir(contenido, nombre)
    leido = formato.leer(resultado.archivo)          # solo con el .sypher
    recuperado = formato.descomprimir(leido)
    return resultado, leido, recuperado


class TextoPequeno(unittest.TestCase):
    """Prueba 1: 'abracadabra' se puede comprobar a mano."""

    def setUp(self):
        self.analisis = formato.analizar(b"abracadabra")

    def test_frecuencias(self):
        self.assertEqual(self.analisis.frecuencias, {"a": 5, "b": 2, "r": 2, "c": 1, "d": 1})

    def test_pasos_voraces(self):
        # Orden inicial: c(1) d(1) b(2) r(2) a(5)
        uniones = [(p.izquierdo.frecuencia, p.derecho.frecuencia, p.nuevo.frecuencia) for p in self.analisis.pasos]
        self.assertEqual(uniones, [(1, 1, 2), (2, 2, 4), (2, 4, 6), (5, 6, 11)])

    def test_codigos(self):
        self.assertEqual(self.analisis.codigos, {"a": "0", "c": "100", "d": "101", "b": "110", "r": "111"})

    def test_bits(self):
        datos, bits = huffman.codificar(self.analisis.texto, self.analisis.codigos)
        esperado = "0" "110" "111" "0" "100" "0" "101" "0" "110" "111" "0"
        self.assertEqual(bits, 23)
        self.assertEqual(huffman.bytes_a_bits(datos, bits), esperado)
        self.assertEqual(len(datos), 3)  # 23 bits -> 3 bytes, 1 bit de relleno

    def test_longitud_media_y_entropia(self):
        media = huffman.longitud_media(self.analisis.frecuencias, self.analisis.codigos)
        self.assertAlmostEqual(media, 23 / 11)
        entropia = huffman.entropia(self.analisis.frecuencias)
        self.assertTrue(entropia <= media < entropia + 1)


class PropiedadesHuffman(unittest.TestCase):
    def test_codigos_libres_de_prefijo(self):
        azar = random.Random(1)
        for _ in range(50):
            texto = "".join(azar.choice("abcdefghij \n") for _ in range(azar.randint(2, 400)))
            codigos = huffman.generar_codigos(huffman.construir_arbol(huffman.calcular_frecuencias(texto))[0])
            lista = sorted(codigos.values())
            for a, b in zip(lista, lista[1:]):
                self.assertFalse(b.startswith(a), f"{a} es prefijo de {b}")

    def test_mas_frecuente_no_tiene_codigo_mas_largo(self):
        frecuencias = {"a": 50, "b": 20, "c": 15, "d": 10, "e": 5}
        codigos = huffman.generar_codigos(huffman.construir_arbol(frecuencias)[0])
        for x in frecuencias:
            for y in frecuencias:
                if frecuencias[x] > frecuencias[y]:
                    self.assertLessEqual(len(codigos[x]), len(codigos[y]))

    def test_optimo_contra_fuerza_bruta(self):
        """Para alfabetos pequeños, ninguna longitud de código prefijo válida
        (desigualdad de Kraft) da menos bits que Huffman."""
        from itertools import product
        azar = random.Random(2)
        for _ in range(30):
            frecuencias = {chr(97 + i): azar.randint(1, 30) for i in range(azar.randint(2, 5))}
            codigos = huffman.generar_codigos(huffman.construir_arbol(frecuencias)[0])
            huff = sum(f * len(codigos[s]) for s, f in frecuencias.items())
            mejor = min(
                sum(f * l for f, l in zip(frecuencias.values(), longitudes))
                for longitudes in product(range(1, 6), repeat=len(frecuencias))
                if sum(2 ** -l for l in longitudes) <= 1
            )
            self.assertEqual(huff, mejor)

    def test_arbol_determinista(self):
        texto = "el mismo texto siempre da el mismo arbol"
        a = huffman.generar_codigos(huffman.construir_arbol(huffman.calcular_frecuencias(texto))[0])
        b = huffman.generar_codigos(huffman.construir_arbol(dict(reversed(huffman.calcular_frecuencias(texto).items())))[0])
        self.assertEqual(a, b)


class CasosLimite(unittest.TestCase):
    def comprobar(self, contenido):
        _, leido, recuperado = ida_y_vuelta(contenido)
        self.assertTrue(recuperado.integro)
        self.assertEqual(recuperado.contenido, contenido)
        return leido

    def test_vacio(self):
        leido = self.comprobar(b"")
        self.assertEqual((leido.bits_validos, leido.datos, leido.frecuencias), (0, b"", {}))

    def test_un_solo_simbolo(self):
        leido = self.comprobar(b"aaaaaaaaaa")
        self.assertEqual(leido.codigos, {"a": "0"})
        self.assertEqual(leido.bits_validos, 10)

    def test_un_caracter(self):
        self.comprobar(b"x")

    def test_unicode_y_saltos_de_linea_windows(self):
        self.comprobar("Señor, ¿qué hacéis?\r\nÑandú — «comillas» 🌍 漢字\r\n".encode("utf-8"))

    def test_latin1(self):
        leido = self.comprobar("canción en Latin-1: ñ á ü".encode("latin-1"))
        self.assertEqual(leido.codificacion, "latin-1")

    def test_bytes_aleatorios(self):
        azar = random.Random(3)
        for _ in range(20):
            self.comprobar(bytes(azar.randrange(256) for _ in range(azar.randint(1, 3000))))

    def test_bom_utf8(self):
        self.comprobar("﻿Texto con BOM".encode("utf-8"))


class FormatoSypher(unittest.TestCase):
    def setUp(self):
        self.contenido = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme".encode("utf-8")
        self.resultado = formato.comprimir(self.contenido, "mancha.txt", fecha=1_700_000_000)
        self.archivo = self.resultado.archivo

    def test_cabecera(self):
        self.assertEqual(self.archivo[:4], b"SYPH")
        self.assertEqual(self.archivo[4], formato.VERSION)
        leido = formato.leer(self.archivo)
        self.assertEqual(leido.tamano_original, len(self.contenido))
        self.assertEqual(leido.nombre_original, "mancha.txt")
        self.assertEqual(leido.fecha, 1_700_000_000)
        self.assertEqual(leido.sha256, hashlib.sha256(self.contenido).digest())
        self.assertEqual(leido.caracteres, len(self.contenido.decode()))
        self.assertEqual(len(leido.datos) * 8 - leido.bits_validos, leido.relleno)

    def test_no_guarda_el_texto(self):
        self.assertNotIn(b"lugar de la Mancha", self.archivo)

    def test_secciones_contiguas(self):
        leido = formato.leer(self.archivo)
        posicion = 0
        for seccion in leido.secciones:
            self.assertEqual(seccion.inicio, posicion, seccion.nombre)
            posicion += seccion.tamano
        self.assertEqual(posicion, len(self.archivo))

    def test_mismo_archivo_byte_a_byte(self):
        otro = formato.comprimir(self.contenido, "mancha.txt", fecha=1_700_000_000)
        self.assertEqual(otro.archivo, self.archivo)

    def test_firma_invalida(self):
        with self.assertRaises(ValueError):
            formato.leer(b"ZIP!" + self.archivo[4:])

    def test_version_desconocida(self):
        with self.assertRaises(ValueError):
            formato.leer(self.archivo[:4] + b"\x09" + self.archivo[5:])

    def test_truncado(self):
        with self.assertRaises(ValueError):
            formato.leer(self.archivo[:-3])

    def test_datos_alterados_rompen_la_integridad(self):
        leido = formato.leer(self.archivo)
        alterado = bytearray(self.archivo)
        alterado[leido.tamano_cabecera + 2] ^= 0b0100_0000
        try:
            recuperado = formato.descomprimir(formato.leer(bytes(alterado)))
            self.assertFalse(recuperado.integro)
        except ValueError:
            pass  # también es válido que el decodificador detecte el error

    def test_tabla_alterada(self):
        alterado = bytearray(self.archivo)
        posicion = next(s.inicio for s in formato.leer(self.archivo).secciones if s.nombre == "Tabla de frecuencias")
        struct.pack_into(">I", alterado, posicion + 4, 999)  # frecuencia falsa
        with self.assertRaises(ValueError):
            formato.leer(bytes(alterado))


class LibroGutenberg(unittest.TestCase):
    """Prueba 2 y 3: un libro real comprimido y recuperado sin diferencias."""

    def test_quijote(self):
        ruta = RAIZ / "libros" / "pg2000.txt"
        if not ruta.exists():
            self.skipTest("Descarga primero el libro 2000 desde la interfaz o con evidencias/generar_evidencias.py")
        contenido = ruta.read_bytes()
        resultado, leido, recuperado = ida_y_vuelta(contenido, ruta.name)
        self.assertTrue(recuperado.integro)
        self.assertIsNone(formato.comparar_bytes(contenido, recuperado.contenido))
        reduccion = 1 - len(resultado.archivo) / len(contenido)
        self.assertGreater(reduccion, 0.40)


class ExpansionMinima(unittest.TestCase):
    def test_ejemplo_clasico(self):
        nodos, aristas = mst.leer_grafo("""
            A B 4
            A H 8
            B C 8
            B H 11
            C D 7
            C F 4
            C I 2
            D E 9
            D F 14
            E F 10
            F G 2
            G H 1
            G I 6
            H I 7""")
        for arbol, _ in (mst.kruskal(nodos, aristas), mst.prim(nodos, aristas, "A")):
            self.assertEqual(mst.peso_total(arbol), 37)
            self.assertEqual(len(arbol), len(nodos) - 1)

    def test_kruskal_y_prim_coinciden(self):
        for semilla in range(100):
            nodos, aristas, _ = mst.generar_grafo(12, 3, semilla)
            self.assertTrue(mst.es_conexo(nodos, aristas))
            k, _ = mst.kruskal(nodos, aristas)
            p, _ = mst.prim(nodos, aristas)
            self.assertEqual(mst.peso_total(k), mst.peso_total(p))
            self.assertTrue(mst.es_conexo(nodos, k))

    def test_contra_fuerza_bruta(self):
        from itertools import combinations
        for semilla in range(15):
            nodos, aristas, _ = mst.generar_grafo(6, 3, semilla)
            mejor = min(
                mst.peso_total(subconjunto)
                for subconjunto in combinations(aristas, len(nodos) - 1)
                if mst.es_conexo(nodos, list(subconjunto))
            )
            self.assertEqual(mst.peso_total(mst.kruskal(nodos, aristas)[0]), mejor)

    def test_ciclo_rechazado(self):
        nodos, aristas = mst.leer_grafo("A B 1\nB C 1\nA C 5")
        _, pasos = mst.kruskal(nodos, aristas)
        self.assertEqual([p.aceptada for p in pasos], [True, True])  # se detiene con n-1 aristas
        nodos, aristas = mst.leer_grafo("A B 1\nB C 1\nA C 1\nC D 9")
        _, pasos = mst.kruskal(nodos, aristas)
        self.assertIn(False, [p.aceptada for p in pasos])

    def test_grafo_no_conexo(self):
        nodos, aristas = mst.leer_grafo("A B 1\nC D 2")
        self.assertFalse(mst.es_conexo(nodos, aristas))
        self.assertEqual(len(mst.kruskal(nodos, aristas)[0]), 2)

    def test_linea_invalida(self):
        with self.assertRaises(ValueError):
            mst.leer_grafo("A B")


if __name__ == "__main__":
    unittest.main()
