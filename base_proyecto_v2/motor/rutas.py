"""PARTE D -- Rutas editables: R7 (agregar/quitar parada, recorrido).

ESTADO ACTUAL: BASE PROVISIONAL de solo lectura (O(n) y sin editar). Quien
tiene la Parte D reemplaza TODO este archivo, MANTENIENDO estas firmas:

    Rutas(filas)        filas: lista de [ruta, orden, estacion] (rutas.csv)
                        (no asuman que las filas vienen ordenadas por `orden`)
    .nombres()          -> lista de nombres de ruta (la usa viaje.py)
    .recorrido(ruta, al_reves=False) -> lista de estaciones en orden
                                        ([] si la ruta no existe)           (R7)
    .tiene_parada(ruta, estacion) -> bool  (False si la ruta no existe)
    .anterior(ruta, estacion) -> nombre de la parada anterior, o None si es
                                 la primera. Solo se llama si tiene_parada.
    .agregar_parada(ruta, nueva, despues_de) -> bool                        (R7)
        True si inserto `nueva` JUSTO DESPUES de `despues_de`.
        False si la ruta no existe, despues_de no esta en la ruta, o `nueva`
        ya esta en la ruta. Caso especial (lo usa "deshacer"): si
        despues_de es None, inserta `nueva` AL INICIO de la ruta y da True.
    .quitar_parada(ruta, estacion) -> bool                                  (R7)
        True si la quito; False si la ruta o la parada no existen.

Pistas: "agregan y quitan todo el tiempo" y "recorrido en los dos sentidos"
-> que estructura inserta/borra en O(1) conociendo el vecino y se recorre
en ambos sentidos? Para encontrar el nodo rapido: TablaHash (estructuras.py).
Prohibido dentro de motor/: dict, set, sorted, .sort, min, max, in sobre
listas, .index, .count, bisect, heapq, collections, functools.
"""


class Rutas:
    def __init__(self, filas):
        self._nombres = []     # nombres de ruta, en orden de aparicion
        self._paradas = []     # _paradas[i] = lista de estaciones de la ruta i
        for fila in filas:     # BASE: asume filas ya ordenadas por `orden`
            i = self._buscar_ruta(fila[0])
            if i < 0:
                self._nombres.append(fila[0])
                self._paradas.append([])
                i = len(self._nombres) - 1
            self._paradas[i].append(fila[2])

    def _buscar_ruta(self, ruta):
        for i in range(len(self._nombres)):
            if self._nombres[i] == ruta:
                return i
        return -1

    def nombres(self):
        return self._nombres[:]

    def recorrido(self, ruta, al_reves=False):
        i = self._buscar_ruta(ruta)
        if i < 0:
            return []
        if al_reves:
            return self._paradas[i][::-1]
        return self._paradas[i][:]

    def tiene_parada(self, ruta, estacion):
        i = self._buscar_ruta(ruta)
        if i < 0:
            return False
        for nombre in self._paradas[i]:
            if nombre == estacion:
                return True
        return False

    def anterior(self, ruta, estacion):
        i = self._buscar_ruta(ruta)
        if i < 0:
            return None
        paradas = self._paradas[i]
        for j in range(len(paradas)):
            if paradas[j] == estacion:
                if j == 0:
                    return None
                return paradas[j - 1]
        return None

    def agregar_parada(self, ruta, nueva, despues_de):
        return False       # TODO (Parte D): R7

    def quitar_parada(self, ruta, estacion):
        return False       # TODO (Parte D): R7
