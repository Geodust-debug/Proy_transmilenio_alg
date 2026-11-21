"""PARTE C -- Horarios: R4 (proximo bus) y conteo de buses por estacion.

ESTADO ACTUAL: BASE PROVISIONAL (devuelve None / 0). Quien tiene la Parte C
reemplaza TODO este archivo, MANTENIENDO estas firmas:

    Horarios(filas)     filas: lista de [ruta, estacion, "HH:MM"] (horarios.csv)
    .proximo_bus(estacion, ruta, hora) -> "HH:MM" del siguiente bus de esa ruta
                  en esa estacion, o None si no hay mas ese dia (o no existe)  (R4)
    .buses_en(estacion) -> int: cuantos buses pasan por esa estacion al dia
                  (sumando todas las rutas). Lo usa ranking.py                 (R6)
    .agregar_parada(ruta, nueva, despues_de) -> None. Aviso de que la ruta
                  ahora pasa tambien por `nueva`. Decidan que horarios/conteo
                  le corresponden (ver docs/reparto.md).
    .quitar_parada(ruta, estacion) -> None. Aviso de que la ruta ya no pasa
                  por `estacion`.
    OJO: deshacer vuelve a llamar a estos dos avisos (con la misma firma),
    asi que lo que quiten debe poder restaurarse.

Datos reales (revisados): las horas de un mismo (ruta, estacion) vienen
DESORDENADAS y a veces REPETIDAS en el CSV (hay que ordenar y decidir que
hacer con repetidas). Las horas son "HH:MM" con ceros a la izquierda.
La fachada ya devuelve None si la estacion esta cerrada o no existe.

Pregunta abierta para el profesor: si hay un bus EXACTAMENTE a la hora
pedida, cuenta como "siguiente"? (sugerencia: si, >=). Documentenlo.

Pistas: cientos de horas por (ruta, estacion) -> piensen en guardarlas
ordenadas como minutos (int) y en busqueda binaria. Para agrupar por
(ruta, estacion) sin dict: TablaHash de motor/estructuras.py.
Prohibido dentro de motor/: dict, set, sorted, .sort, min, max, in sobre
listas, .index, .count, bisect, heapq, collections, functools.
"""


class Horarios:
    def __init__(self, filas):
        self._filas = filas

    def proximo_bus(self, estacion, ruta, hora):
        return None        # TODO (Parte C): R4

    def buses_en(self, estacion):
        return 0           # TODO (Parte C): conteo para R6

    def agregar_parada(self, ruta, nueva, despues_de):
        return None        # TODO (Parte C)

    def quitar_parada(self, ruta, estacion):
        return None        # TODO (Parte C)
