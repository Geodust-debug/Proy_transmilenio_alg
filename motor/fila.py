"""PARTE A (Martin) -- R10: fila de abordaje en hora pico.

simular_fila(llegadas, frecuencia, capacidad) -> lista con el segundo en que
salio el bus de cada persona, en el MISMO orden de `llegadas`.

Reglas: los buses salen en frecuencia, 2*frecuencia, 3*frecuencia...; cada
bus se lleva como maximo `capacidad` personas; la gente sube en orden de
llegada. Quien llega justo en el segundo en que sale un bus alcanza a subir.

Algoritmo:
    1. ORDENAR las personas por (hora de llegada, posicion original). Un
       orden estable deja los empates en el orden en que venian.
         - Si las llegadas son numeros enteros dentro de un rango W pequeno
           (W <= 4n, el caso normal: segundos dentro de una ventana), se usa
           ORDENAMIENTO POR CONTEO: O(n + W) = O(n).        (Parte E)
         - Si no, merge sort sobre la clave llegada*n + posicion: O(n log n).
    2. SIMULAR con una COLA (FIFO) = la fila real de personas:
         para cada bus: encolar a todos los que ya llegaron a su hora de
         salida; desencolar hasta `capacidad` personas y anotar su salida.
       Si la fila esta vacia, se salta directo al primer bus que sale
       despues de la proxima llegada (no se simulan buses vacios).
       Como la gente entra a la fila YA en orden de llegada, la cola es un
       tramo del arreglo ordenado: [cabeza, fin). Encolar = mover `fin`,
       desencolar = mover `cabeza`. Ambas O(1), sin copiar a nadie. (Parte E)
    Costo total: O(n) con conteo, O(n log n) con merge sort; simular O(n)
    (n = numero de personas). Memoria O(n + W).
"""
from .estructuras import ordenar_mezcla


def _orden_por_conteo(llegadas, minimo, rango):
    """Posiciones originales ordenadas por llegada (estable). O(n + rango)."""
    n = len(llegadas)
    inicio = [0] * (rango + 1)     # inicio[v] = primera casilla del valor v
    for x in llegadas:
        inicio[int(x - minimo) + 1] += 1
    for v in range(1, rango + 1):  # sumas acumuladas
        inicio[v] += inicio[v - 1]
    orden = [0] * n
    for i in range(n):             # de izquierda a derecha => estable
        v = int(llegadas[i] - minimo)
        orden[inicio[v]] = i
        inicio[v] += 1
    return orden


def _orden_por_mezcla(llegadas):
    """Igual que arriba pero con merge sort: O(n log n). Sirve para cualquier
    llegada comparable (por ejemplo, rangos enormes o numeros con decimales)."""
    n = len(llegadas)
    claves = [0] * n
    for i in range(n):
        claves[i] = (llegadas[i], i)
    claves = ordenar_mezcla(claves)
    orden = [0] * n
    for k in range(n):
        orden[k] = claves[k][1]
    return orden


def simular_fila(llegadas, frecuencia, capacidad):
    if frecuencia <= 0 or capacidad <= 0:
        raise ValueError("frecuencia y capacidad deben ser mayores que 0")
    n = len(llegadas)
    if n == 0:
        return []

    # 1. Ordenar (conteo si se puede, si no merge sort).
    enteros = True
    minimo = llegadas[0]
    maximo = llegadas[0]
    for x in llegadas:
        if x // 1 != x:            # tiene decimales: no sirve para contar
            enteros = False
            break
        if x < minimo:
            minimo = x
        elif x > maximo:
            maximo = x
    if enteros and maximo - minimo + 1 <= 4 * n + 1024:
        orden = _orden_por_conteo(llegadas, minimo, int(maximo - minimo) + 1)
    else:
        orden = _orden_por_mezcla(llegadas)

    # 2. Simular. La cola es el tramo orden[cabeza:fin] (FIFO).
    salidas = [0] * n
    cabeza = 0                     # primera persona de la fila
    fin = 0                        # la fila llega hasta fin - 1
    bus = 1                        # el bus numero `bus` sale en bus * frecuencia
    while cabeza < n:
        salida = bus * frecuencia
        while fin < n and llegadas[orden[fin]] <= salida:   # encolar
            fin += 1
        if cabeza == fin:
            # Nadie espera: saltar al primer bus que sale en o despues de la
            # proxima llegada (techo de llegada / frecuencia).
            t = llegadas[orden[fin]]
            bus = int(-(-t // frecuencia))     # techo, sirve con int y float
            if bus < 1:
                bus = 1
            continue
        sube = fin - cabeza                                  # desencolar
        if sube > capacidad:
            sube = capacidad
        for k in range(cabeza, cabeza + sube):
            salidas[orden[k]] = salida
        cabeza += sube
        bus += 1
    return salidas
