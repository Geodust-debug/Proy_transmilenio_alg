# Planeador de viajes TransMilenio

Proyecto del último corte de Estructuras de Datos y Algoritmos. Motor en Python (carpeta `motor/`)
y front web con Streamlit (carpeta `front/`) que solo llama al motor.

## Cómo arrancar la app
```bash
pip install -r requirements.txt
streamlit run front/app.py
```

## Estructura del repositorio
```text
motor/          el motor (toda la lógica de R1 a R10)
front/          la app web (solo llama al motor)
datos/          estaciones.csv, rutas.csv, horarios.csv
conversion/     script que convierte el GTFS a los tres CSV
herramientas/   generador de redes sintéticas y medidor de rendimiento (R11)
pruebas/        pruebas y revisor de cosas prohibidas en motor/
docs/           reparto del trabajo y guías de estudio
integrantes.md  quién hizo qué
```

## Notación
`n` se define en cada requisito. `S` = número de estaciones, `L` = filas de `rutas.csv`.

## Decisiones de diseño (R12)

### R1 · Buscar una estación
*(Parte B — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R2 · Autocompletar
*(Parte B — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R3 · Listar un rango
*(Parte B — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R4 · Próximo bus
*(Parte C — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R5 · Planear un viaje
**Estructura:** grafo bipartito estación ↔ ruta. Cada ruta es un arreglo ordenado de estaciones;
cada estación guarda una lista `[ruta, posición]` de las rutas que pasan por ella. Las estaciones
se identifican con un número entero usando una tabla hash propia (`TablaHash`).

**Algoritmo:** búsqueda por niveles (como un BFS limitado a 2 rutas). Desde el origen se recorre
hacia adelante cada ruta que pasa por él y se anota, para cada estación alcanzable, el menor número
de paradas; desde el destino se hace lo mismo hacia atrás. El mejor directo es el costo del origen
al destino; el mejor con transbordo es el mínimo de `desde_origen[t] + hasta_destino[t]` sobre las
estaciones abiertas `t`. Gana el de menos paradas; si empatan, el directo. Las estaciones cerradas no
pueden ser origen, destino ni transbordo.

**Alternativas descartadas:** BFS/Dijkstra sobre estaciones con estado (estación, ruta): sirve para
cualquier número de transbordos pero necesita cola de prioridad y es más complejo; como el enunciado
limita a un transbordo, los dos niveles bastan. Probar todos los pares de rutas: O(rutas²).

**O grande:** construir el índice O(L) (una vez, y otra vez tras editar una ruta); cada consulta
O(S + P), con `P` = paradas de las rutas que pasan por el origen y el destino. R5 no entra en la
medición de crecimiento.

### R6 · Ranking
*(Parte C — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R7 · Editar rutas
*(Parte D — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R8 · Cerrar y reabrir estaciones
*(Parte B — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R9 · Deshacer y rehacer
*(Parte D — pendiente)* Estructura: · Algoritmo: · Alternativa descartada y por qué: · O grande (n = ): 

### R10 · Fila de abordaje
**Estructura:** una cola FIFO (arreglo + índice de cabeza) que representa la fila de personas.

**Algoritmo:** (1) ordenar las personas por (hora de llegada, posición original) con merge sort
estable; (2) simular bus por bus: encolar a todos los que ya llegaron a la hora de salida y
desencolar hasta `capacidad`. Si la fila está vacía se salta directo al primer bus útil, así no se
simulan buses vacíos. Quien llega justo en el segundo en que sale un bus alcanza a subir.

**Alternativas descartadas:** `pop(0)` sobre una lista como cola (O(n) por extracción →
O(n²)); ordenamientos O(n²) (inviables con cientos de miles de personas); simular segundo a
segundo (O(tiempo total), no O(n)).

**O grande** (n = número de personas): ordenar O(n log n) + simular O(n) = **O(n log n)**.

### Decisión sobre horas mayores a 24:00
*(Parte C — pendiente)*

## Panel de rendimiento (R11)
Página `Panel rendimiento` de la app (`front/pages/6_Panel_rendimiento.py`). Genera redes sintéticas
con el formato de los tres CSV (`herramientas/generar_red.py`), mide cada operación con la mediana de
varias repeticiones y calcula la pendiente de log(tiempo) contra log(n): ≈0 es constante, ≈1 es
lineal. Junto a cada medición muestra la O grande esperada; si no coincide, la explicación va en la
misma página. También se puede correr por terminal: `python herramientas/medir.py 10000 20000 40000 80000`.

## App desplegada
*(si se despliega, la URL va aquí)*
