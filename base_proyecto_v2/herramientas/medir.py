"""Mide cuanto tarda cada operacion del motor en redes de tamano creciente (R11).

Uso desde la terminal (desde la raiz del repo):
    python herramientas/medir.py 1000 2000 4000 8000
Los tamanos oficiales de la evaluacion son 10000 20000 40000 80000.

Para cada operacion se toma la MEDIANA de varias repeticiones y luego se
calcula la pendiente de log(tiempo) contra log(n):
    pendiente ~ 0  -> tiempo constante (O(1) u O(log n))
    pendiente ~ 1  -> lineal;  n log n da un poco mas de 1.
Es el metodo del Taller 1 (duplicar n y mirar que pasa) con mas puntos.
Esta fuera de motor/: aqui SI se puede usar cualquier libreria.
"""
import math
import random
import statistics
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "herramientas"))

from generar_red import generar_red  # noqa: E402
from motor import Red, simular_fila  # noqa: E402

# (operacion, requisito, O grande esperada, pendiente esperada)
# Si su diseno es otro (p. ej. cerrar en O(log n)), ajusten la fila y explicalo en el panel.
OPERACIONES = [
    ("carga", "—", "O(n)", 1.0),
    ("estado", "R1", "O(1)", 0.0),
    ("autocompletar", "R2", "O(log n + k)", 0.0),
    ("rango", "R3", "O(log n + m)", 0.0),
    ("proximo_bus", "R4", "O(log m)", 0.0),
    ("ranking", "R6", "O(k)", 0.0),
    ("agregar_parada", "R7", "O(1)", 0.0),
    ("quitar_parada", "R7", "O(1)", 0.0),
    ("recorrido", "R7", "O(largo de la ruta)", 0.0),
    ("cerrar", "R8", "O(1) u O(log n)", 0.0),
    ("reabrir", "R8", "O(1) u O(log n)", 0.0),
    ("deshacer", "R9", "O(1)", 0.0),
    ("rehacer", "R9", "O(1)", 0.0),
    ("simular_fila", "R10", "O(n log n)", 1.1),
    ("viaje", "R5", "no se compara", None),
]
TOLERANCIA = 0.35


def _tiempo(funcion):
    inicio = time.perf_counter()
    funcion()
    return time.perf_counter() - inicio


