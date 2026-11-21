"""Panel de rendimiento (R11): corre cada operacion con redes de tamano creciente
y grafica como crece el tiempo, junto a la complejidad esperada.
Diseno: Parte E (front/visual/)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "herramientas"))
sys.path.insert(0, str(RAIZ / "front"))

import altair as alt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from medir import medir, tabla_resumen, TOLERANCIA  # noqa: E402
from visual import tema  # noqa: E402

# Si una medicion NO coincide con lo esperado, la explicacion va aqui:
#   "operacion": "texto que explica por que crece distinto a lo esperado"
EXPLICACIONES = {
    "carga": "Cargar incluye ordenar (merge sort, O(n log n)) y crear muchas listas; en redes grandes "
             "la memoria del computador hace que cada elemento cueste un poco más.",
    "simular_fila": "Con arreglos grandes cada persona cuesta un poco más por la memoria caché del "
                    "computador, aunque el algoritmo hace el mismo trabajo por persona.",
}

tema.encabezado("panel")
tema.html(
    '<p class="tm-nota" style="font-size:1rem;margin-top:.8rem">Cada operación se mide en redes de tamaño '
    'creciente (mediana de varias repeticiones). Si el tiempo casi no cambia cuando la red crece, la '
    'operación es O(1) u O(log n); si se duplica cuando la red se duplica, es lineal.</p>')

OPCIONES = [500, 1000, 2000, 4000, 8000, 10000, 20000, 40000, 80000]
OFICIALES = [10000, 20000, 40000, 80000]


def usar_oficiales():
    st.session_state["tamanos"] = OFICIALES


with st.container(border=True):
    c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
    tamanos = c1.multiselect("Tamaños de red (estaciones)", OPCIONES, default=[1000, 2000, 4000, 8000],
                             key="tamanos")
    c2.button("Usar los oficiales", on_click=usar_oficiales, width="stretch",
              help="10.000, 20.000, 40.000 y 80.000 estaciones (tarda unos 20 segundos)")
    repeticiones = st.slider("Repeticiones por operación", 5, 100, 30)
    medir_ahora = st.button("Medir", icon=":material/speed:", type="primary", disabled=len(tamanos) < 2)

if medir_ahora:
    with tema.cargando("Generando redes y midiendo cada operación"):
        barra = st.progress(0.0, text="Preparando…")

        def avance(k, total, n):
            barra.progress(k / total, text=f"Red de {n:,} estaciones lista ({k} de {total})".replace(",", "."))

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
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("n:Q", scale=alt.Scale(type="log"), title="Estaciones (n)"),
            y=alt.Y("microsegundos:Q", scale=alt.Scale(type="log"), title="Tiempo (µs, mediana)"),
            color=alt.Color("operación:N", legend=alt.Legend(title="Operación")),
            tooltip=["operación", "n", alt.Tooltip("microsegundos", format=".2f")],
        )
        .properties(height=440)
    )
    with st.container(border=True):
        st.altair_chart(grafica, width="stretch")
        tema.html('<p class="tm-nota">Ejes logarítmicos: una línea plana es O(1) u O(log n); una línea con '
                  'pendiente 1 es lineal.</p>')

    tabla = pd.DataFrame(
        [
            {
                "operación": op,
                "req": req,
                "O grande esperada": esperada,
                "pendiente esperada": "—" if pe is None else str(pe),
                "pendiente medida": f"{pm:.2f}",
                "veredicto": ver,
            }
            for op, req, esperada, pe, pm, ver in resumen
        ]
    )
    st.dataframe(tabla, hide_index=True, width="stretch")
    st.caption(f"Veredicto OK si la pendiente medida está a {TOLERANCIA} o menos de la esperada.")

    for op, _req, _esp, _pe, pm, ver in resumen:
        if ver == "NO COINCIDE":
            st.warning(f"**{op}** (pendiente {pm:.2f}): " + EXPLICACIONES.get(
                op, "no coincide con lo esperado y todavía falta la explicación (editar EXPLICACIONES en este archivo)."))
