"""Pruebas de la Parte C (R4 proximo bus, R6 ranking, conversion del GTFS).
Uso (desde la raiz del repo):   python pruebas/probar_parte_c.py

Fuera de motor/ SI se puede usar dict, sorted, etc.: aqui se usan para escribir
la respuesta de referencia lenta pero obviamente correcta.
"""
import csv
import random
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "conversion"))

from motor import Red
from motor.horarios import Horarios
from motor.ranking import Ranking

aleatorio = random.Random(5)
DATOS = RAIZ / "datos"


def ok(texto):
    print("  ok  ", texto)


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8-sig") as f:
        return [fila for fila in list(csv.reader(f))[1:] if fila]


def minutos(h):
    return int(h[:2]) * 60 + int(h[3:5])


def proximo_referencia(filas, est, ruta, hora):
    candidatas = [f[2] for f in filas if f[0] == ruta and f[1] == est and minutos(f[2]) >= minutos(hora)]
    return min(candidatas, key=minutos) if candidatas else None


# ------------------------------------------------------------------- R4
def probar_proximo_bus():
    filas = leer("horarios.csv")
    h = Horarios(filas)
    pares = sorted({(f[0], f[1]) for f in filas})
    for _ in range(3000):
        ruta, est = aleatorio.choice(pares)
        hora = "%02d:%02d" % (aleatorio.randint(0, 23), aleatorio.randint(0, 59))
        assert h.proximo_bus(est, ruta, hora) == proximo_referencia(filas, est, ruta, hora), (est, ruta, hora)
    ok("3000 consultas al azar iguales a la fuerza bruta")

    ruta, est = pares[0]
    horas = sorted(f[2] for f in filas if f[0] == ruta and f[1] == est)
    assert h.proximo_bus(est, ruta, horas[0]) == horas[0]           # justo a la hora: cuenta
    assert h.proximo_bus(est, ruta, "00:00") == horas[0]            # antes del primero
    assert h.proximo_bus(est, ruta, "23:59") in (None, "23:59")     # despues del ultimo
    assert h.proximo_bus("NO EXISTE", ruta, "10:00") is None
    assert h.proximo_bus(est, "RUTA-NO-EXISTE", "10:00") is None
    assert h.proximo_bus(est, ruta, "hola") is None
    assert h.proximo_bus(est, ruta, "7:05") == proximo_referencia(filas, est, ruta, "07:05")
    ok("bordes: exacto, antes del primero, despues del ultimo, inexistentes, hora mal escrita")


def probar_proximo_bus_via_red():
    red = Red(str(DATOS))
    filas = leer("horarios.csv")
    ruta, est = filas[100][0], filas[100][1]
    assert red.proximo_bus(est, ruta, "05:00") == proximo_referencia(filas, est, ruta, "05:00")
    red.cerrar(est)
    assert red.proximo_bus(est, ruta, "05:00") is None              # estacion cerrada
    red.reabrir(est)
    assert red.proximo_bus(est, ruta, "05:00") == proximo_referencia(filas, est, ruta, "05:00")
    ok("a traves de Red: estacion cerrada -> None, reabierta -> vuelve")


# ------------------------------------------------------------------- R6
def ranking_referencia(filas, nombres, cerradas, k):
    conteo = {n: 0 for n in nombres}
    for f in filas:
        conteo[f[1]] += 1
    orden = sorted((n for n in nombres if n not in cerradas), key=lambda n: (-conteo[n], n))
    return [(n, conteo[n]) for n in orden[:max(k, 0)]]


def probar_ranking():
    filas = leer("horarios.csv")
    nombres = [f[0] for f in leer("estaciones.csv")]
    red = Red(str(DATOS))
    assert red.ranking(3)[0] == ("RICAURTE", 4446)
    assert red.ranking(0) == [] and red.ranking(-1) == []
    cerradas = set()
    for paso in range(300):
        n = aleatorio.choice(nombres)
        if aleatorio.random() < 0.5:
            if red.cerrar(n):
                cerradas.add(n)
        else:
            if red.reabrir(n):
                cerradas.discard(n)
        k = aleatorio.randint(0, 25)
        assert red.ranking(k) == ranking_referencia(filas, nombres, cerradas, k), (paso, k)
    assert len(red.ranking(1000)) == len(nombres) - len(cerradas)
    ok("300 cierres/reaperturas al azar: ranking siempre igual a la referencia")


