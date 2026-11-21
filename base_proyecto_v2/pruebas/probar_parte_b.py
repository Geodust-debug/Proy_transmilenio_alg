"""Pruebas de la Parte B (R1, R2, R3, R8).
Uso (desde la raiz del repo):   python pruebas/probar_parte_b.py

Fuera de motor/ SI se puede usar sorted, set, etc. Aqui se usan para escribir
la "respuesta de referencia" lenta pero obviamente correcta.
"""
import csv
import random
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from motor import Red
from motor.estaciones import Estaciones

aleatorio = random.Random(11)


def ok(texto):
    print("  ok  ", texto)


class Referencia:
    """Lo mismo que Estaciones pero con listas y sorted (lento y obvio)."""

    def __init__(self, nombres):
        self.nombres = sorted(set(nombres))
        self.cerradas = set()

    def estado(self, n):
        if n not in self.nombres:
            return "NO EXISTE"
        return "CERRADA" if n in self.cerradas else "ABIERTA"

    def autocompletar(self, p, k):
        return [n for n in self.nombres if n.startswith(p) and n not in self.cerradas][:max(k, 0)]

    def rango(self, a, b):
        return [n for n in self.nombres if a <= n <= b and n not in self.cerradas]


def nombres_reales():
    with open(RAIZ / "datos" / "estaciones.csv", encoding="utf-8-sig") as f:
        return [fila[0] for fila in list(csv.reader(f))[1:] if fila]


def nombres_sinteticos(n):
    prefijos = ["CALLE", "CARRERA", "AV.", "PORTAL", "PARQUE", "SAN"]
    return [aleatorio.choice(prefijos) + " " + str(i) for i in range(n)]


def comparar(e, ref, nombres):
    # R1
    for _ in range(30):
        n = aleatorio.choice(nombres + ["NO EXISTE ESTA", ""])
        assert e.estado(n) == ref.estado(n), n
        assert e.esta_abierta(n) == (ref.estado(n) == "ABIERTA")
    # R2
    for _ in range(30):
        base = aleatorio.choice(nombres)
        p = base[:aleatorio.randint(0, len(base))]
        k = aleatorio.randint(0, 12)
        assert e.autocompletar(p, k) == ref.autocompletar(p, k), (p, k)
    assert e.autocompletar("ZZZZ", 5) == []
    # R3
    for _ in range(30):
        a, b = aleatorio.choice(nombres), aleatorio.choice(nombres)
        assert e.rango(a, b) == ref.rango(a, b), (a, b)


def probar_basico():
    nombres = nombres_reales()
    e = Estaciones(nombres)
    assert e.estado("PORTAL NORTE") == "ABIERTA"
    assert e.estado("NO EXISTE") == "NO EXISTE"
    assert e.estado("") == "NO EXISTE"
    assert e.cerrar("PORTAL NORTE") is True
    assert e.estado("PORTAL NORTE") == "CERRADA"
    assert e.cerrar("PORTAL NORTE") is False        # ya estaba cerrada
    assert e.cerrar("NO EXISTE") is False
    assert e.reabrir("PORTAL NORTE") is True
    assert e.reabrir("PORTAL NORTE") is False       # ya estaba abierta
    assert e.reabrir("NO EXISTE") is False
    ok("R1/R8 casos basicos y bordes (inexistente, ya cerrada, ya abierta)")

    assert e.autocompletar("CALLE 1", 3) == ["CALLE 100", "CALLE 106", "CALLE 127"]
    assert e.autocompletar("CALLE 1", 0) == []
    assert e.autocompletar("CALLE 1", -2) == []
    assert e.autocompletar("XYZ", 5) == []
    e.cerrar("CALLE 100")
    assert e.autocompletar("CALLE 1", 3) == ["CALLE 106", "CALLE 127", "CALLE 142"]
    assert len(e.autocompletar("", 1000)) == len(nombres) - 1
    e.reabrir("CALLE 100")
    ok("R2 autocompletar: prefijo, k=0, sin resultados, cerradas, prefijo vacio")

    r = e.rango("CALLE 26", "CALLE 40 S.")
    assert r[0] == "CALLE 26" and r[-1] == "CALLE 40 S." and r == sorted(r)
    assert e.rango("CALLE 40 S.", "CALLE 26") == []          # desde > hasta
    assert e.rango("CALLE 26", "CALLE 26") == ["CALLE 26"]
    e.cerrar("CALLE 26")
    assert e.rango("CALLE 26", "CALLE 34")[0] == "CALLE 34" or "CALLE 26" not in e.rango("CALLE 26", "CALLE 34")
    ok("R3 rango: inclusive, desde > hasta, extremo cerrado")


