"""Pagina de la Parte D: editar rutas (R7) y deshacer / rehacer (R9).
Solo llama al motor: ninguna regla vive aqui."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import RAIZ, obtener_red, nombres_estaciones  # noqa: E402

st.set_page_config(page_title="Operar la red", page_icon="🛠️", layout="wide")
st.title("🛠️ Operar la red")

red = obtener_red()
estaciones = nombres_estaciones()


@st.cache_data
def nombres_rutas():
    """Nombres de las rutas, solo para armar el menu."""
    vistos, lista = [], []
    with open(RAIZ / "datos" / "rutas.csv", encoding="utf-8-sig") as f:
        for fila in list(csv.reader(f))[1:]:
            if fila and fila[0] not in vistos:
                vistos.append(fila[0])
                lista.append(fila[0])
    return lista


def avisar(texto, bien):
    st.session_state["aviso"] = (texto, bien)
    st.rerun()


if "aviso" in st.session_state:
    texto, bien = st.session_state.pop("aviso")
    (st.success if bien else st.error)(texto)

ruta = st.selectbox("Ruta", nombres_rutas(), index=None, placeholder="Elige una ruta…")

if ruta:
    sentido = st.radio("Sentido del recorrido", ["Normal", "Al revés"], horizontal=True)
    paradas = red.recorrido(ruta, al_reves=(sentido == "Al revés"))
    st.write(f"**{len(paradas)} paradas**")
    st.caption(" → ".join(paradas) if paradas else "La ruta no tiene paradas.")

    normal = red.recorrido(ruta)
    col1, col2 = st.columns(2)
    with col1, st.container(border=True):
        st.markdown("**Agregar una parada**")
        nueva = st.selectbox("Estación nueva", estaciones, index=None, key="nueva", placeholder="Elige…")
        despues = st.selectbox("Justo después de", normal, index=None, key="despues", placeholder="Elige…")
        if st.button("Agregar", disabled=not (nueva and despues)):
            if red.agregar_parada(ruta, nueva, despues):
                avisar(f"{nueva} agregada después de {despues}.", True)
            else:
                avisar("No se pudo agregar (¿ya está en la ruta?).", False)
    with col2, st.container(border=True):
        st.markdown("**Quitar una parada**")
        quitar = st.selectbox("Parada a quitar", normal, index=None, key="quitar", placeholder="Elige…")
        if st.button("Quitar", disabled=not quitar):
            if red.quitar_parada(ruta, quitar):
                avisar(f"{quitar} quitada de la ruta.", True)
            else:
                avisar("No se pudo quitar.", False)

st.divider()
st.markdown("**Deshacer y rehacer** (cierres, reaperturas y ediciones de ruta)")
b1, b2 = st.columns(2)
if b1.button("↩️ Deshacer"):
    avisar("Cambio deshecho." if red.deshacer() else "No hay nada que deshacer.", True)
if b2.button("↪️ Rehacer"):
    avisar("Cambio rehecho." if red.rehacer() else "No hay nada que rehacer.", True)
