"""Animaciones interactivas (Parte E): el viaje en el mapa y la fila de la hora pico.

Son paginas HTML pequenas (en visual/plantillas/) que se llenan con los datos
que devolvio el motor y se muestran con components.html. Aqui solo se ordenan
y se resumen esos datos para dibujarlos; las reglas siguen en motor/.
"""
import json
import math
from pathlib import Path

import streamlit.components.v1 as components

from . import dibujos

_PLANTILLAS = Path(__file__).resolve().parent / "plantillas"
POR_FILA = 7          # paradas por fila del mapa en pantallas anchas


def _plantilla(nombre, datos):
    codigo = (_PLANTILLAS / nombre).read_text(encoding="utf-8")
    codigo = codigo.replace("__BUS__", dibujos.bus().replace("`", ""))
    return codigo.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))


# ------------------------------------------------------------------ viaje
def mapa_viaje(tramos):
    """tramos: lista de (ruta, [paradas desde donde sube hasta donde baja])."""
    datos_tramos = []
    total = 0
    for ruta, paradas in tramos:
        fondo, texto = dibujos.color_ruta(ruta)
        if datos_tramos and datos_tramos[-1]["color"] == fondo:
            fondo, texto = dibujos.GRAFITO, dibujos.BLANCO   # dos rutas del mismo color: se distinguen
        datos_tramos.append({"ruta": ruta, "color": fondo, "texto": texto, "paradas": paradas})
        total += len(paradas)
    total -= len(tramos) - 1                     # la de transbordo se cuenta una vez
    resumen = "Mapa del viaje: " + ", luego ".join(
        f"ruta {r} de {p[0]} a {p[-1]}" for r, p in tramos)
    filas = math.ceil(total / POR_FILA)
    alto_svg = (64 + (filas - 1) * 136 + 86) * 1.06   # el svg mide ~1060 px de ancho
    components.html(
        _plantilla("viaje.html", {"tramos": datos_tramos, "resumen": resumen, "por_fila": POR_FILA}),
        height=int(alto_svg + 62), scrolling=True,
    )


# ------------------------------------------------------------------ hora pico
MAX_CUADROS = 240     # buses que se animan como maximo (si hay mas, se agrupan)
MAX_FIGURAS = 84      # figuras dibujadas en el anden como maximo


def resumen_fila(llegadas, salidas):
    """Por cada bus que salio con gente: [hora, llegaron, subieron, quedaron en la fila]."""
    orden = sorted(llegadas)
    suben = {}
    for s in salidas:
        suben[s] = suben.get(s, 0) + 1
    buses = []
    i, cola = 0, 0
    for t in sorted(suben):
        llegan = 0
        while i < len(orden) and orden[i] <= t:
            llegan += 1
            i += 1
        cola += llegan - suben[t]
        buses.append([t, llegan, suben[t], cola])
    return buses


def anden_hora_pico(llegadas, salidas):
    buses = resumen_fila(llegadas, salidas)
    total_buses = len(buses)
    grupo = max(1, math.ceil(total_buses / MAX_CUADROS))
    cuadros = []
    for g in range(0, total_buses, grupo):
        parte = buses[g:g + grupo]
        cuadros.append([parte[-1][0], sum(b[1] for b in parte), sum(b[2] for b in parte), parte[-1][3]])
    mayor = max([c[3] + c[2] for c in cuadros] + [1])
    escala = max(1, math.ceil(mayor / MAX_FIGURAS))
    datos = {"buses": cuadros, "grupo": grupo, "total_buses": total_buses,
             "escala": escala, "max_figuras": MAX_FIGURAS}
    components.html(_plantilla("fila.html", datos), height=640, scrolling=True)
