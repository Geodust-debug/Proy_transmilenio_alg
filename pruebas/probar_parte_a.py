"""Pruebas de la Parte A (R5 viaje, R10 fila) y de las estructuras compartidas.
Uso (desde la raiz del repo):   python pruebas/probar_parte_a.py

Fuera de motor/ SI se puede usar dict, set, sorted, etc., asi que aqui se usan
para escribir "respuestas de referencia" lentas pero obviamente correctas.
"""
import random
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from motor import Red, simular_fila
from motor.estructuras import TablaHash, ordenar_mezcla

DATOS = str(RAIZ / "datos")
aleatorio = random.Random(7)


def ok(nombre):
    print("  ok  ", nombre)


# ------------------------------------------------------------ estructuras
def probar_estructuras():
    t = TablaHash()
    ref = {}
    for _ in range(20000):
        clave = "K" + str(aleatorio.randint(0, 3000))
        op = aleatorio.randint(0, 2)
        if op == 0:
            valor = aleatorio.randint(0, 99)
            t.poner(clave, valor)
            ref[clave] = valor
        elif op == 1:
            assert t.obtener(clave) == ref.get(clave)
            assert t.contiene(clave) == (clave in ref)
        else:
            assert t.eliminar(clave) == (clave in ref)
            ref.pop(clave, None)
        assert len(t) == len(ref)
    ok("TablaHash igual que dict en 20000 operaciones al azar")
    for _ in range(200):
        datos = [aleatorio.randint(-50, 50) for _ in range(aleatorio.randint(0, 80))]
        assert ordenar_mezcla(datos) == sorted(datos)
    pares = [(aleatorio.randint(0, 5), i) for i in range(500)]
    assert ordenar_mezcla([p[0] for p in pares]) == sorted(p[0] for p in pares)
    ok("ordenar_mezcla igual que sorted")


