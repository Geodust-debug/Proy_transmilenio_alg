"""Dibujos propios del front (Parte E): bus, iconos y escenas animadas en SVG.

Todo esta dibujado a mano con figuras simples (no son emojis ni imagenes
bajadas de internet). Las animaciones viven en el CSS de visual/tema.py:
aqui solo se ponen las clases (tm-...) que ese CSS anima.
"""

ROJO = "#D42A20"
ROJO_OSCURO = "#A91F17"
GRAFITO = "#262B33"
GRAFITO_2 = "#3A414C"
VIDRIO = "#DCE6EE"
CONCRETO = "#B9BFB8"
AMBAR = "#F0A202"
VERDE = "#12A26A"
GRIS = "#9AA6B2"
BLANCO = "#FFFFFF"

# Color de cada troncal (primera letra del codigo de la ruta). Inspirado en la
# idea de "una troncal, un color"; los tonos son propios del proyecto.
TRONCALES = {
    "A": "#1F6FB2", "B": "#3E9B46", "C": "#E8B100", "D": "#7A4C9E",
    "E": "#8D5B3B", "F": "#D42A20", "G": "#1797C2", "H": "#EF7D16",
    "J": "#B5952F", "K": "#8FA516", "L": "#1E9C93", "M": "#D2457C",
    # rutas que empiezan por numero (1-1, 6-4, ...)
    "1": "#5B6470", "2": "#0F7C8A", "3": "#9C5B2E", "4": "#4D5BB0",
    "5": "#A23E7A", "6": "#2F8F5B", "7": "#B0681A", "8": "#6B4FA0",
}
_TEXTO_OSCURO = "CHJK"      # fondos claros: el codigo va en grafito


def color_ruta(ruta):
    """(fondo, texto) para la insignia de una ruta segun su troncal."""
    letra = ruta[:1].upper() if ruta else ""
    fondo = TRONCALES.get(letra, "#5B6470")
    texto = GRAFITO if letra in _TEXTO_OSCURO else BLANCO
    return fondo, texto


# ---------------------------------------------------------------- el bus
def bus(color=ROJO, clase=""):
    """Bus articulado visto de lado, mirando a la derecha (caja 220 x 70)."""
    return f"""
<g class="{clase}">
  <rect x="4" y="8" width="102" height="44" rx="8" fill="{color}"/>
  <path d="M116 8 H200 Q216 8 216 24 V46 Q216 52 210 52 H116 Z" fill="{color}"/>
  <rect x="104" y="12" width="14" height="38" fill="{GRAFITO}"/>
  <path d="M107 12 V50 M111 12 V50 M115 12 V50" stroke="{GRAFITO_2}" stroke-width="1.6"/>
  <rect x="10" y="15" width="88" height="15" rx="3" fill="{VIDRIO}"/>
  <rect x="122" y="15" width="68" height="15" rx="3" fill="{VIDRIO}"/>
  <path d="M196 13 H204 Q213 13 213 24 V33 H196 Z" fill="{GRAFITO}"/>
  <path d="M30 15 V30 M50 15 V30 M84 15 V30 M140 15 V30 M176 15 V30" stroke="{color}" stroke-width="3"/>
  <g class="tm-puertas">
    <rect x="58" y="15" width="10" height="33" fill="#EEF3F6"/>
    <rect x="68" y="15" width="10" height="33" fill="#EEF3F6"/>
    <rect x="152" y="15" width="10" height="33" fill="#EEF3F6"/>
    <rect x="162" y="15" width="10" height="33" fill="#EEF3F6"/>
    <path d="M68 15 V48 M162 15 V48" stroke="{GRIS}" stroke-width="1.2"/>
  </g>
  <rect x="4" y="40" width="212" height="3" fill="{BLANCO}" opacity=".85"/>
  <circle cx="211" cy="45" r="2.6" fill="#FFD25A"/>
  <g fill="{GRAFITO}"><circle cx="28" cy="56" r="9"/><circle cx="84" cy="56" r="9"/>
     <circle cx="140" cy="56" r="9"/><circle cx="192" cy="56" r="9"/></g>
  <g fill="{GRIS}"><circle cx="28" cy="56" r="3.5"/><circle cx="84" cy="56" r="3.5"/>
     <circle cx="140" cy="56" r="3.5"/><circle cx="192" cy="56" r="3.5"/></g>
</g>"""


