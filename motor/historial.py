class Historial:
    def __init__(self):
        self._hechos = []
        self._deshechos = []

    def registrar(self, orden):
        self._hechos.append(orden)
        self._deshechos = []

    def deshacer(self):
        if len(self._hechos) == 0:
            return None
        orden = self._hechos.pop()
        self._deshechos.append(orden)
        return orden

    def rehacer(self):
        if len(self._deshechos) == 0:
            return None
        orden = self._deshechos.pop()
        self._hechos.append(orden)
        return orden
