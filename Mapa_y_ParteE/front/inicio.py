"""Pagina de inicio: que es la app y a donde ir. Solo llama al motor."""
import csv

import streamlit as st

from comun import RAIZ, nombres_estaciones, obtener_red
from visual import dibujos, tema

tema.encabezado("inicio")
obtener_red()


@st.cache_data
def tamano_red():
    """Cuantas rutas y horarios trae la carpeta datos/ (solo para el texto)."""
    with open(RAIZ / "datos" / "rutas.csv", encoding="utf-8-sig") as f:
        rutas = {fila[0] for fila in list(csv.reader(f))[1:] if fila}
    with open(RAIZ / "datos" / "horarios.csv", encoding="utf-8-sig") as f:
        horarios = sum(1 for _ in f) - 1
    return len(rutas), horarios


rutas, horarios = tamano_red()
tema.html(f"""
<p class="tm-nota" style="font-size:1.05rem;margin-top:1rem">
La red cargada tiene <b>{len(nombres_estaciones())} estaciones</b>, <b>{rutas} rutas</b> y
<b>{horarios:,} horas de paso</b>. Elige qué quieres hacer:</p>""".replace(",", "."))

DESTINOS = [
    ("viaje", "paginas/4_Viaje.py", "Planear un viaje",
     "De una estación a otra, directo o con un transbordo."),
    ("horarios", "paginas/2_Horarios_y_ranking.py", "Horarios y ranking",
     "El próximo bus de una ruta y las estaciones con más buses."),
    ("estaciones", "paginas/1_Estaciones.py", "Estaciones",
     "Buscar, autocompletar, listar por rango, cerrar y reabrir."),
    ("operar", "paginas/3_Operar_red.py", "Operar la red",
     "Agregar y quitar paradas de una ruta; deshacer y rehacer."),
    ("hora_pico", "paginas/5_Hora_pico.py", "Hora pico",
     "Cuánta gente alcanza a subir a cada bus cuando la estación se llena."),
    ("panel", "paginas/6_Panel_rendimiento.py", "Panel de rendimiento",
     "Cuánto tarda cada operación y si crece como dice su O grande."),
]

for fila in range(0, len(DESTINOS), 3):
    columnas = st.columns(3)
    for col, (clave, archivo, titulo, descripcion) in zip(columnas, DESTINOS[fila:fila + 3]):
        color = tema.acento(clave)
        with col.container(border=True, key=f"destino_{clave}"):
            tema.html(f"""
<div class="tm-destino" style="--acento:{color}">
  <div class="tm-destino__icono">{dibujos.icono(tema.PAGINAS[clave][3], color)}</div>
  <div class="tm-destino__titulo">{titulo}</div>
  <p class="tm-destino__texto">{descripcion}</p>
</div>""")
            st.page_link(archivo, label=f"Abrir {titulo.lower()}")