def probar_ranking_con_ediciones():
    filas = [["R1", "A", "10:00"], ["R1", "A", "11:00"], ["R1", "B", "10:05"], ["R2", "C", "10:00"]]
    h = Horarios(filas)
    abiertas = {"A": True, "B": True, "C": True, "D": True}
    r = Ranking(["A", "B", "C", "D"], h, lambda n: abiertas[n])
    assert r.top(4) == [("A", 2), ("B", 1), ("C", 1), ("D", 0)]      # empate B/C: alfabetico
    h.agregar_parada("R1", "D", "B")                                  # D pasa a las horas de B
    assert h.buses_en("D") == 1 and h.proximo_bus("D", "R1", "00:00") == "10:05"
    assert r.top(4) == [("A", 2), ("B", 1), ("C", 1), ("D", 1)]
    h.quitar_parada("R1", "A")
    assert h.buses_en("A") == 0 and h.proximo_bus("A", "R1", "00:00") is None
    assert r.top(1) == [("B", 1)]
    h.agregar_parada("R1", "A", None)                                 # deshacer: se restauran las horas
    assert h.buses_en("A") == 2 and h.proximo_bus("A", "R1", "10:30") == "11:00"
    abiertas["A"] = False
    assert r.top(2) == [("B", 1), ("C", 1)]
    ok("ediciones: agregar copia horas, quitar las guarda, restaurar las devuelve, ranking se actualiza")


# ------------------------------------------------------------ conversion
def probar_conversion():
    from convertir_gtfs import convertir
    with tempfile.TemporaryDirectory() as tmp:
        zip_ruta = Path(tmp) / "gtfs.zip"
        archivos = {
            "stops.txt": "stop_id,stop_name\ns1,Portal Norte\ns2,Calle 142\ns2b,Calle 142\ns3,Héroes\n",
            "routes.txt": "route_id,route_short_name\nr1,B10\nr2,\n",
            "trips.txt": "route_id,trip_id,direction_id\nr1,t1,0\nr1,t2,0\nr1,t3,1\nr2,t4,0\n",
            "stop_times.txt": (
                "trip_id,stop_id,stop_sequence,arrival_time,departure_time\n"
                "t1,s1,1,10:00:00,10:00:00\nt1,s2,2,10:05:00,10:05:00\nt1,s2b,3,10:06:00,10:06:00\nt1,s3,4,10:10:00,10:10:00\n"
                "t2,s1,1,25:10:00,25:10:00\nt2,s2,2,25:15:00,25:15:00\nt2,s3,3,25:20:00,25:20:00\n"
                "t3,s3,1,11:00:00,11:00:00\nt3,s1,2,11:20:00,11:20:00\n"
                "t4,s1,1,09:00:00,09:00:00\nt4,s3,2,09:30:00,09:30:00\n"
            ),
        }
        with zipfile.ZipFile(zip_ruta, "w") as zf:
            for nombre, texto in archivos.items():
                zf.writestr(nombre, texto)
        salida = Path(tmp) / "salida"
        convertir(str(zip_ruta), str(salida), "envolver")
        estaciones = [f[0] for f in list(csv.reader(open(salida / "estaciones.csv")))[1:]]
        assert estaciones == ["CALLE 142", "HEROES", "PORTAL NORTE"], estaciones      # sin tildes, mayusculas, sin repetidos
        rutas = list(csv.reader(open(salida / "rutas.csv")))[1:]
        assert [f for f in rutas if f[0] == "B10-1"] == [
            ["B10-1", "1", "PORTAL NORTE"], ["B10-1", "2", "CALLE 142"], ["B10-1", "3", "HEROES"]]   # andenes colapsados
        assert {f[0] for f in rutas} == {"B10-1", "B10-2", "r2-1"}
        horas = [f[2] for f in list(csv.reader(open(salida / "horarios.csv")))[1:]]
        assert "01:10" in horas and all(len(h) == 5 for h in horas)               # 25:10 -> 01:10
        convertir(str(zip_ruta), str(salida), "descartar")
        horas = [f[2] for f in list(csv.reader(open(salida / "horarios.csv")))[1:]]
        assert "01:10" not in horas and "10:00" in horas
        red = Red(str(salida))                                                     # el motor lee lo generado
        assert red.estado("HEROES") == "ABIERTA"
    ok("conversion GTFS -> CSV (tildes, andenes repetidos, horas 25:10, sentido, ruta sin nombre corto)")


def main():
    print("Parte C: horarios, ranking y conversion")
    probar_proximo_bus()
    probar_proximo_bus_via_red()
    probar_ranking()
    probar_ranking_con_ediciones()
    probar_conversion()
    print("\nTODO BIEN")


if __name__ == "__main__":
    main()
