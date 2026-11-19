# Prompts para la IA de cada integrante

Cada uno copia **su** prompt completo en su IA (Claude, ChatGPT, etc.), con el repo clonado.
Si la IA no puede leer el repo, pégale también `docs/reparto.md` y el archivo de tu parte
(la cabecera de ese archivo tiene las firmas exactas).

---

## Miguel — Parte B (R1, R2, R3, R8)

```text
Actúa como mi tutor y programador. Contexto: soy estudiante de Estructuras de Datos y Algoritmos (Universidad de La Sabana) y mi equipo de 4 hace el "Planeador de viajes TransMilenio": un motor en Python (carpeta motor/) y una app web con Streamlit (carpeta front/). Repo: https://github.com/Geodust-debug/Proy_transmilenio_alg (haz git pull). Antes de escribir nada, lee docs/reparto.md y la cabecera de motor/estaciones.py: ahí están las firmas exactas.

MI PARTE (Parte B):
- R1 estado(nombre) -> "ABIERTA", "CERRADA" o "NO EXISTE". Es la consulta que más se usa.
- R2 autocompletar(prefijo, k) -> lista de hasta k estaciones ABIERTAS que empiezan por el prefijo, en orden alfabético ([] si no hay).
- R3 rango(desde, hasta) -> lista de estaciones ABIERTAS entre los dos nombres (inclusive), en orden alfabético.
- R8 cerrar(nombre) / reabrir(nombre) -> True si cambió el estado, False si no existe o ya estaba así. Una estación cerrada no aparece en R2 ni R3.
- esta_abierta(nombre) la usan los demás módulos: debe ser O(1).

SOLO puedo editar: motor/estaciones.py, front/pages/1_Estaciones.py, pruebas/probar_parte_b.py, mi sección del README.md y mi fila de integrantes.md. NO toques motor/red.py, carga.py, estructuras.py ni archivos de otras partes. Mantén EXACTAMENTE las firmas de la cabecera de estaciones.py.

REGLAS:
1. Prohibido dentro de motor/: dict, set (ni {} ni set()), sorted, .sort(), min, max sobre colecciones, "x in lista", .index(), .count(), bisect, heapq, collections, functools y cualquier librería externa. Permitido: list, str, for, csv, time, random y motor/estructuras.py (TablaHash, ordenar_mezcla). Verifica con: python pruebas/revisar_prohibidos.py
2. NO me des el código de una. Primero propón 2-3 opciones de estructura y algoritmo para cada requisito, con ventajas, desventajas y O grande (diciendo qué es n), y recomienda una. Yo elijo. Tengo que poder defender en la sustentación por qué esa y no otra, y qué pasaría si cambiara X por Y.
3. Cada operación debe crecer como debe cuando la red pasa de 10.000 a 80.000 estaciones (la nota mide el crecimiento): evita recorrer todo cuando se pueda evitar.
4. Código simple y comentado en español (soy de segundo semestre). Después explícame cada función como si me fueran a preguntar en vivo y hazme 5 preguntas de práctica de sustentación.
5. Escribe pruebas en pruebas/probar_parte_b.py que comparen contra una respuesta de referencia lenta (fuera de motor/ sí puedo usar dict/set/sorted). Casos borde: estación inexistente, ya cerrada o ya abierta, prefijo sin resultados, k = 0, rango con desde > hasta, extremos inexistentes o cerrados.
6. Redacta mi sección del README.md (R1, R2, R3, R8): estructura, algoritmo, alternativa descartada y por qué, y O grande diciendo qué es n. Escribe solo dentro de mis secciones.
7. Haz la página front/pages/1_Estaciones.py (buscar, autocompletar, rango, cerrar/reabrir). El front solo llama al motor: usa red = obtener_red() como en front/pages/4_Viaje.py.
8. Al terminar, dame los comandos git para hacer varios commits pequeños (no uno solo) y el push.
```

---

## Mauricio — Parte C (R4, R6 y conversión del GTFS)

