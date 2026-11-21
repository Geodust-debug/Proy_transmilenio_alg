"""Punto de entrada de la app. Arranque (desde la raiz del repo):

    python -m streamlit run front/app.py

Este archivo arma el menu (st.navigation), aplica el tema visual y luego
ejecuta la pagina elegida. Cada pagina vive en front/paginas/ y solo llama al
motor; el tema y las animaciones estan en front/visual/ (Parte E).
"""
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))

import streamlit as st  # noqa: E402

from visual import tema  # noqa: E402

st.set_page_config(
    page_title="Planeador TransMilenio",
    page_icon=str(CARPETA / "static" / "icono.png"),
    layout="wide",
)
tema.aplicar_tema()
st.logo(str(CARPETA / "static" / "logo.png"), size="large",
        icon_image=str(CARPETA / "static" / "icono.png"))

paginas = {
    "": [
        st.Page("inicio.py", title="Inicio", icon=":material/home:", default=True),
    ],
    "Usar la red": [
        st.Page("paginas/4_Viaje.py", title="Planear un viaje", icon=":material/route:", url_path="Viaje"),
        st.Page("paginas/2_Horarios_y_ranking.py", title="Horarios y ranking", icon=":material/schedule:",
                url_path="Horarios_y_ranking"),
        st.Page("paginas/1_Estaciones.py", title="Estaciones", icon=":material/signpost:", url_path="Estaciones"),
    ],
    "Operar y simular": [
        st.Page("paginas/3_Operar_red.py", title="Operar la red", icon=":material/alt_route:", url_path="Operar_red"),
        st.Page("paginas/5_Hora_pico.py", title="Hora pico", icon=":material/groups:", url_path="Hora_pico"),
        st.Page("paginas/6_Panel_rendimiento.py", title="Panel de rendimiento", icon=":material/speed:",
                url_path="Panel_rendimiento"),
    ],
}
navegacion = st.navigation(paginas)

with st.sidebar:
    tema.html('<p class="tm-pie">Proyecto de Estructuras de Datos y Algoritmos<br>'
              'Universidad de La Sabana</p>')

navegacion.run()