def persona(x, y, color=GRAFITO, clase=""):
    """Pictograma de persona de pie; (x, y) son los pies."""
    return f"""
<g transform="translate({x} {y})"><g class="{clase}">
  <g class="tm-camina">
    <circle cx="0" cy="-31" r="5.2" fill="{color}"/>
    <rect x="-5.5" y="-24" width="11" height="15" rx="5" fill="{color}"/>
    <rect class="tm-pierna-a" x="-4.6" y="-11" width="3.6" height="11" rx="1.8" fill="{color}"/>
    <rect class="tm-pierna-b" x="1" y="-11" width="3.6" height="11" rx="1.8" fill="{color}"/>
  </g>
</g></g>"""


# ---------------------------------------------------------------- iconos
# Iconos de 48 x 48 en blanco, para el cuadro de color de cada letrero.
ICONOS = {
    "inicio": f"""
<rect x="10" y="8" width="28" height="30" rx="6" fill="none" stroke="#fff" stroke-width="3.2"/>
<rect x="14.5" y="13" width="19" height="11" rx="2" fill="#fff"/>
<circle cx="17" cy="31" r="2.3" fill="#fff"/><circle cx="31" cy="31" r="2.3" fill="#fff"/>
<path d="M15 38 V42 M33 38 V42" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>""",
    "estaciones": f"""
<path d="M6 16 H42" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>
<path d="M10 18 V36 M38 18 V36" stroke="#fff" stroke-width="3"/>
<rect x="15" y="21" width="8" height="15" rx="1" fill="#fff" class="tm-ico-puerta-a"/>
<rect x="25" y="21" width="8" height="15" rx="1" fill="#fff" class="tm-ico-puerta-b"/>
<rect x="5" y="37" width="38" height="5" rx="1.5" fill="#fff"/>
<rect x="18" y="6" width="12" height="7" rx="2" fill="#fff"/>""",
    "horarios": f"""
<circle cx="24" cy="24" r="16" fill="none" stroke="#fff" stroke-width="3.4"/>
<path class="tm-ico-aguja" d="M24 24 V13" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/>
<path d="M24 24 L31 28" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/>
<circle cx="24" cy="24" r="2.4" fill="#fff"/>""",
    "operar": f"""
<path d="M6 30 H42" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/>
<circle cx="10" cy="30" r="4.2" fill="#fff"/><circle cx="38" cy="30" r="4.2" fill="#fff"/>
<circle class="tm-ico-nodo" cx="24" cy="30" r="5" fill="none" stroke="#fff" stroke-width="3.2"/>
<path d="M24 8 V19 M18.5 13.5 H29.5" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>""",
    "viaje": f"""
<rect x="7" y="13" width="30" height="21" rx="3.5" fill="#fff" transform="rotate(-10 22 23)"/>
<rect x="12" y="19" width="7" height="5.5" rx="1" fill="currentColor" transform="rotate(-10 22 23)"/>
<path class="tm-ico-onda" d="M36 14 Q41 20 36 26 M40 11 Q47 20 40 29" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round"/>
<path d="M10 41 H38" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 6"/>""",
    "hora_pico": f"""
<circle cx="15" cy="15" r="5" fill="#fff"/><rect x="9.5" y="22" width="11" height="18" rx="5.5" fill="#fff"/>
<circle cx="33" cy="15" r="5" fill="#fff"/><rect x="27.5" y="22" width="11" height="18" rx="5.5" fill="#fff"/>
<circle cx="24" cy="10" r="4" fill="#fff" opacity=".75"/>
<path d="M6 44 H42" stroke="#fff" stroke-width="3" stroke-linecap="round"/>""",
    "panel": f"""
<path d="M8 36 A16 16 0 0 1 40 36" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>
<path class="tm-ico-aguja-panel" d="M24 36 L33 22" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>
<circle cx="24" cy="36" r="3.4" fill="#fff"/>
<path d="M12 42 H36" stroke="#fff" stroke-width="3" stroke-linecap="round"/>""",
}


def icono(nombre, color_fondo):
    return (f'<svg viewBox="0 0 48 48" style="color:{color_fondo}" aria-hidden="true">'
            f'{ICONOS[nombre]}</svg>')


# ---------------------------------------------------------------- escenas
# Una escena por pagina: es lo que se ve unos instantes al entrar.

