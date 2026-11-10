"""Interfaz gráfica: compresor Huffman .sypher + árbol de expansión mínima.

Flujo: BUSCAR LIBRO / SUBIR TXT -> ANALIZAR -> CONSTRUIR HUFFMAN -> COMPRIMIR
       -> INSPECCIONAR -> DESCOMPRIMIR
"""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import expansion_minima as mst
import formato
import gutenberg
import huffman

# Paleta Catppuccin Mocha (la misma de las actividades anteriores)
C = {
    "base": "#1e1e2e", "manto": "#181825", "corteza": "#11111b",
    "sup": "#313244", "sup2": "#45475a", "borde": "#585b70",
    "texto": "#cdd6f4", "sub": "#a6adc8", "tenue": "#6c7086",
    "azul": "#89b4fa", "verde": "#a6e3a1", "rojo": "#f38ba8", "durazno": "#fab387",
    "malva": "#cba6f7", "amarillo": "#f9e2af", "turquesa": "#94e2d5",
}

TEXTO_EJEMPLO = "abracadabra"
PASOS_FLUJO = ["Buscar / subir", "Analizar", "Construir árbol", "Comprimir", "Inspeccionar", "Descomprimir"]
MAX_VISTA_PREVIA = 20_000

GRAFO_EJEMPLO = """# Grafo clásico de Cormen et al. (MST de peso 37)
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
H I 7"""
POSICIONES_EJEMPLO = {
    "A": (5, 50), "B": (25, 85), "C": (50, 85), "D": (75, 85), "E": (95, 50),
    "F": (75, 15), "G": (50, 15), "H": (25, 15), "I": (38, 50),
}


# ----------------------------------------------------------------- utilidades

def configurar_estilo(root):
    familia = tkfont.nametofont("TkDefaultFont").actual("family")
    for nombre in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        tkfont.nametofont(nombre).configure(size=10)
    tkfont.nametofont("TkFixedFont").configure(size=10)

    estilo = ttk.Style(root)
    estilo.theme_use("clam")
    estilo.configure(
        ".", background=C["base"], foreground=C["texto"], fieldbackground=C["sup"],
        bordercolor=C["sup2"], lightcolor=C["sup"], darkcolor=C["sup"], troughcolor=C["manto"],
        focuscolor=C["azul"], selectbackground=C["azul"], selectforeground=C["base"],
        insertcolor=C["texto"], arrowcolor=C["sub"],
    )
    estilo.configure("TFrame", background=C["base"])
    estilo.configure("Tarjeta.TFrame", background=C["sup"])
    estilo.configure("Barra.TFrame", background=C["manto"])
    estilo.configure("TLabel", background=C["base"], foreground=C["texto"])
    estilo.configure("Sub.TLabel", foreground=C["sub"])
    estilo.configure("Titulo.TLabel", font=(familia, 17, "bold"))
    estilo.configure("Barra.TLabel", background=C["manto"], foreground=C["sub"])
    estilo.configure("Tarjeta.TLabel", background=C["sup"])
    estilo.configure("TarjetaSub.TLabel", background=C["sup"], foreground=C["sub"])
    estilo.configure("TarjetaTitulo.TLabel", background=C["sup"], font=(familia, 11, "bold"))
    estilo.configure("MetricaTitulo.TLabel", background=C["sup"], foreground=C["sub"], font=(familia, 9))
    estilo.configure("MetricaValor.TLabel", background=C["sup"], font=(familia, 14, "bold"))
    estilo.configure("MetricaDetalle.TLabel", background=C["sup"], foreground=C["tenue"], font=(familia, 9))
    estilo.configure("Bien.TLabel", background=C["sup"], foreground=C["verde"], font=(familia, 12, "bold"))
    estilo.configure("Mal.TLabel", background=C["sup"], foreground=C["rojo"], font=(familia, 12, "bold"))

    estilo.configure("TNotebook", background=C["manto"], borderwidth=0, tabmargins=(10, 6, 10, 0))
    estilo.configure("TNotebook.Tab", background=C["manto"], foreground=C["sub"], padding=(14, 7), borderwidth=0)
    estilo.map("TNotebook.Tab", background=[("selected", C["base"])], foreground=[("selected", C["texto"])])
    estilo.configure("Interno.TNotebook", background=C["base"], tabmargins=(0, 4, 0, 0))
    estilo.configure("Interno.TNotebook.Tab", background=C["base"], padding=(12, 5))
    estilo.map("Interno.TNotebook.Tab", background=[("selected", C["sup"])])

    estilo.configure("TButton", background=C["sup2"], foreground=C["texto"], padding=(12, 6), borderwidth=0)
    estilo.map("TButton", background=[("disabled", C["sup"]), ("active", C["borde"])],
               foreground=[("disabled", C["tenue"])])
    estilo.configure("Acento.TButton", background=C["azul"], foreground=C["corteza"], font=(familia, 10, "bold"))
    estilo.map("Acento.TButton", background=[("disabled", C["sup2"]), ("active", C["malva"])],
               foreground=[("disabled", C["tenue"])])
    estilo.configure("Chico.TButton", padding=(8, 3))

    estilo.configure("Treeview", background=C["manto"], fieldbackground=C["manto"], foreground=C["texto"],
                     rowheight=24, borderwidth=0)
    estilo.configure("Treeview.Heading", background=C["sup2"], foreground=C["texto"], relief="flat", padding=(6, 4))
    estilo.map("Treeview.Heading", background=[("active", C["borde"])])
    estilo.map("Treeview", background=[("selected", C["azul"])], foreground=[("selected", C["corteza"])])
    estilo.configure("TEntry", fieldbackground=C["sup2"], foreground=C["texto"], padding=5)
    estilo.configure("TSpinbox", fieldbackground=C["sup2"], foreground=C["texto"], padding=3)
    estilo.configure("TCombobox", fieldbackground=C["sup2"], foreground=C["texto"], padding=3)
    estilo.map("TCombobox", fieldbackground=[("readonly", C["sup2"])], foreground=[("readonly", C["texto"])])
    root.option_add("*TCombobox*Listbox.background", C["sup2"])
    root.option_add("*TCombobox*Listbox.foreground", C["texto"])
    estilo.configure("TScrollbar", background=C["sup2"], troughcolor=C["manto"], borderwidth=0, arrowcolor=C["sub"])
    estilo.configure("TRadiobutton", background=C["sup"], foreground=C["texto"], indicatorcolor=C["manto"])
    estilo.map("TRadiobutton", indicatorcolor=[("selected", C["azul"])], background=[("active", C["sup"])])
    estilo.configure("Horizontal.TScale", background=C["azul"], troughcolor=C["sup2"])
    estilo.configure("TProgressbar", background=C["azul"], troughcolor=C["manto"], borderwidth=0)
    estilo.configure("TPanedwindow", background=C["base"])
    return familia


def texto_widget(parent, alto=10, mono=True, **kw):
    """tk.Text con colores del tema y barra de desplazamiento."""
    marco = ttk.Frame(parent)
    widget = tk.Text(
        marco, height=alto, wrap=kw.pop("wrap", "word"), bg=C["manto"], fg=C["texto"],
        insertbackground=C["texto"], selectbackground=C["azul"], selectforeground=C["corteza"],
        relief="flat", highlightthickness=0, padx=10, pady=8,
        font="TkFixedFont" if mono else "TkTextFont", **kw,
    )
    barra = ttk.Scrollbar(marco, orient="vertical", command=widget.yview)
    widget.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    widget.pack(side="left", fill="both", expand=True)
    return marco, widget


def poner_texto(widget, contenido, solo_lectura=True):
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", contenido)
    if solo_lectura:
        widget.configure(state="disabled")


def tarjeta(parent, titulo=None, subtitulo=None):
    marco = ttk.Frame(parent, style="Tarjeta.TFrame", padding=14)
    if titulo:
        ttk.Label(marco, text=titulo, style="TarjetaTitulo.TLabel").pack(anchor="w")
    if subtitulo:
        ttk.Label(marco, text=subtitulo, style="TarjetaSub.TLabel", wraplength=520,
                  justify="left").pack(anchor="w", pady=(2, 8))
    return marco


def _clave_orden(valor):
    try:
        return (0, float(str(valor).replace(",", "").replace("%", "").split()[0]))
    except (ValueError, IndexError):
        return (1, str(valor))


def tabla(parent, columnas, alto=12):
    """Treeview con encabezados que ordenan al hacer clic.

    columnas: lista de (id, título, ancho, alineación).
    """
    marco = ttk.Frame(parent)
    arbol = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", height=alto)
    for ident, titulo, ancho, alineacion in columnas:
        arbol.heading(ident, text=titulo, command=lambda c=ident: _ordenar(arbol, c, False))
        arbol.column(ident, width=ancho, anchor=alineacion, stretch=ancho >= 250)
    barra = ttk.Scrollbar(marco, orient="vertical", command=arbol.yview)
    arbol.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    arbol.pack(side="left", fill="both", expand=True)
    arbol.tag_configure("par", background=C["base"])
    return marco, arbol


def _ordenar(arbol, columna, descendente):
    filas = [(arbol.set(i, columna), i) for i in arbol.get_children("")]
    filas.sort(key=lambda par: _clave_orden(par[0]), reverse=descendente)
    for pos, (_, i) in enumerate(filas):
        arbol.move(i, "", pos)
        arbol.item(i, tags=("par",) if pos % 2 else ())
    arbol.heading(columna, command=lambda: _ordenar(arbol, columna, not descendente))


def llenar_tabla(arbol, filas):
    arbol.delete(*arbol.get_children())
    for pos, fila in enumerate(filas):
        arbol.insert("", "end", iid=str(pos), values=fila, tags=("par",) if pos % 2 else ())