def medir_red(n, repeticiones=30, semilla=1):
    """Genera una red de n estaciones y devuelve {operacion: mediana en segundos}."""
    azar = random.Random(semilla)
    carpeta = Path(tempfile.gettempdir()) / "transmilenio_redes" / ("red_%d" % n)
    datos = generar_red(carpeta, n, semilla)
    tiempos = {}

    inicio = time.perf_counter()
    red = Red(str(carpeta))
    tiempos["carga"] = time.perf_counter() - inicio

    nombres = datos.estaciones
    ordenadas = sorted(nombres)
    muestras = {op[0]: [] for op in OPERACIONES}

    for _ in range(repeticiones):
        nombre = azar.choice(nombres)
        muestras["estado"].append(_tiempo(lambda: red.estado(nombre)))

        prefijo = azar.choice(nombres)[:6]
        muestras["autocompletar"].append(_tiempo(lambda: red.autocompletar(prefijo, 10)))

        i = azar.randrange(len(ordenadas) - 30) if len(ordenadas) > 31 else 0
        desde, hasta = ordenadas[i], ordenadas[min(i + 30, len(ordenadas) - 1)]
        muestras["rango"].append(_tiempo(lambda: red.rango(desde, hasta)))

        ruta, paradas = azar.choice(datos.rutas)
        estacion = azar.choice(paradas)
        muestras["proximo_bus"].append(_tiempo(lambda: red.proximo_bus(estacion, ruta, "12:00")))

        muestras["recorrido"].append(_tiempo(lambda: red.recorrido(ruta)))

    red.ranking(10)   # calentamiento: la primera vez puede construir el ranking
    for _ in range(repeticiones):
        muestras["ranking"].append(_tiempo(lambda: red.ranking(10)))

    # agregar / quitar parada (se restaura la ruta despues de cada agregado)
    for _ in range(repeticiones):
        ruta, paradas = azar.choice(datos.rutas)
        en_ruta = set(paradas)
        nueva = azar.choice(nombres)
        while nueva in en_ruta:
            nueva = azar.choice(nombres)
        despues_de = azar.choice(paradas)
        muestras["agregar_parada"].append(_tiempo(lambda: red.agregar_parada(ruta, nueva, despues_de)))
        muestras["quitar_parada"].append(_tiempo(lambda: red.quitar_parada(ruta, nueva)))

    # cerrar -> deshacer -> rehacer -> reabrir sobre las mismas estaciones
    elegidas = azar.sample(nombres, min(repeticiones, len(nombres)))
    for e in elegidas:
        muestras["cerrar"].append(_tiempo(lambda: red.cerrar(e)))
    for _ in elegidas:
        muestras["deshacer"].append(_tiempo(red.deshacer))
    for _ in elegidas:
        muestras["rehacer"].append(_tiempo(red.rehacer))
    for e in elegidas:
        muestras["reabrir"].append(_tiempo(lambda: red.reabrir(e)))

    # R10: n personas
    llegadas = [azar.randint(0, 3600) for _ in range(n)]
    for _ in range(3):
        muestras["simular_fila"].append(_tiempo(lambda: simular_fila(llegadas, 30, 80)))

    # R5 (solo informativo)
    for _ in range(min(repeticiones, 10)):
        _, p1 = azar.choice(datos.rutas)
        _, p2 = azar.choice(datos.rutas)
        o, d = azar.choice(p1), azar.choice(p2)
        muestras["viaje"].append(_tiempo(lambda: red.viaje(o, d)))

    for operacion, lista in muestras.items():
        if lista:
            tiempos[operacion] = statistics.median(lista)
    return tiempos


def pendiente(tamanos, tiempos):
    """Pendiente de la recta de minimos cuadrados de log(tiempo) contra log(n)."""
    xs = [math.log(n) for n in tamanos]
    ys = [math.log(max(t, 1e-9)) for t in tiempos]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def medir(tamanos, repeticiones=30, progreso=None):
    """Mide todos los tamanos. Devuelve {n: {operacion: segundos}}."""
    resultado = {}
    for k, n in enumerate(tamanos):
        resultado[n] = medir_red(n, repeticiones)
        if progreso:
            progreso(k + 1, len(tamanos), n)
    return resultado


def tabla_resumen(resultado):
    """Filas (operacion, requisito, esperada, pendiente esperada, pendiente medida, veredicto)."""
    tamanos = sorted(resultado.keys())
    filas = []
    for operacion, requisito, esperada, p_esperada in OPERACIONES:
        tiempos = [resultado[n].get(operacion) for n in tamanos]
        if len(tamanos) < 2 or any(t is None for t in tiempos):
            continue
        p = pendiente(tamanos, tiempos)
        if p_esperada is None:
            veredicto = "—"
        elif abs(p - p_esperada) <= TOLERANCIA:
            veredicto = "OK"
        else:
            veredicto = "NO COINCIDE"
        filas.append((operacion, requisito, esperada, p_esperada, p, veredicto))
    return filas


if __name__ == "__main__":
    tamanos = [int(x) for x in sys.argv[1:]] or [1000, 2000, 4000, 8000]
    res = medir(tamanos, progreso=lambda k, total, n: print("  medida red de %d (%d/%d)" % (n, k, total)))
    print("\n%-16s %-4s %-20s %9s %9s  %s" % ("operacion", "req", "esperada", "pend.esp", "pend.med", "veredicto"))
    for op, req, esp, pe, pm, ver in tabla_resumen(res):
        print("%-16s %-4s %-20s %9s %9.2f  %s" % (op, req, esp, "—" if pe is None else "%.1f" % pe, pm, ver))
