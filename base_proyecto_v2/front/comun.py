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


@st.cache_resource
def obtener_red():
    """Una sola Red compartida por todas las paginas (se carga una vez)."""
    return Red(str(RAIZ / "datos"))


@st.cache_data
def nombres_estaciones():
    """Todos los nombres de estaciones, en orden alfabetico (para los menus)."""
    with open(RAIZ / "datos" / "estaciones.csv", encoding="utf-8-sig") as f:
        filas = list(csv.reader(f))[1:]
    return sorted(fila[0] for fila in filas if fila)
