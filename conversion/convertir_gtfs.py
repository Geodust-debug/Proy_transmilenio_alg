"""Convierte el GTFS de TransMilenio en los tres CSV que lee el motor.

Uso (desde la raiz del repo):
    python conversion/convertir_gtfs.py ruta/al/gtfs.zip datos/
    python conversion/convertir_gtfs.py gtfs.zip datos/ --horas-24 descartar

Salida en la carpeta indicada:
    estaciones.csv   nombre
    rutas.csv        ruta,orden,estacion
    horarios.csv     ruta,estacion,hora      (HH:MM)

Fuera de motor/ SI se puede usar cualquier libreria; aqui solo se usa la libreria estandar.

DECISIONES (explicarlas en el README)
  * Estacion = nombre de parada en MAYUSCULAS, sin tildes y con espacios simples.
    Varias paradas (andenes) con el mismo nombre quedan como UNA estacion.
  * Ruta = <nombre corto de la ruta>-<sentido 1 o 2>: cada ruta va en un solo sentido.
  * Si una ruta tiene varios recorridos distintos en un mismo sentido, se usa el
    MAS FRECUENTE (el que mas viajes hacen); los viajes con otro recorrido se ignoran.
  * Horas: el GTFS usa horas como 25:10 para viajes que pasan de medianoche.
    --horas-24 envolver (por defecto): 25:10 -> 01:10 (son buses de la madrugada).
    --horas-24 descartar: se ignoran esas horas.
  * Un recorrido consecutivo que repite la estacion (dos andenes seguidos) se colapsa.

OJO: este script esta escrito segun el estandar GTFS y probado con un GTFS pequeno de
prueba (pruebas/probar_parte_c.py). Con el GTFS real hay que mirar stops.txt: si los
nombres traen sufijos (p. ej. "- Anden 1"), ajusten nombre_estacion().
"""
import argparse
import csv
import io
import itertools
import re
import unicodedata
import zipfile
from pathlib import Path


def nombre_estacion(texto):
    sin_tildes = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes.upper()).strip()


def leer_tabla(zf, nombre):
    """Itera las filas de un .txt del zip como diccionarios."""
    with zf.open(nombre) as crudo:
        yield from csv.DictReader(io.TextIOWrapper(crudo, encoding="utf-8-sig", newline=""))


def a_minutos(texto, modo):
    """'25:10:00' -> minutos del dia (o None si se descarta / esta vacio)."""
    texto = (texto or "").strip()
    if not texto:
        return None
    partes = texto.split(":")
    horas, minutos = int(partes[0]), int(partes[1])
    if horas >= 24:
        if modo == "descartar":
            return None
        horas %= 24
    return horas * 60 + minutos


def viajes_por_grupo(zf):
    """Itera (trip_id, filas) de stop_times.txt; exige que vengan agrupadas por trip_id."""
    terminados = set()
    filas = leer_tabla(zf, "stop_times.txt")
    for trip_id, grupo in itertools.groupby(filas, key=lambda f: f["trip_id"]):
        if trip_id in terminados:
            raise SystemExit("stop_times.txt no viene agrupado por trip_id; ordenenlo primero.")
        terminados.add(trip_id)
        yield trip_id, sorted(grupo, key=lambda f: int(f["stop_sequence"]))


def convertir(ruta_zip, carpeta_salida, modo_horas="envolver"):
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ruta_zip) as zf:
        paradas = {f["stop_id"]: nombre_estacion(f["stop_name"]) for f in leer_tabla(zf, "stops.txt")}
        nombres_ruta = {}
        for f in leer_tabla(zf, "routes.txt"):
            corto = (f.get("route_short_name") or "").strip() or f["route_id"]
            nombres_ruta[f["route_id"]] = corto
        ruta_de_viaje = {}
        for f in leer_tabla(zf, "trips.txt"):
            sentido = int(f.get("direction_id") or 0) + 1
            ruta_de_viaje[f["trip_id"]] = nombres_ruta[f["route_id"]] + "-" + str(sentido)

        # Pasada 1: cual es el recorrido mas frecuente de cada ruta.
        frecuencia = {}                      # ruta -> {recorrido: cuantos viajes}
        for trip_id, grupo in viajes_por_grupo(zf):
            ruta = ruta_de_viaje.get(trip_id)
            if ruta is None:
                continue
            recorrido = []
            for f in grupo:
                est = paradas.get(f["stop_id"])
                if est and (not recorrido or recorrido[-1] != est):
                    recorrido.append(est)
            tupla = tuple(recorrido)
            por_ruta = frecuencia.setdefault(ruta, {})
            por_ruta[tupla] = por_ruta.get(tupla, 0) + 1
        elegido = {}
        for ruta, por_ruta in frecuencia.items():
            elegido[ruta] = max(por_ruta.items(), key=lambda par: (par[1], len(par[0])))[0]

        # Pasada 2: horarios de las estaciones del recorrido elegido.
        with open(carpeta / "horarios.csv", "w", newline="", encoding="utf-8") as sal:
            w = csv.writer(sal)
            w.writerow(["ruta", "estacion", "hora"])
            for trip_id, grupo in viajes_por_grupo(zf):
                ruta = ruta_de_viaje.get(trip_id)
                if ruta is None:
                    continue
                valido = set(elegido[ruta])
                ultima = None
                for f in grupo:
                    est = paradas.get(f["stop_id"])
                    if not est or est == ultima or est not in valido:
                        continue
                    ultima = est
                    m = a_minutos(f.get("arrival_time") or f.get("departure_time"), modo_horas)
                    if m is not None:
                        w.writerow([ruta, est, "%02d:%02d" % (m // 60, m % 60)])

    rutas_ord = sorted(elegido.keys())
    with open(carpeta / "rutas.csv", "w", newline="", encoding="utf-8") as sal:
        w = csv.writer(sal)
        w.writerow(["ruta", "orden", "estacion"])
        for ruta in rutas_ord:
            for orden, est in enumerate(elegido[ruta], start=1):
                w.writerow([ruta, orden, est])
    todas = sorted({est for ruta in rutas_ord for est in elegido[ruta]})
    with open(carpeta / "estaciones.csv", "w", newline="", encoding="utf-8") as sal:
        w = csv.writer(sal)
        w.writerow(["nombre"])
        for est in todas:
            w.writerow([est])
    return len(todas), len(rutas_ord)


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="GTFS de TransMilenio -> 3 CSV")
    analizador.add_argument("zip_gtfs")
    analizador.add_argument("carpeta_salida")
    analizador.add_argument("--horas-24", choices=["envolver", "descartar"], default="envolver")
    args = analizador.parse_args()
    estaciones, rutas = convertir(args.zip_gtfs, args.carpeta_salida, args.horas_24)
    print("Listo: %d estaciones y %d rutas en %s" % (estaciones, rutas, args.carpeta_salida))