def escena_inicio():
    return f"""
<svg viewBox="0 0 360 190" class="tm-escena" role="img" aria-label="Un bus llega a la estación">
  <rect x="0" y="150" width="360" height="12" rx="2" fill="#D3D8D1"/>
  <path d="M8 156 H352" stroke="#fff" stroke-width="2" stroke-dasharray="14 10"/>
  <g class="tm-e-estacion">
    <rect x="250" y="128" width="106" height="20" rx="3" fill="{CONCRETO}"/>
    <rect x="250" y="128" width="106" height="3.5" fill="{AMBAR}"/>
    <rect x="258" y="76" width="90" height="52" fill="{VIDRIO}"/>
    <path d="M280 76 V128 M302 76 V128 M326 76 V128" stroke="#fff" stroke-width="3"/>
    <rect x="246" y="64" width="114" height="13" rx="4" fill="{GRAFITO}"/>
    <rect x="286" y="48" width="34" height="14" rx="3" fill="{ROJO}"/>
  </g>
  <g class="tm-e-bus"><g transform="translate(22 94) scale(.95)">{bus(clase="tm-bus-llega")}</g></g>
</svg>"""


def escena_estaciones(acento):
    return f"""
<svg viewBox="0 0 320 200" class="tm-escena" role="img" aria-label="Una estación se arma y abre sus puertas">
  <rect x="10" y="170" width="300" height="4" rx="2" fill="#C9CEC7"/>
  <g class="tm-e-anden">
    <rect x="34" y="146" width="252" height="24" rx="3" fill="{CONCRETO}"/>
    <rect x="34" y="146" width="252" height="4" fill="{AMBAR}"/>
  </g>
  <g class="tm-e-vidrio">
    <rect x="52" y="82" width="216" height="64" fill="{VIDRIO}"/>
    <path d="M80 82 V146 M108 82 V146 M212 82 V146 M240 82 V146" stroke="#fff" stroke-width="3.5"/>
  </g>
  <rect x="134" y="92" width="52" height="54" fill="#C6D3DD"/>
  <rect class="tm-e-puerta-a" x="134" y="92" width="26" height="54" fill="#F2F6F8" stroke="{GRIS}" stroke-width="1.5"/>
  <rect class="tm-e-puerta-b" x="160" y="92" width="26" height="54" fill="#F2F6F8" stroke="{GRIS}" stroke-width="1.5"/>
  <g class="tm-e-techo">
    <rect x="30" y="64" width="260" height="18" rx="5" fill="{GRAFITO}"/>
    <rect x="30" y="79" width="260" height="3" fill="{ROJO}"/>
  </g>
  <g class="tm-e-letrero">
    <rect x="124" y="32" width="72" height="26" rx="5" fill="{acento}"/>
    <path d="M136 45 H184" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <circle cx="140" cy="45" r="4.5" fill="#fff"/><circle cx="160" cy="45" r="4.5" fill="#fff"/>
    <circle cx="180" cy="45" r="4.5" fill="#fff"/>
    <path d="M160 58 V64" stroke="{GRAFITO}" stroke-width="3"/>
  </g>
</svg>"""


def escena_viaje():
    return f"""
<svg viewBox="0 0 320 200" class="tm-escena" role="img" aria-label="Una tarjeta pasa por el validador y se abre el torniquete">
  <rect x="10" y="172" width="300" height="4" rx="2" fill="#C9CEC7"/>
  <rect x="104" y="98" width="58" height="74" rx="7" fill="{GRAFITO}"/>
  <rect x="112" y="108" width="42" height="6" rx="3" fill="{GRAFITO_2}"/>
  <g class="tm-e-brazos">
    <path d="M168 128 H206 M168 128 L149 95 M168 128 L149 161" stroke="{GRIS}" stroke-width="7" stroke-linecap="round"/>
    <circle cx="168" cy="128" r="7" fill="{GRAFITO_2}"/>
  </g>
  <rect x="110" y="66" width="46" height="34" rx="7" fill="#1D2128"/>
  <circle class="tm-e-onda" cx="133" cy="83" r="11" fill="none" stroke="{VERDE}" stroke-width="3"/>
  <circle class="tm-e-lector" cx="133" cy="83" r="10" fill="none" stroke="#5E6670" stroke-width="3"/>
  <path class="tm-e-chulo" d="M127 83.5 L131.5 88 L139.5 79" fill="none" stroke="{VERDE}" stroke-width="3.4"
        stroke-linecap="round" stroke-linejoin="round"/>
  <g class="tm-e-tarjeta">
    <rect x="0" y="0" width="54" height="34" rx="5" fill="{ROJO}"/>
    <rect x="0" y="22" width="54" height="5" fill="#fff" opacity=".9"/>
    <rect x="8" y="7" width="11" height="9" rx="2" fill="#F3C94F"/>
  </g>
  <g fill="{GRAFITO}" opacity=".85">
    <ellipse class="tm-e-paso1" cx="226" cy="166" rx="6" ry="3.2"/>
    <ellipse class="tm-e-paso2" cx="250" cy="160" rx="6" ry="3.2"/>
    <ellipse class="tm-e-paso3" cx="274" cy="166" rx="6" ry="3.2"/>
    <ellipse class="tm-e-paso4" cx="298" cy="160" rx="6" ry="3.2"/>
  </g>
</svg>"""


