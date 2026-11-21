"""Pagina de la Parte A: fila de abordaje en hora pico (R10). Solo llama a simular_fila().
Diseno y animacion del anden: Parte E (front/visual/)."""
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st  # noqa: E402

from motor import simular_fila  # noqa: E402
from visual import animaciones, tema  # noqa: E402

tema.encabezado("hora_pico")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    pasajeros = c1.number_input("Pasajeros", 1, 300000, 9000, step=500)
    ventana = c2.number_input("Llegan durante (segundos)", 60, 7200, 3600, step=60)
    frecuencia = c3.number_input("Un bus cada (segundos)", 1, 600, 30)
    capacidad = c4.number_input("Cupo por bus", 1, 300, 80)
    forma = st.segmented_control(
        "Cómo llega la gente", ["Pico en la mitad", "Pareja todo el tiempo"], default="Pico en la mitad",
        help="Con pico, la mayoría llega a mitad de la ventana, como en una hora pico real.")
    simular = st.button("Simular", icon=":material/play_arrow:", type="primary")

if simular:
    azar = random.Random(42)
    if forma == "Pareja todo el tiempo":
        llegadas = [azar.randint(0, int(ventana)) for _ in range(int(pasajeros))]
    else:
        llegadas = [int(azar.triangular(0, int(ventana), int(ventana) / 2)) for _ in range(int(pasajeros))]
    with tema.cargando("Simulando la fila"):
        inicio = time.perf_counter()
        salidas = simular_fila(llegadas, int(frecuencia), int(capacidad))
        segundos = time.perf_counter() - inicio
    st.session_state["fila"] = (llegadas, salidas, int(frecuencia), segundos)

if "fila" in st.session_state:
    llegadas, salidas, f, segundos = st.session_state["fila"]
    n = len(llegadas)
    total_espera = 0
    espera_max = 0
    sin_cupo = 0
    for i in range(n):
        espera = salidas[i] - llegadas[i]
        total_espera += espera
        if espera > espera_max:
            espera_max = espera
        primer_bus = max(f, -(-llegadas[i] // f) * f)   # el primer bus que pasa cuando ya llegó
        if salidas[i] > primer_bus:
            sin_cupo += 1

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Espera promedio", f"{total_espera / n:.0f} s")
    m2.metric("Espera máxima", f"{espera_max // 60} min {espera_max % 60} s")
    m3.metric("No alcanzaron el primer bus", f"{100 * sin_cupo / n:.0f} %")
    m4.metric("El motor tardó", f"{segundos * 1000:.0f} ms", help="Tiempo de simular_fila (R10)")

    animaciones.anden_hora_pico(llegadas, salidas)
    if sin_cupo == 0:
        st.success("Nadie se quedó sin cupo: los buses alcanzan para todos.")
    elif espera_max > 5 * f:
        st.warning("La fila crece más rápido de lo que los buses la vacían: subir el cupo o la frecuencia "
                   "la haría más corta.")
else:
    tema.html('<p class="tm-nota">Ajusta los valores y oprime <b>Simular</b> para ver la fila en el andén.</p>')
