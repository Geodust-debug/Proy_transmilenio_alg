"""Pruebas de la Parte E: optimizaciones del motor y front nuevo.

Uso (desde la raiz del repo):
    python pruebas/probar_parte_e.py

Revisa que las versiones rapidas den EXACTAMENTE lo mismo que una version
lenta y obvia (fuerza bruta), y que todas las paginas de la app abran sin
errores.
"""
import logging
import random
import sys
from pathlib import Path

logging.disable(logging.WARNING)   # sin avisos de Streamlit al probar fuera del servidor

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "front"))

from motor import Red, simular_fila  # noqa: E402
from motor import fila as modulo_fila  # noqa: E402
from motor.estructuras import TablaHash, ordenar_mezcla  # noqa: E402
from motor.viaje import _INFINITO  # noqa: E402

DATOS = str(RAIZ / "datos")


def ok(texto):
    print("  ok ·", texto)


# ------------------------------------------------------------ R5 viaje O(P)
def viaje_fuerza_bruta(red, rutas, origen, destino):
    """Costo del mejor viaje (paradas) y numero de tramos, probando TODO."""
    if origen == destino or red.estado(origen) != "ABIERTA" or red.estado(destino) != "ABIERTA":
        return None
    recorridos = [red.recorrido(r) for r in rutas]
    mejor_directo = None
    mejor_transbordo = None
    for a in recorridos:
        for i in range(len(a)):
            if a[i] != origen:
                continue
            for j in range(i + 1, len(a)):
                costo1 = j - i
                if a[j] == destino and (mejor_directo is None or costo1 < mejor_directo):
                    mejor_directo = costo1
                t = a[j]
                if t == destino or red.estado(t) != "ABIERTA":
                    continue
                for b in recorridos:
                    for k in range(len(b)):
                        if b[k] != t:
                            continue
                        for m in range(k + 1, len(b)):
                            if b[m] == destino:
                                total = costo1 + m - k
                                if mejor_transbordo is None or total < mejor_transbordo:
                                    mejor_transbordo = total
    if mejor_directo is not None and (mejor_transbordo is None or mejor_directo <= mejor_transbordo):
        return mejor_directo, 1
    if mejor_transbordo is not None:
        return mejor_transbordo, 2
    return None


def costo_de(red, tramos):
    if tramos is None:
        return None
    total = 0
    for ruta, sube, baja in tramos:
        paradas = red.recorrido(ruta)
        total += paradas.index(baja) - paradas.index(sube)
    return total, len(tramos)


def probar_viaje():
    red = Red(DATOS)
    rutas = red._rutas.nombres()
    nombres = red.rango("A", "ZZZZ")
    azar = random.Random(7)
    assert red.viaje("PORTAL NORTE", "PORTAL SUR") == [
        ("F28-1", "PORTAL NORTE", "AV. CHILE"), ("G22-1", "AV. CHILE", "PORTAL SUR")]
    for vuelta in range(4):
        for _ in range(120):
            o, d = azar.choice(nombres), azar.choice(nombres)
            assert costo_de(red, red.viaje(o, d)) == viaje_fuerza_bruta(red, rutas, o, d), (o, d)
        red.cerrar(azar.choice(nombres))
        ruta = azar.choice(rutas)
        red.agregar_parada(ruta, azar.choice(nombres), red.recorrido(ruta)[0])
    ok("viaje da el mismo costo que la fuerza bruta (con cierres y rutas editadas)")
    v = red._viaje
    limpios = True
    for i in range(len(v._desde_o)):
        if v._desde_o[i] != _INFINITO or v._hasta_d[i] != _INFINITO:
            limpios = False
    assert limpios
    ok("los arreglos de trabajo quedan limpios despues de cada consulta")


# ------------------------------------------------------------ R10 fila
def fila_lenta(llegadas, frecuencia, capacidad):
    """Simulacion obvia segundo a segundo (solo para comparar)."""
    pendientes = sorted(range(len(llegadas)), key=lambda i: (llegadas[i], i))
    salidas = [None] * len(llegadas)
    bus = 1
    while pendientes:
        t = bus * frecuencia
        suben = [i for i in pendientes if llegadas[i] <= t][:capacidad]
        for i in suben:
            salidas[i] = t
        pendientes = [i for i in pendientes if salidas[i] is None]
        bus += 1
    return salidas


