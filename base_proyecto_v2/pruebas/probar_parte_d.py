"""Pruebas de la Parte D (R7 editar rutas, R9 deshacer/rehacer).
Uso (desde la raiz del repo):   python pruebas/probar_parte_d.py

Se compara el motor contra un MODELO SIMPLE hecho con listas de Python: cada
operacion se hace en los dos y deben coincidir siempre. Fuera de motor/ se puede
usar cualquier cosa, asi que el modelo es lento pero obviamente correcto.
"""
import csv
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from motor import Red
from motor.historial import Historial
from motor.rutas import Rutas

aleatorio = random.Random(21)
DATOS = RAIZ / "datos"


def ok(texto):
    print("  ok  ", texto)


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8-sig") as f:
        return [fila for fila in list(csv.reader(f))[1:] if fila]


# ------------------------------------------------------------- Rutas solas
def probar_rutas_basico():
    filas = [["A", "1", "X"], ["A", "2", "Y"], ["A", "3", "Z"], ["B", "1", "Y"]]
    r = Rutas(filas)
    assert r.nombres() == ["A", "B"]
    assert r.recorrido("A") == ["X", "Y", "Z"]
    assert r.recorrido("A", al_reves=True) == ["Z", "Y", "X"]
    assert r.recorrido("NO") == [] and r.recorrido("NO", True) == []
    assert r.agregar_parada("A", "W", "Y") is True
    assert r.recorrido("A") == ["X", "Y", "W", "Z"]
    assert r.recorrido("A", True) == ["Z", "W", "Y", "X"]
    assert r.agregar_parada("A", "V", "Z") is True              # despues de la ultima
    assert r.recorrido("A") == ["X", "Y", "W", "Z", "V"]
    assert r.agregar_parada("A", "U", None) is True             # al inicio (lo usa deshacer)
    assert r.recorrido("A") == ["U", "X", "Y", "W", "Z", "V"]
    assert r.agregar_parada("A", "W", "X") is False             # ya esta en la ruta
    assert r.agregar_parada("A", "Q", "NO-ESTA") is False       # despues_de no esta
    assert r.agregar_parada("NO", "Q", "X") is False            # ruta inexistente
    assert r.quitar_parada("A", "U") is True                    # la primera
    assert r.quitar_parada("A", "V") is True                    # la ultima
    assert r.quitar_parada("A", "V") is False                   # ya no esta
    assert r.quitar_parada("A", "NO-ESTA") is False
    assert r.quitar_parada("NO", "X") is False
    assert r.recorrido("A") == ["X", "Y", "W", "Z"]
    assert r.anterior("A", "X") is None and r.anterior("A", "W") == "Y"
    assert r.tiene_parada("A", "W") and not r.tiene_parada("A", "V") and not r.tiene_parada("NO", "X")
    unica = Rutas([["U", "1", "S"]])
    assert unica.quitar_parada("U", "S") is True and unica.recorrido("U") == []
    assert unica.agregar_parada("U", "T", None) is True and unica.recorrido("U") == ["T"]
    ok("Rutas: insertar (medio, final, inicio), quitar (primera, ultima, unica), bordes, dos sentidos")


def probar_rutas_desordenadas():
    filas = [["A", "3", "Z"], ["A", "1", "X"], ["B", "2", "Q"], ["A", "2", "Y"], ["B", "1", "P"]]
    r = Rutas(filas)
    assert r.recorrido("A") == ["X", "Y", "Z"] and r.recorrido("B") == ["P", "Q"]
    ok("Rutas: las filas del CSV no tienen que venir ordenadas")


def probar_rutas_reales():
    filas = leer("rutas.csv")
    r = Rutas(filas)
    esperado = {}
    for fila in filas:
        esperado.setdefault(fila[0], []).append((int(fila[1]), fila[2]))
    assert len(r.nombres()) == len(esperado)
    for nombre, pares in esperado.items():
        paradas = [e for _, e in sorted(pares)]
        assert r.recorrido(nombre) == paradas
        assert r.recorrido(nombre, True) == paradas[::-1]
    ok("Rutas: las 181 rutas reales se recorren igual en los dos sentidos")


