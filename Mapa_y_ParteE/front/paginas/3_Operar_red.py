"""Pagina de la Parte D: editar rutas (R7) y deshacer / rehacer (R9).
Solo llama al motor: ninguna regla vive aqui. Diseno: Parte E (front/visual/)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones, nombres_rutas  # noqa: E402
from visual import componentes, dibujos, tema  # noqa: E402

tema.encabezado("operar")
red = obtener_red()
estaciones = nombres_estaciones()


# Los botones usan on_click: el cambio se hace ANTES de volver a pintar la
# pagina, asi el mapa de la ruta siempre muestra el estado actual.
if "aviso_operar" in st.session_state:
    texto, icono = st.session_state.pop("aviso_operar")
    st.toast(texto, icon=icono)


def avisar(texto, icono):
    st.session_state["aviso_operar"] = (texto, icono)


def agregar(ruta):
    nueva, despues = st.session_state.get("nueva"), st.session_state.get("despues")
    if red.agregar_parada(ruta, nueva, despues):
        st.session_state["resaltada"] = nueva
        st.session_state["nueva"] = None
        st.session_state["despues"] = None
        avisar(f"{nueva} agregada después de {despues}.", ":material/add_location_alt:")
    else:
        avisar("No se pudo agregar: esa estación ya está en la ruta.", ":material/error:")


def elegir_tramo():
    """Clic en un tramo de la linea: deja elegida la parada 'justo despues de' para agregar ahi."""
    tramo = st.session_state["linea_ruta"].tramo
    if not tramo:
        return
    al_reves = st.session_state.get("sentido") == "Al revés"
    # el motor siempre trabaja en el sentido normal: si se ve al reves, la parada "anterior" es la segunda
    st.session_state["despues"] = tramo["b"] if al_reves else tramo["a"]
    st.session_state["nueva"] = None
    st.session_state.pop("resaltada", None)


def quitar(ruta):
    estacion = st.session_state.get("quitar")
    if red.quitar_parada(ruta, estacion):
        st.session_state["quitar"] = None
        st.session_state.pop("resaltada", None)
        avisar(f"{estacion} quitada de la ruta {ruta}.", ":material/wrong_location:")
    else:
        avisar("No se pudo quitar esa parada.", ":material/error:")


def deshacer():
    st.session_state.pop("resaltada", None)
    avisar(*(("Cambio deshecho.", ":material/undo:") if red.deshacer()
             else ("No hay nada que deshacer.", ":material/info:")))


def rehacer():
    st.session_state.pop("resaltada", None)
    avisar(*(("Cambio rehecho.", ":material/redo:") if red.rehacer()
             else ("No hay nada que rehacer.", ":material/info:")))


ruta = st.selectbox("Ruta", nombres_rutas(), index=None, placeholder="Elige una ruta…")

if ruta:
    sentido = st.segmented_control("Sentido del recorrido", ["Normal", "Al revés"], default="Normal",
                                   key="sentido")
    paradas = red.recorrido(ruta, al_reves=(sentido == "Al revés"))
    cerradas = [p for p in paradas if red.estado(p) == "CERRADA"]
    color, _ = dibujos.color_ruta(ruta)
    tema.html(f'<p>{tema.insignia(ruta)} &nbsp;<b>{len(paradas)} paradas</b>'
              + (f' &nbsp;<span class="tm-nota">({len(cerradas)} cerradas, en rojo)</span>' if cerradas else "")
              + '</p>')
    if paradas:
        al_reves = sentido == "Al revés"
        elegida = st.session_state.get("despues")
        tramo_elegido = -1
        for i in range(len(paradas) - 1):
            if (paradas[i + 1] if al_reves else paradas[i]) == elegida:
                tramo_elegido = i
        componentes.linea_editable(paradas, color, key="linea_ruta", al_elegir=elegir_tramo,
                                   nueva=st.session_state.get("resaltada"), cerradas=cerradas,
                                   elegido=tramo_elegido)
    else:
        st.info("La ruta no tiene paradas.")

    normal = red.recorrido(ruta)
    col1, col2 = st.columns(2)
    with col1, st.container(border=True):
        tema.html('<div class="tm-subtitulo">Agregar una parada</div>')
        elegida = st.session_state.get("despues")
        if elegida in normal and normal.index(elegida) + 1 < len(normal):
            tema.html(f'<p class="tm-nota">Entre <b>{tema.texto(elegida)}</b> y '
                      f'<b>{tema.texto(normal[normal.index(elegida) + 1])}</b>. Elige qué estación va ahí.</p>')
        else:
            tema.html('<p class="tm-nota">Toca un tramo de la línea de arriba, o elígelo aquí.</p>')
        nueva = st.selectbox("Estación nueva", estaciones, index=None, key="nueva", placeholder="Elige…")
        despues = st.selectbox("Justo después de", normal, index=None, key="despues", placeholder="Elige…")
        st.button("Agregar", icon=":material/add:", type="primary", disabled=not (nueva and despues),
                  on_click=agregar, args=(ruta,))
    with col2, st.container(border=True):
        tema.html('<div class="tm-subtitulo">Quitar una parada</div>')
        quitar_sel = st.selectbox("Parada a quitar", normal, index=None, key="quitar", placeholder="Elige…")
        st.button("Quitar", icon=":material/remove:", disabled=not quitar_sel, on_click=quitar, args=(ruta,))
else:
    tema.html('<p class="tm-nota">Elige una ruta para ver su recorrido y editarla.</p>')

st.divider()
tema.html('<div class="tm-subtitulo">Deshacer y rehacer</div>'
          '<p class="tm-nota">Sirve para cierres, reaperturas y ediciones de ruta, en orden inverso (R9).</p>')
b1, b2, _ = st.columns([1, 1, 3])
b1.button("Deshacer", icon=":material/undo:", width="stretch", on_click=deshacer)
b2.button("Rehacer", icon=":material/redo:", width="stretch", on_click=rehacer)
