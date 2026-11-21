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
**Estructura:** tabla hash propia (`TablaHash`, encadenamiento con rehash al pasar 0,75 de carga) de
nombre → posición, más un arreglo de banderas `cerrada`. **Algoritmo:** consulta directa por clave.
**Alternativas descartadas:** recorrer la lista (O(n)); búsqueda binaria sobre el arreglo ordenado
(O(log n), más lenta que la tabla hash). **O grande** (n = número de estaciones): **O(1)** promedio.

### R2 · Autocompletar
**Estructura:** arreglo con todos los nombres en orden alfabético (merge sort al cargar) y un árbol de
Fenwick con las estaciones abiertas. **Algoritmo:** búsqueda binaria de la primera estación ≥ prefijo y
avance mientras empiece por el prefijo; las cerradas se saltan con el árbol de Fenwick (siguiente abierta en
O(log n)). **Alternativas descartadas:** trie (gasta mucha memoria y no sirve para R3); recorrer toda la lista
(O(n)). **O grande** (n = estaciones, k = resultados pedidos): **O(log n + k)**.

### R3 · Listar un rango
**Estructura:** la misma de R2. **Algoritmo:** dos búsquedas binarias (inicio ≥ desde y fin > hasta) y
recorrido saltando cerradas. Si desde > hasta devuelve `[]`; los extremos no tienen que existir.
**Alternativa descartada:** filtrar toda la lista (O(n)). **O grande** (n = estaciones, m = resultados):
**O(log n + m)**.

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
Estructura: una lista doblemente enlazada por ruta (nodos en arreglos paralelos _est, _sig, _ant, con cabeza, cola y largo por
ruta) y una tabla hash propia (ruta, estación) → nodo para encontrar cualquier parada al instante.

Algoritmo: agregar justo después de X = ubicar el nodo de X con la tabla hash y reconectar cuatro punteros; 
quitar = enlazar entre sí el anterior y el siguiente; el recorrido normal sigue _sig desde lacabeza y el recorrido
al revés sigue _ant desde la cola. Devuelve False si la ruta o la parada no existen, o si la estación nueva ya está en la ruta. 
despues_de = None inserta al inicio (lo usa deshacer).

Alternativas descartadas: arreglo por ruta (insertar/quitar mueveelementos, O(L)); lista simple 
(recorrer al revés o quitar es O(L)); lista doble sin tabla hash (encontrar la parada es O(L)); árbol balanceado 
(O(log L) y mucho más código).

O grande (L = paradas de la ruta): agregar y quitar O(1); recorrido O(L); cargar O(N log L) con N filas de rutas.csv.

### R8 · Cerrar y reabrir estaciones
**Estructura:** bandera por estación + árbol de Fenwick (un 1 por estación abierta). **Algoritmo:** cambiar la
bandera y actualizar el árbol; el arreglo ordenado no se mueve. Devuelve `False` si la estación no existe o ya
estaba en ese estado. **Alternativas descartadas:** quitar/insertar en el arreglo al cerrar/reabrir (O(n));
saltar cerradas una por una (peor caso O(cerradas)); árbol AVL (más complejo para el mismo O(log n)).
**O grande** (n = estaciones): **O(log n)**.

### R9 · Deshacer y rehacer
Estructura: dos pilas (LIFO) con listas: operaciones hechas y operaciones deshechas.

Algoritmo: cada cierre, reapertura o edición exitosa se apila como una tupla (("cerrar", e), ("agregar", ruta, nueva, despues_de),
("quitar", ruta, e, anterior)...) y borra la pila de rehacer; deshacer pasa la cima de una pila a la otra y la fachada ejecuta la operación
inversa (por eso quitar guarda el anterior); rehacer hace lo contrario. Si no hay nada, devuelve False.

Alternativas descartadas: guardar una copia completa de la red en cada cambio (O(tamaño de la red) de memoria y tiempo por cambio); una
sola lista con puntero (equivalente, pero las dos pilas se explican mejor).

O grande: registrar, deshacer y rehacer O(1) (n = cantidad de operaciones guardadas no influye).

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