class Metricas(ttk.Frame):
    """Rejilla de tarjetas con un número grande y un detalle."""

    def __init__(self, parent, claves, columnas=4):
        super().__init__(parent)
        self.valores, self.detalles = {}, {}
        for i, clave in enumerate(claves):
            celda = ttk.Frame(self, style="Tarjeta.TFrame", padding=(12, 8))
            celda.grid(row=i // columnas, column=i % columnas, sticky="nsew", padx=4, pady=4)
            ttk.Label(celda, text=clave.upper(), style="MetricaTitulo.TLabel").pack(anchor="w")
            self.valores[clave] = ttk.Label(celda, text="—", style="MetricaValor.TLabel")
            self.valores[clave].pack(anchor="w")
            self.detalles[clave] = ttk.Label(celda, text="", style="MetricaDetalle.TLabel")
            self.detalles[clave].pack(anchor="w")
        for c in range(columnas):
            self.columnconfigure(c, weight=1, uniform="metricas")

    def poner(self, clave, valor, detalle="", estilo="MetricaValor.TLabel"):
        self.valores[clave].configure(text=valor, style=estilo)
        self.detalles[clave].configure(text=detalle)

    def limpiar(self):
        for clave in self.valores:
            self.poner(clave, "—")


def tamano_corto(n):
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.2f} MB"
    if n >= 1024:
        return f"{n / 1024:.2f} KB"
    return f"{n} B"


