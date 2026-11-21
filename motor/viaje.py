"""PARTE A (Martin) -- R5: planear un viaje con menos paradas.

Modelo (un GRAFO BIPARTITO estacion <-> ruta):
    * cada ruta es una lista ordenada de estaciones (un solo sentido);
    * cada estacion guarda en que rutas aparece y en que posicion.
Un viaje es: subir a una ruta en el origen y bajar en el destino (directo),
o subir a r1 en el origen, bajar en una estacion T, subir a r2 en T y bajar
en el destino (un transbordo). Es como un BFS por niveles de "numero de
rutas", limitado a 2 niveles, donde ademas medimos el costo en paradas.

Algoritmo (por consulta):
    1. desde_o[t]  = menos paradas para llegar de origen a t en UNA ruta.
    2. hasta_d[t]  = menos paradas para ir de t a destino en UNA ruta.
    3. directo     = desde_o[destino].
    4. transbordo  = min sobre t abiertas de desde_o[t] + hasta_d[t].
    5. se elige el menor; si empatan, gana el directo (menos tramos).

Las estaciones cerradas: no pueden ser origen, destino ni estacion de
transbordo (pasar por ellas dentro de una ruta si cuenta como parada).

Optimizacion (Parte E): los arreglos desde_o / hasta_d NO se crean en cada
consulta. Se crean una vez (al construir el indice) llenos de "infinito" y
cada consulta anota en una lista `tocados` que posiciones cambio. Al final
solo se limpian esas posiciones. Asi una consulta ya no recorre las S
estaciones de la red: solo las paradas que de verdad visito.
    antes  : O(S + P) por consulta  (crear 4 arreglos de tamano S y recorrerlos)
    ahora  : O(P)     por consulta

Costos (S = estaciones de la red, P = paradas de las rutas que pasan por
el origen y por el destino, L = total de filas de rutas.csv):
    construir el indice : O(L), una sola vez; se rehace tras editar rutas.
    viaje()             : O(P).
"""
from .estructuras import TablaHash

_INFINITO = 10 ** 18


class Viaje:
    def __init__(self, rutas, esta_abierta):
        self._rutas = rutas                # objeto Rutas (Parte D)
        self._esta_abierta = esta_abierta  # funcion nombre -> bool (Parte B)
        self._listo = False

    def invalidar(self):
        """La fachada lo llama cuando se edita una ruta: hay que reconstruir."""
        self._listo = False

    # ------------------------------------------------------------------
    def _construir(self):
        self._nombres_ruta = self._rutas.nombres()
        self._ids_ruta = []        # _ids_ruta[r] = ids de estacion, en orden
        self._id_de = TablaHash()  # nombre de estacion -> id (0, 1, 2, ...)
        self._nombre_de = []       # id -> nombre
        self._entradas = []        # id -> lista de [ruta, posicion]
        for r in range(len(self._nombres_ruta)):
            paradas = self._rutas.recorrido(self._nombres_ruta[r])
            ids = []
            for pos in range(len(paradas)):
                nombre = paradas[pos]
                e = self._id_de.obtener(nombre)
                if e is None:
                    e = len(self._nombre_de)
                    self._id_de.poner(nombre, e)
                    self._nombre_de.append(nombre)
                    self._entradas.append([])
                ids.append(e)
                self._entradas[e].append([r, pos])
            self._ids_ruta.append(ids)
        # Arreglos de trabajo reutilizables (siempre "limpios" entre consultas).
        n = len(self._nombre_de)
        self._desde_o = [_INFINITO] * n
        self._ruta_o = [-1] * n
        self._hasta_d = [_INFINITO] * n
        self._ruta_d = [-1] * n
        self._listo = True

    # ------------------------------------------------------------------
    def viaje(self, origen, destino):
        """Lista de tramos (ruta, sube_en, baja_en) o None si no hay viaje."""
        if origen == destino:
            return None
        if not self._esta_abierta(origen) or not self._esta_abierta(destino):
            return None            # cerrada o inexistente
        if not self._listo:
            self._construir()
        o = self._id_de.obtener(origen)
        d = self._id_de.obtener(destino)
        if o is None or d is None:
            return None            # existe pero ninguna ruta pasa por ahi

        desde_o = self._desde_o
        ruta_o = self._ruta_o
        hasta_d = self._hasta_d
        ruta_d = self._ruta_d

        # 1. Hacia adelante desde el origen, por cada ruta que pasa por el.
        tocados_o = []             # ids donde desde_o dejo de ser infinito
        for entrada in self._entradas[o]:
            r = entrada[0]
            pos_o = entrada[1]
            ids = self._ids_ruta[r]
            for q in range(pos_o + 1, len(ids)):
                e = ids[q]
                costo = q - pos_o
                if costo < desde_o[e]:
                    if desde_o[e] == _INFINITO:
                        tocados_o.append(e)
                    desde_o[e] = costo
                    ruta_o[e] = r

        # 2. Hacia atras desde el destino, por cada ruta que pasa por el.
        tocados_d = []
        for entrada in self._entradas[d]:
            r = entrada[0]
            pos_d = entrada[1]
            ids = self._ids_ruta[r]
            for q in range(pos_d):
                e = ids[q]
                costo = pos_d - q
                if costo < hasta_d[e]:
                    if hasta_d[e] == _INFINITO:
                        tocados_d.append(e)
                    hasta_d[e] = costo
                    ruta_d[e] = r

        # 3. Mejor viaje directo.
        costo_directo = desde_o[d]

        # 4. Mejor viaje con un transbordo: una estacion t tiene que estar en
        #    las DOS listas de tocados, asi que basta recorrer la mas corta.
        #    En empate se elige el id menor (el mismo resultado de siempre).
        if len(tocados_o) <= len(tocados_d):
            candidatos = tocados_o
        else:
            candidatos = tocados_d
        mejor_total = _INFINITO
        mejor_t = -1
        for t in candidatos:
            if desde_o[t] == _INFINITO or hasta_d[t] == _INFINITO:
                continue
            if t == o or t == d:
                continue
            total = desde_o[t] + hasta_d[t]
            if total < mejor_total or (total == mejor_total and t < mejor_t):
                if self._esta_abierta(self._nombre_de[t]):
                    mejor_total = total
                    mejor_t = t

        # 5. Elegir (se arma la respuesta ANTES de limpiar los arreglos).
        respuesta = None
        if costo_directo < _INFINITO and costo_directo <= mejor_total:
            respuesta = [(self._nombres_ruta[ruta_o[d]], origen, destino)]
        elif mejor_t >= 0:
            nombre_t = self._nombre_de[mejor_t]
            respuesta = [(self._nombres_ruta[ruta_o[mejor_t]], origen, nombre_t),
                         (self._nombres_ruta[ruta_d[mejor_t]], nombre_t, destino)]

        # 6. Limpiar SOLO lo que se toco: O(P), no O(S).
        for e in tocados_o:
            desde_o[e] = _INFINITO
            ruta_o[e] = -1
        for e in tocados_d:
            hasta_d[e] = _INFINITO
            ruta_d[e] = -1
        return respuesta