def probar_fila():
    azar = random.Random(11)
    for _ in range(300):
        n = azar.randint(1, 70)
        f, c = azar.randint(1, 15), azar.randint(1, 9)
        tope = azar.choice([3, 40, 400, 10 ** 7])
        llegadas = [azar.randint(0, tope) for _ in range(n)]
        if tope < 10 ** 7:   # con rangos enormes la version lenta tardaria mucho
            assert simular_fila(llegadas, f, c) == fila_lenta(llegadas, f, c)
        # las dos formas de ordenar dan el mismo orden
        minimo, maximo = min(llegadas), max(llegadas)
        if maximo - minimo < 5000:
            assert (modulo_fila._orden_por_conteo(llegadas, minimo, maximo - minimo + 1)
                    == modulo_fila._orden_por_mezcla(llegadas))
    ok("simular_fila igual a una simulacion lenta y obvia")
    con_decimales = [0.5, 2.25, 2.25, 31.0, 7.75]
    assert simular_fila(con_decimales, 10, 2) == [10, 10, 20, 40, 20]
    ok("llegadas con decimales usan merge sort y funcionan")


# ------------------------------------------------------------ estructuras
def probar_estructuras():
    azar = random.Random(3)
    t, d = TablaHash(), {}
    for _ in range(30000):
        clave = (azar.choice("ABCDEFG"), azar.randint(0, 900))
        op = azar.random()
        if op < 0.5:
            v = azar.randint(0, 99)
            t.poner(clave, v)
            d[clave] = v
        elif op < 0.8:
            assert t.obtener(clave) == d.get(clave)
            assert t.contiene(clave) == (clave in d)
        else:
            assert t.eliminar(clave) == (d.pop(clave, None) is not None)
        assert len(t) == len(d)
    ok("TablaHash se comporta igual que dict")

    class Par:
        def __init__(self, a, b):
            self.a, self.b = a, b

        def __lt__(self, otro):
            return self.a < otro.a

    for n in [0, 1, 2, 15, 16, 17, 33, 500, 4097]:
        datos = [Par(azar.randint(0, 9), i) for i in range(n)]
        salida = ordenar_mezcla(datos)
        assert [(p.a, p.b) for p in salida] == sorted((p.a, p.b) for p in datos)
        numeros = [azar.random() for _ in range(n)]
        assert ordenar_mezcla(numeros) == sorted(numeros)
        assert ordenar_mezcla(sorted(numeros)) == sorted(numeros)
    ok("ordenar_mezcla ordena y es estable (bloques de 16 + mezcla)")


