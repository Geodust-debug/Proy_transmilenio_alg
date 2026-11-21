from .estructuras import TablaHash, ordenar_mezcla


def _a_minutos(texto):
    """'14:30' -> 870.  Devuelve None si el texto no tiene formato H:MM."""
    partes = texto.split(":")
    if len(partes) != 2:
        return None
    horas = partes[0].strip()
    minutos = partes[1].strip()
    if not horas.isdigit() or not minutos.isdigit():
        return None
    return int(horas) * 60 + int(minutos)


def _a_texto(minutos):
    """870 -> '14:30'."""
    return "%02d:%02d" % (minutos // 60, minutos % 60)


class Horarios:
    def __init__(self, filas):
        self._indice = TablaHash()
        self._listas = []
        self._conteo = TablaHash()
        self._papelera = TablaHash()
        self._version = 0
        # 1. Agrupar las horas por (ruta, estacion).
        for fila in filas:
            minutos = _a_minutos(fila[2])
            if minutos is None:
                continue
            clave = (fila[0], fila[1])
            i = self._indice.obtener(clave)
            if i is None:
                i = len(self._listas)
                self._listas.append([])
                self._indice.poner(clave, i)
            self._listas[i].append(minutos)
            self._conteo.poner(fila[1], self._conteo.obtener(fila[1], 0) + 1)
        # 2. Ordenar cada lista una sola vez.
        for i in range(len(self._listas)):
            self._listas[i] = ordenar_mezcla(self._listas[i])

    def version(self):
        """Numero que sube cada vez que cambian los conteos (lo usa Ranking)."""
        return self._version

    # ------------------------------------------------------------- R4
    def proximo_bus(self, estacion, ruta, hora):
        pedida = _a_minutos(hora)
        if pedida is None:
            return None
        i = self._indice.obtener((ruta, estacion))
        if i is None:
            return None
        horas = self._listas[i]
        izq = 0
        der = len(horas)
        while izq < der:                      # busqueda binaria: primera hora >= pedida
            medio = (izq + der) // 2
            if horas[medio] < pedida:
                izq = medio + 1
            else:
                der = medio
        if izq == len(horas):
            return None                       # no hay mas buses ese dia
        return _a_texto(horas[izq])

    # ------------------------------------------------------------- R6
    def buses_en(self, estacion):
        return self._conteo.obtener(estacion, 0)

    # --------------------------------------- avisos de la fachada (R7 / R9)
    def agregar_parada(self, ruta, nueva, despues_de):
        clave = (ruta, nueva)
        horas = self._papelera.obtener(clave)
        if horas is not None:                 # estaba quitada: restaurar sus horas
            self._papelera.eliminar(clave)
        else:
            horas = []
            if despues_de is not None:
                j = self._indice.obtener((ruta, despues_de))
                if j is not None:
                    horas = self._listas[j][:]    # mismas horas que la parada anterior
        i = self._indice.obtener(clave)
        if i is None:
            i = len(self._listas)
            self._listas.append(horas)
            self._indice.poner(clave, i)
        else:
            self._conteo.poner(nueva, self._conteo.obtener(nueva, 0) - len(self._listas[i]))
            self._listas[i] = horas
        self._conteo.poner(nueva, self._conteo.obtener(nueva, 0) + len(horas))
        self._version += 1

    def quitar_parada(self, ruta, estacion):
        clave = (ruta, estacion)
        i = self._indice.obtener(clave)
        if i is None:
            return None
        horas = self._listas[i]
        self._papelera.poner(clave, horas)    # guardarlas por si se deshace
        self._listas[i] = []
        self._conteo.poner(estacion, self._conteo.obtener(estacion, 0) - len(horas))
        self._version += 1