# --------------------------------------------------------------- Historial
def probar_historial():
    h = Historial()
    assert h.deshacer() is None and h.rehacer() is None
    h.registrar(("cerrar", "A"))
    h.registrar(("cerrar", "B"))
    assert h.deshacer() == ("cerrar", "B")
    assert h.rehacer() == ("cerrar", "B")
    assert h.rehacer() is None
    assert h.deshacer() == ("cerrar", "B") and h.deshacer() == ("cerrar", "A") and h.deshacer() is None
    h.registrar(("reabrir", "C"))                               # un cambio nuevo borra el rehacer
    assert h.rehacer() is None
    assert h.deshacer() == ("reabrir", "C")
    ok("Historial: dos pilas, orden LIFO, un cambio nuevo borra el rehacer")


# ------------------------------------------------- Red completa vs modelo
class Modelo:
    """La misma logica de R7/R8/R9 con listas y un historial de Python."""

    def __init__(self, filas, estaciones):
        self.rutas = {}
        for fila in filas:
            self.rutas.setdefault(fila[0], []).append((int(fila[1]), fila[2]))
        self.rutas = {k: [e for _, e in sorted(v)] for k, v in self.rutas.items()}
        self.estaciones = set(estaciones)
        self.cerradas = set()
        self.hechos, self.deshechos = [], []

    def _agregar(self, ruta, nueva, despues):
        p = self.rutas.get(ruta)
        if p is None or nueva in p:
            return False
        if despues is None:
            p.insert(0, nueva)
        elif despues in p:
            p.insert(p.index(despues) + 1, nueva)
        else:
            return False
        return True

    def _quitar(self, ruta, est):
        p = self.rutas.get(ruta)
        if p is None or est not in p:
            return False
        p.remove(est)
        return True

    def agregar_parada(self, ruta, nueva, despues):
        if despues is None or nueva not in self.estaciones or not self._agregar(ruta, nueva, despues):
            return False
        self.hechos.append(("agregar", ruta, nueva, despues)); self.deshechos = []
        return True

    def quitar_parada(self, ruta, est):
        p = self.rutas.get(ruta)
        if p is None or est not in p:
            return False
        i = p.index(est)
        anterior = p[i - 1] if i > 0 else None
        self._quitar(ruta, est)
        self.hechos.append(("quitar", ruta, est, anterior)); self.deshechos = []
        return True

    def cerrar(self, n):
        if n not in self.estaciones or n in self.cerradas:
            return False
        self.cerradas.add(n); self.hechos.append(("cerrar", n)); self.deshechos = []
        return True

    def reabrir(self, n):
        if n not in self.cerradas:
            return False
        self.cerradas.discard(n); self.hechos.append(("reabrir", n)); self.deshechos = []
        return True

    def deshacer(self):
        if not self.hechos:
            return False
        o = self.hechos.pop(); self.deshechos.append(o)
        if o[0] == "cerrar": self.cerradas.discard(o[1])
        elif o[0] == "reabrir": self.cerradas.add(o[1])
        elif o[0] == "agregar": self._quitar(o[1], o[2])
        else: self._agregar(o[1], o[2], o[3])
        return True

    def rehacer(self):
        if not self.deshechos:
            return False
        o = self.deshechos.pop(); self.hechos.append(o)
        if o[0] == "cerrar": self.cerradas.add(o[1])
        elif o[0] == "reabrir": self.cerradas.discard(o[1])
        elif o[0] == "agregar": self._agregar(o[1], o[2], o[3])
        else: self._quitar(o[1], o[2])
        return True


def comparar_todo(red, modelo):
    for nombre, paradas in modelo.rutas.items():
        assert red.recorrido(nombre) == paradas, nombre
        assert red.recorrido(nombre, al_reves=True) == paradas[::-1], nombre
    for n in modelo.estaciones:
        esperado = "CERRADA" if n in modelo.cerradas else "ABIERTA"
        assert red.estado(n) == esperado, n