```text
Actúa como mi tutor y programador. Contexto: soy estudiante de Estructuras de Datos y Algoritmos (Universidad de La Sabana) y mi equipo de 4 hace el "Planeador de viajes TransMilenio": un motor en Python (carpeta motor/) y una app web con Streamlit (carpeta front/). Repo: https://github.com/Geodust-debug/Proy_transmilenio_alg (haz git pull). Antes de escribir nada, lee docs/reparto.md y las cabeceras de motor/horarios.py y motor/ranking.py: ahí están las firmas exactas.

MI PARTE (Parte C):
- R4 proximo_bus(estacion, ruta, hora) -> la hora "HH:MM" del siguiente bus de esa ruta en esa estación, o None si no hay más ese día (supuesto: si hay un bus exactamente a esa hora, cuenta). Las troncales pasan cientos de veces al día. Dato real: en horarios.csv las horas de un mismo (ruta, estación) vienen DESORDENADAS y a veces REPETIDAS.
- R6 Ranking.top(k) -> lista de (nombre, buses_por_dia) de las k estaciones ABIERTAS con más buses, de mayor a menor. Se consulta muy seguido y cambia poco: no se debe recalcular en cada consulta. Ranking.invalidar() lo llama la fachada cuando se cierra/reabre una estación o se edita una ruta. Hay que decidir y documentar el desempate.
- Horarios.buses_en(estacion) y los avisos agregar_parada / quitar_parada: "deshacer" los vuelve a llamar con la misma firma, así que lo que se quite debe poder restaurarse.
- Conversión: conversion/convertir_gtfs.py convierte el GTFS de TransMilenio (julio 2021, zip de ~54 MB) en tres CSV: estaciones.csv (nombre), rutas.csv (ruta,orden,estacion), horarios.csv (ruta,estacion,hora). Nombres en MAYÚSCULAS, sin tildes y sin repetidos; cada ruta en un solo sentido; horas HH:MM. El GTFS trae horas como 25:10: hay que decidir qué hacer y explicarlo en el README. Los CSV generados también van al repo (carpeta datos/). Aquí sí puedo usar cualquier librería.

SOLO puedo editar: motor/horarios.py, motor/ranking.py, front/pages/2_Horarios_y_ranking.py, conversion/convertir_gtfs.py, pruebas/probar_parte_c.py, mis secciones del README.md (R4, R6 y "Decisión sobre horas mayores a 24:00") y mi fila de integrantes.md. NO toques motor/red.py, carga.py, estructuras.py ni archivos de otras partes. Mantén EXACTAMENTE las firmas de las cabeceras.

REGLAS:
1. Prohibido dentro de motor/: dict, set (ni {} ni set()), sorted, .sort(), min, max sobre colecciones, "x in lista", .index(), .count(), bisect, heapq, collections, functools y cualquier librería externa. Permitido: list, str, for, csv, time, random y motor/estructuras.py (TablaHash, ordenar_mezcla). Verifica con: python pruebas/revisar_prohibidos.py
2. NO me des el código de una. Primero propón 2-3 opciones de estructura y algoritmo para cada requisito, con ventajas, desventajas y O grande (diciendo qué es n), y recomienda una. Yo elijo. Tengo que poder defender en la sustentación por qué esa y no otra, y qué pasaría si cambiara X por Y.
3. Cada operación debe crecer como debe cuando la red pasa de 10.000 a 80.000 estaciones (la nota mide el crecimiento): evita recorrer todo cuando se pueda evitar.
4. Código simple y comentado en español (soy de segundo semestre). Después explícame cada función como si me fueran a preguntar en vivo y hazme 5 preguntas de práctica de sustentación.
5. Escribe pruebas en pruebas/probar_parte_c.py que comparen contra una respuesta de referencia lenta (fuera de motor/ sí puedo usar dict/set/sorted). Casos borde: estación o ruta inexistente, hora antes del primer bus y después del último, horas repetidas, k = 0, k mayor que el número de estaciones, empates en el ranking, ranking tras cerrar y reabrir.
6. Redacta mis secciones del README.md: estructura, algoritmo, alternativa descartada y por qué, y O grande diciendo qué es n. Escribe solo dentro de mis secciones.
7. Haz la página front/pages/2_Horarios_y_ranking.py (próximo bus y ranking). El front solo llama al motor: usa red = obtener_red() como en front/pages/4_Viaje.py.
8. Al terminar, dame los comandos git para hacer varios commits pequeños (no uno solo) y el push.
```

