# Guía de estudio — Parte E: optimización del motor y front animado

Objetivo: poder explicar qué se cambió, por qué es más rápido y cómo funciona cada animación. En la
sustentación pueden preguntar **"¿qué cambiaron, qué O grande tenía antes y cuál tiene ahora, y cómo lo
comprobaron?"**.

## 0. Mapa de archivos

| Archivo | Qué hace la Parte E ahí |
|---|---|
| `motor/viaje.py` | R5 pasa de O(S + P) a O(P) por consulta |
| `motor/fila.py` | R10 ordena por conteo (O(n)) y la cola es un tramo del arreglo ordenado |
| `motor/estructuras.py` | `TablaHash` y `ordenar_mezcla` más rápidas, misma interfaz |
| `herramientas/medir.py` | Mide por lotes las consultas cortas; filas nuevas para R5 y R10 |
| `front/app.py` | Menú con `st.navigation`, tema y logo |
| `front/visual/tema.py` | CSS global, letreros, escenas de entrada, cargas y piezas reutilizables |
| `front/visual/dibujos.py` | Todos los dibujos SVG (bus, estación, torniquete, reloj, personas, iconos) |
| `front/visual/animaciones.py` | Prepara los datos y muestra las dos animaciones interactivas |
| `front/visual/plantillas/viaje.html` | Mapa del viaje (JavaScript) |
| `front/visual/plantillas/fila.html` | Andén de hora pico y gráfica (JavaScript) |
| `front/static/` | Fuentes Barlow (licencia OFL) y logo |
| `.streamlit/config.toml` | Colores, fuentes y opciones del tema |
| `pruebas/probar_parte_e.py` | Compara todo contra fuerza bruta y abre las 7 páginas |

Regla que se respetó: **nada de esto cambia el contrato del motor** (`motor/red.py` no se tocó) y los
archivos de B, C y D tampoco. Ellos se benefician porque usan `TablaHash` y `ordenar_mezcla`.

---

## 1. R5 — de O(S + P) a O(P)

**Antes.** Cada consulta hacía `desde_o = [INFINITO] * S` (y otros tres arreglos iguales) y al final
recorría las S estaciones buscando el mejor transbordo. Aunque el viaje tocara 20 paradas, se pagaba S.
En la red de 80 000 estaciones eso eran ~2 ms por consulta.

**Ahora.**
1. Los cuatro arreglos se crean **una vez**, al construir el índice, llenos de infinito.
2. Cada vez que una posición deja de ser infinito, se anota en `tocados_o` (o `tocados_d`).
3. El transbordo `t` tiene que tener `desde_o[t]` y `hasta_d[t]` finitos, o sea estar en las **dos** listas:
   basta recorrer la más corta.
4. Antes de devolver, se ponen en infinito **solo** las posiciones tocadas, así la siguiente consulta los
   encuentra limpios.

Cada paso cuesta lo que se tocó, que es a lo sumo P → **O(P)**. Resultado: 1,95 ms → 0,017 ms (115 veces
más rápido) y la pendiente en el panel bajó de ~1,1 a ~0,2.

**Empates.** Antes se recorría `t` de 0 a S−1 y se quedaba el primero con el menor total, o sea el id menor.
Ahora el orden de `tocados` es otro, así que se desempata explícitamente por id menor
(`total == mejor_total and t < mejor_t`). Por eso la respuesta es **idéntica** a la de antes (se comprobó en
los 21 316 pares de estaciones, también con cierres y rutas editadas).

**Preguntas típicas**
* *¿Por qué no se limpia todo el arreglo al final?* Sería O(S) otra vez; limpiar solo lo tocado es O(P).
* *¿Y si una consulta se interrumpe a la mitad?* No hay forma de interrumpirla (no hay `return` antes de
  limpiar: la respuesta se arma primero y se devuelve después de limpiar).
* *¿Qué pasa al editar una ruta?* `invalidar()` hace que la siguiente consulta reconstruya el índice
  (O(L)) y con él los arreglos de trabajo, del tamaño correcto.

## 2. R10 — ordenamiento por conteo y cola sin copias

**Ordenar por conteo** (cuando las llegadas son enteros en un rango W ≤ 4n):
1. `inicio[v + 1] += 1` por cada llegada `v` → cuántas personas llegan en cada segundo.
2. Sumas acumuladas → `inicio[v]` = primera casilla del segundo `v` en el arreglo ordenado.
3. Se recorre la lista original de izquierda a derecha y cada persona va a `inicio[v]` (y se avanza).
   Como se recorre en orden, los empates quedan en su orden original: es **estable**.
Costo O(n + W). Con W ≤ 4n eso es O(n). Si W es enorme (o hay decimales) se usa merge sort.

**La cola.** La gente entra a la fila en orden de llegada, que es justo el orden del arreglo ordenado. Así
la fila siempre es un tramo continuo `orden[cabeza:fin]`: encolar es `fin += 1`, desencolar es
`cabeza += 1`. Es la misma idea de "arreglo + índice de cabeza", pero sin copiar a nadie a otra lista.

**Resultado:** 195 ms → 33 ms con 80 000 personas.

**Preguntas típicas**
* *¿Por qué W ≤ 4n?* Para que O(n + W) siga siendo O(n): el arreglo de conteo nunca es más de 4 veces
  la cantidad de personas (+1024 para casos chicos).
* *¿Conteo es estable?* Sí, porque el tercer paso recorre a las personas en su orden original.
* *¿Por qué el panel mide un poco más de 1?* Con arreglos grandes cada acceso cuesta un poco más por la
  memoria caché del computador; el algoritmo hace el mismo trabajo por persona.

## 3. `TablaHash` y `ordenar_mezcla`

