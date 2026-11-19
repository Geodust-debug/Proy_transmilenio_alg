"""Pagina de la Parte A: planear un viaje (R5). Solo llama a red.viaje()."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones  # noqa: E402

st.set_page_config(page_title="Planear viaje", page_icon="🗺️", layout="wide")
st.title("🗺️ Planear un viaje")
st.caption("Directo o con un solo transbordo, el que pase por menos paradas.")

red = obtener_red()
nombres = nombres_estaciones()

col1, col2 = st.columns(2)
origen = col1.selectbox("Origen", nombres, index=None, placeholder="Escribe para buscar…")
destino = col2.selectbox("Destino", nombres, index=None, placeholder="Escribe para buscar…")

if origen and destino:
    if red.estado(origen) == "CERRADA" or red.estado(destino) == "CERRADA":
        st.warning("Una de las dos estaciones está cerrada: no se puede viajar desde/hacia ella.")
    else:
        tramos = red.viaje(origen, destino)
        if tramos is None:
            st.error("No hay viaje posible entre esas dos estaciones.")
        else:
            total = 0
            for numero, (ruta, sube, baja) in enumerate(tramos, start=1):
                paradas = red.recorrido(ruta)
                inicio, fin = 0, 0
                for i, nombre in enumerate(paradas):
                    if nombre == sube:
                        inicio = i
                    if nombre == baja:
                        fin = i
                recorridas = fin - inicio
                total += recorridas
                with st.container(border=True):
                    st.markdown(f"**Tramo {numero} · Ruta `{ruta}`**")
                    st.write(f"Sube en **{sube}** y baja en **{baja}** ({recorridas} paradas).")
                    st.caption(" → ".join(paradas[inicio:fin + 1]))
            if len(tramos) == 1:
                st.success(f"Viaje directo · {total} paradas")
            else:
                st.success(f"Un transbordo en **{tramos[0][2]}** · {total} paradas en total")
