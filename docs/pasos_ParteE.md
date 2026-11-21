# Cómo subir la Parte E y los cambios del mapa (paso a paso)

Pega los bloques **uno a la vez** en Git Bash, desde la carpeta del proyecto (`~/Proy_transmilenio_alg`).
Si algo da error, no sigas: copia el mensaje y revísalo antes del siguiente bloque.

## 0. Antes de empezar

Si la página está corriendo, detenla con `Ctrl + C` (la terminal queda ocupada mientras Streamlit corre).

```bash
git checkout main
git pull
```

## 1. Poner los archivos nuevos

Copia el zip dentro de la carpeta del proyecto y extráelo encima (reemplaza lo viejo):

```bash
python -m zipfile -e Mapa_y_ParteE.zip .
rm Mapa_y_ParteE.zip
```

Si el zip quedó en Descargas, usa `python -m zipfile -e ~/Downloads/Mapa_y_ParteE.zip .`

## 2. Quitar lo que ya no sirve

La carpeta de páginas se llama ahora `paginas/` (con el nombre `pages/` Streamlit se rompe al recargar con F5).
También sobra el zip que subió Juan David, porque sus archivos ya están extraídos.

```bash
git rm -r --ignore-unmatch front/pages ParteE_Animaciones_y_Optimizacion.zip
```

## 3. Los archivos de Mauricio (Horarios y Ranking)

En GitHub, Mauricio subió su código a la raíz con los nombres `Horarios` y `ranking` (sin `.py` y fuera de `motor/`).
Por eso el motor sigue usando la versión provisional (el ranking sale vacío y Horarios no encuentra buses).
Avísale y, con su permiso, muévelos a su lugar:

```bash
git mv -f Horarios motor/horarios.py
git mv -f ranking motor/ranking.py
```

> Falta también `motor/rutas.py` de Tomás (la edición de rutas): mientras siga siendo la base provisional,
> **Operar la red** no puede agregar ni quitar paradas. Cuando él lo suba, no hay que cambiar nada más.

## 4. Instalar y probar

```bash
python -m pip install -r requirements.txt
python pruebas/probar_parte_e.py
```

Debe terminar en `TODO BIEN`. Si aparece una línea `PENDIENTE · rutas.py`, es lo del paso anterior (Tomás).

```bash
python -m streamlit run front/app.py
```

Revisa: **Planear un viaje** → botón *Mostrar mapa*; **Estaciones** → escribe `PORTAL`; **Horarios y ranking**;
**Operar la red** (cuando esté `rutas.py`). Detén con `Ctrl + C`.

## 5. Agregar a Juan David en `integrantes.md`

Abre `integrantes.md` y agrega esta fila al final de la tabla (revisa si su apellido es Riano o Riaño):

```
| Juan David Riano | Parte E: animaciones del front, hora pico, optimización del motor (R5, R10, TablaHash, ordenamiento) | `front/visual/`, `front/inicio.py`, `motor/viaje.py`, `motor/fila.py`, `motor/estructuras.py` |
```

## 6. Subir

```bash
git add -A
git status
git commit -m "Parte E (Juan David Riano) y mapa interactivo: animaciones, nuevo diseño, optimización del motor"
git push
```

`git status` antes del commit es para mirar qué se va a subir: deben verse `front/paginas/`, `front/visual/`,
`datos/posiciones.csv` y los archivos movidos; no debe aparecer nada raro como `__pycache__`.

Después abre `github.com/Geodust-debug/Proy_transmilenio_alg` y revisa que el README muestre las capturas.

## Qué trae este zip

- **Mapa de papel** en *Planear un viaje* (`datos/posiciones.csv`, `front/visual/componentes/`).
- **Autocompletar dentro de Buscar** en *Estaciones* (ya no es una pestaña aparte).
- **Línea editable** en *Operar la red*: clic en un tramo para agregar una parada ahí.
- **Horarios**: tabla con las rutas que pasan por la estación y el próximo bus de cada una.
- Carpeta `front/paginas/` (antes `front/pages/`), arreglo del F5.
- Todo lo de la Parte E: tema, animaciones, optimización de `viaje`, `fila`, `TablaHash` y el ordenamiento.
