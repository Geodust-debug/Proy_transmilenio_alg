"""Pagina de la Parte A: planear un viaje (R5). Solo llama a red.viaje().
Diseno y animacion del mapa: Parte E (front/visual/)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones, nombres_rutas, posiciones  # noqa: E402
from visual import animaciones, componentes, tema  # noqa: E402

tema.encabezado("viaje")
red = obtener_red()
nombres = nombres_estaciones()


def invertir():
    st.session_state["origen"], st.session_state["destino"] = (
        st.session_state.get("destino"), st.session_state.get("origen"))


def alternar_mapa():
    st.session_state["mapa_abierto"] = not st.session_state.get("mapa_abierto", False)


def elegir_en_mapa():
    """Clic en una estacion del mapa: la primera es el origen; las siguientes cambian el destino
    (con Shift se elige el origen)."""
    clic = st.session_state["mapa_red"].estacion
    if not clic:
        return
    nombre = clic["nombre"]
    if clic.get("origen") or not st.session_state.get("origen"):
        st.session_state["origen"] = nombre
        if st.session_state.get("destino") == nombre:
            st.session_state["destino"] = None
    elif nombre != st.session_state.get("origen"):
        st.session_state["destino"] = nombre


col1, col2, col3 = st.columns([10, 10, 3], vertical_alignment="bottom")
origen = col1.selectbox("Origen", nombres, index=None, key="origen", placeholder="Escribe para buscar…")
destino = col2.selectbox("Destino", nombres, index=None, key="destino", placeholder="Escribe para buscar…")
col3.button("Invertir", icon=":material/swap_horiz:", on_click=invertir, width="stretch",
            help="Cambia el origen por el destino")

abierto = st.session_state.get("mapa_abierto", False)
st.button("Ocultar mapa" if abierto else "Mostrar mapa", icon=":material/map:", on_click=alternar_mapa,
          help="Un mapa de papel con todas las estaciones: elige tu origen y tu destino con un clic")
tramos = None
if origen and destino and origen != destino and red.estado(origen) == "ABIERTA" \
        and red.estado(destino) == "ABIERTA":
    tramos = red.viaje(origen, destino)
if abierto:
    datos = componentes.datos_mapa(red, posiciones(), nombres_rutas(), origen, destino, tramos)
    componentes.mapa_red(datos, key="mapa_red", al_elegir=elegir_en_mapa)

if not (origen and destino):
    tema.html('<p class="tm-nota">Elige de dónde sales y a dónde vas; el mapa muestra el recorrido '
              'parada por parada.</p>')
elif origen == destino:
    st.info("El origen y el destino son la misma estación.")
elif red.estado(origen) == "CERRADA" or red.estado(destino) == "CERRADA":
    cerrada = origen if red.estado(origen) == "CERRADA" else destino
    st.warning(f"{cerrada} está cerrada: no se puede viajar desde ni hacia ella. "
               "Puedes reabrirla en la página Estaciones.")
else:
    if tramos is None:
        st.error("No hay un viaje directo ni con un transbordo entre esas dos estaciones.")
    else:
        recorridos = []
        for ruta, sube, baja in tramos:
            paradas = red.recorrido(ruta)
            inicio, fin = 0, 0
            for i, nombre in enumerate(paradas):
                if nombre == sube:
                    inicio = i
                if nombre == baja:
                    fin = i
            recorridos.append((ruta, paradas[inicio:fin + 1]))

        animaciones.mapa_viaje(recorridos)

        total = sum(len(p) - 1 for _, p in recorridos)
        columnas = st.columns(len(recorridos) + 1)
        for numero, ((ruta, paradas), col) in enumerate(zip(recorridos, columnas), start=1):
            with col:
                tema.html(f"""
<div class="tm-tramo">
  <div class="tm-tramo__cabeza">Tramo {numero} {tema.insignia(ruta)}</div>
  <div>Sube en <b>{tema.texto(paradas[0])}</b> y baja en <b>{tema.texto(paradas[-1])}</b>.</div>
  <div class="tm-nota">{len(paradas) - 1} {"parada" if len(paradas) == 2 else "paradas"}</div>
</div>""")
        with columnas[-1]:
            resumen = ("Viaje directo" if len(recorridos) == 1
                       else f"Un transbordo en {tema.texto(recorridos[0][1][-1])}")
            tema.html(f"""
<div class="tm-tramo tm-tramo--total">
  <div class="tm-tramo__cabeza">En total</div>
  <div class="tm-tramo__numero">{total} {"parada" if total == 1 else "paradas"}</div>
  <div class="tm-nota">{resumen}</div>
</div>""")
