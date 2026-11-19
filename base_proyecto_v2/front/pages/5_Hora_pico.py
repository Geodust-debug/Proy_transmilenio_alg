"""Pagina de la Parte A: fila de abordaje en hora pico (R10)."""
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from motor import simular_fila  # noqa: E402

st.set_page_config(page_title="Hora pico", page_icon="⏱️", layout="wide")
st.title("⏱️ Hora pico: fila de abordaje")
st.caption("Los buses salen cada cierto tiempo con cupo limitado; la gente sube en orden de llegada.")

c1, c2, c3, c4 = st.columns(4)
pasajeros = c1.number_input("Pasajeros", 1, 300000, 5000, step=500)
ventana = c2.number_input("Llegan durante (segundos)", 60, 7200, 3600, step=60)
frecuencia = c3.number_input("Un bus cada (segundos)", 1, 600, 30)
capacidad = c4.number_input("Cupo por bus", 1, 300, 80)

if st.button("Simular", type="primary"):
    azar = random.Random(42)
    llegadas = [azar.randint(0, int(ventana)) for _ in range(int(pasajeros))]
    inicio = time.perf_counter()
    salidas = simular_fila(llegadas, int(frecuencia), int(capacidad))
    segundos = time.perf_counter() - inicio

    esperas = [salidas[i] - llegadas[i] for i in range(len(llegadas))]
    espera_max = 0
    total_esperas = 0
    for espera in esperas:
        total_esperas += espera
        if espera > espera_max:
            espera_max = espera
    buses = len({s for s in salidas})

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Buses que salieron", buses)
    m2.metric("Espera promedio", f"{total_esperas / len(esperas):.0f} s")
    m3.metric("Espera máxima", f"{espera_max} s")
    m4.metric("Tiempo de la simulación", f"{segundos * 1000:.0f} ms")

    muestra = sorted(range(len(llegadas)), key=lambda i: llegadas[i])
    paso = max(1, len(muestra) // 400)
    datos = pd.DataFrame(
        {"llegada (s)": [llegadas[i] for i in muestra[::paso]],
         "espera (s)": [esperas[i] for i in muestra[::paso]]}
    ).set_index("llegada (s)")
    st.line_chart(datos)
    if espera_max > 5 * frecuencia:
        st.warning("La fila crece: llegan más personas de las que caben en los buses.")
