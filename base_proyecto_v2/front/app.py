"""Pagina de inicio. Arranque:   streamlit run front/app.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones  # noqa: E402

st.set_page_config(page_title="Planeador TransMilenio", page_icon="🚌", layout="wide")

st.title("🚌 Planeador de viajes TransMilenio")
st.write(
    "Busca estaciones, planea tu viaje y mira a qué hora pasa tu bus, "
    "con la red real de TransMilenio. Usa el menú de la izquierda para "
    "cambiar de página."
)

obtener_red()
st.metric("Estaciones en la red", len(nombres_estaciones()))

st.info(
    "Cada página del menú es de una parte del equipo. Las que todavía no "
    "existen aparecen cuando su responsable hace push."
)
