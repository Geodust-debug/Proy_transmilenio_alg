"""Componentes interactivos del front (Parte E): el mapa de la red y el recorrido editable.

Son "componentes v2" de Streamlit: un poco de HTML, CSS y JavaScript (en la
carpeta visual/componentes/) que se dibujan con datos que arma Python y que
le avisan a Python cuando el usuario hace clic. Asi el JavaScript solo dibuja
y reacciona al mouse; todas las reglas (que estacion esta cerrada, que rutas
pasan, si se puede agregar una parada) siguen saliendo del motor.
"""
from pathlib import Path

import streamlit as st

from . import dibujos

_CARPETA = Path(__file__).resolve().parent / "componentes"


def _leer(nombre):
    return (_CARPETA / nombre).read_text(encoding="utf-8")


_mapa = st.components.v2.component(
    "tm_mapa_red",
    html='<div class="mapa"></div>',
    css=_leer("mapa_red.css"),
    js=_leer("mapa_red.js"),
)
_linea = st.components.v2.component(
    "tm_linea_editable",
    html='<div class="linea"></div>',
    css=_leer("linea_editable.css"),
    js=_leer("linea_editable.js"),
)


# ---------------------------------------------------------------- mapa de la red
def datos_mapa(red, posiciones, nombres_rutas, origen=None, destino=None, tramos=()):
    """Arma lo que necesita el mapa a partir del estado ACTUAL de la red.

    posiciones: {estacion: (x, y)}.  tramos: lo que devuelve red.viaje().
    """
    nombres = sorted(posiciones)
    indice = {n: i for i, n in enumerate(nombres)}
    rutas_por = {n: [] for n in nombres}
    aristas = set()
    colores = []
    for k, ruta in enumerate(nombres_rutas):
        fondo, texto = dibujos.color_ruta(ruta)
        colores.append([ruta, fondo, texto])
        paradas = red.recorrido(ruta)
        for p in paradas:
            if p in rutas_por:
                rutas_por[p].append(k)
        for a, b in zip(paradas, paradas[1:]):
            if a in indice and b in indice and a != b:
                aristas.add((min(indice[a], indice[b]), max(indice[a], indice[b])))

    viaje = []
    for ruta, sube, baja in tramos or ():
        paradas = red.recorrido(ruta)
        i = j = 0
        for pos, nombre in enumerate(paradas):
            if nombre == sube:
                i = pos
            if nombre == baja:
                j = pos
        fondo, _ = dibujos.color_ruta(ruta)
        if viaje and viaje[-1]["color"] == fondo:
            fondo = dibujos.GRAFITO
        viaje.append({"color": fondo,
                      "paradas": [indice[p] for p in paradas[i:j + 1] if p in indice]})

    return {
        "ancho": 1000, "alto": 700,
        "estaciones": [{"n": n, "x": posiciones[n][0], "y": posiciones[n][1],
                        "r": rutas_por[n], "c": red.estado(n) == "CERRADA"} for n in nombres],
        "rutas": colores,
        "aristas": sorted(list(a) for a in aristas),
        "viaje": viaje,
        "origen": indice.get(origen, -1),
        "destino": indice.get(destino, -1),
    }


def mapa_red(datos, key, al_elegir):
    """Dibuja el mapa. al_elegir se llama cuando se hace clic en una estacion; dentro de
    esa funcion el clic esta en st.session_state[key].estacion ({nombre, origen})."""
    return _mapa(data=datos, key=key, on_estacion_change=al_elegir)


# ---------------------------------------------------------------- recorrido editable
def linea_editable(paradas, color, key, al_elegir, nueva=None, cerradas=(), elegido=-1):
    """Recorrido de una ruta; al hacer clic en un tramo se llama a al_elegir.
    El tramo esta en st.session_state[key].tramo ({a, b}), en el orden en que se ve."""
    datos = {
        "paradas": [{"n": p, "c": p in cerradas, "nueva": p == nueva} for p in paradas],
        "color": color,
        "elegido": elegido,
    }
    return _linea(data=datos, key=key, on_tramo_change=al_elegir)