# ------------------------------------------------------------------- R10
def fila_referencia(llegadas, frecuencia, capacidad):
    """Respuesta lenta y obvia: para cada persona (en orden de llegada)
    busca el primer bus con cupo que sale en o despues de su llegada."""
    orden = sorted(range(len(llegadas)), key=lambda i: (llegadas[i], i))
    ocupados = {}
    salidas = [0] * len(llegadas)
    for i in orden:
        bus = max(1, -(-llegadas[i] // frecuencia))
        while ocupados.get(bus, 0) >= capacidad:
            bus += 1
        ocupados[bus] = ocupados.get(bus, 0) + 1
        salidas[i] = bus * frecuencia
    return salidas


def probar_fila():
    assert simular_fila([30, 5, 5, 70], 60, 2) == [120, 60, 60, 120]
    ok("ejemplo del enunciado [30,5,5,70] -> [120,60,60,120]")
    assert simular_fila([], 60, 2) == []
    assert simular_fila([0], 60, 2) == [60]
    assert simular_fila([60], 60, 2) == [60]        # llega justo cuando sale
    assert simular_fila([61], 60, 2) == [120]
    assert simular_fila([5, 5, 5], 10, 1) == [10, 20, 30]
    assert simular_fila([1000], 60, 5) == [1020]    # salta buses vacios
    ok("bordes: vacia, llegada en 0, llegada justo en la salida, saltos")
    for frecuencia, capacidad in ((60, 2), (7, 3), (1, 1), (100, 50)):
        for _ in range(300):
            n = aleatorio.randint(0, 40)
            llegadas = [aleatorio.randint(0, 400) for _ in range(n)]
            assert simular_fila(llegadas, frecuencia, capacidad) == \
                fila_referencia(llegadas, frecuencia, capacidad), (llegadas, frecuencia, capacidad)
    ok("1200 casos al azar iguales a la referencia")
    try:
        simular_fila([1], 0, 1)
        raise AssertionError("debio fallar con frecuencia 0")
    except ValueError:
        pass
    ok("frecuencia/capacidad invalidas -> ValueError")
    llegadas = [aleatorio.randint(0, 3600) for _ in range(300000)]
    inicio = time.perf_counter()
    salidas = simular_fila(llegadas, 30, 80)
    seg = time.perf_counter() - inicio
    assert len(salidas) == 300000
    ok("300.000 personas en %.2f s" % seg)


# ------------------------------------------------------------------- R5
def cargar_rutas_referencia():
    import csv
    rutas = {}
    with open(DATOS + "/rutas.csv", encoding="utf-8-sig") as f:
        for fila in list(csv.reader(f))[1:]:
            rutas.setdefault(fila[0], []).append(fila[2])
    return rutas


def costo_referencia(rutas, abiertas, o, d):
    """Menor numero de paradas (directo o 1 transbordo) por fuerza bruta."""
    if o == d or o not in abiertas or d not in abiertas:
        return None
    mejor = None
    for r1, p1 in rutas.items():
        if o not in p1:
            continue
        i = p1.index(o)
        if d in p1[i + 1:]:
            c = p1.index(d, i + 1) - i
            mejor = c if mejor is None or c < mejor else mejor
        for q in range(i + 1, len(p1)):
            t = p1[q]
            if t == d or t not in abiertas:
                continue
            for r2, p2 in rutas.items():
                if t in p2 and d in p2:
                    j = p2.index(t)
                    if d in p2[j + 1:]:
                        c = (q - i) + (p2.index(d, j + 1) - j)
                        mejor = c if mejor is None or c < mejor else mejor
    return mejor


def costo_de_viaje(rutas, tramos):
    """Valida un viaje devuelto y calcula sus paradas."""
    total = 0
    for ruta, sube, baja in tramos:
        paradas = rutas[ruta]
        i, j = paradas.index(sube), paradas.index(baja)
        assert j > i, "baja antes de subir: %r" % ((ruta, sube, baja),)
        total += j - i
    for a, b in zip(tramos, tramos[1:]):
        assert a[2] == b[1], "el transbordo no empalma"
    return total


def probar_viaje():
    red = Red(DATOS)
    rutas = cargar_rutas_referencia()
    todas = sorted({e for p in rutas.values() for e in p})

    v = red.viaje("PORTAL NORTE", "PORTAL SUR")
    assert v is not None and 1 <= len(v) <= 2
    ok("PORTAL NORTE -> PORTAL SUR: %s" % (v,))

    assert red.viaje("NO ESTOY", "PORTAL SUR") is None
    assert red.viaje("PORTAL SUR", "NO ESTOY") is None
    assert red.viaje("PORTAL SUR", "PORTAL SUR") is None
    ok("bordes: inexistente, mismo origen y destino -> None")

    # Comparar con fuerza bruta en 400 pares al azar (abiertas todas).
    abiertas = set(todas)
    for _ in range(400):
        o, d = aleatorio.choice(todas), aleatorio.choice(todas)
        v = red.viaje(o, d)
        esperado = costo_referencia(rutas, abiertas, o, d)
        if esperado is None:
            assert v is None, (o, d, v)
        else:
            assert v is not None and v[0][1] == o and v[-1][2] == d
            assert costo_de_viaje(rutas, v) == esperado, (o, d, v, esperado)
    ok("400 pares al azar: mismo costo minimo que la fuerza bruta")

    # Estaciones cerradas.
    o, d = "PORTAL NORTE", "PORTAL SUR"
    assert red.cerrar(d) is True
    assert red.viaje(o, d) is None
    assert red.viaje(d, o) is None
    red.reabrir(d)
    ok("destino/origen cerrado -> None")

    for _ in range(150):
        o, d = aleatorio.choice(todas), aleatorio.choice(todas)
        v = red.viaje(o, d)
        if v is not None and len(v) == 2:
            t = v[0][2]
            assert red.cerrar(t) is True
            cerradas = {t}
            nuevo = red.viaje(o, d)
            esperado = costo_referencia(rutas, set(todas) - cerradas, o, d)
            if esperado is None:
                assert nuevo is None
            else:
                assert nuevo is not None
                assert all(x[2] != t or x[2] == d for x in nuevo[:-1])
                assert costo_de_viaje(rutas, nuevo) == esperado
            red.reabrir(t)
    ok("150 casos con la estacion de transbordo cerrada: se evita y es optimo")


def main():
    print("Estructuras compartidas")
    probar_estructuras()
    print("R10 fila de abordaje")
    probar_fila()
    print("R5 viaje")
    probar_viaje()
    print("\nTODO BIEN")


if __name__ == "__main__":
    main()