def escena_hora_pico():
    gente = ""
    colores = [GRAFITO, ROJO, GRAFITO, GRAFITO, ROJO, GRAFITO, ROJO, GRAFITO]
    for i in range(8):
        gente += persona(0, 176, colores[i], f"tm-e-caminante tm-e-c{i}")
    marcas = ""
    for k in range(12):
        largo = 7 if k % 3 == 0 else 4
        marcas += (f'<path d="M84 {38 + 1} V{38 + 1 + largo}" stroke="{GRAFITO}" stroke-width="2.4" '
                   f'transform="rotate({k * 30} 84 84)"/>')
    return f"""
<svg viewBox="0 0 340 200" class="tm-escena" role="img" aria-label="Un reloj corre rápido y la gente camina hacia el bus">
  <circle cx="84" cy="84" r="47" fill="#fff" stroke="{GRAFITO}" stroke-width="6"/>
  {marcas}
  <path class="tm-e-horero" d="M84 84 V58" stroke="{GRAFITO}" stroke-width="5" stroke-linecap="round"/>
  <path class="tm-e-minutero" d="M84 84 V46" stroke="{ROJO}" stroke-width="3.6" stroke-linecap="round"/>
  <circle cx="84" cy="84" r="4.5" fill="{ROJO}"/>
  <rect x="232" y="60" width="96" height="10" rx="3" fill="{GRAFITO}"/>
  <rect x="240" y="70" width="80" height="58" fill="{VIDRIO}"/>
  <path d="M266 70 V128 M294 70 V128" stroke="#fff" stroke-width="3"/>
  <rect x="226" y="128" width="108" height="10" rx="2" fill="{CONCRETO}"/>
  <rect x="226" y="128" width="108" height="2.5" fill="{AMBAR}"/>
  <rect x="0" y="176" width="340" height="4" rx="2" fill="#C9CEC7"/>
  {gente}
</svg>"""


def escena_horarios(acento):
    filas = [("B13", "05:42"), ("F28", "05:49"), ("G22", "05:57")]
    contenido = ""
    for i in range(3):
        ruta, hora = filas[i]
        fondo, texto = color_ruta(ruta)
        y = 70 + i * 36
        contenido += f"""
  <g class="tm-e-fila tm-e-fila{i}">
    <rect x="46" y="{y}" width="46" height="26" rx="5" fill="{fondo}"/>
    <text x="69" y="{y + 19}" text-anchor="middle" class="tm-svg-cond" font-size="17" fill="{texto}">{ruta}</text>
    <text x="270" y="{y + 20}" text-anchor="end" class="tm-svg-cond" font-size="24" fill="#fff">{hora}</text>
    <rect x="104" y="{y + 9}" width="{70 - i * 12}" height="8" rx="4" fill="{GRAFITO_2}"/>
  </g>"""
    return f"""
<svg viewBox="0 0 320 200" class="tm-escena" role="img" aria-label="Un tablero de salidas muestra las próximas horas">
  <rect x="30" y="26" width="260" height="160" rx="12" fill="{GRAFITO}"/>
  <rect x="30" y="26" width="260" height="8" rx="4" fill="{acento}"/>
  <circle cx="262" cy="50" r="10" fill="none" stroke="#fff" stroke-width="2.4"/>
  <path class="tm-e-tic" d="M262 50 V43" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>
  <rect x="46" y="45" width="90" height="10" rx="5" fill="{GRAFITO_2}"/>
  {contenido}
</svg>"""


