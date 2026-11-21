# Reparto del trabajo (4 partes) y cómo hacer los pushes sin pisarse

## La idea en una frase
Cada integrante trabaja **solo en sus propios archivos**. Git junta los archivos de todos sin
conflictos, y el repo siempre arranca porque la base ya trae una versión provisional de cada
pieza que cada quien va reemplazando.

## Orden
1. **Martín** hace el primer push (base del repo + Parte A). Ya está todo listo para eso.
2. Los otros tres hacen `git clone` (o `git pull` si ya lo tenían) y trabajan **su** parte.
3. Cada uno hace varios commits **a lo largo de los días** (no uno solo al final: el historial
   de Git vale puntos y se penaliza si es de una sola persona o de un solo día).

## Las 4 partes

| Parte | Quién | Requisitos | Archivos que edita (solo estos) |
|---|---|---|---|
| **A** | Martín | R5 viaje, R10 fila, panel R11 | `motor/viaje.py`, `motor/fila.py`, `front/paginas/4_Viaje.py`, `front/paginas/5_Hora_pico.py`, `front/paginas/6_Panel_rendimiento.py`, `herramientas/` |
| **B** | Miguel | R1, R2, R3, R8 | `motor/estaciones.py`, `front/paginas/1_Estaciones.py` |
| **C** | Mauricio | R4, R6 + conversión GTFS | `motor/horarios.py`, `motor/ranking.py`, `front/paginas/2_Horarios_y_ranking.py`, `conversion/` |
| **D** | Tomás | R7, R9 | `motor/rutas.py`, `motor/historial.py`, `front/paginas/3_Operar_red.py` |

(Los nombres son una propuesta: cámbienlos si quieren, pero cada parte la hace UNA persona.)

### Parte E (paquete extra: optimización y front animado)
Se sube **de última**, cuando B, C y D ya estén en GitHub, porque le da el diseño nuevo a todas las
páginas. Cambia `motor/viaje.py`, `motor/fila.py` y `motor/estructuras.py` (misma interfaz, más rápidos),
`herramientas/medir.py`, todo `front/` y agrega `front/visual/`, `front/static/` y `.streamlit/`.
Pasos en `docs/pasos_ParteE.md` y explicación en `docs/guia_parte_E.md`.

Todos editan además **su sección** del `README.md` (decisiones, estructura, O grande) y su línea
en `integrantes.md`. Nadie toca `motor/red.py`, `motor/carga.py` ni `motor/estructuras.py`.
Si alguien necesita un cambio ahí, lo habla con el grupo primero.

## Flujo de Git para cada uno
```bash
git clone https://github.com/Geodust-debug/Proy_transmilenio_alg   # solo la primera vez
cd Proy_transmilenio_alg
git pull                                    # SIEMPRE antes de empezar a trabajar

# ... editan SUS archivos ...

python pruebas/revisar_prohibidos.py        # que motor/ no use nada prohibido
git add motor/estaciones.py front/paginas/1_Estaciones.py README.md   # solo lo suyo
git commit -m "Describo lo que hice"
git pull                                    # por si otro subió algo mientras trabajaban
git push
```
Si `git push` dice *rejected*, es que alguien subió antes: hagan `git pull` y repitan `git push`.
Como cada uno edita archivos distintos, `git pull` los mezcla solo. Lo único compartido es
`README.md`: cada uno escribe **solo dentro de su sección**.

## Contrato entre módulos (lo que NO se puede cambiar)
La fachada `motor/red.py` llama a estas firmas. Cada archivo provisional ya las trae en su
cabecera con la explicación completa; aquí el resumen:

```text
Estaciones(nombres)                 .estado(n) .autocompletar(prefijo,k) .rango(a,b)
  (Parte B)                         .cerrar(n) .reabrir(n) .esta_abierta(n)  <- O(1), la usan todos
Horarios(filas)                     .proximo_bus(est,ruta,hora) .buses_en(est)
  (Parte C)                         .agregar_parada(ruta,nueva,despues_de) .quitar_parada(ruta,est)
Ranking(nombres,horarios,esta_abierta)   .invalidar() .top(k)
Rutas(filas)                        .nombres() .recorrido(ruta,al_reves) .tiene_parada(ruta,est)
  (Parte D)                         .anterior(ruta,est) .agregar_parada(ruta,nueva,despues_de)
                                    .quitar_parada(ruta,est)   (despues_de=None => al inicio)
Historial()                         .registrar(orden) .deshacer() .rehacer()
Viaje(rutas,esta_abierta)  (A)      .invalidar() .viaje(origen,destino)
```

