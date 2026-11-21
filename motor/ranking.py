from .estructuras import ordenar_mezcla


class Ranking:
    def __init__(self, nombres, horarios, esta_abierta):
        self._nombres = nombres
        self._horarios = horarios
        self._esta_abierta = esta_abierta
        self._orden = None             # cache: lista de (-buses, nombre)
        self._version_vista = -1       # version de Horarios con la que se armo

    def invalidar(self):
        """La fachada lo llama al cerrar/reabrir o editar rutas.

        Cerrar/reabrir no obliga a rehacer el orden (se filtra al consultar) y
        las ediciones de ruta suben horarios.version(), asi que aqui basta con
        olvidar el cache solo si hiciera falta. Se deja el aviso por contrato.
        """
        return None

    def _reconstruir(self):
        pares = []
        for nombre in self._nombres:
            pares.append((-self._horarios.buses_en(nombre), nombre))
        self._orden = ordenar_mezcla(pares)
        self._version_vista = self._horarios.version()

    def top(self, k):
        resultado = []
        if k <= 0:
            return resultado
        if self._orden is None or self._version_vista != self._horarios.version():
            self._reconstruir()
        for par in self._orden:
            if len(resultado) >= k:
                break
            if self._esta_abierta(par[1]):
                resultado.append((par[1], -par[0]))
        return resultado
