"""Búsqueda y descarga de libros de Project Gutenberg.

Primero se consulta el catálogo OPDS oficial de gutenberg.org. Si no responde
se usa Gutendex (API JSON no oficial). No se guarda el repositorio completo: solo se
descarga el libro que el usuario elige.
"""

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

AGENTE = {"User-Agent": "HADA-Huffman/1.0 (actividad escolar de Analisis de Algoritmos)"}
CARPETA_LIBROS = Path(__file__).parent / "libros"


@dataclass
class Libro:
    id: int
    titulo: str
    autores: str
    idiomas: str = ""
    descargas: int | None = None
    url_txt: str | None = None


def _get(url, tiempo=15):
    peticion = urllib.request.Request(url, headers=AGENTE)
    with urllib.request.urlopen(peticion, timeout=tiempo) as respuesta:
        return respuesta.read()


def _buscar_gutendex(consulta):
    url = "https://gutendex.com/books/?" + urllib.parse.urlencode({"search": consulta})
    datos = json.loads(_get(url, tiempo=10))
    libros = []
    for r in datos.get("results", []):
        formatos = r.get("formats", {})
        url_txt = formatos.get("text/plain; charset=utf-8") or next(
            (u for tipo, u in formatos.items() if tipo.startswith("text/plain") and not u.endswith(".zip")),
            None,
        )
        if not url_txt:
            continue  # sin versión en texto plano
        libros.append(Libro(
            id=r["id"],
            titulo=r["title"],
            autores="; ".join(a["name"] for a in r.get("authors", [])) or "Anónimo",
            idiomas=", ".join(r.get("languages", [])),
            descargas=r.get("download_count"),
            url_txt=url_txt,
        ))
    return libros


def _buscar_opds(consulta):
    url = "https://www.gutenberg.org/ebooks/search.opds/?" + urllib.parse.urlencode({"query": consulta})
    raiz = ET.fromstring(_get(url))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    libros = []
    for entrada in raiz.findall("a:entry", ns):
        identificador = entrada.findtext("a:id", default="", namespaces=ns)
        # Los libros tienen id del tipo https://www.gutenberg.org/ebooks/2000.opds
        numero = identificador.rsplit("/", 1)[-1].removesuffix(".opds")
        if not numero.isdigit():
            continue  # entradas de navegación ("ordenar por...", etc.)
        titulo = " ".join(entrada.findtext("a:title", default="", namespaces=ns).split())
        idioma = ""
        if titulo.endswith(")") and " (" in titulo:
            titulo, idioma = titulo[:-1].rsplit(" (", 1)
        libros.append(Libro(
            id=int(numero),
            titulo=titulo,
            autores=entrada.findtext("a:content", default="", namespaces=ns) or "Anónimo",
            idiomas=idioma,
        ))
    return libros


def buscar(consulta):
    """Busca por título, autor o palabras clave. Devuelve (libros, fuente)."""
    consulta = consulta.strip()
    if not consulta:
        return [], ""
    try:
        return _buscar_opds(consulta), "gutenberg.org (OPDS)"
    except Exception:
        return _buscar_gutendex(consulta), "Gutendex"


def descargar(libro):
    """Descarga el .txt de un libro y guarda una copia en libros/pg<id>.txt.

    Devuelve (bytes, ruta). Si ya se descargó antes, se reutiliza la copia.
    """
    CARPETA_LIBROS.mkdir(exist_ok=True)
    ruta = CARPETA_LIBROS / f"pg{libro.id}.txt"
    if ruta.exists():
        return ruta.read_bytes(), ruta

    urls = [f"https://www.gutenberg.org/cache/epub/{libro.id}/pg{libro.id}.txt"]
    if libro.url_txt:
        urls.append(libro.url_txt)
    ultimo_error = None
    for url in urls:
        try:
            contenido = _get(url, tiempo=60)
            if contenido:
                ruta.write_bytes(contenido)
                return contenido, ruta
        except Exception as error:
            ultimo_error = error
    raise ConnectionError(f"No se pudo descargar el libro {libro.id}: {ultimo_error}")
