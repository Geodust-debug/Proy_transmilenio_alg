# Guía de estudio — Parte A (Martín): R5 viaje y R10 fila

Objetivo: poder explicar cada línea y defender cada decisión. En la sustentación te hacen
**"qué usaron, por qué no otra cosa, qué pasa si cambias X por Y, cuál es la O grande y qué es n"**
y además te piden un **cambio en vivo**.

## 0. Mapa de archivos
| Archivo | Qué hace |
|---|---|
| `motor/estructuras.py` | `TablaHash` (diccionario propio) y `ordenar_mezcla` (merge sort) |
| `motor/viaje.py` | R5 |
| `motor/fila.py` | R10 (`simular_fila`) |
| `motor/red.py` | Fachada: la clase `Red` del contrato; solo delega y avisa a los módulos |

## 1. `TablaHash` (la usa `viaje.py`)
* **Problema:** dado un nombre de estación, encontrar su id sin recorrer todo (y sin `dict`).
* **Cómo funciona:** un arreglo de cubetas; `hash(nombre) % capacidad` dice en cuál cubeta va.
  Cada cubeta es una lista corta de pares `[clave, valor]`. Si dos claves caen juntas
  (*colisión*) se busca en esa lista corta.
* **Por qué es O(1):** cuando hay más de 0,75 elementos por cubeta, la tabla duplica su tamaño y
  reubica todo (*rehash*). Así las cubetas siempre son cortas. Duplicar cuesta O(n) pero pasa pocas
  veces → O(1) amortizado.
* **Si te preguntan "¿y si todas las claves caen en la misma cubeta?"** Degenera a O(n). Con un
  buen `hash` y rehash es rarísimo.
* **Alternativa:** arreglo ordenado + búsqueda binaria (O(log n)); más lento que O(1) pero guarda orden.
* **Optimización (Parte E):** la capacidad siempre es potencia de 2, así la cubeta sale con
  `hash & (capacidad - 1)` (igual que `%` pero más rápido); cada entrada guarda su hash
  (`[clave, valor, hash]`), así al crecer no se recalcula y al buscar se comparan primero dos enteros.
  Detalle en `docs/guia_parte_E.md`.

## 2. `ordenar_mezcla` (merge sort)
* Mezclar dos bloques ya ordenados es O(n) (se avanza con dos punteros). Se parte desde bloques de
  1 elemento: tamaño 1 → 2 → 4 → … Son log₂ n vueltas de O(n) = **O(n log n)**.
* **Estable:** si dos elementos son iguales conserva el orden original (por eso la comparación es
  `origen[j] < origen[i]` estricta). Lo necesitamos en R10.
* **Por qué no quicksort:** O(n²) en el peor caso y no es estable. **Por qué no insertion/bubble:**
  O(n²), inviable con cientos de miles de personas.
* **Optimización (Parte E):** los bloques iniciales de 16 se ordenan por inserción (con 16 elementos
  la inserción es rápida y se ahorran 4 vueltas) y si dos bloques vecinos ya están en orden se copian
  sin mezclar. Sigue siendo O(n log n) y estable (la misma idea de Timsort).

## 3. R5 — `viaje.py`
**Modelo.** Un grafo bipartito: nodos *estación* y nodos *ruta*. `_entradas[e]` = rutas que pasan
por la estación `e` con su posición. `_ids_ruta[r]` = estaciones de la ruta `r` en orden.

**Idea.** Con un solo transbordo hay dos formas de viajar:
1. **Directo:** una ruta que pase por el origen y luego por el destino.
2. **Transbordo:** ruta `r1` del origen hasta `T`, y ruta `r2` de `T` al destino.

Entonces:
* `desde_o[t]` = menos paradas de origen a `t` **en una ruta**.
* `hasta_d[t]` = menos paradas de `t` a destino **en una ruta**.
* Directo = `desde_o[destino]`. Transbordo = mínimo de `desde_o[t] + hasta_d[t]` (con `t` abierta).

**Ejemplo (los datos reales):** `PORTAL NORTE → PORTAL SUR` da
`[('F28-1','PORTAL NORTE','AV. CHILE'), ('G22-1','AV. CHILE','PORTAL SUR')]`: sube a F28-1, baja en
AV. CHILE, cambia a G22-1.

**Por qué es un BFS.** Nivel 1 = rutas que pasan por el origen; nivel 2 = rutas que se cruzan con
las del nivel 1 y llegan al destino. Es un BFS cortado a 2 niveles, pero en vez de contar saltos
contamos **paradas**.

**Casos borde que maneja:** origen o destino cerrado/inexistente → `None`; origen = destino → `None`;
estación sin rutas → `None`; estación de transbordo cerrada → no se usa; empate directo vs.
transbordo → directo.

