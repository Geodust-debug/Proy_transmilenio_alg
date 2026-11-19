"""Revisa que motor/ no use nada prohibido.   Uso:  python pruebas/revisar_prohibidos.py

ERROR  = seguro prohibido (dict, set, sorted, .sort, min, max, .index, .count,
         bisect, heapq, collections, functools, cualquier libreria externa).
AVISO  = un `x in algo`: esta prohibido si `algo` es una LISTA (en un texto
         o en range esta bien). Revisenlo a mano.
"""
import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PERMITIDOS = ("csv", "time", "random")
NOMBRES_PROHIBIDOS = ("dict", "set", "frozenset", "sorted", "min", "max")
METODOS_PROHIBIDOS = ("sort", "index", "count")


def revisar(archivo):
    errores = []
    avisos = []
    arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))
    for nodo in ast.walk(arbol):
        linea = getattr(nodo, "lineno", 0)
        if isinstance(nodo, (ast.Dict, ast.DictComp)):
            errores.append((linea, "diccionario ({...: ...})"))
        elif isinstance(nodo, (ast.Set, ast.SetComp)):
            errores.append((linea, "conjunto ({...})"))
        elif isinstance(nodo, ast.Name) and nodo.id in NOMBRES_PROHIBIDOS:
            errores.append((linea, "uso de " + nodo.id))
        elif isinstance(nodo, ast.Attribute) and nodo.attr in METODOS_PROHIBIDOS:
            errores.append((linea, "metodo ." + nodo.attr))
        elif isinstance(nodo, ast.Import):
            for alias in nodo.names:
                if alias.name.split(".")[0] not in PERMITIDOS:
                    errores.append((linea, "import " + alias.name))
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level == 0 and nodo.module.split(".")[0] not in PERMITIDOS:
                errores.append((linea, "from " + nodo.module + " import ..."))
        elif isinstance(nodo, ast.Compare):
            for operador in nodo.ops:
                if isinstance(operador, (ast.In, ast.NotIn)):
                    avisos.append((linea, "`in`: ok en texto/range, PROHIBIDO en listas"))
    return errores, avisos


def main():
    hay_errores = False
    for archivo in sorted((RAIZ / "motor").glob("*.py")):
        errores, avisos = revisar(archivo)
        for linea, msg in errores:
            print("ERROR  motor/%s:%d  %s" % (archivo.name, linea, msg))
            hay_errores = True
        for linea, msg in avisos:
            print("AVISO  motor/%s:%d  %s" % (archivo.name, linea, msg))
    if hay_errores:
        print("\nHay cosas prohibidas en motor/. Corrijanlas.")
        sys.exit(1)
    print("\nOK: no se encontro nada prohibido (revisa los AVISO a mano).")


if __name__ == "__main__":
    main()
