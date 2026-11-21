"""PARTE D (Tomas) -- Rutas editables: R7 (agregar/quitar parada y recorrido).

ESTRUCTURA: una LISTA DOBLEMENTE ENLAZADA por ruta.
    Cada parada es un "nodo" que sabe cual es su siguiente y su anterior.
    Los nodos viven en arreglos paralelos (no hay objetos sueltos):
        _est[nodo]   nombre de la estacion
        _sig[nodo]   nodo siguiente  (-1 = no hay)
        _ant[nodo]   nodo anterior   (-1 = no hay)
    Por ruta r:  _cabeza[r] (primer nodo), _cola[r] (ultimo nodo), _largo[r].
    _nodo_de : TablaHash (ruta, estacion) -> nodo, para encontrar una parada de
               una ruta en O(1) sin recorrer la lista.
    _libres  : pila de nodos liberados, para reutilizarlos.

POR QUE ASI
    * Agregar una parada "justo despues de X" y quitar una parada son cambiar
      unos pocos punteros: O(1), sin mover el resto (un arreglo mover O(largo)).
    * El recorrido "al reves" es seguir los punteros _ant desde la cola: la
      misma lista sirve en los dos sentidos.
    * La tabla hash evita buscar la parada recorriendo la ruta.

SUPUESTOS (documentarlos en el README)
    * Una estacion aparece una sola vez por ruta (se cumple en los datos reales).
    * No hace falta que las filas del CSV vengan ordenadas: se ordenan por `orden`.
    * Se puede quitar cualquier parada, incluso la primera o la ultima.

COSTOS (L = paradas de la ruta, R = rutas, N = filas de rutas.csv)
    cargar : O(N log L)    tiene_parada / anterior / agregar / quitar : O(1)
    recorrido : O(L)  (hay que devolver las L paradas)
"""
from .estructuras import TablaHash, ordenar_mezcla


class Rutas:
    def __init__(self, filas):
        self._indice = TablaHash()          # nombre de ruta -> numero de ruta
        self._nombres = []
        self._cabeza = []
        self._cola = []
        self._largo = []
        self._est = []
        self._sig = []
        self._ant = []
        self._libres = []
        self._nodo_de = TablaHash()
        # 1. Agrupar las filas por ruta: (orden, estacion).
        pendientes = []
        for fila in filas:
            r = self._indice.obtener(fila[0])
            if r is None:
                r = len(self._nombres)
                self._indice.poner(fila[0], r)
                self._nombres.append(fila[0])
                self._cabeza.append(-1)
                self._cola.append(-1)
                self._largo.append(0)
                pendientes.append([])
            pendientes[r].append((int(fila[1]), fila[2]))
        # 2. Ordenar por `orden` y construir la lista enlazada de cada ruta.
        for r in range(len(self._nombres)):
            for par in ordenar_mezcla(pendientes[r]):
                self._poner_al_final(r, par[1])

    # ------------------------------------------------------ nodos internos
    def _nuevo_nodo(self, estacion):
        if len(self._libres) > 0:
            nodo = self._libres.pop()
            self._est[nodo] = estacion
            self._sig[nodo] = -1
            self._ant[nodo] = -1
        else:
            nodo = len(self._est)
            self._est.append(estacion)
            self._sig.append(-1)
            self._ant.append(-1)
        return nodo

    def _poner_al_final(self, r, estacion):
        if self._nodo_de.contiene((r, estacion)):      # estacion repetida en la ruta: se ignora
            return
        nodo = self._nuevo_nodo(estacion)
        self._nodo_de.poner((r, estacion), nodo)
        ultimo = self._cola[r]
        if ultimo == -1:
            self._cabeza[r] = nodo
        else:
            self._sig[ultimo] = nodo
            self._ant[nodo] = ultimo
        self._cola[r] = nodo
        self._largo[r] += 1

    # --------------------------------------------------------- consultas
    def nombres(self):
        return self._nombres[:]

    def tiene_parada(self, ruta, estacion):
        r = self._indice.obtener(ruta)
        return r is not None and self._nodo_de.contiene((r, estacion))

    def anterior(self, ruta, estacion):
        r = self._indice.obtener(ruta)
        if r is None:
            return None
        nodo = self._nodo_de.obtener((r, estacion))
        if nodo is None or self._ant[nodo] == -1:
            return None
        return self._est[self._ant[nodo]]

    def recorrido(self, ruta, al_reves=False):
        resultado = []
        r = self._indice.obtener(ruta)
        if r is None:
            return resultado
        if al_reves:
            nodo = self._cola[r]
            while nodo != -1:
                resultado.append(self._est[nodo])
                nodo = self._ant[nodo]
        else:
            nodo = self._cabeza[r]
            while nodo != -1:
                resultado.append(self._est[nodo])
                nodo = self._sig[nodo]
        return resultado

    # ----------------------------------------------------------- ediciones
    def agregar_parada(self, ruta, nueva, despues_de):
        """True si inserto `nueva` justo despues de `despues_de` (None = al inicio)."""
        r = self._indice.obtener(ruta)
        if r is None or self._nodo_de.contiene((r, nueva)):
            return False
        if despues_de is None:                          # insertar al inicio
            nodo = self._nuevo_nodo(nueva)
            primero = self._cabeza[r]
            self._sig[nodo] = primero
            if primero == -1:
                self._cola[r] = nodo
            else:
                self._ant[primero] = nodo
            self._cabeza[r] = nodo
        else:
            previo = self._nodo_de.obtener((r, despues_de))
            if previo is None:
                return False
            nodo = self._nuevo_nodo(nueva)
            siguiente = self._sig[previo]
            self._sig[previo] = nodo
            self._ant[nodo] = previo
            self._sig[nodo] = siguiente
            if siguiente == -1:
                self._cola[r] = nodo
            else:
                self._ant[siguiente] = nodo
        self._nodo_de.poner((r, nueva), nodo)
        self._largo[r] += 1
        return True

    def quitar_parada(self, ruta, estacion):
        r = self._indice.obtener(ruta)
        if r is None:
            return False
        nodo = self._nodo_de.obtener((r, estacion))
        if nodo is None:
            return False
        previo = self._ant[nodo]
        siguiente = self._sig[nodo]
        if previo == -1:
            self._cabeza[r] = siguiente
        else:
            self._sig[previo] = siguiente
        if siguiente == -1:
            self._cola[r] = previo
        else:
            self._ant[siguiente] = previo
        self._nodo_de.eliminar((r, estacion))
        self._libres.append(nodo)
        self._largo[r] -= 1
        return True