# ------------------------------------------------------------ front
def probar_front():
    import csv
    import sys
    from motor import Red
    from visual import animaciones, dibujos, tema

    assert dibujos.color_ruta("B13-1")[0] == dibujos.TRONCALES["B"]
    assert dibujos.color_ruta("6-4")[0] == dibujos.TRONCALES["6"]
    for clave in tema.PAGINAS:
        assert tema.PAGINAS[clave][4](tema.acento(clave)).startswith("\n<svg")
    resumen = animaciones.resumen_fila([0, 1, 2, 3, 10], simular_fila([0, 1, 2, 3, 10], 5, 2))
    assert resumen == [[5, 4, 2, 2], [10, 1, 2, 1], [15, 0, 1, 0]]
    ok("dibujos, escenas y resumen de la fila")

    try:
        from streamlit.testing.v1 import AppTest
    except ImportError:
        print("  (streamlit no esta instalado: no se prueban las paginas)")
        return
    paginas = ["inicio.py", "paginas/1_Estaciones.py", "paginas/2_Horarios_y_ranking.py",
               "paginas/3_Operar_red.py", "paginas/4_Viaje.py", "paginas/5_Hora_pico.py",
               "paginas/6_Panel_rendimiento.py"]
    for pagina in paginas:
        app = AppTest.from_file(str(RAIZ / "front" / "app.py"), default_timeout=60)
        app.run()
        if pagina != "inicio.py":
            app.switch_page(pagina)
            app.run()
        assert not app.exception, (pagina, app.exception)
    ok("las 7 paginas abren sin errores")

    # ---- cosas nuevas: mapa, autocompletar dentro de Buscar, rutas de Horarios
    def abrir(pagina):
        app = AppTest.from_file(str(RAIZ / "front" / "app.py"), default_timeout=60)
        app.run()
        app.switch_page(pagina)
        app.run()
        return app

    app = abrir("paginas/1_Estaciones.py")
    assert [t.label for t in app.tabs] == ["Buscar", "Rango", "Cerrar y reabrir"], "autocompletar va dentro de Buscar"
    app.text_input(key="buscar").input("PORTAL").run()
    assert not app.exception
    opciones = app.button_group[0].options
    assert "PORTAL NORTE" in opciones and len(opciones) == 8, opciones
    ok("Estaciones: autocompletar dentro de Buscar (sugerencias de R2)")

    app = abrir("paginas/2_Horarios_y_ranking.py")
    app.selectbox[0].select("RICAURTE").run()
    assert not app.exception
    codigo = " ".join(m.value for m in app.markdown)
    assert "tm-salidas" in codigo and "rutas pasan por" in codigo
    ok("Horarios: al elegir una estacion salen sus rutas y el proximo bus de cada una")

    app = abrir("paginas/4_Viaje.py")
    app.button[1].click().run()        # Mostrar mapa (el 0 es Invertir)
    assert not app.exception and app.session_state["mapa_abierto"] is True
    ok("Viaje: el boton Mostrar mapa abre el mapa sin errores")

    sys.path.insert(0, str(RAIZ / "front"))
    from comun import nombres_rutas, posiciones, rutas_que_pasan
    from visual import componentes

    pos = posiciones()
    nombres = [fila[0] for fila in list(csv.reader(open(RAIZ / "datos" / "estaciones.csv",
                                                        encoding="utf-8-sig")))[1:] if fila]
    assert sorted(pos) == sorted(nombres), "posiciones.csv tiene que cubrir todas las estaciones"
    lista = list(pos.values())
    assert all(0 <= x <= 1000 and 0 <= y <= 700 for x, y in lista)
    assert all((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 > 100 for i, a in enumerate(lista) for b in lista[i + 1:]), \
        "dos estaciones quedaron casi encima en el mapa"
    ok("posiciones.csv: las 147 estaciones, dentro del lienzo y sin quedar encimadas")

    red = Red(str(RAIZ / "datos"))
    ruta = nombres_rutas()[0]
    paradas = red.recorrido(ruta)
    nueva = next(n for n in nombres if n not in paradas)
    if not red.agregar_parada(ruta, nueva, paradas[0]):
        print("  PENDIENTE · rutas.py (Parte D) todavia es la base provisional, que no edita rutas: "
              "no se prueba que el mapa siga las ediciones")
        return
    assert ruta in rutas_que_pasan(red, nueva), "Horarios debe ver las paradas que se agregan en Operar la red"
    datos = componentes.datos_mapa(red, pos, nombres_rutas(), paradas[0], nueva, red.viaje(paradas[0], nueva))
    nombres_ord = sorted(pos)
    i, j = nombres_ord.index(paradas[0]), nombres_ord.index(nueva)
    assert [min(i, j), max(i, j)] in datos["aristas"], "el mapa debe dibujar la conexion recien creada"
    assert datos["origen"] == i and datos["destino"] == j
    assert datos["viaje"] and datos["viaje"][0]["paradas"][0] == i and datos["viaje"][-1]["paradas"][-1] == j
    assert red.cerrar(nueva)
    cerrada = componentes.datos_mapa(red, pos, nombres_rutas())["estaciones"][j]
    assert cerrada["c"] is True
    assert red.deshacer() and red.deshacer()
    assert ruta not in rutas_que_pasan(red, nueva)
    ok("mapa y rutas de Horarios siguen los cambios de Operar la red (agregar, cerrar, deshacer)")


if __name__ == "__main__":
    print("Parte E")
    probar_estructuras()
    probar_fila()
    probar_viaje()
    probar_front()
    print("TODO BIEN")