## Fichas por parte

### Parte B — Estaciones (R1, R2, R3, R8)
* Reemplazar `motor/estaciones.py` (hoy provisional y lento). Lea la cabecera del archivo.
* Página: `front/paginas/1_Estaciones.py` (buscar, autocompletar, rango, cerrar/reabrir).
* Cuidado: `esta_abierta` la llaman todos los demás módulos; tiene que ser O(1).
* Casos borde: estación inexistente, ya cerrada, ya abierta, prefijo sin resultados, k = 0,
  rango con `desde` > `hasta`, rango cuyos extremos no existen o están cerrados.

### Parte A — Panel de rendimiento (R11), además de R5 y R10
* Ya viene hecho: `herramientas/generar_red.py` (redes sintéticas), `herramientas/medir.py`
  (mide y calcula la pendiente log-log) y `front/paginas/6_Panel_rendimiento.py`.
* Mientras las partes de los demás sean provisionales, el panel marcará "NO COINCIDE" en sus
  operaciones: es justo para lo que sirve. Cuando cada uno suba su versión eficiente, deben dar OK.
* Al final: correr con 10.000, 20.000, 40.000 y 80.000 y escribir en `EXPLICACIONES` (en la página)
  por qué alguna operación no coincide, si pasa. Ajustar en `OPERACIONES` (medir.py) la O esperada
  de cada operación según lo que decida cada parte.

### Parte C — Horarios y ranking (R4, R6) + conversión de datos
* Reemplazar `motor/horarios.py` y `motor/ranking.py`.
* Dato real: las horas de un mismo (ruta, estación) vienen **desordenadas y a veces repetidas**.
* R6: el ranking "se consulta muy seguido y cambia poco": no lo recalculen en cada consulta.
  Las cerradas no entran. Decidan el desempate.
* Qué pasa con los horarios y el conteo cuando se agrega o quita una parada (y cuando se
  deshace): decidan, documenten y pregunten al profesor (ver preguntas abiertas).
* Página: `front/paginas/2_Horarios_y_ranking.py`.
* Conversión: `conversion/convertir_gtfs.py` (GTFS de TransMilenio → los 3 CSV). Necesitan el zip
  del GTFS (~54 MB). Decidan qué hacer con horas tipo `25:10` y expliquenlo en el README.

### Parte D — Rutas editables y deshacer (R7, R9)
* Reemplazar `motor/rutas.py` y `motor/historial.py`.
* `agregar_parada` inserta justo después de `despues_de`; `quitar_parada` la quita;
  `recorrido` va en los dos sentidos; ambas ediciones deben ser rápidas.
* `Historial` solo guarda y devuelve órdenes (tuplas); la fachada ejecuta la inversa.
  Un cambio nuevo borra lo que había para rehacer.
* Casos borde: ruta inexistente, `despues_de` que no está, `nueva` ya en la ruta, quitar la
  única/primera/última parada, deshacer sin nada que deshacer.
* Página: `front/paginas/3_Operar_red.py` (editar rutas, deshacer/rehacer).

## Preguntas abiertas para el profesor (el enunciado no lo dice)
1. **R4:** si hay un bus exactamente a la hora pedida, ¿cuenta como "siguiente"? (Supuesto: sí.)
2. **R10:** quien llega justo en el segundo en que sale un bus, ¿alcanza a subir? (Supuesto: sí.
   La Parte A ya lo implementa así.)
3. **R5:** si origen = destino, ¿qué devuelve? (Supuesto: `None`.) Y si hay un viaje directo
   y uno con transbordo con las mismas paradas, ¿cuál? (Supuesto: el directo.)
4. **R6/R7:** cuando se agrega una parada nueva a una ruta, ¿cuántos buses por día tiene en esa
   ruta? ¿Y su horario en R4?
5. **R4:** pedir el próximo bus en una estación cerrada: ¿`None`? (Supuesto: sí.)
6. **R7:** ¿`nueva` debe ser una estación que ya existe en la red? (Supuesto: sí.)