def compacto(n):
    """Frecuencia corta para el árbol: 1234 -> '1234', 98765 -> '99k'."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n / 1000:.0f}k"
    return str(n)


def figura_oscura(ancho=5, alto=4):
    figura = Figure(figsize=(ancho, alto), dpi=100, facecolor=C["base"])
    return figura


def estilizar_ejes(ax):
    ax.set_facecolor(C["manto"])
    for lado in ax.spines.values():
        lado.set_color(C["sup2"])
    ax.tick_params(colors=C["sub"], labelsize=8)
    ax.xaxis.label.set_color(C["sub"])
    ax.yaxis.label.set_color(C["sub"])
    ax.title.set_color(C["texto"])


# --------------------------------------------------------------- vista árbol

class VistaArbol(ttk.Frame):
    """Dibuja el árbol de Huffman y permite reproducir su construcción voraz.

    Las posiciones son las del árbol final; en el paso k solo se ven los nodos
    creados hasta ese paso y los que faltan aparecen como fantasmas.
    """

    def __init__(self, parent, familia, al_seleccionar=None):
        super().__init__(parent)
        self.familia = familia
        self.al_seleccionar = al_seleccionar
        self.raiz, self.pasos, self.nodos = None, [], []
        self.zoom, self.paso, self.camino = 1.0, 0, set()
        self.animacion = None
        self.posiciones, self.padres, self.codigos = {}, {}, {}

        barra = ttk.Frame(self, style="Tarjeta.TFrame", padding=(10, 6))
        barra.pack(fill="x")
        ttk.Button(barra, text="−", width=3, style="Chico.TButton", command=lambda: self._zoom(0.8)).pack(side="left")
        ttk.Button(barra, text="+", width=3, style="Chico.TButton", command=lambda: self._zoom(1.25)).pack(side="left", padx=4)
        ttk.Button(barra, text="Ajustar", style="Chico.TButton", command=self._ajustar).pack(side="left")
        ttk.Label(barra, text="   Construcción voraz:", style="TarjetaSub.TLabel").pack(side="left")
        ttk.Button(barra, text="⏮", width=3, style="Chico.TButton", command=lambda: self.ir_a(0)).pack(side="left", padx=(6, 0))
        ttk.Button(barra, text="◀", width=3, style="Chico.TButton", command=lambda: self.ir_a(self.paso - 1)).pack(side="left", padx=2)
        self.boton_play = ttk.Button(barra, text="▶ Reproducir", style="Chico.TButton", command=self._reproducir)
        self.boton_play.pack(side="left", padx=2)
        ttk.Button(barra, text="▶|", width=3, style="Chico.TButton", command=lambda: self.ir_a(self.paso + 1)).pack(side="left", padx=2)
        ttk.Button(barra, text="⏭", width=3, style="Chico.TButton", command=lambda: self.ir_a(len(self.pasos))).pack(side="left")
        self.escala = ttk.Scale(barra, from_=0, to=1, orient="horizontal", command=self._mover_escala)
        self.escala.pack(side="left", fill="x", expand=True, padx=10)
        self.etiqueta_paso = ttk.Label(barra, text="", style="Tarjeta.TLabel", width=16)
        self.etiqueta_paso.pack(side="left")

        self.explicacion = ttk.Label(self, text="", style="Sub.TLabel", padding=(10, 6), wraplength=1100, justify="left")
        self.explicacion.pack(fill="x")

        cuerpo = ttk.PanedWindow(self, orient="horizontal")
        cuerpo.pack(fill="both", expand=True)
        marco_lienzo = ttk.Frame(cuerpo)
        self.lienzo = tk.Canvas(marco_lienzo, bg=C["manto"], highlightthickness=0)
        sx = ttk.Scrollbar(marco_lienzo, orient="horizontal", command=self.lienzo.xview)
        sy = ttk.Scrollbar(marco_lienzo, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.pack(side="bottom", fill="x")
        sy.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.lienzo.bind("<Button-1>", self._clic)
        self.lienzo.bind("<ButtonPress-3>", lambda e: self.lienzo.scan_mark(e.x, e.y))
        self.lienzo.bind("<B3-Motion>", lambda e: self.lienzo.scan_dragto(e.x, e.y, gain=1))
        self.lienzo.bind("<MouseWheel>", lambda e: self.lienzo.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.lienzo.bind("<Button-4>", lambda e: self.lienzo.yview_scroll(-2, "units"))
        self.lienzo.bind("<Button-5>", lambda e: self.lienzo.yview_scroll(2, "units"))
        self.lienzo.bind("<Shift-Button-4>", lambda e: self.lienzo.xview_scroll(-2, "units"))
        self.lienzo.bind("<Shift-Button-5>", lambda e: self.lienzo.xview_scroll(2, "units"))
        cuerpo.add(marco_lienzo, weight=4)

        lateral = ttk.Frame(cuerpo, style="Tarjeta.TFrame", padding=8)
        ttk.Label(lateral, text="Pasos (uniones)", style="TarjetaTitulo.TLabel").pack(anchor="w")
        marco_lista = ttk.Frame(lateral)
        marco_lista.pack(fill="both", expand=True, pady=(6, 0))
        self.lista = tk.Listbox(marco_lista, bg=C["manto"], fg=C["texto"], selectbackground=C["durazno"],
                                selectforeground=C["corteza"], relief="flat", highlightthickness=0,
                                font="TkFixedFont", activestyle="none", width=30)
        barra_lista = ttk.Scrollbar(marco_lista, orient="vertical", command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra_lista.set)
        barra_lista.pack(side="right", fill="y")
        self.lista.pack(side="left", fill="both", expand=True)
        self.lista.bind("<<ListboxSelect>>", self._elegir_lista)
        cuerpo.add(lateral, weight=1)

        self.mostrar(None, [])

    # -- datos
    def mostrar(self, raiz, pasos):
        self._detener()
        self.raiz, self.pasos = raiz, pasos
        self.nodos = huffman.recorrer(raiz)
        self.codigos = huffman.generar_codigos(raiz)
        self.camino = set()
        self._calcular_posiciones()
        self.lista.delete(0, "end")
        self.lista.insert("end", " 0. hojas iniciales")
        for p in pasos:
            self.lista.insert("end", f"{p.numero:>2}. {self._nombre(p.izquierdo)} + {self._nombre(p.derecho)} = {p.nuevo.frecuencia:,}")
        self.escala.configure(to=max(len(pasos), 1))
        self.paso = len(pasos)
        self.escala.set(self.paso)
        self._ajustar()

    def _calcular_posiciones(self):
        """x: orden de las hojas en un recorrido inorden; y: profundidad."""
        self.posiciones, self.padres = {}, {}
        if self.raiz is None:
            return
        siguiente_x = 0
        pila = [(self.raiz, 0, False)]
        while pila:
            nodo, prof, visitado = pila.pop()
            hijos = [h for h in (nodo.izquierdo, nodo.derecho) if h]
            if not hijos:
                self.posiciones[nodo] = (siguiente_x, prof)
                siguiente_x += 1
            elif visitado:
                xs = [self.posiciones[h][0] for h in hijos]
                self.posiciones[nodo] = (sum(xs) / len(xs), prof)
            else:
                pila.append((nodo, prof, True))
                for h in reversed(hijos):
                    self.padres[h] = nodo
                    pila.append((h, prof + 1, False))

    def _nombre(self, nodo):
        if nodo.es_hoja:
            return f"'{huffman.mostrar_simbolo(nodo.simbolo)}'({nodo.frecuencia:,})"
        return f"N{nodo.paso}({nodo.frecuencia:,})"

    # -- controles
    def ir_a(self, paso):
        self.paso = max(0, min(len(self.pasos), int(paso)))
        self.escala.set(self.paso)
        self.lista.selection_clear(0, "end")
        self.lista.selection_set(self.paso)
        self.lista.see(self.paso)
        self.dibujar()
        if 0 < self.paso <= len(self.pasos):
            self._ver(self.pasos[self.paso - 1].nuevo)

    def _mover_escala(self, valor):
        paso = round(float(valor))
        if paso != self.paso:
            self.paso = paso
            self.dibujar()

    def _elegir_lista(self, _evento):
        seleccion = self.lista.curselection()
        if seleccion and seleccion[0] != self.paso:
            self._detener()
            self.ir_a(seleccion[0])

    def _reproducir(self):
        if self.animacion:
            self._detener()
            return
        if self.paso >= len(self.pasos):
            self.ir_a(0)
        self.boton_play.configure(text="⏸ Pausa")
        self._avanzar()

    def _avanzar(self):
        if self.paso >= len(self.pasos):
            self._detener()
            return
        self.ir_a(self.paso + 1)
        espera = max(60, min(700, 9000 // max(len(self.pasos), 1)))
        self.animacion = self.after(espera, self._avanzar)

    def _detener(self):
        if self.animacion:
            self.after_cancel(self.animacion)
            self.animacion = None
        self.boton_play.configure(text="▶ Reproducir")

    def _zoom(self, factor):
        self.zoom = max(0.35, min(2.5, self.zoom * factor))
        self.dibujar()

    def _ajustar(self):
        if self.posiciones:
            ancho = max(self.lienzo.winfo_width(), 600)
            hojas = max(x for x, _ in self.posiciones.values()) + 1
            self.zoom = max(0.6, min(1.6, (ancho - 80) / (hojas * 46)))
        self.dibujar()

    def seleccionar_simbolo(self, simbolo):
        hoja = next((n for n in self.nodos if n.es_hoja and n.simbolo == simbolo), None)
        if hoja is None:
            return
        self.camino = set()
        nodo = hoja
        while nodo is not None:
            self.camino.add(nodo)
            nodo = self.padres.get(nodo)
        self.dibujar()
        self._ver(hoja)

    def _ver(self, nodo):
        """Desplaza el lienzo solo si el nodo quedó fuera de la vista."""
        x, y = self._xy(nodo)
        lienzo = self.lienzo
        izquierda, arriba = lienzo.canvasx(0), lienzo.canvasy(0)
        ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
        if izquierda + 40 <= x <= izquierda + ancho - 40 and arriba + 40 <= y <= arriba + alto - 40:
            return
        x0, y0, x1, y1 = (float(v) for v in str(lienzo.cget("scrollregion")).split())
        lienzo.xview_moveto(max(0, (x - ancho / 2 - x0) / max(x1 - x0, 1)))
        lienzo.yview_moveto(max(0, (y - alto / 2 - y0) / max(y1 - y0, 1)))

    def _clic(self, evento):
        elementos = self.lienzo.find_withtag("current")
        if not elementos:
            return
        for etiqueta in self.lienzo.gettags(elementos[0]):
            if etiqueta.startswith("n") and etiqueta[1:].isdigit():
                nodo = self.nodos[int(etiqueta[1:])]
                if nodo.es_hoja:
                    self.seleccionar_simbolo(nodo.simbolo)
                    if self.al_seleccionar:
                        self.al_seleccionar(nodo.simbolo)
                return

    # -- dibujo
    def _xy(self, nodo):
        x, prof = self.posiciones[nodo]
        return 40 + x * 46 * self.zoom, 50 + prof * 72 * self.zoom

    def dibujar(self):
        lienzo = self.lienzo
        lienzo.delete("all")
        self.etiqueta_paso.configure(text=f"paso {self.paso} de {len(self.pasos)}")
        if self.raiz is None:
            lienzo.create_text(30, 30, anchor="nw", fill=C["tenue"], font=(self.familia, 12),
                               text="Aún no hay árbol: carga un texto y presiona «Analizar».")
            self.explicacion.configure(text="")
            return

        k = self.paso
        completo = k == len(self.pasos)
        visible = lambda n: completo or n.es_hoja or n.paso <= k
        actual = self.pasos[k - 1] if 0 < k <= len(self.pasos) else None
        resaltados = {actual.izquierdo, actual.derecho, actual.nuevo} if actual else set()
        r = max(9, 15 * self.zoom)
        tam = max(7, round(9 * self.zoom))
        tam_hoja = max(8, round(11 * self.zoom))

        for nodo in self.nodos:
            x1, y1 = self._xy(nodo)
            for bit, hijo in (("0", nodo.izquierdo), ("1", nodo.derecho)):
                if hijo is None:
                    continue
                x2, y2 = self._xy(hijo)
                en_camino = nodo in self.camino and hijo in self.camino
                if not visible(nodo):
                    color, ancho, guiones = C["sup"], 1, (3, 4)
                elif en_camino:
                    color, ancho, guiones = C["verde"], 3, None
                elif nodo is (actual.nuevo if actual else None):
                    color, ancho, guiones = C["durazno"], 2.5, None
                else:
                    color, ancho, guiones = C["borde"], 1.4, None
                lienzo.create_line(x1, y1, x2, y2, fill=color, width=ancho, dash=guiones)
                if visible(nodo) and self.zoom >= 0.5:
                    lienzo.create_text((x1 + x2) / 2 + (-7 if bit == "0" else 7), (y1 + y2) / 2 - 6,
                                       text=bit, fill=C["amarillo"] if en_camino else C["tenue"],
                                       font=(self.familia, tam, "bold"))

        for i, nodo in enumerate(self.nodos):
            x, y = self._xy(nodo)
            etiqueta = f"n{i}"
            if not visible(nodo):
                lienzo.create_oval(x - r, y - r, x + r, y + r, outline=C["sup2"], dash=(2, 3), tags=etiqueta)
                continue
            if nodo in resaltados:
                relleno, borde, texto = C["durazno"], C["durazno"], C["corteza"]
            elif nodo in self.camino:
                relleno, borde, texto = C["verde"], C["verde"], C["corteza"]
            elif nodo.es_hoja:
                relleno, borde, texto = C["sup2"], C["azul"], C["texto"]
            else:
                relleno, borde, texto = C["sup"], C["malva"], C["sub"]
            if nodo.es_hoja:
                lienzo.create_rectangle(x - r, y - r, x + r, y + r, fill=relleno, outline=borde, width=2, tags=etiqueta)
                lienzo.create_text(x, y, text=huffman.mostrar_simbolo(nodo.simbolo), fill=texto,
                                   font=(self.familia, tam_hoja, "bold"), tags=etiqueta)
                if self.zoom >= 0.75:
                    lienzo.create_text(x, y + r + 8, text=compacto(nodo.frecuencia), fill=C["tenue"],
                                       font=(self.familia, tam), tags=etiqueta)
                if nodo in self.camino:
                    lienzo.create_text(x, y + r + 21, text=self.codigos.get(nodo.simbolo, ""),
                                       fill=C["verde"], font=("TkFixedFont", tam, "bold"))
            else:
                lienzo.create_oval(x - r, y - r, x + r, y + r, fill=relleno, outline=borde, width=2, tags=etiqueta)
                if self.zoom >= 0.75:
                    lienzo.create_text(x, y, text=compacto(nodo.frecuencia), fill=texto,
                                       font=(self.familia, max(6, tam - 1)), tags=etiqueta)

        region = lienzo.bbox("all")
        if region:
            lienzo.configure(scrollregion=(region[0] - 30, region[1] - 30, region[2] + 30, region[3] + 40))
        self._explicar(actual)

    def _explicar(self, actual):
        k = self.paso
        # La cola de prioridad en el paso k: raíces del bosque (nodos visibles sin padre visible).
        completo = k == len(self.pasos)
        cola = [n for n in self.nodos
                if (completo or n.es_hoja or n.paso <= k)
                and not (self.padres.get(n) and (completo or self.padres[n].paso <= k))]
        cola.sort(key=lambda n: n.frecuencia)
        muestra = "  ".join(self._nombre(n) for n in cola[:10]) + ("  …" if len(cola) > 10 else "")
        if actual:
            texto = (f"Paso {k}: se sacan de la cola los dos nodos de menor frecuencia, "
                     f"{self._nombre(actual.izquierdo)} → rama 0 y {self._nombre(actual.derecho)} → rama 1, "
                     f"y se forma un nodo de {actual.nuevo.frecuencia:,}. ")
        elif k == 0:
            texto = "Paso 0: cada símbolo es una hoja dentro de la cola de prioridad. "
        else:
            texto = ""
        texto += f"Cola ({len(cola)} nodos): {muestra}"
        if k == len(self.pasos):
            texto += "   ·   Árbol completo. Haz clic en una hoja para ver su código."
        self.explicacion.configure(text=texto)


# ------------------------------------------------------------------ app

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sypher · Compresor Huffman y árbol de expansión mínima")
        self.root.geometry("1360x880")
        self.root.minsize(1100, 720)
        self.root.configure(bg=C["base"])
        self.familia = configurar_estilo(root)

        self.original = None       # bytes del .txt cargado
        self.nombre = None         # nombre del .txt cargado
        self.analisis = None       # formato.Analisis
        self.resultado = None      # formato.Resultado
        self.inspeccion = None     # formato.ArchivoSypher abierto en el inspector
        self.nombre_sypher = None
        self.recuperado = None     # formato.Descompresion
        self.libros = []
        self.hechos = set()
        self.ocupado = False
        self.cola = queue.Queue()

        self._crear_encabezado()
        self.cuaderno = ttk.Notebook(self.root)
        self.cuaderno.pack(fill="both", expand=True)
        self._crear_pestana_entrada()
        self._crear_pestana_frecuencias()
        self._crear_pestana_arbol()
        self._crear_pestana_compresion()
        self._crear_pestana_inspector()
        self._crear_pestana_mst()
        self._crear_barra_estado()
        self._actualizar_flujo()
        self.root.after(60, self._revisar_cola)

    # ------------------------------------------------------------ estructura
    def _crear_encabezado(self):
        encabezado = ttk.Frame(self.root, padding=(18, 12, 18, 8))
        encabezado.pack(fill="x")
        izquierda = ttk.Frame(encabezado)
        izquierda.pack(side="left")
        ttk.Label(izquierda, text="Sypher · Compresor Huffman", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(izquierda, text="Técnica voraz: frecuencias → árbol → códigos → bits → archivo .sypher",
                  style="Sub.TLabel").pack(anchor="w")

        self.chips = []
        flujo = ttk.Frame(encabezado)
        flujo.pack(side="right")
        for i, nombre in enumerate(PASOS_FLUJO):
            if i:
                tk.Label(flujo, text="→", bg=C["base"], fg=C["tenue"]).pack(side="left", padx=2)
            chip = tk.Label(flujo, text=f"{i + 1}  {nombre}", padx=10, pady=5, font=(self.familia, 9, "bold"))
            chip.pack(side="left")
            self.chips.append(chip)

    def _crear_barra_estado(self):
        barra = ttk.Frame(self.root, style="Barra.TFrame", padding=(14, 5))
        barra.pack(fill="x", side="bottom")
        self.estado = ttk.Label(barra, text="Listo. Empieza en «1 · Texto de entrada».", style="Barra.TLabel")
        self.estado.pack(side="left")
        self.progreso = ttk.Progressbar(barra, mode="indeterminate", length=160)

    def _actualizar_flujo(self):
        ultimo = max(self.hechos, default=-1)
        siguiente = ultimo + 1 if ultimo + 1 < len(PASOS_FLUJO) else None
        for i, chip in enumerate(self.chips):
            if i in self.hechos:
                chip.configure(bg=C["verde"], fg=C["corteza"])
            elif i == siguiente:
                chip.configure(bg=C["azul"], fg=C["corteza"])
            else:
                chip.configure(bg=C["sup"], fg=C["tenue"])

    def _marcar(self, *pasos):
        self.hechos.update(pasos)
        self._actualizar_flujo()

    # --------------------------------------------------------- tareas largas
    def _en_segundo_plano(self, mensaje, funcion, al_terminar):
        if self.ocupado:
            messagebox.showinfo("Espera", "Hay una tarea en curso.")
            return
        self.ocupado = True
        self.estado.configure(text=mensaje)
        self.progreso.pack(side="right")
        self.progreso.start(12)

        def trabajo():
            try:
                self.cola.put((True, funcion(), al_terminar))
            except Exception as error:  # se muestra en la interfaz
                self.cola.put((False, error, al_terminar))

        threading.Thread(target=trabajo, daemon=True).start()

    def _revisar_cola(self):
        try:
            while True:
                exito, valor, al_terminar = self.cola.get_nowait()
                self.ocupado = False
                self.progreso.stop()
                self.progreso.pack_forget()
                if exito:
                    al_terminar(valor)
                else:
                    self.estado.configure(text=f"Error: {valor}")
                    messagebox.showerror("Error", str(valor))
        except queue.Empty:
            pass
        self.root.after(60, self._revisar_cola)

    # ------------------------------------------------- 1 · texto de entrada
    def _crear_pestana_entrada(self):
        pestana = ttk.Frame(self.cuaderno, padding=14)
        self.cuaderno.add(pestana, text="1 · Texto de entrada")
        pestana.columnconfigure(0, weight=2)
        pestana.columnconfigure(1, weight=3)
        pestana.rowconfigure(1, weight=1)

        local = tarjeta(pestana, "A) Archivo local",
                        "Carga cualquier .txt de tu equipo, o escribe un texto corto para comprobar a mano "
                        "las frecuencias y los códigos.")
        local.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        ttk.Button(local, text="📂  Abrir archivo .txt…", style="Acento.TButton",
                   command=self._abrir_txt).pack(anchor="w", pady=(0, 10))
        marco, self.texto_manual = texto_widget(local, alto=5, mono=True)
        marco.pack(fill="x")
        self.texto_manual.insert("1.0", TEXTO_EJEMPLO)
        ttk.Button(local, text="Usar este texto", command=self._usar_texto_manual).pack(anchor="w", pady=(8, 0))

        remoto = tarjeta(pestana, "B) Project Gutenberg",
                         "Busca por título, autor o palabras clave. Solo se descarga el libro elegido "
                         "(se guarda una copia en libros/).")
        remoto.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        fila = ttk.Frame(remoto, style="Tarjeta.TFrame")
        fila.pack(fill="x")
        self.consulta = ttk.Entry(fila)
        self.consulta.pack(side="left", fill="x", expand=True)
        self.consulta.insert(0, "Cervantes")
        self.consulta.bind("<Return>", lambda _e: self._buscar_libros())
        ttk.Button(fila, text="🔎  Buscar", command=self._buscar_libros).pack(side="left", padx=(8, 0))
        marco, self.tabla_libros = tabla(remoto, [
            ("id", "ID", 60, "e"), ("titulo", "Título", 330, "w"),
            ("autor", "Autor(es)", 200, "w"), ("idioma", "Idioma", 70, "center"),
        ], alto=6)
        marco.pack(fill="both", expand=True, pady=8)
        self.tabla_libros.bind("<Double-1>", lambda _e: self._descargar_libro())
        fila = ttk.Frame(remoto, style="Tarjeta.TFrame")
        fila.pack(fill="x")
        ttk.Button(fila, text="⬇  Descargar y usar", command=self._descargar_libro).pack(side="left")
        self.estado_busqueda = ttk.Label(fila, text="", style="TarjetaSub.TLabel")
        self.estado_busqueda.pack(side="left", padx=10)

        cargado = tarjeta(pestana, "Texto cargado")
        cargado.grid(row=1, column=0, columnspan=2, sticky="nsew")
        fila = ttk.Frame(cargado, style="Tarjeta.TFrame")
        fila.pack(fill="x", pady=(4, 8))
        self.info_texto = ttk.Label(fila, text="Ningún texto cargado todavía.", style="TarjetaSub.TLabel")
        self.info_texto.pack(side="left")
        self.boton_analizar = ttk.Button(fila, text="Analizar y construir Huffman  →", style="Acento.TButton",
                                         command=self._analizar, state="disabled")
        self.boton_analizar.pack(side="right")
        marco, self.vista_previa = texto_widget(cargado, alto=8)
        marco.pack(fill="both", expand=True)
        self.vista_previa.configure(state="disabled")

    def _abrir_txt(self):
        ruta = filedialog.askopenfilename(title="Elegir archivo de texto",
                                          filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if ruta:
            self._cargar_texto(Path(ruta).read_bytes(), Path(ruta).name, f"archivo local · {ruta}")

    def _usar_texto_manual(self):
        texto = self.texto_manual.get("1.0", "end-1c")
        if not texto:
            messagebox.showwarning("Texto vacío", "Escribe algo para comprimir.")
            return
        self._cargar_texto(texto.encode("utf-8"), "texto_manual.txt", "texto escrito a mano")

    def _buscar_libros(self):
        consulta = self.consulta.get().strip()
        if not consulta:
            return
        self.estado_busqueda.configure(text="Buscando…")
        self._en_segundo_plano(f"Buscando «{consulta}» en Project Gutenberg…",
                               lambda: gutenberg.buscar(consulta), self._mostrar_libros)

    def _mostrar_libros(self, respuesta):
        self.libros, fuente = respuesta
        llenar_tabla(self.tabla_libros, [(l.id, l.titulo, l.autores, l.idiomas or "—") for l in self.libros])
        texto = f"{len(self.libros)} resultados · fuente: {fuente}" if self.libros else "Sin resultados."
        self.estado_busqueda.configure(text=texto)
        self.estado.configure(text=texto)

    def _descargar_libro(self):
        seleccion = self.tabla_libros.selection()
        if not seleccion:
            messagebox.showinfo("Elige un libro", "Selecciona un libro de la lista.")
            return
        libro = self.libros[int(seleccion[0])]
        self._en_segundo_plano(f"Descargando «{libro.titulo}» (#{libro.id})…",
                               lambda: gutenberg.descargar(libro),
                               lambda r: self._cargar_texto(r[0], r[1].name,
                                                            f"Project Gutenberg #{libro.id} · {libro.titulo}"))

    def _cargar_texto(self, contenido, nombre, origen):
        self.original, self.nombre = contenido, nombre
        self.analisis = self.resultado = None
        texto, codificacion = formato.decodificar_texto(contenido)
        self.info_texto.configure(
            text=f"{nombre}   ·   {formato.formato_tamano(len(contenido))}   ·   {len(texto):,} caracteres   ·   "
                 f"{formato.CODIFICACIONES[codificacion].upper()}   ·   {origen}")
        vista = texto[:MAX_VISTA_PREVIA].replace("\r\n", "\n")
        if len(texto) > MAX_VISTA_PREVIA:
            vista += f"\n\n[… vista previa: {MAX_VISTA_PREVIA:,} de {len(texto):,} caracteres …]"
        poner_texto(self.vista_previa, vista)
        self.boton_analizar.configure(state="normal")
        self.boton_comprimir.configure(state="disabled")
        self.boton_guardar.configure(state="disabled")
        self.boton_a_inspector.configure(state="disabled")
        self.metricas_compresion.limpiar()
        self.hechos = {0}
        self._actualizar_flujo()
        self.estado.configure(text=f"Texto cargado: {nombre}. Siguiente: Analizar.")

    def _analizar(self):
        if self.original is None:
            return
        original = self.original
        self._en_segundo_plano("Contando frecuencias y construyendo el árbol…",
                               lambda: formato.analizar(original), self._mostrar_analisis)

    def _mostrar_analisis(self, analisis):
        self.analisis = analisis
        self._llenar_frecuencias(analisis)
        self.vista_arbol.mostrar(analisis.raiz, analisis.pasos)
        self.boton_comprimir.configure(state="normal")
        self._marcar(1, 2)
        t = analisis.tiempos
        self.estado.configure(text=f"Análisis listo: {len(analisis.frecuencias)} símbolos, "
                                   f"{len(analisis.pasos)} uniones voraces "
                                   f"(frecuencias {t['frecuencias'] * 1000:.1f} ms, árbol {t['arbol'] * 1000:.1f} ms).")
        self.cuaderno.select(1)

    # ----------------------------------------------- 2 · frecuencias y códigos
    def _crear_pestana_frecuencias(self):
        pestana = ttk.Frame(self.cuaderno, padding=14)
        self.cuaderno.add(pestana, text="2 · Frecuencias y códigos")
        self.metricas_frecuencias = Metricas(pestana, [
            "Caracteres", "Símbolos distintos", "Bits/símbolo Huffman", "Entropía (mínimo teórico)",
        ])
        self.metricas_frecuencias.pack(fill="x", pady=(0, 10))

        cuerpo = ttk.PanedWindow(pestana, orient="horizontal")
        cuerpo.pack(fill="both", expand=True)
        izquierda = tarjeta(cuerpo, "Tabla de frecuencias y códigos",
                            "Haz clic en un encabezado para ordenar. Al elegir un símbolo se marca su camino en el árbol.")
        marco, self.tabla_frecuencias = tabla(izquierda, [
            ("simbolo", "Símbolo", 70, "center"), ("unicode", "Unicode", 80, "center"),
            ("frecuencia", "Frecuencia", 95, "e"), ("porcentaje", "%", 70, "e"),
            ("codigo", "Código Huffman", 260, "w"), ("bits", "Bits", 50, "e"), ("total", "f × bits", 100, "e"),
        ], alto=18)
        marco.pack(fill="both", expand=True)
        self.tabla_frecuencias.bind("<<TreeviewSelect>>", self._simbolo_desde_tabla)
        cuerpo.add(izquierda, weight=3)

        derecha = tarjeta(cuerpo, "Distribución: más frecuente → código más corto")
        self.figura_frecuencias = figura_oscura(5.5, 4.5)
        self.lienzo_frecuencias = FigureCanvasTkAgg(self.figura_frecuencias, master=derecha)
        self.lienzo_frecuencias.get_tk_widget().pack(fill="both", expand=True)
        cuerpo.add(derecha, weight=2)

    def _llenar_frecuencias(self, analisis):
        frecuencias, codigos = analisis.frecuencias, analisis.codigos
        total = len(analisis.texto)
        orden = sorted(frecuencias, key=lambda s: (-frecuencias[s], ord(s)))
        self.simbolos_tabla = orden
        llenar_tabla(self.tabla_frecuencias, [
            (huffman.mostrar_simbolo(s), f"U+{ord(s):04X}", f"{frecuencias[s]:,}",
             f"{frecuencias[s] / total * 100:.3f}%", codigos[s], len(codigos[s]),
             f"{frecuencias[s] * len(codigos[s]):,}")
            for s in orden
        ])
        media = huffman.longitud_media(frecuencias, codigos)
        entropia = huffman.entropia(frecuencias)
        fija = max(1, (len(frecuencias) - 1).bit_length())
        self.metricas_frecuencias.poner("Caracteres", f"{total:,}", f"{len(self.original):,} bytes en disco")
        self.metricas_frecuencias.poner("Símbolos distintos", f"{len(frecuencias)}", f"código fijo: {fija} bits/símbolo")
        self.metricas_frecuencias.poner("Bits/símbolo Huffman", f"{media:.4f}",
                                        f"original: {len(self.original) * 8 / max(total, 1):.2f} bits/carácter")
        self.metricas_frecuencias.poner("Entropía (mínimo teórico)", f"{entropia:.4f}",
                                        f"Huffman queda a {media - entropia:.4f} bits del mínimo")

        figura = self.figura_frecuencias
        figura.clear()
        ax = figura.add_subplot(111)
        estilizar_ejes(ax)
        top = orden[:40]
        posiciones = range(len(top))
        ax.bar(posiciones, [frecuencias[s] for s in top], color=C["azul"], width=0.75)
        ax.set_xticks(list(posiciones), [huffman.mostrar_simbolo(s) for s in top], fontsize=8)
        ax.set_ylabel("frecuencia")
        ax2 = ax.twinx()
        ax2.step(list(posiciones), [len(codigos[s]) for s in top], where="mid", color=C["durazno"], linewidth=2)
        ax2.set_ylabel("longitud del código (bits)", color=C["durazno"])
        ax2.tick_params(colors=C["durazno"], labelsize=8)
        for lado in ax2.spines.values():
            lado.set_color(C["sup2"])
        titulo = "Los 40 símbolos más frecuentes" if len(orden) > 40 else "Todos los símbolos"
        ax.set_title(titulo, fontsize=10)
        figura.tight_layout()
        self.lienzo_frecuencias.draw_idle()

    def _simbolo_desde_tabla(self, _evento):
        seleccion = self.tabla_frecuencias.selection()
        if seleccion and self.analisis:
            fila = self.tabla_frecuencias.item(seleccion[0], "values")
            simbolo = chr(int(fila[1][2:], 16))
            self.vista_arbol.seleccionar_simbolo(simbolo)

    # ------------------------------------------------------- 3 · árbol
    def _crear_pestana_arbol(self):
        pestana = ttk.Frame(self.cuaderno, padding=(14, 10))
        self.cuaderno.add(pestana, text="3 · Árbol de Huffman")
        ttk.Label(pestana, text="Hojas = símbolos (cuadros) · nodos internos = suma de frecuencias (círculos) · "
                                "rama izquierda 0, rama derecha 1 · clic derecho y arrastrar para moverse",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 6))
        self.vista_arbol = VistaArbol(pestana, self.familia, al_seleccionar=self._simbolo_desde_arbol)
        self.vista_arbol.pack(fill="both", expand=True)

    def _simbolo_desde_arbol(self, simbolo):
        codigo = self.analisis.codigos.get(simbolo, "") if self.analisis else ""
        self.estado.configure(text=f"'{huffman.mostrar_simbolo(simbolo)}' → {codigo}  ({len(codigo)} bits)")

    # ---------------------------------------------------- 4 · compresión
    def _crear_pestana_compresion(self):
        pestana = ttk.Frame(self.cuaderno, padding=14)
        self.cuaderno.add(pestana, text="4 · Compresión")
        fila = ttk.Frame(pestana)
        fila.pack(fill="x", pady=(0, 10))
        self.boton_comprimir = ttk.Button(fila, text="🗜  Comprimir a .sypher", style="Acento.TButton",
                                          command=self._comprimir, state="disabled")
        self.boton_comprimir.pack(side="left")
        self.boton_guardar = ttk.Button(fila, text="💾  Guardar .sypher…", command=self._guardar_sypher, state="disabled")
        self.boton_guardar.pack(side="left", padx=8)
        self.boton_a_inspector = ttk.Button(fila, text="Abrir en el inspector  →", command=self._resultado_a_inspector,
                                            state="disabled")
        self.boton_a_inspector.pack(side="left")

        self.metricas_compresion = Metricas(pestana, [
            "Original", "Comprimido (.sypher)", "Ahorro", "Reducción",
            "Razón de compresión", "Símbolos distintos", "Bits codificados", "Cabecera + tabla",
        ])
        self.metricas_compresion.pack(fill="x")

        cuerpo = ttk.Frame(pestana)
        cuerpo.pack(fill="both", expand=True, pady=(10, 0))
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)
        grafica = tarjeta(cuerpo, "¿En qué se van los bytes?")
        grafica.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.figura_compresion = figura_oscura(6, 3.2)
        self.lienzo_compresion = FigureCanvasTkAgg(self.figura_compresion, master=grafica)
        self.lienzo_compresion.get_tk_widget().pack(fill="both", expand=True)
        detalle = tarjeta(cuerpo, "Detalle")
        detalle.grid(row=0, column=1, sticky="nsew")
        marco, self.texto_detalle = texto_widget(detalle, alto=12)
        marco.pack(fill="both", expand=True)
        poner_texto(self.texto_detalle, "Analiza un texto y presiona «Comprimir».")

    def _comprimir(self):
        if not self.analisis:
            return
        original, nombre, analisis = self.original, self.nombre, self.analisis
        self._en_segundo_plano("Codificando y empaquetando bits…",
                               lambda: formato.comprimir(original, nombre, analisis), self._mostrar_compresion)

    def _mostrar_compresion(self, resultado):
        self.resultado = resultado
        sypher = resultado.sypher
        original, comprimido = len(resultado.original), len(resultado.archivo)
        ahorro = original - comprimido
        reduccion = ahorro / original * 100 if original else 0
        m = self.metricas_compresion
        m.poner("Original", tamano_corto(original), f"{original:,} bytes")
        m.poner("Comprimido (.sypher)", tamano_corto(comprimido), f"{comprimido:,} bytes")
        m.poner("Ahorro", tamano_corto(abs(ahorro)) if ahorro >= 0 else "−" + tamano_corto(-ahorro),
                f"{ahorro:,} bytes")
        m.poner("Reducción", f"{reduccion:.2f} %", "positivo = el archivo se hizo más chico",
                "Bien.TLabel" if reduccion > 0 else "Mal.TLabel")
        m.poner("Razón de compresión", f"{original / comprimido:.3f} : 1" if comprimido else "—", "original / comprimido")
        m.poner("Símbolos distintos", f"{len(sypher.frecuencias)}", f"{len(resultado.analisis.pasos)} uniones voraces")
        m.poner("Bits codificados", f"{sypher.bits_validos:,}", f"+ {sypher.relleno} bits de relleno")
        m.poner("Cabecera + tabla", f"{sypher.tamano_cabecera:,} B", f"{len(sypher.datos):,} B de datos")

        figura = self.figura_compresion
        figura.clear()
        ax = figura.add_subplot(111)
        estilizar_ejes(ax)
        fijo_bits = max(1, (len(sypher.frecuencias) - 1).bit_length())
        fijo = sypher.caracteres * fijo_bits / 8
        tabla_bytes = len(sypher.frecuencias) * 8 + 4
        cabecera = sypher.tamano_cabecera - tabla_bytes
        # y = 0 abajo: Huffman, código fijo y original de abajo hacia arriba.
        ax.barh(2, original, color=C["sup2"], label="texto original")
        ax.barh(1, fijo, color=C["malva"], label="código fijo (teórico)")
        ax.barh(0, cabecera, color=C["durazno"], label="cabecera")
        ax.barh(0, tabla_bytes, left=cabecera, color=C["amarillo"], label="tabla de frecuencias")
        ax.barh(0, len(sypher.datos), left=cabecera + tabla_bytes, color=C["verde"], label="datos Huffman")
        ax.set_yticks([0, 1, 2], ["Huffman (.sypher)", f"Código fijo ({fijo_bits} bits)", "Original"])
        for y, valor in enumerate([comprimido, fijo, original]):
            ax.text(valor, y, f"  {tamano_corto(int(valor))}", va="center", color=C["texto"], fontsize=9)
        ax.set_xlim(0, original * 1.2 if original else 1)
        ax.xaxis.set_major_formatter(lambda x, _pos: tamano_corto(int(x)) if x else "0")
        leyenda = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8,
                            facecolor=C["sup"], edgecolor=C["sup2"])
        for t in leyenda.get_texts():
            t.set_color(C["texto"])
        figura.tight_layout()
        self.lienzo_compresion.draw_idle()

        t = resultado.tiempos
        a = resultado.analisis
        poner_texto(self.texto_detalle, "\n".join([
            f"Archivo:            {self.nombre} → {Path(self.nombre).stem}{formato.EXTENSION}",
            f"Codificación:       {sypher.codificacion}",
            f"Caracteres:         {sypher.caracteres:,}",
            f"Bits por carácter:  {original * 8 / max(sypher.caracteres, 1):.3f} → "
            f"{huffman.longitud_media(a.frecuencias, a.codigos):.3f}",
            f"Entropía:           {huffman.entropia(a.frecuencias):.3f} bits/símbolo",
            f"Bits de datos:      {sypher.bits_validos:,} (+{sypher.relleno} de relleno)",
            f"SHA-256 original:   {sypher.sha256.hex()[:32]}…",
            "",
            "Tiempos",
            f"  frecuencias:      {t['frecuencias'] * 1000:9.2f} ms   O(n)",
            f"  árbol + códigos:  {t['arbol'] * 1000:9.2f} ms   O(k log k)",
            f"  codificar:        {t['codificar'] * 1000:9.2f} ms   O(n)",
        ]))
        self.boton_guardar.configure(state="normal")
        self.boton_a_inspector.configure(state="normal")
        self._marcar(3)
        self.estado.configure(text=f"Comprimido: {tamano_corto(original)} → {tamano_corto(comprimido)} "
                                   f"({reduccion:.2f} % de reducción).")

    def _guardar_sypher(self):
        if not self.resultado:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar archivo comprimido", defaultextension=formato.EXTENSION,
            initialfile=Path(self.nombre).stem + formato.EXTENSION,
            filetypes=[("Archivo Sypher", "*" + formato.EXTENSION)])
        if ruta:
            Path(ruta).write_bytes(self.resultado.archivo)
            self.nombre_sypher = Path(ruta).name
            self.estado.configure(text=f"Guardado: {ruta} ({len(self.resultado.archivo):,} bytes)")

    def _resultado_a_inspector(self):
        if self.resultado:
            nombre = self.nombre_sypher or Path(self.nombre).stem + formato.EXTENSION
            self._mostrar_inspeccion(self.resultado.archivo, nombre, self.resultado.sypher)
            self.cuaderno.select(4)

    # ------------------------------------------------------- 5 · inspector
    def _crear_pestana_inspector(self):
        pestana = ttk.Frame(self.cuaderno, padding=14)
        self.cuaderno.add(pestana, text="5 · Inspector .sypher")
        fila = ttk.Frame(pestana)
        fila.pack(fill="x", pady=(0, 10))
        ttk.Button(fila, text="📂  Abrir archivo .sypher…", style="Acento.TButton",
                   command=self._abrir_sypher).pack(side="left")
        self.info_inspector = ttk.Label(fila, text="  Solo se necesita el .sypher: el .txt original no hace falta.",
                                        style="Sub.TLabel")
        self.info_inspector.pack(side="left", padx=8)

        self.metricas_inspector = Metricas(pestana, [
            "Archivo", "Formato", "Tamaño original", "Tamaño comprimido",
            "Ahorro", "Compresión", "Símbolos", "Bits codificados",
        ])
        self.metricas_inspector.pack(fill="x", pady=(0, 8))

        self.sub = ttk.Notebook(pestana, style="Interno.TNotebook")
        self.sub.pack(fill="both", expand=True)

        estructura = ttk.Frame(self.sub, padding=8)
        self.sub.add(estructura, text="Estructura del archivo")
        marco, self.tabla_secciones = tabla(estructura, [
            ("seccion", "Sección", 180, "w"), ("inicio", "Offset", 80, "e"),
            ("tamano", "Bytes", 90, "e"), ("valor", "Valor", 600, "w"),
        ], alto=14)
        marco.pack(fill="both", expand=True)

        codigos = ttk.Frame(self.sub, padding=8)
        self.sub.add(codigos, text="Frecuencias y códigos")
        marco, self.tabla_inspector = tabla(codigos, [
            ("simbolo", "Símbolo", 80, "center"), ("unicode", "Unicode", 90, "center"),
            ("frecuencia", "Frecuencia", 110, "e"), ("codigo", "Código reconstruido", 260, "w"),
            ("bits", "Bits", 60, "e"),
        ], alto=14)
        marco.pack(fill="both", expand=True)

        arbol = ttk.Frame(self.sub, padding=8)
        self.sub.add(arbol, text="Árbol reconstruido")
        self.arbol_inspector = VistaArbol(arbol, self.familia)
        self.arbol_inspector.pack(fill="both", expand=True)

        binario = ttk.Frame(self.sub, padding=8)
        self.sub.add(binario, text="Datos binarios")
        marco, self.texto_binario = texto_widget(binario, alto=20, wrap="none")
        marco.pack(fill="both", expand=True)
        for etiqueta, color in (("cabecera", C["durazno"]), ("nombre", C["malva"]), ("tabla", C["amarillo"]),
                                ("datos", C["verde"]), ("relleno", C["rojo"]), ("titulo", C["azul"]),
                                ("tenue", C["tenue"]), ("cod0", C["verde"]), ("cod1", C["turquesa"])):
            self.texto_binario.tag_configure(etiqueta, foreground=color)
        self.texto_binario.tag_configure("titulo", font=(self.familia, 11, "bold"))

        descompresion = ttk.Frame(self.sub, padding=8)
        self.sub.add(descompresion, text="Descomprimir y verificar")
        fila = ttk.Frame(descompresion)
        fila.pack(fill="x", pady=(0, 8))
        self.boton_descomprimir = ttk.Button(fila, text="⚡  DESCOMPRIMIR", style="Acento.TButton",
                                             command=self._descomprimir, state="disabled")
        self.boton_descomprimir.pack(side="left")
        self.boton_guardar_txt = ttk.Button(fila, text="💾  Guardar .txt recuperado…",
                                            command=self._guardar_txt, state="disabled")
        self.boton_guardar_txt.pack(side="left", padx=8)
        self.metricas_integridad = Metricas(descompresion, [
            "Integridad (SHA-256)", "Comparación byte a byte", "Tamaño recuperado", "Tiempo",
        ])
        self.metricas_integridad.pack(fill="x")
        self.hashes = ttk.Label(descompresion, text="", style="Sub.TLabel", font="TkFixedFont", padding=(4, 6))
        self.hashes.pack(fill="x")
        marco, self.texto_recuperado = texto_widget(descompresion, alto=10)
        marco.pack(fill="both", expand=True)
        self.texto_recuperado.configure(state="disabled")

    def _abrir_sypher(self):
        ruta = filedialog.askopenfilename(title="Abrir archivo comprimido",
                                          filetypes=[("Archivo Sypher", "*" + formato.EXTENSION), ("Todos", "*.*")])
        if not ruta:
            return
        contenido = Path(ruta).read_bytes()
        self._en_segundo_plano("Leyendo cabecera y reconstruyendo el árbol…", lambda: formato.leer(contenido),
                               lambda sypher: self._mostrar_inspeccion(contenido, Path(ruta).name, sypher))

    def _mostrar_inspeccion(self, archivo, nombre, sypher):
        self.inspeccion, self.nombre_sypher, self.archivo_inspeccion = sypher, nombre, archivo
        self.recuperado = None
        original, comprimido = sypher.tamano_original, sypher.tamano_archivo
        ahorro = original - comprimido
        m = self.metricas_inspector
        m.poner("Archivo", Path(nombre).stem[:18], f"extensión {Path(nombre).suffix or '(ninguna)'}")
        m.poner("Formato", f"Sypher v{sypher.version}", f"texto {sypher.codificacion}")
        m.poner("Tamaño original", tamano_corto(original), f"{original:,} bytes")
        m.poner("Tamaño comprimido", tamano_corto(comprimido), f"{comprimido:,} bytes")
        m.poner("Ahorro", tamano_corto(abs(ahorro)) if ahorro >= 0 else "−" + tamano_corto(-ahorro), f"{ahorro:,} bytes")
        m.poner("Compresión", f"{ahorro / original * 100:.2f} %" if original else "—",
                f"razón {original / comprimido:.3f} : 1" if comprimido else "")
        m.poner("Símbolos", f"{len(sypher.frecuencias)}", f"{sypher.caracteres:,} caracteres")
        m.poner("Bits codificados", f"{sypher.bits_validos:,}", f"+ {sypher.relleno} de relleno")
        self.info_inspector.configure(text=f"  {nombre}  ·  original: {sypher.nombre_original}")

        llenar_tabla(self.tabla_secciones, [(s.nombre, f"{s.inicio:,}", f"{s.tamano:,}", s.valor)
                                            for s in sypher.secciones])
        orden = sorted(sypher.frecuencias, key=lambda s: (-sypher.frecuencias[s], ord(s)))
        llenar_tabla(self.tabla_inspector, [
            (huffman.mostrar_simbolo(s), f"U+{ord(s):04X}", f"{sypher.frecuencias[s]:,}", sypher.codigos[s],
             len(sypher.codigos[s])) for s in orden
        ])
        self.arbol_inspector.mostrar(sypher.raiz, sypher.pasos)
        self._llenar_binario(archivo, sypher)

        poner_texto(self.texto_recuperado, "Presiona «DESCOMPRIMIR» para reconstruir el texto a partir del árbol y los bits.")
        self.metricas_integridad.limpiar()
        self.hashes.configure(text=f"SHA-256 guardado en la cabecera: {sypher.sha256.hex()}")
        self.boton_descomprimir.configure(state="normal")
        self.boton_guardar_txt.configure(state="disabled")
        self.hechos.discard(5)
        self._marcar(4)
        self.sub.select(0)
        self.estado.configure(text=f"Inspeccionando {nombre}: {len(sypher.secciones)} secciones, "
                                   f"{len(sypher.frecuencias)} símbolos.")

    def _llenar_binario(self, archivo, sypher):
        t = self.texto_binario
        t.configure(state="normal")
        t.delete("1.0", "end")

        inicio_nombre = next(s.inicio for s in sypher.secciones if s.nombre == "Nombre original")
        inicio_tabla = next(s.inicio for s in sypher.secciones if s.nombre == "Número de símbolos")
        inicio_datos = sypher.tamano_cabecera

        def seccion(pos):
            if pos < inicio_nombre:
                return "cabecera"
            if pos < inicio_tabla:
                return "nombre"
            if pos < inicio_datos:
                return "tabla"
            return "datos"

        t.insert("end", "Volcado hexadecimal del archivo", "titulo")
        t.insert("end", "   ")
        for nombre, etiqueta in (("cabecera", "cabecera"), ("nombre", "nombre"), ("tabla", "tabla"), ("datos", "datos")):
            t.insert("end", "■ ", etiqueta)
            t.insert("end", nombre + "   ", "tenue")
        t.insert("end", "\n\n")

        # Primeras líneas del archivo y las primeras líneas de los datos.
        rangos = [(0, min(len(archivo), inicio_datos + 64, 384))]
        if inicio_datos + 64 < len(archivo) and inicio_datos > 384:
            rangos.append((inicio_datos - inicio_datos % 16, min(len(archivo), inicio_datos - inicio_datos % 16 + 128)))
        for n, (desde, hasta) in enumerate(rangos):
            if n:
                t.insert("end", "   ⋮\n", "tenue")
            for linea in range(desde, hasta, 16):
                t.insert("end", f"{linea:08X}  ", "tenue")
                fragmento = archivo[linea:min(linea + 16, hasta)]
                for i, byte in enumerate(fragmento):
                    t.insert("end", f"{byte:02X} " + (" " if i == 7 else ""), seccion(linea + i))
                t.insert("end", "   " * (16 - len(fragmento)) + (" " if len(fragmento) <= 8 else ""))
                t.insert("end", " |", "tenue")
                for i, byte in enumerate(fragmento):
                    t.insert("end", chr(byte) if 32 <= byte < 127 else "·", seccion(linea + i))
                t.insert("end", "|\n", "tenue")
        t.insert("end", f"   … {len(archivo):,} bytes en total\n\n", "tenue")

        t.insert("end", "Primeros bits de los datos, separados por código Huffman\n", "titulo")
        t.insert("end", "Cada grupo de bits es un recorrido de la raíz a una hoja; debajo, el símbolo al que llega.\n\n", "tenue")
        bits = huffman.bytes_a_bits(sypher.datos[:40], min(sypher.bits_validos, 320))
        grupos, nodo, actual = [], sypher.raiz, ""
        for bit in bits:
            if nodo is None:
                break
            nodo = nodo.derecho if bit == "1" else nodo.izquierdo
            actual += bit
            if nodo is not None and nodo.es_hoja:
                grupos.append((actual, huffman.mostrar_simbolo(nodo.simbolo)))
                nodo, actual = sypher.raiz, ""
        linea_bits, linea_simbolos, ancho = [], [], 0
        for i, (codigo, simbolo) in enumerate(grupos):
            celda = max(len(codigo), len(simbolo)) + 2
            if ancho + celda > 96:
                self._insertar_grupos(t, linea_bits, linea_simbolos)
                linea_bits, linea_simbolos, ancho = [], [], 0
            linea_bits.append((codigo.ljust(celda), f"cod{i % 2}"))
            linea_simbolos.append(simbolo.ljust(celda))
            ancho += celda
        self._insertar_grupos(t, linea_bits, linea_simbolos)

        t.insert("end", "\nÚltimo byte de los datos y bits de relleno\n", "titulo")
        if sypher.datos:
            ultimo = f"{sypher.datos[-1]:08b}"
            validos = 8 - sypher.relleno
            t.insert("end", f"byte {len(sypher.datos) - 1:,}:  ")
            t.insert("end", ultimo[:validos], "datos")
            t.insert("end", ultimo[validos:], "relleno")
            t.insert("end", f"   → {validos} bits válidos y {sypher.relleno} de relleno (en rojo) que el descompresor ignora\n", "tenue")
        else:
            t.insert("end", "(sin datos: el texto original estaba vacío)\n", "tenue")
        t.configure(state="disabled")

    @staticmethod
    def _insertar_grupos(t, linea_bits, linea_simbolos):
        if not linea_bits:
            return
        for texto, etiqueta in linea_bits:
            t.insert("end", texto, etiqueta)
        t.insert("end", "\n" + "".join(linea_simbolos) + "\n\n", "tenue")

    def _descomprimir(self):
        if not self.inspeccion:
            return
        sypher = self.inspeccion
        self._en_segundo_plano("Recorriendo el árbol bit por bit…", lambda: formato.descomprimir(sypher),
                               self._mostrar_descompresion)

    def _mostrar_descompresion(self, recuperado):
        self.recuperado = recuperado
        sypher = self.inspeccion
        m = self.metricas_integridad
        if recuperado.integro:
            m.poner("Integridad (SHA-256)", "✔ Íntegro", "el hash coincide con la cabecera", "Bien.TLabel")
        else:
            m.poner("Integridad (SHA-256)", "✘ No coincide", "el archivo está dañado", "Mal.TLabel")
        if self.original is not None and self.nombre == sypher.nombre_original:
            diferencia = formato.comparar_bytes(self.original, recuperado.contenido)
            if diferencia is None:
                m.poner("Comparación byte a byte", "✔ Idénticos", f"contra {self.nombre} cargado", "Bien.TLabel")
            else:
                m.poner("Comparación byte a byte", "✘ Distintos", f"primer byte distinto: {diferencia:,}", "Mal.TLabel")
        else:
            m.poner("Comparación byte a byte", "—", "carga el .txt original en la pestaña 1 para comparar")
        m.poner("Tamaño recuperado", tamano_corto(len(recuperado.contenido)), f"{len(recuperado.contenido):,} bytes")
        m.poner("Tiempo", f"{recuperado.segundos * 1000:.0f} ms", "decodificación O(bits)")
        self.hashes.configure(text=f"SHA-256 guardado:    {sypher.sha256.hex()}\n"
                                   f"SHA-256 recuperado:  {recuperado.sha256}")
        vista = recuperado.texto[:MAX_VISTA_PREVIA * 5]
        if len(recuperado.texto) > len(vista):
            vista += f"\n\n[… se muestran {MAX_VISTA_PREVIA * 5:,} de {len(recuperado.texto):,} caracteres; guarda el .txt para verlo completo …]"
        poner_texto(self.texto_recuperado, vista.replace("\r\n", "\n"))
        self.boton_guardar_txt.configure(state="normal")
        self._marcar(5)
        self.estado.configure(text="Descompresión " + ("correcta: el contenido es idéntico al original."
                                                       if recuperado.integro else "con errores de integridad."))

    def _guardar_txt(self):
        if not self.recuperado:
            return
        nombre = Path(self.inspeccion.nombre_original or "recuperado.txt")
        ruta = filedialog.asksaveasfilename(title="Guardar texto recuperado", defaultextension=".txt",
                                            initialfile=f"{nombre.stem}_recuperado.txt",
                                            filetypes=[("Texto", "*.txt")])
        if ruta:
            Path(ruta).write_bytes(self.recuperado.contenido)
            self.estado.configure(text=f"Guardado: {ruta}")

    # --------------------------------------------- 6 · expansión mínima
    def _crear_pestana_mst(self):
        pestana = ttk.Frame(self.cuaderno, padding=14)
        self.cuaderno.add(pestana, text="6 · Expansión mínima")
        pestana.columnconfigure(1, weight=1)
        pestana.rowconfigure(0, weight=1)

        panel = tarjeta(pestana, "Árbol de expansión mínima",
                        "Otro algoritmo voraz: en cada paso se elige la arista más barata que no forme ciclo.")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.configure(width=360)

        fila = ttk.Frame(panel, style="Tarjeta.TFrame")
        fila.pack(fill="x")
        ttk.Label(fila, text="Nodos", style="Tarjeta.TLabel").pack(side="left")
        self.mst_nodos = ttk.Spinbox(fila, from_=3, to=26, width=4)
        self.mst_nodos.set(10)
        self.mst_nodos.pack(side="left", padx=(4, 10))
        ttk.Label(fila, text="Vecinos", style="Tarjeta.TLabel").pack(side="left")
        self.mst_vecinos = ttk.Spinbox(fila, from_=1, to=6, width=3)
        self.mst_vecinos.set(3)
        self.mst_vecinos.pack(side="left", padx=(4, 10))
        ttk.Label(fila, text="Semilla", style="Tarjeta.TLabel").pack(side="left")
        self.mst_semilla = ttk.Entry(fila, width=6)
        self.mst_semilla.insert(0, "7")
        self.mst_semilla.pack(side="left", padx=4)
        fila = ttk.Frame(panel, style="Tarjeta.TFrame")
        fila.pack(fill="x", pady=8)
        ttk.Button(fila, text="🎲 Grafo aleatorio", command=self._mst_aleatorio).pack(side="left")
        ttk.Button(fila, text="Ejemplo clásico", command=self._mst_ejemplo).pack(side="left", padx=6)

        ttk.Label(panel, text="Aristas (origen destino peso), editables:", style="TarjetaSub.TLabel").pack(anchor="w")
        marco, self.mst_texto = texto_widget(panel, alto=9)
        marco.pack(fill="x", pady=(2, 8))
        self.mst_texto.configure(width=34)

        fila = ttk.Frame(panel, style="Tarjeta.TFrame")
        fila.pack(fill="x")
        self.mst_algoritmo = tk.StringVar(value="Kruskal")
        ttk.Radiobutton(fila, text="Kruskal", value="Kruskal", variable=self.mst_algoritmo).pack(side="left")
        ttk.Radiobutton(fila, text="Prim desde", value="Prim", variable=self.mst_algoritmo).pack(side="left", padx=(10, 2))
        self.mst_inicio = ttk.Combobox(fila, width=5, state="readonly")
        self.mst_inicio.pack(side="left")
        ttk.Button(fila, text="Ejecutar", style="Acento.TButton", command=self._mst_ejecutar).pack(side="right")

        fila = ttk.Frame(panel, style="Tarjeta.TFrame")
        fila.pack(fill="x", pady=(10, 4))
        ttk.Button(fila, text="⏮", width=3, style="Chico.TButton", command=lambda: self._mst_ir(0)).pack(side="left")
        ttk.Button(fila, text="◀", width=3, style="Chico.TButton", command=lambda: self._mst_ir(self.mst_paso - 1)).pack(side="left", padx=2)
        self.mst_boton_play = ttk.Button(fila, text="▶", width=3, style="Chico.TButton", command=self._mst_reproducir)
        self.mst_boton_play.pack(side="left", padx=2)
        ttk.Button(fila, text="▶|", width=3, style="Chico.TButton", command=lambda: self._mst_ir(self.mst_paso + 1)).pack(side="left", padx=2)
        ttk.Button(fila, text="⏭", width=3, style="Chico.TButton", command=lambda: self._mst_ir(len(self.mst_pasos))).pack(side="left")
        self.mst_etiqueta_paso = ttk.Label(fila, text="", style="TarjetaSub.TLabel")
        self.mst_etiqueta_paso.pack(side="left", padx=8)

        marco = ttk.Frame(panel)
        marco.pack(fill="both", expand=True)
        self.mst_lista = tk.Listbox(marco, bg=C["manto"], fg=C["texto"], selectbackground=C["durazno"],
                                    selectforeground=C["corteza"], relief="flat", highlightthickness=0,
                                    font="TkFixedFont", activestyle="none", height=8)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.mst_lista.yview)
        self.mst_lista.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.mst_lista.pack(side="left", fill="both", expand=True)
        self.mst_lista.bind("<<ListboxSelect>>", self._mst_elegir_lista)
        self.mst_resultado = ttk.Label(panel, text="", style="Tarjeta.TLabel", wraplength=330, justify="left")
        self.mst_resultado.pack(anchor="w", pady=(8, 0))

        lienzo = tarjeta(pestana)
        lienzo.grid(row=0, column=1, sticky="nsew")
        self.mst_figura = figura_oscura(7, 6)
        self.mst_lienzo = FigureCanvasTkAgg(self.mst_figura, master=lienzo)
        self.mst_lienzo.get_tk_widget().pack(fill="both", expand=True)

        self.mst_nombres, self.mst_aristas, self.mst_posiciones = [], [], {}
        self.mst_arbol, self.mst_pasos, self.mst_paso, self.mst_animacion = [], [], 0, None
        self._mst_ejemplo()

    def _mst_poner_grafo(self, texto, posiciones):
        poner_texto(self.mst_texto, texto, solo_lectura=False)
        self.mst_posiciones = posiciones
        self._mst_ejecutar()

    def _mst_ejemplo(self):
        self._mst_poner_grafo(GRAFO_EJEMPLO, POSICIONES_EJEMPLO)

    def _mst_aleatorio(self):
        try:
            n = int(self.mst_nodos.get())
            vecinos = int(self.mst_vecinos.get())
        except ValueError:
            messagebox.showwarning("Valores inválidos", "Nodos y vecinos deben ser enteros.")
            return
        semilla = self.mst_semilla.get().strip() or None
        nombres, aristas, posiciones = mst.generar_grafo(max(3, min(n, 26)), max(1, vecinos), semilla)
        self._mst_poner_grafo(mst.grafo_a_texto(aristas), posiciones)

    def _mst_ejecutar(self):
        self._mst_detener()
        try:
            nombres, aristas = mst.leer_grafo(self.mst_texto.get("1.0", "end"))
        except ValueError as error:
            messagebox.showerror("Grafo inválido", str(error))
            return
        if not aristas:
            messagebox.showwarning("Grafo vacío", "Escribe al menos una arista.")
            return
        if not all(n in self.mst_posiciones for n in nombres):
            self.mst_posiciones = mst.posiciones_circulares(nombres)
        self.mst_nombres, self.mst_aristas = nombres, aristas
        self.mst_inicio.configure(values=nombres)
        if self.mst_inicio.get() not in nombres:
            self.mst_inicio.set(nombres[0])

        if self.mst_algoritmo.get() == "Kruskal":
            self.mst_arbol, self.mst_pasos = mst.kruskal(nombres, aristas)
        else:
            self.mst_arbol, self.mst_pasos = mst.prim(nombres, aristas, self.mst_inicio.get())
        otro = (mst.prim(nombres, aristas)[0] if self.mst_algoritmo.get() == "Kruskal" else mst.kruskal(nombres, aristas)[0])
        nombre_otro = "Prim" if self.mst_algoritmo.get() == "Kruskal" else "Kruskal"

        self.mst_lista.delete(0, "end")
        for p in self.mst_pasos:
            self.mst_lista.insert("end", f"{p.numero:>2}. {'✔' if p.aceptada else '✘'} {p.arista}  {p.motivo}")
            self.mst_lista.itemconfigure("end", foreground=C["verde"] if p.aceptada else C["rojo"])
        conexo = mst.es_conexo(nombres, aristas)
        total = mst.peso_total(self.mst_arbol)
        self.mst_resultado.configure(text=(
            f"{self.mst_algoritmo.get()}: peso total {total:g} con {len(self.mst_arbol)} aristas "
            f"({len(nombres)} nodos, {len(aristas)} aristas en el grafo).\n"
            f"{nombre_otro} obtiene {mst.peso_total(otro):g}"
            f"{' ✔ mismo peso' if abs(mst.peso_total(otro) - total) < 1e-9 else ''}."
            + ("" if conexo else "\n⚠ El grafo no es conexo: se obtiene un bosque.")
        ))
        self._mst_ir(len(self.mst_pasos))

    def _mst_ir(self, paso):
        self.mst_paso = max(0, min(len(self.mst_pasos), int(paso)))
        self.mst_lista.selection_clear(0, "end")
        if self.mst_paso:
            self.mst_lista.selection_set(self.mst_paso - 1)
            self.mst_lista.see(self.mst_paso - 1)
        self.mst_etiqueta_paso.configure(text=f"paso {self.mst_paso} de {len(self.mst_pasos)}")
        self._mst_dibujar()

    def _mst_elegir_lista(self, _evento):
        seleccion = self.mst_lista.curselection()
        if seleccion and seleccion[0] + 1 != self.mst_paso:
            self._mst_detener()
            self._mst_ir(seleccion[0] + 1)

    def _mst_reproducir(self):
        if self.mst_animacion:
            self._mst_detener()
            return
        if self.mst_paso >= len(self.mst_pasos):
            self._mst_ir(0)
        self.mst_boton_play.configure(text="⏸")
        self._mst_avanzar()

    def _mst_avanzar(self):
        if self.mst_paso >= len(self.mst_pasos):
            self._mst_detener()
            return
        self._mst_ir(self.mst_paso + 1)
        self.mst_animacion = self.root.after(650, self._mst_avanzar)

    def _mst_detener(self):
        if self.mst_animacion:
            self.root.after_cancel(self.mst_animacion)
            self.mst_animacion = None
        self.mst_boton_play.configure(text="▶")

    def _mst_dibujar(self):
        figura = self.mst_figura
        figura.clear()
        ax = figura.add_subplot(111)
        ax.set_facecolor(C["manto"])
        ax.set_axis_off()
        pos = self.mst_posiciones
        hechos = self.mst_pasos[:self.mst_paso]
        aceptadas = {p.arista for p in hechos if p.aceptada}
        actual = hechos[-1] if hechos else None
        en_arbol = set()
        for a in aceptadas:
            en_arbol.update((a.u, a.v))
        if self.mst_algoritmo.get() == "Prim" and self.mst_nombres:
            en_arbol.add(self.mst_inicio.get())

        for a in self.mst_aristas:
            (x1, y1), (x2, y2) = pos[a.u], pos[a.v]
            if actual and a == actual.arista:
                color, ancho, estilo = (C["durazno"], 4, "-") if actual.aceptada else (C["rojo"], 3, "--")
            elif a in aceptadas:
                color, ancho, estilo = C["verde"], 3.5, "-"
            else:
                color, ancho, estilo = C["sup2"], 1.2, "-"
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=ancho, linestyle=estilo, zorder=1)
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{a.peso:g}", color=C["texto"], fontsize=8, ha="center",
                    va="center", zorder=3, bbox=dict(boxstyle="round,pad=0.2", fc=C["base"], ec=color, lw=0.8))
        for n in self.mst_nombres:
            x, y = pos[n]
            ax.scatter([x], [y], s=520, color=C["verde"] if n in en_arbol else C["azul"],
                       edgecolors=C["corteza"], linewidths=1.5, zorder=4)
            ax.text(x, y, n, color=C["corteza"], fontsize=10, fontweight="bold", ha="center", va="center", zorder=5)

        peso = sum(a.peso for a in aceptadas)
        if actual:
            titulo = (f"{self.mst_algoritmo.get()} · paso {self.mst_paso}: "
                      f"{'acepta' if actual.aceptada else 'descarta'} {actual.arista} — {actual.motivo} · "
                      f"peso acumulado {peso:g}")
        else:
            titulo = f"{self.mst_algoritmo.get()} · paso 0: ninguna arista elegida"
        ax.set_title(titulo, color=C["texto"], fontsize=10)
        ax.margins(0.08)
        ax.set_aspect("equal", adjustable="datalim")
        figura.tight_layout()
        self.mst_lienzo.draw_idle()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
