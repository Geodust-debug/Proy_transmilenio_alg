"""Motor del planeador TransMilenio.

El script del profesor hace exactamente esto:
    from motor import Red, simular_fila
"""
from .red import Red
from .fila import simular_fila

__all__ = ["Red", "simular_fila"]
