"""Panel de rendimiento (R11): corre cada operacion con redes de tamano creciente
y grafica como crece el tiempo, junto a la complejidad esperada."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "herramientas"))

import altair as alt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from medir import medir, tabla_resumen, TOLERANCIA  # noqa: E402

# Si una medicion NO coincide con lo esperado, la explicacion va aqui:
#   "operacion": "texto que explica por que crece distinto a lo esperado"
EXPLICACIONES = {}

st.set_page_config(page_title="Panel de rendimiento", page_icon="📈", layout="wide")
st.title("📈 Panel de rendimiento")
st.write(
    "Cada operación del motor se mide en redes de tamaño creciente (mediana de varias "
    "repeticiones). Si el tiempo casi no cambia al crecer la red, la operación es O(1) u "
    "O(log n); si se duplica cuando la red se duplica, es lineal."
)

OPCIONES = [500, 1000, 2000, 4000, 8000, 10000, 20000, 40000, 80000]
tamanos = st.multiselect("Tamaños de red (estaciones)", OPCIONES, default=[1000, 2000, 4000, 8000])
st.caption("Los tamaños oficiales de la evaluación son 10.000, 20.000, 40.000 y 80.000. "
           "Las redes grandes tardan en generarse y cargarse.")
repeticiones = st.slider("Repeticiones por operación", 5, 100, 30)

if st.button("Medir", type="primary", disabled=len(tamanos) < 2):
    barra = st.progress(0.0, text="Midiendo…")

    def avance(k, total, n):
        barra.progress(k / total, text=f"Red de {n:,} estaciones lista ({k}/{total})")

    st.session_state["medidas"] = medir(sorted(tamanos), repeticiones, avance)
    barra.empty()

medidas = st.session_state.get("medidas")
if medidas:
    resumen = tabla_resumen(medidas)

    filas = []
    for n, tiempos in medidas.items():
        for operacion, segundos in tiempos.items():
            filas.append({"n": n, "operación": operacion, "microsegundos": segundos * 1e6})
    largo = pd.DataFrame(filas)
    grafica = (
        alt.Chart(largo)
        .mark_line(point=True)
        .encode(
            x=alt.X("n:Q", scale=alt.Scale(type="log"), title="Estaciones (n)"),
            y=alt.Y("microsegundos:Q", scale=alt.Scale(type="log"), title="Tiempo (µs, mediana)"),
            color="operación:N",
            tooltip=["operación", "n", "microsegundos"],
        )
        .properties(height=420)
    )
    st.altair_chart(grafica, width="stretch")
    st.caption("Ejes logarítmicos: una línea plana es O(1)/O(log n); una línea con pendiente 1 es lineal.")

    tabla = pd.DataFrame(
        [
            {
                "operación": op,
                "req": req,
                "O grande esperada": esperada,
                "pendiente esperada": "—" if pe is None else str(pe),
                "pendiente medida": round(pm, 2),
                "veredicto": ver,
            }
            for op, req, esperada, pe, pm, ver in resumen
        ]
    )
    st.dataframe(tabla, hide_index=True, width="stretch")
    st.caption(f"Veredicto OK si |pendiente medida − esperada| ≤ {TOLERANCIA}.")

    for op, _req, _esp, _pe, pm, ver in resumen:
        if ver == "NO COINCIDE":
            st.warning(f"**{op}** (pendiente {pm:.2f}): " + EXPLICACIONES.get(
                op, "no coincide con lo esperado y todavía falta la explicación (editar EXPLICACIONES en este archivo)."))
