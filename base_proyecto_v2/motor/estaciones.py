"""PARTE B (Miguel) -- Catalogo de estaciones: R1, R2, R3 y R8 (cerrar/reabrir).

ESTRUCTURAS
    _ordenadas : arreglo con TODOS los nombres en orden alfabetico (merge sort).
    _posicion  : TablaHash nombre -> posicion en _ordenadas        -> R1 en O(1).
    _cerrada   : arreglo de bool (una casilla por estacion).
    _arbol     : arbol de Fenwick (BIT) con 1 por cada estacion ABIERTA.
                 Permite, en O(log n), contar cuantas abiertas hay antes de una
                 posicion y encontrar la j-esima abierta.

POR QUE ASI
    * R1  : la tabla hash responde "existe? y esta abierta?" sin recorrer nada.
    * R2/R3: en un arreglo ORDENADO, todo lo que empieza por un prefijo (o esta
      entre dos nombres) queda contiguo. Se encuentra el inicio con busqueda
      binaria y se avanza hacia adelante.
    * R8  : cerrar/reabrir es poner una casilla en True/False y actualizar el
      arbol de Fenwick (O(log n)). El arreglo ordenado NO cambia, asi que no hay
      que mover elementos. Al avanzar, si la estacion siguiente esta cerrada, el
      arbol permite SALTAR a la proxima abierta en O(log n) (en vez de ir una por
      una, que seria O(estaciones cerradas)).

COSTOS (n = numero de estaciones, k = cuantas se piden, m = cuantas se devuelven)
    cargar             : O(n log n)  (ordenar una vez)
    estado / esta_abierta : O(1) en promedio (tabla hash)
    autocompletar      : O(log n + k)  (O(log n) extra por cada tramo de cerradas)
    rango              : O(log n + m)  (idem)
    cerrar / reabrir   : O(log n)
"""
from .estructuras import TablaHash, ordenar_mezcla


class Estaciones:
    def __init__(self, nombres):
        todos = ordenar_mezcla(list(nombres))
        self._ordenadas = []
        for nombre in todos:                       # quitar repetidos (quedan juntos)
            if len(self._ordenadas) == 0 or self._ordenadas[-1] != nombre:
                self._ordenadas.append(nombre)
        n = len(self._ordenadas)
        self._n = n
        self._posicion = TablaHash()
        for i in range(n):
            self._posicion.poner(self._ordenadas[i], i)
        self._cerrada = [False] * n
        self._abiertas = n
        # Arbol de Fenwick con un 1 en cada estacion (todas abiertas al inicio).
        # tree[i] guarda la suma de las (i & -i) casillas que terminan en i.
        self._arbol = [0] * (n + 1)
        for i in range(1, n + 1):
            self._arbol[i] = i & (-i)
        self._paso = 1                             # mayor potencia de 2 <= n
        while self._paso * 2 <= n:
            self._paso *= 2

    # ------------------------------------------------------------ Fenwick
    def _abiertas_antes(self, i):
        """Cuantas estaciones abiertas hay en las posiciones 0..i-1."""
        total = 0
        while i > 0:
            total += self._arbol[i]
            i -= i & (-i)
        return total

    def _cambiar(self, i, delta):
        """Suma delta (+1 o -1) a la casilla i del arbol."""
        j = i + 1
        while j <= self._n:
            self._arbol[j] += delta
            j += j & (-j)

    def _kesima_abierta(self, j):
        """Posicion de la abierta numero j (0 = la primera abierta)."""
        faltan = j + 1
        pos = 0
        paso = self._paso
        while paso > 0:
            if pos + paso <= self._n and self._arbol[pos + paso] < faltan:
                pos += paso
                faltan -= self._arbol[pos]
            paso //= 2
        return pos

    def _siguiente_abierta(self, i):
        """Primera posicion >= i con estacion abierta (o n si ya no hay)."""
        if i >= self._n:
            return self._n
        if not self._cerrada[i]:
            return i                               # caso comun: O(1)
        j = self._abiertas_antes(i)
        if j >= self._abiertas:
            return self._n
        return self._kesima_abierta(j)

    # ---------------------------------------------------- busqueda binaria
    def _primero_mayor_o_igual(self, texto):
        """Primera posicion cuyo nombre es >= texto (n si ninguno)."""
        izq = 0
        der = self._n
        while izq < der:
            medio = (izq + der) // 2
            if self._ordenadas[medio] < texto:
                izq = medio + 1
            else:
                der = medio
        return izq

    def _primero_mayor(self, texto):
        """Primera posicion cuyo nombre es > texto (n si ninguno)."""
        izq = 0
        der = self._n
        while izq < der:
            medio = (izq + der) // 2
            if self._ordenadas[medio] <= texto:
                izq = medio + 1
            else:
                der = medio
        return izq

    # ------------------------------------------------------------- R1
    def estado(self, nombre):
        i = self._posicion.obtener(nombre)
        if i is None:
            return "NO EXISTE"
        if self._cerrada[i]:
            return "CERRADA"
        return "ABIERTA"

    def esta_abierta(self, nombre):
        i = self._posicion.obtener(nombre)
        return i is not None and not self._cerrada[i]

    # ------------------------------------------------------------- R2
    def autocompletar(self, prefijo, k):
        resultado = []
        if k <= 0:
            return resultado
        i = self._primero_mayor_o_igual(prefijo)   # donde empezarian los que tienen el prefijo
        while len(resultado) < k:
            i = self._siguiente_abierta(i)
            if i >= self._n or not self._ordenadas[i].startswith(prefijo):
                break
            resultado.append(self._ordenadas[i])
            i += 1
        return resultado

    # ------------------------------------------------------------- R3
    def rango(self, desde, hasta):
        resultado = []
        if desde > hasta:
            return resultado
        fin = self._primero_mayor(hasta)           # primera posicion que ya se pasa de `hasta`
        i = self._primero_mayor_o_igual(desde)
        while True:
            i = self._siguiente_abierta(i)
            if i >= fin:
                break
            resultado.append(self._ordenadas[i])
            i += 1
        return resultado

    # ------------------------------------------------------------- R8
    def cerrar(self, nombre):
        i = self._posicion.obtener(nombre)
        if i is None or self._cerrada[i]:
            return False
        self._cerrada[i] = True
        self._cambiar(i, -1)
        self._abiertas -= 1
        return True

    def reabrir(self, nombre):
        i = self._posicion.obtener(nombre)
        if i is None or not self._cerrada[i]:
            return False
        self._cerrada[i] = False
        self._cambiar(i, 1)
        self._abiertas += 1
        return True