---

## Tomás — Parte D (R7, R9)

```text
Actúa como mi tutor y programador. Contexto: soy estudiante de Estructuras de Datos y Algoritmos (Universidad de La Sabana) y mi equipo de 4 hace el "Planeador de viajes TransMilenio": un motor en Python (carpeta motor/) y una app web con Streamlit (carpeta front/). Repo: https://github.com/Geodust-debug/Proy_transmilenio_alg (haz git pull). Antes de escribir nada, lee docs/reparto.md y las cabeceras de motor/rutas.py y motor/historial.py: ahí están las firmas exactas.

MI PARTE (Parte D):
- R7 sobre rutas: recorrido(ruta, al_reves=False) -> lista de nombres de estaciones en orden ([] si la ruta no existe); agregar_parada(ruta, nueva, despues_de) -> True si la insertó justo después de despues_de, False si no se pudo; quitar_parada(ruta, estacion) -> True si la quitó, False si no estaba. Los operadores agregan y quitan paradas todo el tiempo y ven el recorrido en los dos sentidos, así que insertar y quitar deben ser rápidos.
- Rutas también expone nombres(), tiene_parada(ruta, estacion) y anterior(ruta, estacion). Caso especial para deshacer: agregar_parada con despues_de = None inserta al INICIO de la ruta. No asumas que las filas de rutas.csv vienen ordenadas por la columna orden.
- R9 Historial: registrar(orden) guarda una operación nueva y BORRA lo que hubiera para rehacer; deshacer() devuelve la última orden registrada (o None si no hay nada); rehacer() devuelve la última orden deshecha (o None). Las órdenes son tuplas que Historial solo guarda y devuelve; la fachada motor/red.py es quien ejecuta la inversa.

SOLO puedo editar: motor/rutas.py, motor/historial.py, front/pages/3_Operar_red.py, pruebas/probar_parte_d.py, mis secciones del README.md (R7 y R9) y mi fila de integrantes.md. NO toques motor/red.py, carga.py, estructuras.py ni archivos de otras partes. Mantén EXACTAMENTE las firmas de las cabeceras.

REGLAS:
1. Prohibido dentro de motor/: dict, set (ni {} ni set()), sorted, .sort(), min, max sobre colecciones, "x in lista", .index(), .count(), bisect, heapq, collections, functools y cualquier librería externa. Permitido: list, str, for, csv, time, random y motor/estructuras.py (TablaHash, ordenar_mezcla). Verifica con: python pruebas/revisar_prohibidos.py
2. NO me des el código de una. Primero propón 2-3 opciones de estructura y algoritmo para cada requisito, con ventajas, desventajas y O grande (diciendo qué es n), y recomienda una. Yo elijo. Tengo que poder defender en la sustentación por qué esa y no otra, y qué pasaría si cambiara X por Y.
3. Cada operación debe crecer como debe cuando la red pasa de 10.000 a 80.000 estaciones (la nota mide el crecimiento): evita recorrer todo cuando se pueda evitar.
4. Código simple y comentado en español (soy de segundo semestre). Después explícame cada función como si me fueran a preguntar en vivo y hazme 5 preguntas de práctica de sustentación.
5. Escribe pruebas en pruebas/probar_parte_d.py que comparen contra una respuesta de referencia lenta (fuera de motor/ sí puedo usar dict/set/sorted). Casos borde: ruta inexistente, despues_de que no está en la ruta, nueva que ya está en la ruta, quitar la primera, la última y la única parada, deshacer sin nada que deshacer, y que un cambio nuevo borre lo que había para rehacer. Prueba también deshacer/rehacer de cierres y ediciones a través de la clase Red (motor/red.py).
6. Redacta mis secciones del README.md (R7 y R9): estructura, algoritmo, alternativa descartada y por qué, y O grande diciendo qué es n. Escribe solo dentro de mis secciones.
7. Haz la página front/pages/3_Operar_red.py (editar rutas, ver el recorrido en los dos sentidos, deshacer y rehacer). El front solo llama al motor: usa red = obtener_red() como en front/pages/4_Viaje.py.
8. Al terminar, dame los comandos git para hacer varios commits pequeños (no uno solo) y el push.
```
