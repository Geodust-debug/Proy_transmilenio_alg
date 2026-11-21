"""Prueba de INTEGRACION: llama a TODO el contrato del motor, como lo hace el profesor.
Uso (desde la raiz del repo):   python pruebas/probar_integracion.py

Revisa que cada metodo exista, devuelva el tipo correcto (nunca dict ni set) y que
los casos borde del enunciado den lo esperado. Si alguna parte todavia es la
version provisional, esta prueba fallara en esa parte.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from motor import Red, simular_fila


def ok(texto):
    print("  ok  ", texto)


def sin_dict_ni_set(valor):
    assert not isinstance(valor, (dict, set, frozenset)), valor
    if isinstance(valor, (list, tuple)):
        for x in valor:
            sin_dict_ni_set(x)


def main():
    red = Red(str(RAIZ / "datos"))
    print("Contrato del motor")

    assert red.estado("PORTAL NORTE") == "ABIERTA"
    assert red.estado("NO EXISTE ESTA") == "NO EXISTE"
    ok("R1 estado")

    r = red.autocompletar("CALLE 1", 4)
    assert isinstance(r, list) and len(r) == 4 and r == sorted(r) and all(x.startswith("CALLE 1") for x in r)
    assert red.autocompletar("ZZZ", 3) == []
    ok("R2 autocompletar")

    r = red.rango("CALLE 26", "CALLE 40 S.")
    assert r[0] == "CALLE 26" and r[-1] == "CALLE 40 S." and r == sorted(r)
    ok("R3 rango")

    h = red.proximo_bus("PORTAL NORTE", "F28-1", "00:00")
    assert h is None or (isinstance(h, str) and len(h) == 5 and h[2] == ":")
    assert red.proximo_bus("PORTAL NORTE", "F28-1", "23:59") in (None, "23:59")
    assert red.proximo_bus("NO EXISTE ESTA", "F28-1", "10:00") is None
    ok("R4 proximo_bus")

    v = red.viaje("PORTAL NORTE", "PORTAL SUR")
    assert isinstance(v, list) and 1 <= len(v) <= 2 and all(isinstance(t, tuple) and len(t) == 3 for t in v)
    assert red.viaje("PORTAL NORTE", "NO EXISTE ESTA") is None
    ok("R5 viaje")

    top = red.ranking(5)
    assert len(top) == 5 and all(isinstance(t, tuple) and len(t) == 2 for t in top)
    assert [t[1] for t in top] == sorted([t[1] for t in top], reverse=True)
    ok("R6 ranking")

    ruta = v[0][0]
    antes = red.recorrido(ruta)
    assert isinstance(antes, list) and red.recorrido("NO-EXISTE") == []
    assert red.recorrido(ruta, al_reves=True) == antes[::-1]
    assert red.agregar_parada(ruta, "CALLE 19", antes[0]) in (True, False)
    assert red.quitar_parada(ruta, "NO EXISTE ESTA") is False
    assert red.agregar_parada(ruta, "NO EXISTE ESTA", antes[0]) is False
    ok("R7 agregar_parada / quitar_parada / recorrido")

    assert red.cerrar("RICAURTE") is True and red.cerrar("RICAURTE") is False
    assert red.cerrar("NO EXISTE ESTA") is False
    assert red.estado("RICAURTE") == "CERRADA" and "RICAURTE" not in [t[0] for t in red.ranking(200)]
    assert red.viaje("RICAURTE", "PORTAL SUR") is None
    assert red.proximo_bus("RICAURTE", ruta, "10:00") is None
    assert red.reabrir("RICAURTE") is True and red.reabrir("RICAURTE") is False
    ok("R8 cerrar / reabrir (y su efecto en R2-R6)")

    nueva = Red(str(RAIZ / "datos"))
    assert nueva.deshacer() is False and nueva.rehacer() is False         # nada que deshacer
    nueva.cerrar("RICAURTE")
    assert nueva.deshacer() is True and nueva.estado("RICAURTE") == "ABIERTA"
    assert nueva.rehacer() is True and nueva.estado("RICAURTE") == "CERRADA"
    nueva.deshacer()
    nueva.cerrar("BANDERAS")                                               # cambio nuevo: borra el rehacer
    assert nueva.rehacer() is False
    ok("R9 deshacer / rehacer")

    assert simular_fila([30, 5, 5, 70], 60, 2) == [120, 60, 60, 120]
    ok("R10 simular_fila")

    for valor in (red.estado("X"), red.autocompletar("C", 3), red.rango("A", "Z"), red.ranking(3), v, antes):
        sin_dict_ni_set(valor)
    ok("ningun metodo devuelve diccionarios ni conjuntos")
    print("\nTODO BIEN")


if __name__ == "__main__":
    main()
