"""Generador de redes sinteticas con el MISMO formato de los tres CSV.

Sirve para el panel de rendimiento (R11): crear redes de 10.000, 20.000,
40.000 y 80.000 estaciones y medir como crece cada operacion del motor.
Esta fuera de motor/, asi que aqui SI se puede usar cualquier libreria.

Uso desde la terminal (desde la raiz del repo):
    python herramientas/generar_red.py 10000 carpeta_salida
"""
import csv
import random
import sys
from pathlib import Path

PREFIJOS = ["CALLE", "CARRERA", "AVENIDA", "PORTAL", "PARQUE", "BARRIO", "PUENTE", "TERMINAL"]


class RedGenerada:
    """Los datos de la red generada, para poder armar consultas validas."""

    def __init__(self, carpeta, estaciones, rutas):
        self.carpeta = carpeta
        self.estaciones = estaciones      # lista de nombres
        self.rutas = rutas                # lista de (nombre_ruta, [estaciones en orden])


def generar_red(carpeta, n_estaciones, semilla=1, paradas_por_ruta=12, viajes_por_ruta=6):
    """Escribe estaciones.csv, rutas.csv y horarios.csv en `carpeta`.

    * n_estaciones nombres unicos (p. ej. "PORTAL 1234").
    * n_estaciones // 5 rutas, cada una con `paradas_por_ruta` estaciones distintas.
    * `viajes_por_ruta` horarios por (ruta, estacion), escritos viaje por viaje
      (como en el CSV real: por estacion quedan desordenados y a veces repetidos).
    """
    azar = random.Random(semilla)
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    estaciones = []
    for i in range(n_estaciones):
        estaciones.append(PREFIJOS[azar.randrange(len(PREFIJOS))] + " " + str(i))

    n_rutas = max(2, n_estaciones // 5)
    largo = min(paradas_por_ruta, n_estaciones)
    rutas = []
    for r in range(n_rutas):
        indices = azar.sample(range(n_estaciones), largo)
        rutas.append(("G" + str(r) + "-1", [estaciones[i] for i in indices]))

    with open(carpeta / "estaciones.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nombre"])
        for nombre in estaciones:
            w.writerow([nombre])

    with open(carpeta / "rutas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ruta", "orden", "estacion"])
        for nombre, paradas in rutas:
            for orden, estacion in enumerate(paradas, start=1):
                w.writerow([nombre, orden, estacion])

    with open(carpeta / "horarios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ruta", "estacion", "hora"])
        for nombre, paradas in rutas:
            for _ in range(viajes_por_ruta):
                salida = azar.randint(5 * 60, 20 * 60)          # minutos desde las 00:00
                for orden, estacion in enumerate(paradas):
                    minutos = salida + 2 * orden
                    w.writerow([nombre, estacion, "%02d:%02d" % (minutos // 60, minutos % 60)])

    return RedGenerada(str(carpeta), estaciones, rutas)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python herramientas/generar_red.py <n_estaciones> <carpeta_salida>")
        sys.exit(1)
    red = generar_red(sys.argv[2], int(sys.argv[1]))
    print("Red de %d estaciones y %d rutas en %s" % (len(red.estaciones), len(red.rutas), red.carpeta))