def probar_red_aleatoria():
    filas = leer("rutas.csv")
    estaciones = [f[0] for f in leer("estaciones.csv")]
    red = Red(str(DATOS))
    modelo = Modelo(filas, estaciones)
    rutas = sorted(modelo.rutas)
    for paso in range(1500):
        op = aleatorio.randint(0, 6)
        ruta = aleatorio.choice(rutas + ["RUTA-NO-EXISTE"])
        est = aleatorio.choice(estaciones + ["ESTACION NO EXISTE"])
        paradas = modelo.rutas.get(ruta, [])
        if op == 0:
            despues = aleatorio.choice(paradas) if paradas and aleatorio.random() < 0.8 else aleatorio.choice(estaciones)
            assert red.agregar_parada(ruta, est, despues) == modelo.agregar_parada(ruta, est, despues), (paso, ruta, est, despues)
        elif op == 1:
            quitar = aleatorio.choice(paradas) if paradas and aleatorio.random() < 0.8 else est
            assert red.quitar_parada(ruta, quitar) == modelo.quitar_parada(ruta, quitar), (paso, ruta, quitar)
        elif op == 2:
            assert red.cerrar(est) == modelo.cerrar(est)
        elif op == 3:
            assert red.reabrir(est) == modelo.reabrir(est)
        elif op in (4, 5):
            assert red.deshacer() == modelo.deshacer(), paso
        else:
            assert red.rehacer() == modelo.rehacer(), paso
        if paso % 50 == 0:
            comparar_todo(red, modelo)
    comparar_todo(red, modelo)
    ok("1500 operaciones al azar (agregar, quitar, cerrar, reabrir, deshacer, rehacer) iguales al modelo")


def probar_deshacer_todo():
    """Si se deshace TODO, la red debe quedar exactamente como al inicio (rutas, estados, horarios, ranking)."""
    estaciones = [f[0] for f in leer("estaciones.csv")]
    inicial = Red(str(DATOS))
    red = Red(str(DATOS))
    rutas = sorted({f[0] for f in leer("rutas.csv")})
    for _ in range(400):
        ruta = aleatorio.choice(rutas)
        paradas = red.recorrido(ruta)
        op = aleatorio.randint(0, 3)
        if op == 0:
            red.agregar_parada(ruta, aleatorio.choice(estaciones), aleatorio.choice(paradas))
        elif op == 1 and paradas:
            red.quitar_parada(ruta, aleatorio.choice(paradas))
        elif op == 2:
            red.cerrar(aleatorio.choice(estaciones))
        else:
            red.reabrir(aleatorio.choice(estaciones))
    veces = 0
    while red.deshacer():
        veces += 1
    assert veces > 100 and red.deshacer() is False
    for ruta in rutas:
        assert red.recorrido(ruta) == inicial.recorrido(ruta), ruta
    assert red.ranking(20) == inicial.ranking(20)
    assert all(red.estado(e) == "ABIERTA" for e in estaciones)
    horarios = leer("horarios.csv")
    for f in aleatorio.sample(horarios, 300):
        assert red.proximo_bus(f[1], f[0], f[2]) == inicial.proximo_bus(f[1], f[0], f[2])
    veces_r = 0
    while red.rehacer():
        veces_r += 1
    assert veces_r == veces
    ok("deshacer todo (%d cambios) deja la red como al inicio; rehacer todo los reaplica" % veces)


def probar_viaje_tras_editar():
    red = Red(str(DATOS))
    v = red.viaje("PORTAL NORTE", "PORTAL SUR")
    assert v is not None
    ruta, sube, baja = v[0]
    paradas = red.recorrido(ruta)
    assert red.quitar_parada(ruta, baja) is True                    # la ruta ya no llega ahi
    v2 = red.viaje("PORTAL NORTE", "PORTAL SUR")
    if v2 is not None:
        for r, s, b in v2:
            tramo = red.recorrido(r)
            assert b in tramo and tramo.index(b) > tramo.index(s)
    assert red.deshacer() is True
    assert red.viaje("PORTAL NORTE", "PORTAL SUR") == v
    ok("viaje (R5) se actualiza al editar una ruta y vuelve a lo original al deshacer")


def main():
    print("Parte D: rutas e historial")
    probar_rutas_basico()
    probar_rutas_desordenadas()
    probar_rutas_reales()
    probar_historial()
    probar_red_aleatoria()
    probar_deshacer_todo()
    probar_viaje_tras_editar()
    print("\nTODO BIEN")


if __name__ == "__main__":
    main()
