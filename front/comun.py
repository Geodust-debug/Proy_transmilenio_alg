"""Cosas compartidas por todas las paginas del front (cualquier libreria vale aqui).

El front SOLO llama al motor: ninguna regla del sistema vive aqui.
"""
import csv
import sys
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from motor import Red  # noqa: E402
from visual import tema  # noqa: E402

_ya_cargada = [False]   # vive mientras el servidor este prendido


@st.cache_resource(show_spinner=False)
def _cargar_red():
    return Red(str(RAIZ / "datos"))


def obtener_red():
    """Una sola Red compartida por todas las paginas (se carga una vez).
    La primera vez se muestra el bus de carga mientras se leen los CSV."""
    if _ya_cargada[0]:
        return _cargar_red()
    with tema.cargando("Cargando la red de TransMilenio"):
        red = _cargar_red()
    _ya_cargada[0] = True
    return red


@st.cache_data
def nombres_estaciones():
    """Todos los nombres de estaciones, en orden alfabetico (para los menus)."""
    with open(RAIZ / "datos" / "estaciones.csv", encoding="utf-8-sig") as f:
        filas = list(csv.reader(f))[1:]
    return sorted(fila[0] for fila in filas if fila)


@st.cache_data
def nombres_rutas():
    """Nombres de las rutas, en el orden del CSV (solo para armar menus y el mapa)."""
    vistos, lista = set(), []
    with open(RAIZ / "datos" / "rutas.csv", encoding="utf-8-sig") as f:
        for fila in list(csv.reader(f))[1:]:
            if fila and fila[0] not in vistos:
                vistos.add(fila[0])
                lista.append(fila[0])
    return lista


@st.cache_data
def posiciones():
    """Donde se dibuja cada estacion en el mapa: {nombre: (x, y)}. Ver herramientas/generar_posiciones.py."""
    with open(RAIZ / "datos" / "posiciones.csv", encoding="utf-8") as f:
        return {fila[0]: (float(fila[1]), float(fila[2])) for fila in list(csv.reader(f))[1:] if fila}


def rutas_que_pasan(red, estacion):
    """Rutas que pasan por una estacion HOY (con las paradas agregadas o quitadas en Operar la red).

    Se le pregunta a la red en vez de leer el CSV, asi la lista siempre esta al dia.
    """
    return sorted(r for r in nombres_rutas() if estacion in red.recorrido(r))
