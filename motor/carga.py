"""Lectura de los tres CSV. Devuelve listas simples (nada de diccionarios).

Cada fila queda como lista de textos, tal cual viene en el CSV:
    estaciones : [nombre]
    rutas      : [ruta, orden, estacion]
    horarios   : [ruta, estacion, "HH:MM"]
Cada modulo (Parte B, C, D, A) arma a partir de estas filas SU propia estructura.
"""
import csv


class Datos:
    def __init__(self, estaciones, rutas, horarios):
        self.estaciones = estaciones   # lista de nombres (str)
        self.rutas = rutas             # lista de [ruta, orden, estacion]
        self.horarios = horarios       # lista de [ruta, estacion, hora]


def _leer_filas(ruta_archivo):
    filas = []
    with open(ruta_archivo, newline="", encoding="utf-8-sig") as archivo:
        primera = True
        for fila in csv.reader(archivo):
            if primera:          # encabezado
                primera = False
                continue
            if len(fila) == 0:   # linea vacia
                continue
            filas.append(fila)
    return filas


def cargar_datos(carpeta):
    # Se une con "/" (funciona tambien en Windows) para no usar el modulo os.
    if len(carpeta) > 0 and (carpeta[-1] == "/" or carpeta[-1] == "\\"):
        base = carpeta
    else:
        base = carpeta + "/"
    estaciones = []
    for fila in _leer_filas(base + "estaciones.csv"):
        estaciones.append(fila[0])
    rutas = _leer_filas(base + "rutas.csv")
    horarios = _leer_filas(base + "horarios.csv")
    return Datos(estaciones, rutas, horarios)
