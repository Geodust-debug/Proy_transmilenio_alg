"""PARTE B -- Catalogo de estaciones: R1, R2, R3 y R8 (cerrar/reabrir).

ESTADO ACTUAL: BASE PROVISIONAL. Funciona, pero busca con un for (O(n)) y
autocompletar/rango devuelven []. Quien tiene la Parte B reemplaza TODO este
archivo por su version eficiente, MANTENIENDO estas firmas (la fachada
motor/red.py las llama tal cual):

    Estaciones(nombres)              nombres: lista de str (estaciones.csv)
    .estado(nombre)       -> "ABIERTA" | "CERRADA" | "NO EXISTE"            (R1)
    .autocompletar(prefijo, k) -> lista de hasta k nombres ABIERTOS que
                                  empiezan por prefijo, en orden alfabetico  (R2)
    .rango(desde, hasta)  -> lista de nombres ABIERTOS entre los dos nombres
                             (inclusive), orden alfabetico                   (R3)
    .cerrar(nombre)       -> True si cambio el estado; False si no existe o
                             ya estaba cerrada                               (R8)
    .reabrir(nombre)      -> True si cambio el estado; False si no existe o
                             ya estaba abierta                               (R8)
    .esta_abierta(nombre) -> bool (False si esta cerrada o no existe).
                             Lo usan TODOS los demas modulos: debe ser O(1).

Pistas (la decision es de ustedes; documenten en el README por que):
  * R1 se consulta "todo el tiempo": que cueste O(1).
  * R2 y R3 necesitan orden alfabetico: piensen en arreglo ordenado + busqueda
    binaria, trie, arbol de busqueda... y en como NO recorrer las cerradas.
  * Prohibido dentro de motor/: dict, set, sorted, .sort, min, max, in sobre
    listas, .index, .count, bisect, heapq, collections, functools.
    Ayudas permitidas: motor/estructuras.py (TablaHash, ordenar_mezcla).
  * Corran:  python pruebas/revisar_prohibidos.py
"""


class Estaciones:
    def __init__(self, nombres):
        self._nombres = list(nombres)
        self._cerradas = [False] * len(self._nombres)

    def _posicion(self, nombre):
        for i in range(len(self._nombres)):
            if self._nombres[i] == nombre:
                return i
        return -1

    def estado(self, nombre):
        i = self._posicion(nombre)
        if i < 0:
            return "NO EXISTE"
        if self._cerradas[i]:
            return "CERRADA"
        return "ABIERTA"

    def esta_abierta(self, nombre):
        return self.estado(nombre) == "ABIERTA"

    def cerrar(self, nombre):
        i = self._posicion(nombre)
        if i < 0 or self._cerradas[i]:
            return False
        self._cerradas[i] = True
        return True

    def reabrir(self, nombre):
        i = self._posicion(nombre)
        if i < 0 or not self._cerradas[i]:
            return False
        self._cerradas[i] = False
        return True

    def autocompletar(self, prefijo, k):
        return []          # TODO (Parte B): R2

    def rango(self, desde, hasta):
        return []          # TODO (Parte B): R3
