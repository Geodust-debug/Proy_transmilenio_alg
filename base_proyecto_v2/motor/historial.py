"""PARTE D -- Historial para deshacer / rehacer: R9.

ESTADO ACTUAL: BASE PROVISIONAL (no guarda nada). Quien tiene la Parte D
reemplaza TODO este archivo, MANTENIENDO estas firmas:

    Historial()
    .registrar(orden) -> None. Guarda una operacion nueva y BORRA todo lo que
                         hubiera para rehacer ("un cambio nuevo borra el rehacer").
    .deshacer() -> la ultima orden registrada (que pasa a poder rehacerse),
                   o None si no hay nada que deshacer.
    .rehacer()  -> la ultima orden deshecha (vuelve a poder deshacerse),
                   o None si no hay nada que rehacer.

`orden` es una tupla que este archivo NO interpreta, solo guarda y devuelve:
    ("cerrar", nombre)   ("reabrir", nombre)
    ("agregar", ruta, nueva, despues_de)   ("quitar", ruta, estacion, anterior)
(La fachada motor/red.py es quien ejecuta la inversa o la directa.)

Pista: dos estructuras LIFO. Cual es la costo de cada operacion?
Prohibido dentro de motor/: dict, set, sorted, .sort, min, max, in sobre
listas, .index, .count, bisect, heapq, collections, functools.
"""


class Historial:
    def __init__(self):
        pass

    def registrar(self, orden):
        return None        # TODO (Parte D): R9

    def deshacer(self):
        return None        # TODO (Parte D): R9

    def rehacer(self):
        return None        # TODO (Parte D): R9
