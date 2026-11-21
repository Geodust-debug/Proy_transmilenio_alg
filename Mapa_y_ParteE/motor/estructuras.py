"""Estructuras y algoritmos compartidos por todo el motor.

Aqui NO se usa dict, set, sorted, min, max, bisect, heapq ni collections
(estan prohibidos dentro de motor/). Todo se construye con listas.

Contenido:
    TablaHash      -> "diccionario" propio (clave -> valor) con encadenamiento.
    ordenar_mezcla -> merge sort estable (O(n log n)).

Optimizado en la Parte E (misma interfaz, mismos resultados, menos trabajo):
    * TablaHash: la capacidad es siempre potencia de 2, asi el indice de la
      cubeta sale con `hash & (capacidad - 1)` en vez de `%`; cada operacion
      calcula hash(clave) UNA sola vez (antes poner() lo calculaba 2 veces) y
      el hash queda guardado en la entrada, asi crecer no lo recalcula.
    * ordenar_mezcla: los bloques de 16 se ordenan por insercion (como
      Timsort) y dos bloques vecinos que ya estan en orden se copian sin
      mezclar.
"""


class TablaHash:
    """Tabla hash con encadenamiento (separate chaining).

    Idea: un arreglo de "cubetas". La clave se convierte en un entero con
    hash(clave) y el indice de la cubeta son los ultimos bits de ese entero:
    hash(clave) & (capacidad - 1)  (equivale a % capacidad porque la
    capacidad es potencia de 2, pero es mas rapido).
    Cada cubeta es una lista pequena de entradas [clave, valor, hash]. Si dos
    claves caen en la misma cubeta (colision) se recorre esa lista corta.
    Guardar el hash en la entrada sirve dos veces: al crecer no hay que
    volver a calcularlo, y al buscar se comparan primero dos enteros (barato)
    antes de comparar claves completas (una tupla de textos es mas cara).

    Cuando hay mas de 0.75 elementos por cubeta, se duplica la capacidad y se
    reubican todos los pares (rehash). Asi las cubetas siguen siendo cortas
    y poner/obtener/eliminar cuestan O(1) en promedio (amortizado).

    Las claves pueden ser str, int o tuplas de ellos.
    """

    def __init__(self, capacidad=16):
        real = 16
        while real < capacidad:          # potencia de 2 mayor o igual
            real *= 2
        self._capacidad = real
        self._mascara = real - 1
        self._cubetas = [None] * real    # None = cubeta vacia
        self._n = 0

    def __len__(self):
        return self._n

    def obtener(self, clave, defecto=None):
        h = hash(clave)
        cubeta = self._cubetas[h & self._mascara]
        if cubeta is not None:
            for par in cubeta:
                if par[2] == h and par[0] == clave:
                    return par[1]
        return defecto

    def contiene(self, clave):
        h = hash(clave)
        cubeta = self._cubetas[h & self._mascara]
        if cubeta is not None:
            for par in cubeta:
                if par[2] == h and par[0] == clave:
                    return True
        return False

    def poner(self, clave, valor):
        h = hash(clave)                  # una sola vez
        cubeta = self._cubetas[h & self._mascara]
        if cubeta is not None:
            for par in cubeta:
                if par[2] == h and par[0] == clave:
                    par[1] = valor       # ya estaba: solo se actualiza
                    return
        if (self._n + 1) * 4 > self._capacidad * 3:   # factor de carga > 0.75
            self._crecer()
            cubeta = self._cubetas[h & self._mascara]
        if cubeta is None:
            cubeta = []
            self._cubetas[h & self._mascara] = cubeta
        cubeta.append([clave, valor, h])
        self._n += 1

    def eliminar(self, clave):
        """Quita la clave. True si estaba, False si no."""
        h = hash(clave)
        cubeta = self._cubetas[h & self._mascara]
        if cubeta is None:
            return False
        for i in range(len(cubeta)):
            if cubeta[i][2] == h and cubeta[i][0] == clave:
                cubeta.pop(i)            # la cubeta es corta: O(1) en promedio
                self._n -= 1
                return True
        return False

    def _crecer(self):
        nueva_capacidad = self._capacidad * 2
        mascara = nueva_capacidad - 1
        nuevas = [None] * nueva_capacidad
        for cubeta in self._cubetas:
            if cubeta is not None:
                for par in cubeta:
                    indice = par[2] & mascara     # hash guardado: no se recalcula
                    if nuevas[indice] is None:
                        nuevas[indice] = [par]
                    else:
                        nuevas[indice].append(par)
        self._cubetas = nuevas
        self._capacidad = nueva_capacidad
        self._mascara = mascara


_BLOQUE = 16   # tamano de los bloques que se ordenan por insercion


def ordenar_mezcla(datos):
    """Merge sort (de abajo hacia arriba). Devuelve una lista NUEVA ordenada.

    - Funciona con cualquier cosa comparable con < (int, str, tuplas).
    - Es estable: si dos elementos son iguales, conserva su orden original.
    - Costo: O(n log n) tiempo, O(n) memoria extra.

    Idea: una lista de 1 elemento ya esta ordenada. Mezclamos bloques
    ordenados de tamano b para formar bloques de 2b, luego de 4b... hasta que
    un solo bloque cubre toda la lista (log2(n/b) vueltas, cada una O(n)).

    Dos mejoras de la Parte E (la misma idea que usa Timsort):
      1. Los bloques iniciales de 16 se ordenan por INSERCION. Con bloques tan
         cortos la insercion es mas rapida que mezclar de a 1, 2, 4 y 8, y se
         ahorran 4 vueltas completas. Sigue siendo O(n log n): ordenar n/16
         bloques de 16 cuesta O(16 * n) = O(n).
      2. Si el ultimo del bloque izquierdo ya es <= que el primero del
         derecho, los dos ya estan en orden: se copian sin mezclar.
    """
    n = len(datos)
    origen = datos[:]

    # 1. Insercion dentro de cada bloque de _BLOQUE elementos (estable: un
    #    elemento solo salta a otro si es ESTRICTAMENTE menor).
    for inicio in range(0, n, _BLOQUE):
        fin = inicio + _BLOQUE
        if fin > n:
            fin = n
        for x in range(inicio + 1, fin):
            valor = origen[x]
            y = x - 1
            while y >= inicio and valor < origen[y]:
                origen[y + 1] = origen[y]
                y -= 1
            origen[y + 1] = valor

    # 2. Mezclar bloques vecinos: 16 -> 32 -> 64 -> ...
    destino = [None] * n
    ancho = _BLOQUE
    while ancho < n:
        inicio = 0
        while inicio < n:
            medio = inicio + ancho
            if medio > n:
                medio = n
            fin = inicio + 2 * ancho
            if fin > n:
                fin = n
            if medio >= fin or not (origen[medio] < origen[medio - 1]):
                # El bloque derecho no existe o ya va despues del izquierdo:
                # no hay nada que mezclar, se copia tal cual (sigue estable).
                destino[inicio:fin] = origen[inicio:fin]
                inicio += 2 * ancho
                continue
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
            if i < medio:                      # copiar lo que sobro
                destino[k:fin] = origen[i:medio]
            elif j < fin:
                destino[k:fin] = origen[j:fin]
            inicio += 2 * ancho
        origen, destino = destino, origen
        ancho *= 2
    return origen
