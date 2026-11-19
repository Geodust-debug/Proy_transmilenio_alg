"""Fachada del motor: la clase Red del contrato.

*** NADIE EDITA ESTE ARCHIVO despues del push inicial. ***
Aqui solo se "conectan" los modulos de cada parte. Cada integrante trabaja
SOLO en sus archivos, asi los 4 pushes no se pisan.

    Parte A (Martin)   : viaje.py, fila.py            (R5, R10)
    Parte B            : estaciones.py                (R1, R2, R3, R8)
    Parte C            : horarios.py, ranking.py      (R4, R6)
    Parte D            : rutas.py, historial.py       (R7, R9)

Protocolo entre modulos (ver docs/reparto.md para las firmas completas):
  * Cualquier cambio (cerrar, reabrir, agregar/quitar parada) pasa por los
    metodos _aplicar_* de abajo, que avisan a todos los modulos afectados.
  * Los cambios exitosos se guardan en el historial como tuplas:
        ("cerrar", nombre)                       ("reabrir", nombre)
        ("agregar", ruta, nueva, despues_de)     ("quitar", ruta, estacion, anterior)
    deshacer/rehacer ejecutan la operacion inversa/directa con _aplicar_*.
"""
from .carga import cargar_datos
from .estaciones import Estaciones
from .horarios import Horarios
from .ranking import Ranking
from .rutas import Rutas
from .historial import Historial
from .viaje import Viaje


class Red:
    def __init__(self, carpeta):
        datos = cargar_datos(carpeta)
        self._estaciones = Estaciones(datos.estaciones)
        self._rutas = Rutas(datos.rutas)
        self._horarios = Horarios(datos.horarios)
        self._ranking = Ranking(datos.estaciones, self._horarios,
                                self._estaciones.esta_abierta)
        self._viaje = Viaje(self._rutas, self._estaciones.esta_abierta)
        self._historial = Historial()

    # ------------------------------------------------------------ consultas
    def estado(self, nombre):                       # R1
        return self._estaciones.estado(nombre)

    def autocompletar(self, prefijo, k):            # R2
        return self._estaciones.autocompletar(prefijo, k)

    def rango(self, desde, hasta):                  # R3
        return self._estaciones.rango(desde, hasta)

    def proximo_bus(self, estacion, ruta, hora):    # R4
        if not self._estaciones.esta_abierta(estacion):
            return None                             # cerrada o inexistente
        return self._horarios.proximo_bus(estacion, ruta, hora)

    def viaje(self, origen, destino):               # R5
        return self._viaje.viaje(origen, destino)

    def ranking(self, k):                           # R6
        return self._ranking.top(k)

    def recorrido(self, ruta, al_reves=False):      # R7
        return self._rutas.recorrido(ruta, al_reves)

    # ------------------------------------------------- operaciones (R7, R8)
    def agregar_parada(self, ruta, nueva, despues_de):
        if despues_de is None:
            return False
        if self._estaciones.estado(nueva) == "NO EXISTE":
            return False
        if not self._aplicar_agregar(ruta, nueva, despues_de):
            return False
        self._historial.registrar(("agregar", ruta, nueva, despues_de))
        return True

    def quitar_parada(self, ruta, estacion):
        if not self._rutas.tiene_parada(ruta, estacion):
            return False
        anterior = self._rutas.anterior(ruta, estacion)   # None si era la primera
        if not self._aplicar_quitar(ruta, estacion):
            return False
        self._historial.registrar(("quitar", ruta, estacion, anterior))
        return True

    def cerrar(self, nombre):
        if not self._aplicar_cierre(nombre):
            return False
        self._historial.registrar(("cerrar", nombre))
        return True

    def reabrir(self, nombre):
        if not self._aplicar_apertura(nombre):
            return False
        self._historial.registrar(("reabrir", nombre))
        return True

    # ----------------------------------------------------- deshacer / rehacer
    def deshacer(self):                             # R9
        orden = self._historial.deshacer()
        if orden is None:
            return False
        tipo = orden[0]
        if tipo == "cerrar":
            self._aplicar_apertura(orden[1])
        elif tipo == "reabrir":
            self._aplicar_cierre(orden[1])
        elif tipo == "agregar":
            self._aplicar_quitar(orden[1], orden[2])
        elif tipo == "quitar":
            self._aplicar_agregar(orden[1], orden[2], orden[3])
        return True

    def rehacer(self):                              # R9
        orden = self._historial.rehacer()
        if orden is None:
            return False
        tipo = orden[0]
        if tipo == "cerrar":
            self._aplicar_cierre(orden[1])
        elif tipo == "reabrir":
            self._aplicar_apertura(orden[1])
        elif tipo == "agregar":
            self._aplicar_agregar(orden[1], orden[2], orden[3])
        elif tipo == "quitar":
            self._aplicar_quitar(orden[1], orden[2])
        return True

    # ------------------------------ operaciones internas (sin historial)
    def _aplicar_cierre(self, nombre):
        if not self._estaciones.cerrar(nombre):
            return False
        self._ranking.invalidar()
        return True

    def _aplicar_apertura(self, nombre):
        if not self._estaciones.reabrir(nombre):
            return False
        self._ranking.invalidar()
        return True

    def _aplicar_agregar(self, ruta, nueva, despues_de):
        if not self._rutas.agregar_parada(ruta, nueva, despues_de):
            return False
        self._horarios.agregar_parada(ruta, nueva, despues_de)
        self._ranking.invalidar()
        self._viaje.invalidar()
        return True

    def _aplicar_quitar(self, ruta, estacion):
        if not self._rutas.quitar_parada(ruta, estacion):
            return False
        self._horarios.quitar_parada(ruta, estacion)
        self._ranking.invalidar()
        self._viaje.invalidar()
        return True
