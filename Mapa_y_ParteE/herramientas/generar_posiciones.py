"""Genera datos/posiciones.csv: donde se dibuja cada estacion en el mapa del front.

El GTFS que se uso para armar la red no trae coordenadas, asi que el mapa es
ESQUEMATICO (como los planos de metro): no esta a escala. Para que se parezca
a Bogota se fijan, de forma aproximada, unas 30 estaciones conocidas (los
portales y algunas estaciones de las troncales) y el resto se acomoda solo con
un "grafo de resortes": las estaciones consecutivas de una ruta se atraen,
las demas se alejan un poco.

Uso (desde la raiz del repo):  python herramientas/generar_posiciones.py
Solo se corre una vez; el resultado queda guardado en datos/posiciones.csv.
Este script NO es del motor: aqui si se pueden usar librerias.
"""
import csv
import math
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# (latitud, longitud) aproximadas de estaciones conocidas. Son solo "anclas".
ANCLAS = {
    "PORTAL NORTE": (4.7545, -74.0460), "CALLE 187": (4.7655, -74.0450),
    "TOBERIN": (4.7470, -74.0440), "CALLE 161": (4.7380, -74.0470),
    "CALLE 146": (4.7290, -74.0500), "CALLE 127": (4.7110, -74.0545),
    "CALLE 100": (4.6860, -74.0560), "CALLE 85": (4.6735, -74.0590),
    "CALLE 72": (4.6580, -74.0620), "CALLE 63": (4.6490, -74.0640),
    "CALLE 45": (4.6330, -74.0660), "CALLE 26": (4.6270, -74.0690),
    "AV. JIMENEZ": (4.6020, -74.0685), "CALLE 19": (4.6045, -74.0680),
    "MUSEO DEL ORO": (4.6020, -74.0720), "UNIVERSIDADES": (4.6018, -74.0650),
    "U. NACIONAL": (4.6360, -74.0830), "RICAURTE": (4.6112, -74.0932),
    "PORTAL 80": (4.7090, -74.1090), "PORTAL SUBA": (4.7440, -74.0950),
    "PORTAL ELDORADO": (4.6590, -74.1130), "PORTAL AMERICAS": (4.6270, -74.1370),
    "PORTAL TUNAL": (4.5740, -74.1300), "PORTAL SUR": (4.5950, -74.1850),
    "PORTAL USME": (4.5290, -74.1190), "PORTAL 20 DE JULIO": (4.5890, -74.0980),
    "BANDERAS": (4.6180, -74.1210), "CALLE 76": (4.6610, -74.0600),
    "PUENTE ARANDA": (4.6190, -74.1100), "AV. CHILE": (4.6740, -74.0610),
    "CALLE 40 S.": (4.5880, -74.1030), "BOSA": (4.6120, -74.1880),
}

ANCHO, ALTO = 1000, 700
MARGEN = 40


def leer():
    nombres = [f[0] for f in list(csv.reader(open(RAIZ / "datos" / "estaciones.csv",
                                                  encoding="utf-8-sig")))[1:] if f]
    rutas = {}
    for f in list(csv.reader(open(RAIZ / "datos" / "rutas.csv", encoding="utf-8-sig")))[1:]:
        if f:
            rutas.setdefault(f[0], []).append(f[2])
    return nombres, rutas


def main():
    random.seed(7)
    nombres, rutas = leer()
    indice = {n: i for i, n in enumerate(nombres)}
    n = len(nombres)

    aristas = {}
    for paradas in rutas.values():
        for a, b in zip(paradas, paradas[1:]):
            if a in indice and b in indice and a != b:
                clave = (min(indice[a], indice[b]), max(indice[a], indice[b]))
                aristas[clave] = aristas.get(clave, 0) + 1

    # lat/lon -> plano (x crece al este, y crece al sur)
    lats = [v[0] for v in ANCLAS.values()]
    lons = [v[1] for v in ANCLAS.values()]
    la0, la1, lo0, lo1 = min(lats), max(lats), min(lons), max(lons)
    escala = min((ANCHO - 2 * MARGEN) / (lo1 - lo0), (ALTO - 2 * MARGEN) / (la1 - la0))
    ox = (ANCHO - escala * (lo1 - lo0)) / 2
    oy = (ALTO - escala * (la1 - la0)) / 2
    ancla_xy = {indice[k]: (ox + (v[1] - lo0) * escala, oy + (la1 - v[0]) * escala)
                for k, v in ANCLAS.items() if k in indice}

    # posicion inicial: ancla si tiene; si no, el promedio de sus vecinas ancladas (o al azar)
    vecinas = {i: [] for i in range(n)}
    for (a, b) in aristas:
        vecinas[a].append(b)
        vecinas[b].append(a)
    pos = [None] * n
    for i, p in ancla_xy.items():
        pos[i] = list(p)
    for _ in range(40):
        for i in range(n):
            if pos[i] is None:
                con = [pos[j] for j in vecinas[i] if pos[j] is not None]
                if con:
                    pos[i] = [sum(p[0] for p in con) / len(con) + random.uniform(-6, 6),
                              sum(p[1] for p in con) / len(con) + random.uniform(-6, 6)]
    for i in range(n):
        if pos[i] is None:
            pos[i] = [random.uniform(MARGEN, ANCHO - MARGEN), random.uniform(MARGEN, ALTO - MARGEN)]

    # relajacion: resortes entre vecinas, repulsion general y un hilo hacia el ancla
    ideal = 46.0
    for paso in range(600):
        fuerza = [[0.0, 0.0] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx, dy = pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]
                d2 = dx * dx + dy * dy + 0.01
                if d2 < 130 * 130:
                    d = math.sqrt(d2)
                    f = 2600.0 / d2
                    fuerza[i][0] += f * dx / d
                    fuerza[i][1] += f * dy / d
                    fuerza[j][0] -= f * dx / d
                    fuerza[j][1] -= f * dy / d
        for (a, b), veces in aristas.items():
            dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
            d = math.sqrt(dx * dx + dy * dy) + 0.01
            f = 0.045 * (d - ideal) * (1 + 0.2 * min(veces, 4))
            fuerza[a][0] += f * dx / d
            fuerza[a][1] += f * dy / d
            fuerza[b][0] -= f * dx / d
            fuerza[b][1] -= f * dy / d
        enfriar = 1.0 - paso / 600
        for i in range(n):
            if i in ancla_xy:
                ax, ay = ancla_xy[i]
                fuerza[i][0] += 0.12 * (ax - pos[i][0])
                fuerza[i][1] += 0.12 * (ay - pos[i][1])
            mx = max(-6.0, min(6.0, fuerza[i][0])) * (0.2 + 0.8 * enfriar)
            my = max(-6.0, min(6.0, fuerza[i][1])) * (0.2 + 0.8 * enfriar)
            pos[i][0] += mx
            pos[i][1] += my

    # se ajusta al lienzo
    xs = [p[0] for p in pos]
    ys = [p[1] for p in pos]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    # el plano es esquematico: se estira para llenar el lienzo (que es mas ancho que alto)
    kx = (ANCHO - 2 * MARGEN) / (x1 - x0)
    ky = (ALTO - 2 * MARGEN) / (y1 - y0)
    cx = cy = MARGEN

    with open(RAIZ / "datos" / "posiciones.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["estacion", "x", "y"])
        for i, nombre in enumerate(nombres):
            w.writerow([nombre, round(cx + (pos[i][0] - x0) * kx, 1), round(cy + (pos[i][1] - y0) * ky, 1)])
    print(f"datos/posiciones.csv listo: {n} estaciones.")


if __name__ == "__main__":
    main()
