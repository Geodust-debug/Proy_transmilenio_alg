"""Estructuras y algoritmos compartidos por todo el motor.

Aqui NO se usa dict, set, sorted, min, max, bisect, heapq ni collections
(estan prohibidos dentro de motor/). Todo se construye con listas.

Contenido:
    TablaHash      -> "diccionario" propio (clave -> valor) con encadenamiento.
    ordenar_mezcla -> merge sort estable (O(n log n)).
"""


class TablaHash:
    """Tabla hash con encadenamiento (separate chaining).

    Idea: un arreglo de "cubetas". La clave se convierte en un entero con
    hash(clave) y el indice de la cubeta es hash(clave) % capacidad.
    Cada cubeta es una lista pequena de pares [clave, valor]. Si dos claves
    caen en la misma cubeta (colision) se recorre esa lista corta.

    Cuando hay mas de 0.75 elementos por cubeta, se duplica la capacidad y se
    reubican todos los pares (rehash). Asi las cubetas siguen siendo cortas
    y poner/obtener/eliminar cuestan O(1) en promedio (amortizado).

    Las claves pueden ser str, int o tuplas de ellos.
    """

    def __init__(self, capacidad=16):
        self._capacidad = capacidad
        self._cubetas = [None] * capacidad   # None = cubeta vacia
        self._n = 0

    def __len__(self):
        return self._n

    def _buscar(self, clave):
        """Devuelve el par [clave, valor] o None si no existe."""
        cubeta = self._cubetas[hash(clave) % self._capacidad]
        if cubeta is not None:
            for par in cubeta:
                if par[0] == clave:
                    return par
        return None

    def obtener(self, clave, defecto=None):
        par = self._buscar(clave)
        if par is None:
            return defecto
        return par[1]

    def contiene(self, clave):
        return self._buscar(clave) is not None

    def poner(self, clave, valor):
        par = self._buscar(clave)
        if par is not None:
            par[1] = valor
            return
        if (self._n + 1) * 4 > self._capacidad * 3:   # factor de carga > 0.75
            self._crecer()
        indice = hash(clave) % self._capacidad
        if self._cubetas[indice] is None:
            self._cubetas[indice] = []
        self._cubetas[indice].append([clave, valor])
        self._n += 1

    def eliminar(self, clave):
        """Quita la clave. True si estaba, False si no."""
        cubeta = self._cubetas[hash(clave) % self._capacidad]
        if cubeta is None:
            return False
        for i in range(len(cubeta)):
            if cubeta[i][0] == clave:
                cubeta.pop(i)
                self._n -= 1
                return True
        return False

    def _crecer(self):
        nueva_capacidad = self._capacidad * 2
        nuevas = [None] * nueva_capacidad
        for cubeta in self._cubetas:
            if cubeta is not None:
                for par in cubeta:
                    indice = hash(par[0]) % nueva_capacidad
                    if nuevas[indice] is None:
                        nuevas[indice] = []
                    nuevas[indice].append(par)
        self._cubetas = nuevas
        self._capacidad = nueva_capacidad


def ordenar_mezcla(datos):
    """Merge sort (de abajo hacia arriba). Devuelve una lista NUEVA ordenada.

    - Funciona con cualquier cosa comparable con < (int, str, tuplas).
    - Es estable: si dos elementos son iguales, conserva su orden original.
    - Costo: O(n log n) tiempo, O(n) memoria extra.

    Idea: una lista de 1 elemento ya esta ordenada. Mezclamos bloques de
    tamano 1 para formar bloques ordenados de 2, luego de 4, de 8... hasta
    que un solo bloque cubre toda la lista (log2 n vueltas, cada una O(n)).
    """
    n = len(datos)
    origen = datos[:]
    destino = [None] * n
    ancho = 1
    while ancho < n:
        inicio = 0
        while inicio < n:
            medio = inicio + ancho
            if medio > n:
                medio = n
            fin = inicio + 2 * ancho
            if fin > n:
                fin = n
            i = inicio
            j = medio
            k = inicio
            while i < medio and j < fin:
                if origen[j] < origen[i]:      # estricto => estable
                    destino[k] = origen[j]
                    j += 1
                else:
                    destino[k] = origen[i]
                    i += 1
                k += 1
            while i < medio:
                destino[k] = origen[i]
                i += 1
                k += 1
            while j < fin:
                destino[k] = origen[j]
                j += 1
                k += 1
            inicio += 2 * ancho
        origen, destino = destino, origen
        ancho *= 2
    return origen