def probar_contra_referencia():
    for nombres in (nombres_reales(), nombres_sinteticos(300), nombres_sinteticos(1), []):
        if len(nombres) == 0:
            e = Estaciones([])
            assert e.estado("A") == "NO EXISTE" and e.autocompletar("", 3) == [] and e.rango("A", "Z") == []
            continue
        e, ref = Estaciones(nombres), Referencia(nombres)
        for paso in range(400):
            op = aleatorio.randint(0, 3)
            n = aleatorio.choice(nombres + ["NO EXISTE ESTA"])
            if op == 0:
                esperado = ref.estado(n) == "ABIERTA"
                assert e.cerrar(n) == esperado
                if esperado:
                    ref.cerradas.add(n)
            elif op == 1:
                esperado = ref.estado(n) == "CERRADA"
                assert e.reabrir(n) == esperado
                if esperado:
                    ref.cerradas.discard(n)
            comparar(e, ref, nombres)
    ok("400 operaciones al azar (cerrar/reabrir + consultas) iguales a la referencia, 3 redes")


def probar_muchas_cerradas():
    nombres = nombres_sinteticos(2000)
    e, ref = Estaciones(nombres), Referencia(nombres)
    for n in aleatorio.sample(nombres, 1700):                 # 85% cerradas
        e.cerrar(n)
        ref.cerradas.add(n)
    for _ in range(100):
        comparar(e, ref, nombres)
    ok("con 85% de las estaciones cerradas sigue igual a la referencia")


def probar_via_red():
    red = Red(str(RAIZ / "datos"))
    assert red.estado("RICAURTE") == "ABIERTA"
    assert red.cerrar("RICAURTE") is True
    assert red.estado("RICAURTE") == "CERRADA"
    assert "RICAURTE" not in red.rango("QUIROGA", "SAN BERNARDO")
    assert "RICAURTE" not in red.autocompletar("RIC", 5)
    assert red.reabrir("RICAURTE") is True
    assert red.autocompletar("RIC", 5) == ["RICAURTE"]
    ok("a traves de Red: cerrar saca la estacion de R2/R3 y reabrir la devuelve")


def probar_velocidad():
    for n in (10000, 80000):
        nombres = nombres_sinteticos(n)
        t0 = time.perf_counter()
        e = Estaciones(nombres)
        carga = time.perf_counter() - t0
        t0 = time.perf_counter()
        for _ in range(2000):
            e.estado(aleatorio.choice(nombres))
            e.autocompletar("CALLE 1", 10)
            e.cerrar(aleatorio.choice(nombres))
        consultas = (time.perf_counter() - t0) / 2000 * 1e6
        print("        n=%6d  carga %.2f s   3 operaciones: %.1f us en promedio" % (n, carga, consultas))
    ok("velocidad medida (ver panel de rendimiento para las curvas)")


def main():
    print("Parte B: estaciones")
    probar_basico()
    probar_contra_referencia()
    probar_muchas_cerradas()
    probar_via_red()
    probar_velocidad()
    print("\nTODO BIEN")


if __name__ == "__main__":
    main()
