"""Pagina de la Parte B: buscar, autocompletar, rango y cerrar/reabrir (R1, R2, R3, R8).
Solo llama al motor: ninguna regla vive aqui. Diseno: Parte E (front/visual/)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones  # noqa: E402
from visual import tema  # noqa: E402

tema.encabezado("estaciones")
red = obtener_red()
nombres = nombres_estaciones()

# Los botones usan on_click: el cambio se hace ANTES de volver a pintar la
# pagina, asi lo que se ve siempre es el estado actual de la red.
if "aviso_estaciones" in st.session_state:
    texto, icono = st.session_state.pop("aviso_estaciones")
    st.toast(texto, icon=icono)


def avisar(texto, icono):
    st.session_state["aviso_estaciones"] = (texto, icono)


def cerrar(nombre):
    if red.cerrar(nombre):
        avisar(f"{nombre} quedó cerrada.", ":material/block:")


def reabrir(nombre):
    if red.reabrir(nombre):
        avisar(f"{nombre} está abierta otra vez.", ":material/check_circle:")


def deshacer():
    avisar(*(("Cambio deshecho.", ":material/undo:") if red.deshacer()
             else ("No hay nada que deshacer.", ":material/info:")))


def rehacer():
    avisar(*(("Cambio rehecho.", ":material/redo:") if red.rehacer()
             else ("No hay nada que rehacer.", ":material/info:")))


def elegir_sugerencia():
    """Clic en una sugerencia: pasa a ser el texto buscado."""
    elegida = st.session_state.get("sugerencia")
    if elegida:
        st.session_state["buscar"] = elegida
        st.session_state["sugerencia"] = None


pestana1, pestana2, pestana3 = st.tabs(["Buscar", "Rango", "Cerrar y reabrir"])

with pestana1:
    tema.html('<p class="tm-nota">Escribe el nombre de una estación y pulsa Enter: se muestra si existe y si '
              'está abierta (R1), y debajo aparecen las estaciones abiertas que empiezan igual (R2).</p>')
    c1, c2 = st.columns([4, 1])
    nombre = c1.text_input("Nombre de la estación", key="buscar",
                           placeholder="Por ejemplo: RICAURTE o POR").strip().upper()
    k = c2.number_input("Sugerencias", 1, 50, 8, help="Cuántas estaciones sugerir como máximo")
    if nombre:
        estado = red.estado(nombre)
        if estado != "NO EXISTE":
            tema.ficha_estacion(nombre, estado)
        sugerencias = [s for s in red.autocompletar(nombre, int(k)) if s != nombre]
        if sugerencias:
            tema.html(f'<p class="tm-nota">Estaciones abiertas que empiezan por «{tema.texto(nombre)}». '
                      'Toca una para verla:</p>')
            st.pills("Sugerencias", sugerencias, key="sugerencia", label_visibility="collapsed",
                     on_change=elegir_sugerencia)
        elif estado == "NO EXISTE":
            tema.ficha_estacion(nombre, estado)
            st.info("Ninguna estación abierta empieza por ese texto.")

with pestana2:
    tema.html('<p class="tm-nota">Todas las estaciones abiertas entre dos nombres, en orden alfabético '
              '(R3).</p>')
    c1, c2 = st.columns(2)
    desde = c1.selectbox("Desde", nombres, index=nombres.index("CALLE 26") if "CALLE 26" in nombres else 0)
    hasta = c2.selectbox("Hasta", nombres,
                         index=nombres.index("CALLE 72") if "CALLE 72" in nombres else len(nombres) - 1)
    lista = red.rango(desde, hasta)
    tema.html(f'<p><b>{len(lista)}</b> {"estación abierta" if len(lista) == 1 else "estaciones abiertas"} '
              f'entre {tema.texto(desde)} y {tema.texto(hasta)}</p>')
    if lista:
        tema.html(tema.chips(lista))

with pestana3:
    tema.html('<p class="tm-nota">Una estación cerrada desaparece de las búsquedas, el autocompletado, '
              'los rangos, el ranking y los viajes (R8).</p>')
    elegida = st.selectbox("Estación", nombres, index=None, placeholder="Elige una estación…")
    if elegida:
        estado = red.estado(elegida)
        tema.ficha_estacion(elegida, estado)
        b1, b2, _ = st.columns([1, 1, 3])
        b1.button("Cerrar", icon=":material/block:", type="primary", width="stretch",
                  disabled=estado != "ABIERTA", on_click=cerrar, args=(elegida,))
        b2.button("Reabrir", icon=":material/lock_open:", width="stretch",
                  disabled=estado != "CERRADA", on_click=reabrir, args=(elegida,))

    cerradas = [n for n in nombres if red.estado(n) == "CERRADA"]
    st.divider()
    if cerradas:
        tema.html(f'<p><b>Estaciones cerradas ahora ({len(cerradas)})</b></p>'
                  + tema.chips(cerradas, "tm-chip--cerrada"))
    else:
        tema.html('<p class="tm-nota">Todas las estaciones están abiertas.</p>')
    d1, d2, _ = st.columns([1, 1, 3])
    d1.button("Deshacer", icon=":material/undo:", width="stretch", on_click=deshacer)
    d2.button("Rehacer", icon=":material/redo:", width="stretch", on_click=rehacer)
