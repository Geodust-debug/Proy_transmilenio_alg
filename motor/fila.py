"""PARTE A (Martin) -- R10: fila de abordaje en hora pico.

simular_fila(llegadas, frecuencia, capacidad) -> lista con el segundo en que
salio el bus de cada persona, en el MISMO orden de `llegadas`.

Reglas: los buses salen en frecuencia, 2*frecuencia, 3*frecuencia...; cada
bus se lleva como maximo `capacidad` personas; la gente sube en orden de
llegada. Quien llega justo en el segundo en que sale un bus alcanza a subir.

Algoritmo:
    1. ORDENAR las personas por (hora de llegada, posicion original) con
       merge sort -> O(n log n). Incluir la posicion original hace que los
       empates se atiendan en el orden en que venian (estable).
    2. SIMULAR con una COLA (FIFO) = la fila real de personas:
         para cada bus: encolar a todos los que ya llegaron a su hora de
         salida; desencolar hasta `capacidad` personas y anotar su salida.
       Si la fila esta vacia, se salta directo al primer bus que sale
       despues de la proxima llegada (no se simulan buses vacios).
    Costo total: O(n log n) por el ordenamiento + O(n) la simulacion
    (n = numero de personas). Memoria O(n).
"""
from .estructuras import ordenar_mezcla


class Cola:
    """Cola FIFO con un arreglo y un indice de cabeza: encolar y
    desencolar son O(1). (Quitar con pop(0) seria O(n).)"""

    def __init__(self):
        self._items = []
        self._cabeza = 0           # posicion del proximo a salir

    def encolar(self, x):
        self._items.append(x)

    def desencolar(self):
        x = self._items[self._cabeza]
        self._cabeza += 1
        if self._cabeza > 1024 and self._cabeza * 2 > len(self._items):
            self._items = self._items[self._cabeza:]   # liberar memoria
            self._cabeza = 0
        return x

    def vacia(self):
        return self._cabeza >= len(self._items)

    def __len__(self):
        return len(self._items) - self._cabeza


def simular_fila(llegadas, frecuencia, capacidad):
    if frecuencia <= 0 or capacidad <= 0:
        raise ValueError("frecuencia y capacidad deben ser mayores que 0")
    n = len(llegadas)
    if n == 0:
        return []

    # 1. Ordenar: clave = llegada * n + posicion (un solo entero que ordena
    #    primero por llegada y, en empate, por posicion original).
    claves = [0] * n
    for i in range(n):
        claves[i] = llegadas[i] * n + i
    claves = ordenar_mezcla(claves)
    orden = [0] * n                # orden[k] = posicion original de la k-esima persona
    for k in range(n):
        orden[k] = claves[k] % n

    # 2. Simular con una cola.
    salidas = [0] * n
    cola = Cola()
    siguiente = 0                  # proxima persona (en `orden`) que aun no llega a la fila
    atendidos = 0
    bus = 1                        # el bus numero `bus` sale en bus * frecuencia
    while atendidos < n:
        salida = bus * frecuencia
        while siguiente < n and llegadas[orden[siguiente]] <= salida:
            cola.encolar(orden[siguiente])
            siguiente += 1
        if cola.vacia():
            # Nadie espera: saltar al primer bus que sale en o despues de la
            # proxima llegada (techo de llegada / frecuencia).
            t = llegadas[orden[siguiente]]
            bus = (t + frecuencia - 1) // frecuencia
            continue
        cupo = capacidad
        while cupo > 0 and not cola.vacia():
            salidas[cola.desencolar()] = salida
            cupo -= 1
            atendidos += 1
        bus += 1
    return salidas