**TablaHash**
* La capacidad es siempre potencia de 2 (16, 32, 64…). Entonces `hash & (capacidad − 1)` da lo mismo
  que `hash % capacidad` (los últimos bits), pero es una operación más barata.
* Cada entrada es `[clave, valor, hash]`. Al crecer no se vuelve a calcular `hash(clave)`, y al buscar se
  comparan primero los hash (dos enteros) antes de comparar las claves (una tupla de textos es más cara).
* `poner` calcula el hash una sola vez (antes lo hacía dos veces: una al buscar y otra al insertar).
* Sigue siendo O(1) promedio. Insertar 150 000 claves quedó ~20 % más rápido.

**ordenar_mezcla**
* Primero ordena por **inserción** bloques de 16 elementos: con tan pocos elementos la inserción es
  rápida, y así el merge empieza en bloques de 16 en vez de 1 (4 vueltas menos).
* Si el último del bloque izquierdo es ≤ al primero del derecho, ya están en orden: se copian sin mezclar.
* Sigue siendo O(n log n) y estable (la inserción solo mueve un elemento si es *estrictamente* menor).
  Es la misma idea de Timsort, el ordenamiento que usa Python por dentro.

## 4. Cómo se comprobó (`pruebas/probar_parte_e.py`)

* `viaje` contra una **fuerza bruta** que prueba todas las combinaciones de rutas: mismo costo y misma
  cantidad de tramos, también con estaciones cerradas y rutas editadas. Además revisa que los arreglos de
  trabajo queden limpios.
* `simular_fila` contra una simulación lenta y obvia, y conteo contra merge sort (mismo orden).
* `TablaHash` contra `dict` en 30 000 operaciones al azar; `ordenar_mezcla` contra `sorted` y su estabilidad.
* Abre las 7 páginas de la app con `AppTest` de Streamlit y revisa que no haya errores.

## 5. El front

**Cómo se arma una página.** `front/app.py` pone el tema (`tema.aplicar_tema()`), el logo y el menú
(`st.navigation`), y ejecuta la página elegida. Cada página empieza con `tema.encabezado("clave")`, que
pinta el letrero y, solo la primera vez que se entra, la escena animada.

**¿Cómo sabe que es la primera vez?** Guarda la clave de la página en `st.session_state["tm_pagina"]`. Si
la página actual es distinta de la guardada, muestra la escena; si se vuelve a ejecutar la misma página (por
ejemplo al mover un control), no.

**Las escenas** son SVG dibujados a mano (`dibujos.py`) con clases `tm-…` que el CSS anima con
`@keyframes`: el bus que llega, la estación que se arma, la tarjeta en el validador, el reloj y la gente
caminando, el tablero de salidas, la parada nueva en la ruta, las curvas del panel. La pantalla se desvanece
sola a los ~2 s y deja pasar los clics (`pointer-events: none`).

**El mapa del viaje** (`plantillas/viaje.html`):
* Recibe los tramos con sus paradas (lo que devolvió `red.viaje` + `red.recorrido`).
* Reparte las paradas en filas de 7 que se devuelven (serpiente); entre filas dibuja un medio círculo.
* Cada tramo entre paradas es un `<path>`. El bus se ubica con `getPointAtLength` y se gira con la dirección
  del camino; si va a la izquierda se refleja para que no quede de cabeza.
* La línea se "pinta" detrás del bus con `stroke-dashoffset`.
* En el transbordo cambia la insignia de ruta que va encima del bus.

**El andén de hora pico** (`plantillas/fila.html`):
* Python resume el resultado de `simular_fila` por bus: hora, cuántos llegaron, cuántos subieron, cuántos
  quedaron (`animaciones.resumen_fila`). Si hay más de 240 buses, se agrupan.
* Cada figura del andén es una persona o un grupo (si son miles). Las figuras se mueven con transiciones CSS:
  llegan por la izquierda, el bus entra, suben las primeras hasta el cupo, el bus sale y las que quedaron se
  ponen en rojo.
* La gráfica de abajo es la fila después de cada bus; la línea punteada sigue a la animación y la barra
  permite saltar a cualquier bus.

**Otras piezas:** el tablero de salidas (R4) calcula cuántos minutos faltan; el ranking (R6) dibuja barras
proporcionales al primero; el mapa de línea (R7) marca en verde la parada recién agregada y en rojo las
cerradas.

**Accesibilidad.** Con `prefers-reduced-motion` no hay escenas de entrada y las animaciones muestran el
resultado final directamente. Los botones tienen foco visible y los textos de estado usan `aria-live`.

**Preguntas típicas del front**
* *¿El front tiene lógica del sistema?* No: quién sube a qué bus lo decide `simular_fila`; el front solo
  cuenta para dibujar. El viaje lo decide `red.viaje`; el front solo lo recorre.
* *¿Por qué `components.html` y no `st.markdown` para las animaciones?* `st.markdown` acepta SVG y CSS pero
  no ejecuta JavaScript; el mapa y el andén necesitan JavaScript para moverse paso a paso.
* *¿Por qué las fuentes están en el repo?* Para que la app se vea igual sin internet (la licencia OFL lo
  permite).

## 6. Cambios en vivo que podrían pedirte

* "Que el bus del mapa vaya más lento": en `viaje.html`, subir el `7000` de `tSeg` (milisegundos que dura
  todo el recorrido).
* "Que en hora pico quepan más figuras": subir `MAX_FIGURAS` en `animaciones.py`.
* "Que el conteo se use solo si W ≤ 2n": cambiar `4 * n` en `simular_fila`.
* "Que la tabla hash crezca al pasar 0,5 de carga": cambiar `* 4 > ... * 3` por `* 2 > ...` en `poner`.
