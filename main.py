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
