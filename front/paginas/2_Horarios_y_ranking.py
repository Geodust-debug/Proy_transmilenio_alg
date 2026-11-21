"""Pagina de la Parte C: proximo bus (R4) y ranking de estaciones (R6).
Solo llama al motor: ninguna regla vive aqui. Diseno: Parte E (front/visual/)."""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from comun import obtener_red, nombres_estaciones, rutas_que_pasan  # noqa: E402
from visual import tema  # noqa: E402

tema.encabezado("horarios")
COLOR = tema.acento("horarios")
red = obtener_red()
nombres = nombres_estaciones()


def minutos(hhmm):
    horas, mins = hhmm.split(":")
    return int(horas) * 60 + int(mins)


pestana1, pestana2 = st.tabs(["Próximo bus", "Ranking de estaciones"])

with pestana1:
    tema.html('<p class="tm-nota">¿A qué hora pasa el siguiente bus por una estación? Elige la estación y la hora '
              'desde la que esperas (R4).</p>')
    c1, c2 = st.columns([3, 1])
    estacion = c1.selectbox("Estación", nombres, index=None, placeholder="Elige una estación…")
    hora = c2.time_input("Desde las", value=datetime.time(8, 0), step=300)
    pedida = hora.strftime("%H:%M")

    if estacion:
        # las rutas se le preguntan a la red (no al CSV): incluyen lo que se agregó o quitó en Operar la red
        rutas = rutas_que_pasan(red, estacion)
        if red.estado(estacion) == "CERRADA":
            st.warning("La estación está cerrada: no pasan buses por ahí. Puedes reabrirla en Estaciones.")
        elif not rutas:
            st.info("Ninguna ruta pasa por esa estación.")
        else:
            filas = []
            for r in rutas:
                siguiente = red.proximo_bus(estacion, r, pedida)
                if siguiente is None:
                    filas.append((r, None, f"No hay más buses después de las {pedida}"))
                else:
                    espera = minutos(siguiente) - minutos(pedida)
                    nota = ("Justo a la hora que pediste" if espera == 0
                            else "Falta 1 minuto" if espera == 1 else f"Faltan {espera} minutos")
                    filas.append((r, siguiente, nota))
            filas.sort(key=lambda f: (f[1] is None, f[1] or "", f[0]))
            con_bus = [f for f in filas if f[1]]
            if con_bus:
                ruta0, hora0, _ = con_bus[0]
                espera = minutos(hora0) - minutos(pedida)
                detalle = ("Está pasando justo a la hora que pediste." if espera == 0
                           else f"Faltan <b>{espera} {'minuto' if espera == 1 else 'minutos'}</b> "
                                f"desde las {pedida}.")
                tema.tablero(ruta0, estacion, hora0, detalle, COLOR)
            else:
                st.info(f"Ya no pasan más buses por {estacion} después de las {pedida}.")
            tema.html(f'<p><b>{len(rutas)}</b> {"ruta pasa" if len(rutas) == 1 else "rutas pasan"} por '
                      f'{tema.texto(estacion)}. Próximo bus de cada una desde las {pedida}:</p>')
            tema.salidas(filas)
    else:
        tema.html('<p class="tm-nota">Elige una estación para ver qué rutas pasan por ella y cuándo sale el '
                  'próximo bus de cada una.</p>')

with pestana2:
    tema.html('<p class="tm-nota">Las estaciones abiertas por donde pasan más buses al día (R6). '
              'Las cerradas no aparecen.</p>')
    k = st.slider("¿Cuántas mostrar?", 1, 30, 10)
    top = red.ranking(k)
    if top:
        tema.html(f'<p>Las <b>{len(top)}</b> {"estación" if len(top) == 1 else "estaciones"} con más buses al día '
                  '(se actualiza al mover la barra):</p>')
        tema.ranking(top, COLOR)
    else:
        st.info("No hay estaciones abiertas para mostrar.")
