"""PARTE C -- Ranking de estaciones: R6.

ESTADO ACTUAL: BASE PROVISIONAL (devuelve []). Quien tiene la Parte C
reemplaza TODO este archivo, MANTENIENDO estas firmas:

    Ranking(nombres, horarios, esta_abierta)
        nombres      : lista con todos los nombres de estaciones
        horarios     : objeto Horarios (usar horarios.buses_en(nombre))
        esta_abierta : funcion nombre -> bool (cerradas NO entran al ranking)
    .invalidar() -> None. La fachada lo llama cuando se cierra/reabre una
                    estacion o se edita una ruta (el ranking pudo cambiar).
    .top(k) -> lista de (nombre, buses_por_dia) de las k estaciones ABIERTAS
               con mas buses, de mayor a menor.

Enunciado: "se consulta muy seguido y cambia poco" -> piensen en NO
recalcularlo en cada consulta. Decidan (y documenten) el desempate cuando
dos estaciones tienen los mismos buses (sugerencia: orden alfabetico).
Prohibido dentro de motor/: dict, set, sorted, .sort, min, max, in sobre
listas, .index, .count, bisect, heapq, collections, functools.
(Pueden hacer su propio heap o usar ordenar_mezcla de estructuras.py.)
"""


class Ranking:
    def __init__(self, nombres, horarios, esta_abierta):
        self._nombres = nombres
        self._horarios = horarios
        self._esta_abierta = esta_abierta

    def invalidar(self):
        return None        # TODO (Parte C)

    def top(self, k):
        return []          # TODO (Parte C): R6
