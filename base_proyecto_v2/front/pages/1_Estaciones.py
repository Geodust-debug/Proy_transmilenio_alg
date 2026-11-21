"""Pagina de la Parte B: buscar, autocompletar, rango y cerrar/reabrir (R1, R2, R3, R8).
Solo llama al motor: ninguna regla vive aqui."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones  # noqa: E402

st.set_page_config(page_title="Estaciones", page_icon="🚏", layout="wide")
st.title("🚏 Estaciones")

red = obtener_red()
nombres = nombres_estaciones()

pestana1, pestana2, pestana3, pestana4 = st.tabs(
    ["Buscar", "Autocompletar", "Rango", "Cerrar / reabrir"]
)

with pestana1:
    st.caption("R1 · Escribe el nombre exacto de la estación.")
    nombre = st.text_input("Nombre de la estación", key="buscar").strip().upper()
    if nombre:
        estado = red.estado(nombre)
        if estado == "ABIERTA":
            st.success(f"{nombre}: ABIERTA")
        elif estado == "CERRADA":
            st.warning(f"{nombre}: CERRADA")
        else:
            st.error(f"{nombre}: NO EXISTE")

with pestana2:
    st.caption("R2 · Mientras escribes, se muestran hasta k estaciones abiertas que empiezan por ese texto.")
    c1, c2 = st.columns([3, 1])
    prefijo = c1.text_input("Empieza por…", key="prefijo").strip().upper()
    k = c2.number_input("k (máximo)", 1, 50, 8)
    if prefijo:
        sugerencias = red.autocompletar(prefijo, int(k))
        if sugerencias:
            for s in sugerencias:
                st.write("•", s)
        else:
            st.info("Ninguna estación abierta empieza por ese texto.")

with pestana3:
    st.caption("R3 · Todas las estaciones abiertas entre dos nombres, en orden alfabético.")
    c1, c2 = st.columns(2)
    desde = c1.selectbox("Desde", nombres, index=nombres.index("CALLE 26") if "CALLE 26" in nombres else 0)
    hasta = c2.selectbox("Hasta", nombres, index=nombres.index("CALLE 72") if "CALLE 72" in nombres else len(nombres) - 1)
    lista = red.rango(desde, hasta)
    st.write(f"**{len(lista)}** estaciones abiertas entre «{desde}» y «{hasta}»")
    if lista:
        st.dataframe({"estación": lista}, hide_index=True, width="stretch")

with pestana4:
    st.caption("R8 · Una estación cerrada desaparece de búsquedas, autocompletado, rangos, ranking y viajes.")
    elegida = st.selectbox("Estación", nombres, index=None, placeholder="Elige una estación…")
    b1, b2 = st.columns(2)
    if elegida:
        st.write("Estado actual:", red.estado(elegida))
        if b1.button("Cerrar", disabled=red.estado(elegida) != "ABIERTA"):
            red.cerrar(elegida)
            st.rerun()
        if b2.button("Reabrir", disabled=red.estado(elegida) != "CERRADA"):
            red.reabrir(elegida)
            st.rerun()
    if st.button("Deshacer último cambio"):
        st.write("Deshecho." if red.deshacer() else "No hay nada que deshacer.")
    if st.button("Rehacer"):
        st.write("Rehecho." if red.rehacer() else "No hay nada que rehacer.")