def escena_operar(acento):
    return f"""
<svg viewBox="0 0 320 200" class="tm-escena" role="img" aria-label="Una parada nueva entra en la ruta">
  <path d="M40 120 H128" stroke="{acento}" stroke-width="9" stroke-linecap="round"/>
  <path d="M192 120 H280" stroke="{acento}" stroke-width="9" stroke-linecap="round"/>
  <path class="tm-e-une" d="M128 120 H192" stroke="{acento}" stroke-width="9" stroke-linecap="round"/>
  <g fill="#fff" stroke="{GRAFITO}" stroke-width="4">
    <circle cx="44" cy="120" r="11"/><circle cx="108" cy="120" r="11"/>
    <circle cx="212" cy="120" r="11"/><circle cx="276" cy="120" r="11"/>
  </g>
  <g class="tm-e-nueva">
    <circle cx="160" cy="120" r="14" fill="#fff" stroke="{VERDE}" stroke-width="5"/>
    <path d="M160 113 V127 M153 120 H167" stroke="{VERDE}" stroke-width="3.4" stroke-linecap="round"/>
  </g>
  <g class="tm-e-deshacer">
    <path d="M252 54 A18 18 0 1 0 270 72" fill="none" stroke="{GRAFITO}" stroke-width="4" stroke-linecap="round"/>
    <path d="M244 46 L252 54 L244 62" fill="none" stroke="{GRAFITO}" stroke-width="4"
          stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>"""


def escena_panel(acento):
    return f"""
<svg viewBox="0 0 320 200" class="tm-escena" role="img" aria-label="Se dibujan las curvas de tiempo de cada operación">
  <path d="M50 30 V168 H292" fill="none" stroke="{GRAFITO}" stroke-width="4" stroke-linecap="round"/>
  <path class="tm-e-curva tm-e-curva1" d="M58 150 L120 148 L190 147 L280 146" fill="none" stroke="{VERDE}"
        stroke-width="5" stroke-linecap="round"/>
  <path class="tm-e-curva tm-e-curva2" d="M58 132 L120 124 L190 118 L280 112" fill="none" stroke="#1F6FB2"
        stroke-width="5" stroke-linecap="round"/>
  <path class="tm-e-curva tm-e-curva3" d="M58 128 L120 104 L190 76 L280 40" fill="none" stroke="{ROJO}"
        stroke-width="5" stroke-linecap="round"/>
  <g class="tm-e-puntos">
    <circle cx="280" cy="146" r="6" fill="{VERDE}"/><circle cx="280" cy="112" r="6" fill="#1F6FB2"/>
    <circle cx="280" cy="40" r="6" fill="{ROJO}"/>
  </g>
</svg>"""


# ------------------------------------------------- dibujos de resultados
def estacion_estado(estado):
    """Estacion pequena que se ve abierta, cerrada o inexistente (120 x 84)."""
    if estado == "ABIERTA":
        luz, extra, clase = VERDE, "", "tm-f-abierta"
    elif estado == "CERRADA":
        luz = ROJO
        clase = "tm-f-cerrada"
        extra = f"""
  <g class="tm-f-barrera">
    <rect x="14" y="58" width="92" height="9" rx="2" fill="{ROJO}"/>
    <path d="M24 58 L32 67 M44 58 L52 67 M64 58 L72 67 M84 58 L92 67" stroke="#fff" stroke-width="3"/>
  </g>"""
    else:
        luz, clase = GRIS, "tm-f-nada"
        extra = f"""<text x="60" y="62" text-anchor="middle" class="tm-svg-cond" font-size="30" fill="{GRIS}">?</text>"""
    vidrio = VIDRIO if estado != "NO EXISTE" else "#EEF0EE"
    trazo = "" if estado != "NO EXISTE" else 'stroke-dasharray="5 4"'
    return f"""
<svg viewBox="0 0 120 84" class="tm-ficha-dibujo {clase}" aria-hidden="true">
  <rect x="6" y="72" width="108" height="8" rx="2" fill="{CONCRETO}"/>
  <rect x="14" y="26" width="92" height="46" fill="{vidrio}" stroke="{GRIS}" stroke-width="1.5" {trazo}/>
  <rect class="tm-f-puerta-a" x="44" y="34" width="16" height="38" fill="#F2F6F8" stroke="{GRIS}" stroke-width="1.2"/>
  <rect class="tm-f-puerta-b" x="60" y="34" width="16" height="38" fill="#F2F6F8" stroke="{GRIS}" stroke-width="1.2"/>
  <rect x="8" y="16" width="104" height="11" rx="3" fill="{GRAFITO}"/>
  <circle class="tm-f-luz" cx="60" cy="9" r="6" fill="{luz}"/>
  {extra}
</svg>"""