**O grande.** `L` = filas de rutas.csv, `S` = estaciones, `P` = paradas de las rutas que pasan por
origen y destino.
* construir índice: O(L) (una vez; se invalida cuando se edita una ruta);
* consulta: **O(P)**. Antes era O(S + P) porque cada consulta creaba arreglos de tamaño S y los
  recorría buscando el transbordo. Desde la Parte E los arreglos se crean una vez, cada consulta
  anota en `tocados_o` / `tocados_d` qué posiciones cambió, busca el transbordo solo entre esas y al
  final limpia solo esas. En la red de 80.000 estaciones pasó de ~2 ms a ~0,02 ms por consulta.

**Preguntas típicas**
* *¿Por qué no Dijkstra?* Con máximo 1 transbordo, dos pasadas bastan; Dijkstra necesitaría cola de
  prioridad (heap) y estado (estación, ruta). Si el enunciado permitiera N transbordos, sí.
* *¿Qué pasa si permiten 2 transbordos?* Habría que encadenar un nivel más (o pasar a BFS/Dijkstra
  sobre (estación, ruta)).
* *¿Por qué una lista de `[ruta, posición]` por estación?* Para saber en una ruta qué estaciones
  vienen después/antes sin buscarlas.
* *¿Por qué reconstruir el índice al editar rutas?* Porque las posiciones cambian al insertar o
  quitar una parada; reconstruir es O(L) y solo ocurre tras editar.

## 4. R10 — `fila.py`
**Paso 1: ordenar.** Hay que ordenar a las personas por llegada y, en empate, por posición
original (orden estable). Dos caminos (Parte E):
* **Conteo** (el caso normal): si las llegadas son enteros en un rango W ≤ 4n, se cuenta cuántas
  personas llegan en cada segundo, se hacen sumas acumuladas para saber dónde empieza cada segundo
  y se reparten las personas en orden. Es O(n + W) = O(n) y estable.
* **Merge sort** (rangos enormes o llegadas con decimales): se ordenan pares `(llegada, posición)`,
  O(n log n).

**Paso 2: simular con una cola (FIFO).** Como la gente entra a la fila ya en orden de llegada, la
cola es un tramo del arreglo ordenado: `orden[cabeza:fin]`. Encolar = mover `fin`; desencolar =
mover `cabeza`. Para el bus número `b` (sale en `b * frecuencia`):
1. Encolar a todas las personas que llegaron en o antes de esa hora.
2. Si la cola está vacía, saltar al primer bus que sale en o después de la próxima llegada:
   `ceil(t / frecuencia)` = `-(-t // f)`.
3. Si no, desencolar hasta `capacidad` personas: su salida es la hora del bus.

**Traza del ejemplo** `simular_fila([30, 5, 5, 70], 60, 2)`:
* Orden por llegada: persona 1 (5), persona 2 (5), persona 0 (30), persona 3 (70).
* Bus 1 (t=60): entran 1, 2, 0 a la cola (70 > 60 aún no). Suben 1 y 2 → salida 60. Queda 0.
* Bus 2 (t=120): entra 3. Suben 0 y 3 → salida 120.
* Resultado en el orden original: `[120, 60, 60, 120]` ✔

**O grande** (n = personas): ordenar O(n) con conteo (u O(n log n) con merge sort) + simular O(n)
= **O(n)** en el caso normal. Número de buses simulados ≤ 2n (cada iteración atiende a alguien o salta).

**Preguntas típicas**
* *¿Por qué una cola?* La fila real es FIFO: el primero en llegar es el primero en subir.
* *¿Por qué no `lista.pop(0)`?* Es O(n) (mueve todos los elementos); haría la simulación O(n²).
  Aquí la cola son dos índices (cabeza y fin) sobre el arreglo ordenado → O(1).
* *¿Por qué hay que ordenar?* Las llegadas vienen en cualquier orden y sube quien llegó antes.
* *¿Por qué conteo y no merge sort siempre?* Las llegadas son segundos dentro de una ventana
  (rango pequeño comparado con n): contar es O(n) y en la práctica unas 4 veces más rápido.
* *¿Por qué el techo `-(-t // f)`?* Es la división hacia arriba: el primer múltiplo de `f` que es
  ≥ `t` (sirve con enteros y con decimales).

## 5. Cambios en vivo que podrían pedirte (ensáyalos)
* "Que quien llega justo cuando sale el bus **no** alcance": cambia `<=` por `<` en la condición de
  encolar y ajusta el salto: `bus = t // f + 1`.
* "Que cada bus tenga capacidad distinta": pasar una lista de capacidades y usar
  `capacidad[bus]` en vez de un valor fijo.
* "Que viaje devuelva el de menos **transbordos** primero": comparar directo primero y solo si no
  existe buscar transbordo.
* "Que viaje no pase por estaciones cerradas aunque no se baje ahí": hay que filtrar las paradas
  cerradas al recorrer las rutas en `viaje()`.

## 6. Cómo correr las pruebas
```bash
python pruebas/probar_parte_a.py        # R5, R10 y estructuras
python pruebas/revisar_prohibidos.py    # que motor/ no use nada prohibido
```
