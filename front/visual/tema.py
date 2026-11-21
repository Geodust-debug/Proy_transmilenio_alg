"""Tema visual de toda la app (Parte E): colores, letreros, animaciones y cargas.

Idea del diseno: la app se ve como la senaletica de una estacion puesta sobre
un plano en blanco de la ciudad. Cada pagina es "una troncal" con su color,
los titulos van en letreros grafito y las rutas en insignias de color.

Aqui NO hay reglas del sistema: solo HTML y CSS para mostrar lo que devuelve
el motor. Las paginas llaman a estas funciones en vez de st.title, etc.
"""
import html as _html
import re
from contextlib import contextmanager

import streamlit as st

from . import dibujos

# ------------------------------------------------------------------ paginas
# clave -> (titulo, bajada, color de la troncal, icono, escena, frase de entrada)
PAGINAS = {
    "inicio": ("Planeador de viajes TransMilenio",
               "Busca estaciones, planea tu viaje y mira a qué hora pasa tu bus.",
               dibujos.ROJO, "inicio", lambda c: dibujos.escena_inicio(), "Bienvenido a bordo"),
    "estaciones": ("Estaciones",
                   "Busca una estación, mira si está abierta y ciérrala o reábrela.",
                   "#1F6FB2", "estaciones", dibujos.escena_estaciones, "Entrando a la estación"),
    "horarios": ("Horarios y ranking",
                 "A qué hora pasa el próximo bus y cuáles son las estaciones con más buses.",
                 "#EF7D16", "horarios", dibujos.escena_horarios, "Revisando el tablero de salidas"),
    "operar": ("Operar la red",
               "Agrega o quita paradas de una ruta y deshaz cualquier cambio.",
               "#7A4C9E", "operar", dibujos.escena_operar, "Abriendo el editor de rutas"),
    "viaje": ("Planear un viaje",
              "Directo o con un transbordo: el camino con menos paradas.",
              dibujos.ROJO, "viaje", lambda c: dibujos.escena_viaje(), "Pasa la tarjeta y sube"),
    "hora_pico": ("Hora pico",
                  "Simula la fila de abordaje: quién sube a cada bus y quién se queda esperando.",
                  "#1797C2", "hora_pico", lambda c: dibujos.escena_hora_pico(), "Llega la hora pico"),
    "panel": ("Panel de rendimiento",
              "Mide cada operación en redes cada vez más grandes y compárala con su O grande.",
              "#3E9B46", "panel", dibujos.escena_panel, "Preparando las mediciones"),
}


def acento(clave):
    return PAGINAS[clave][2]


# ------------------------------------------------------------------ utilidades
def html(codigo):
    """Pinta HTML/SVG en la pagina. Se compacta en una linea para que el
    markdown de Streamlit no lo confunda con texto (sangrias = codigo)."""
    st.markdown(re.sub(r"\n\s*", " ", codigo).strip(), unsafe_allow_html=True)


def texto(valor):
    """Escapa un texto que viene de los datos antes de meterlo en HTML."""
    return _html.escape(str(valor))


# ------------------------------------------------------------------ CSS global
_CSS = """
<style>
:root{
  --tm-rojo:#D42A20; --tm-rojo-osc:#A91F17; --tm-grafito:#262B33; --tm-grafito-2:#3A414C;
  --tm-plano:#ECEEEA; --tm-calle:#E0E3DD; --tm-borde:#D3D8D1; --tm-suave:#5E6670;
  --tm-verde:#12A26A; --tm-ambar:#F0A202; --tm-azul:#1F6FB2;
  --tm-cond:'Barlow Condensed','Arial Narrow',Barlow,sans-serif;
}

/* ---------- el plano en blanco de fondo ---------- */
.stApp{
  background-color:var(--tm-plano);
  background-image:
    linear-gradient(var(--tm-calle) 2px,transparent 2px),
    linear-gradient(90deg,var(--tm-calle) 2px,transparent 2px),
    linear-gradient(rgba(214,218,211,.5) 1px,transparent 1px),
    linear-gradient(90deg,rgba(214,218,211,.5) 1px,transparent 1px);
  background-size:240px 240px,240px 240px,48px 48px,48px 48px;
}
[data-testid="stHeader"]{background:transparent}
[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none}
[data-testid="stMainBlockContainer"]{max-width:1180px;padding-top:2.2rem;padding-bottom:4rem}

/* ---------- letrero de cada pagina ---------- */
.tm-letrero{position:relative;display:flex;align-items:center;gap:22px;background:var(--tm-grafito);
  color:#fff;border-radius:14px;padding:24px 28px 22px 22px;overflow:hidden}
.tm-letrero::before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:var(--acento)}
.tm-letrero__icono{flex:0 0 72px;height:72px;border-radius:12px;background:var(--acento);
  display:grid;place-items:center;transition:transform .25s ease}
.tm-letrero__icono svg{width:46px;height:46px}
.tm-letrero:hover .tm-letrero__icono{transform:rotate(-4deg) scale(1.05)}
.tm-letrero__titulo{font-family:var(--tm-cond);font-weight:700;font-size:2.55rem;line-height:1.02;margin:0}
.tm-letrero__bajada{margin:.4rem 0 0;color:#C5CBD3;font-size:1.06rem;line-height:1.4;max-width:64ch}
@media (max-width:640px){
  .tm-letrero{padding:20px 18px 18px 16px;gap:14px}
  .tm-letrero__icono{flex-basis:54px;height:54px}.tm-letrero__icono svg{width:34px;height:34px}
  .tm-letrero__titulo{font-size:1.9rem}
}
/* el icono del letrero se mueve un poco cuando se le pasa el mouse */
.tm-letrero:hover .tm-ico-aguja{animation:tm-gira 1.2s linear infinite;transform-origin:24px 24px}
.tm-letrero:hover .tm-ico-onda{animation:tm-titila .6s ease-in-out infinite alternate}
.tm-letrero:hover .tm-ico-puerta-a{animation:tm-abre-izq .5s ease forwards}
.tm-letrero:hover .tm-ico-puerta-b{animation:tm-abre-der .5s ease forwards}
.tm-letrero:hover .tm-ico-nodo{animation:tm-late .6s ease-in-out infinite alternate;transform-origin:24px 30px}
.tm-letrero:hover .tm-ico-aguja-panel{animation:tm-aguja .5s ease-in-out infinite alternate;transform-origin:24px 36px}

/* ---------- pantalla de entrada de cada pagina ---------- */
.tm-bienvenida{position:fixed;inset:0;z-index:999990;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:10px;background:rgba(236,238,234,.96);backdrop-filter:blur(5px);
  pointer-events:none;animation:tm-salir .45s ease 1.85s forwards}
.tm-bienvenida svg{width:min(360px,72vw);height:auto}
.tm-bienvenida__frase{font-family:var(--tm-cond);font-weight:700;font-size:1.9rem;color:var(--tm-grafito);
  opacity:0;animation:tm-aparece .35s ease .45s forwards}
.tm-bienvenida__barra{width:min(220px,50vw);height:5px;border-radius:3px;background:#D3D8D1;overflow:hidden}
.tm-bienvenida__barra span{display:block;height:100%;width:100%;background:var(--acento);
  transform-origin:left;animation:tm-llena 1.7s cubic-bezier(.4,0,.2,1) both}
.tm-svg-cond{font-family:var(--tm-cond);font-weight:700}

/* ---------- botones: se hunden como un boton de verdad ---------- */
button[data-testid^="stBaseButton"]{font-weight:600;letter-spacing:.01em;
  transition:transform .1s ease,box-shadow .1s ease,background-color .15s ease,border-color .15s ease}
button[data-testid="stBaseButton-primary"]{box-shadow:0 4px 0 var(--tm-rojo-osc)}
button[data-testid="stBaseButton-primary"]:hover{transform:translateY(-1px);box-shadow:0 5px 0 var(--tm-rojo-osc)}
button[data-testid="stBaseButton-primary"]:active{transform:translateY(4px);box-shadow:0 0 0 var(--tm-rojo-osc)}
button[data-testid="stBaseButton-secondary"]{background:#fff;box-shadow:0 4px 0 #C9CEC7}
button[data-testid="stBaseButton-secondary"]:hover{transform:translateY(-1px);box-shadow:0 5px 0 #C9CEC7;
  border-color:var(--tm-grafito);color:var(--tm-grafito)}
button[data-testid="stBaseButton-secondary"]:active{transform:translateY(4px);box-shadow:0 0 0 #C9CEC7}
button[data-testid^="stBaseButton"]:disabled{box-shadow:none;transform:none}
button[data-testid^="stBaseButton"]:focus-visible{outline:3px solid var(--tm-azul);outline-offset:2px}

/* ---------- pestanas ---------- */
[data-testid="stTab"] p{font-family:var(--tm-cond);font-weight:600;font-size:1.2rem}
[data-testid="stTab"]{transition:color .15s ease}

/* ---------- metricas: placas blancas con borde de color ---------- */
[data-testid="stMetric"]{background:#fff;border:1px solid var(--tm-borde);border-left:6px solid var(--tm-grafito);
  border-radius:10px;padding:12px 16px}
[data-testid="stMetricValue"]{font-family:var(--tm-cond)}
[data-testid="stMetricLabel"] p{color:var(--tm-suave);font-weight:500}

/* ---------- menu lateral ---------- */
[data-testid="stSidebarNavLink"]{border-radius:8px;transition:background-color .15s ease,transform .15s ease}
[data-testid="stSidebarNavLink"]:hover{transform:translateX(3px)}
[data-testid="stSidebarNavLink"][aria-current="page"]{box-shadow:inset 4px 0 0 var(--tm-rojo)}
[data-testid="stSidebarNavSeparator"]{border-color:#3B424D}
.tm-pie{color:#9AA3AE;font-size:.85rem;line-height:1.45;margin-top:.5rem}

/* ---------- cargas ---------- */
.tm-cargando{display:flex;align-items:center;gap:16px;padding:14px 18px;background:#fff;
  border:1px solid var(--tm-borde);border-radius:12px;width:fit-content;max-width:100%}
.tm-cargando svg{width:170px;height:36px;flex:0 0 auto}
.tm-cargando__texto{font-weight:600;color:var(--tm-grafito)}
.tm-cargando__bus{animation:tm-va-y-viene 1.6s cubic-bezier(.45,0,.55,1) infinite alternate}
.tm-cargando__parada{animation:tm-enciende 1.6s ease-in-out infinite alternate}
[data-testid="stSpinner"] svg,[data-testid="stSpinner"] i{display:none}
[data-testid="stSpinner"]>div{display:flex;align-items:center;gap:10px}
[data-testid="stSpinner"]>div::before{content:"";width:46px;height:14px;border-radius:7px;flex:0 0 auto;
  background:linear-gradient(90deg,var(--tm-rojo) 0 30%,#D3D8D1 30% 100%);background-size:200% 100%;
  animation:tm-barrido 1s linear infinite}
[data-testid="stProgress"] [role="progressbar"]>div>div>div{
  background-image:repeating-linear-gradient(-45deg,rgba(255,255,255,.25) 0 8px,transparent 8px 16px)!important;
  background-size:23px 23px;animation:tm-rayas .8s linear infinite}

/* ---------- piezas reutilizables ---------- */
.tm-ruta{display:inline-flex;align-items:center;justify-content:center;min-width:3.1em;padding:1px 8px;
  border-radius:6px;font-family:var(--tm-cond);font-weight:700;font-size:1.08rem;line-height:1.5;
  vertical-align:middle}
.tm-chips{display:flex;flex-wrap:wrap;gap:8px;margin:.2rem 0 .6rem}
.tm-chip{background:#fff;border:1px solid var(--tm-borde);border-radius:999px;padding:4px 13px;
  font-weight:500;font-size:.95rem}
.tm-chip--cerrada{background:#FFF1F0;border-color:#F2BDB8;color:#9E2018}
.tm-nota{color:var(--tm-suave);font-size:.95rem;margin:.1rem 0 .4rem}
.tm-subtitulo{font-family:var(--tm-cond);font-weight:700;font-size:1.35rem;line-height:1.2;margin:.1rem 0 .3rem}

.tm-ficha{display:flex;align-items:center;gap:22px;background:#fff;border:1px solid var(--tm-borde);
  border-radius:12px;padding:16px 22px;margin:.3rem 0}
.tm-ficha svg{width:120px;flex:0 0 auto}
.tm-ficha__nombre{font-family:var(--tm-cond);font-weight:700;font-size:1.9rem;line-height:1.05}
.tm-estado{display:inline-block;margin-top:6px;padding:2px 12px;border-radius:999px;font-weight:600;font-size:.95rem}
.tm-estado--ABIERTA{background:#E6F6EF;color:#0B6E48}
.tm-estado--CERRADA{background:#FFF1F0;color:#9E2018}
.tm-estado--NO{background:#EEF0EE;color:#5E6670}
.tm-f-abierta .tm-f-puerta-a{animation:tm-abre-izq-f .6s ease .15s both}
.tm-f-abierta .tm-f-puerta-b{animation:tm-abre-der-f .6s ease .15s both}
.tm-f-abierta .tm-f-luz,.tm-f-cerrada .tm-f-luz{animation:tm-titila .35s ease 3 alternate}
.tm-f-barrera{animation:tm-baja-barrera .55s cubic-bezier(.3,1.5,.6,1) both;transform-box:fill-box}

.tm-tablero{display:flex;flex-wrap:wrap;align-items:center;gap:14px 26px;background:var(--tm-grafito);
  color:#fff;border-radius:12px;padding:18px 24px;margin:.4rem 0;position:relative;overflow:hidden}
.tm-tablero::before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--acento)}
.tm-tablero__hora{font-family:var(--tm-cond);font-weight:700;font-size:3.4rem;line-height:1;
  display:inline-block;animation:tm-voltea .55s cubic-bezier(.2,.9,.3,1.2) both;transform-origin:50% 0}
.tm-tablero__detalle{color:#C5CBD3;line-height:1.45}
.tm-tablero__detalle b{color:#fff}
.tm-salidas{list-style:none;margin:.4rem 0;padding:0;background:#fff;border:1px solid var(--tm-borde);border-radius:12px}
.tm-salidas li{margin:0!important;display:grid;grid-template-columns:5.5rem 5rem 1fr;align-items:center;gap:12px;padding:8px 16px;
  border-top:1px solid #EEF0EB}
.tm-salidas li:first-child{border-top:0}
.tm-salidas__hora{font-family:var(--tm-cond);font-weight:700;font-size:1.4rem;line-height:1}
.tm-salidas__nota{color:#5E6670}
.tm-salidas--vacia{color:#8A929C}

.tm-ranking{list-style:none;margin:.4rem 0;padding:0;background:#fff;border:1px solid var(--tm-borde);border-radius:12px}
.tm-ranking li{margin:0!important;display:grid;grid-template-columns:2.4rem minmax(9rem,15rem) 1fr 4.6rem;align-items:center;gap:12px;
  padding:7px 16px;border-top:1px solid #EEF0EC}
.tm-ranking li:first-child{border-top:0}
.tm-ranking__puesto{font-family:var(--tm-cond);font-weight:700;font-size:1.25rem;color:var(--tm-suave)}
.tm-ranking__nombre{font-weight:600}
.tm-ranking__barra{height:12px;border-radius:6px;background:#EEF0EC;overflow:hidden}
.tm-ranking__barra span{display:block;height:100%;border-radius:6px;background:var(--acento);transform-origin:left;
  animation:tm-crece .8s cubic-bezier(.2,.8,.2,1) both;animation-delay:calc(var(--i) * 45ms)}
.tm-ranking__valor{text-align:right;font-family:var(--tm-cond);font-weight:700;font-size:1.15rem}
@media (max-width:640px){.tm-ranking li{grid-template-columns:2rem 1fr 4rem}.tm-ranking__barra{display:none}}

.tm-linea{overflow-x:auto;background:#fff;border:1px solid var(--tm-borde);border-radius:12px;margin:.4rem 0}
.tm-linea ol{display:flex;list-style:none;margin:0;padding:150px 40px 18px 24px;min-width:max-content}
.tm-linea li{position:relative;flex:0 0 44px;height:24px;margin:0!important;padding:0!important}
.tm-linea li::before{content:"";position:absolute;left:0;right:0;top:9px;height:7px;background:var(--acento)}
.tm-linea li:first-child::before{left:50%}
.tm-linea li:last-child::before{right:50%}
.tm-parada__punto{position:absolute;left:50%;top:4px;width:17px;height:17px;margin-left:-8.5px;border-radius:50%;
  background:#fff;border:4px solid var(--tm-grafito);box-sizing:border-box}
.tm-parada--extremo .tm-parada__punto{width:22px;height:22px;margin-left:-11px;top:1.5px;border-width:5px}
.tm-parada__nombre{position:absolute;left:50%;bottom:30px;transform:rotate(-52deg);transform-origin:left bottom;
  white-space:nowrap;font-size:.84rem;font-weight:600;color:var(--tm-grafito)}
.tm-parada--nueva .tm-parada__punto{border-color:var(--tm-verde);animation:tm-entra-parada .7s cubic-bezier(.3,1.6,.5,1) both}
.tm-parada--nueva .tm-parada__nombre{color:#0B6E48}
.tm-parada--cerrada .tm-parada__punto{border-color:var(--tm-rojo);background:#FFE3E0}
.tm-parada--cerrada .tm-parada__nombre{color:#9E2018;text-decoration:line-through}

/* ---------- viaje: tarjetas de cada tramo ---------- */
.tm-tramo{background:#fff;border:1px solid var(--tm-borde);border-radius:12px;padding:14px 18px;height:100%;
  line-height:1.5}
.tm-tramo__cabeza{display:flex;align-items:center;gap:10px;font-family:var(--tm-cond);font-weight:700;
  font-size:1.3rem;margin-bottom:4px}
.tm-tramo--total{background:var(--tm-grafito);border-color:var(--tm-grafito);color:#fff}
.tm-tramo--total .tm-nota{color:#C5CBD3}
.tm-tramo__numero{font-family:var(--tm-cond);font-weight:700;font-size:2.3rem;line-height:1.05}

/* ---------- inicio: tarjetas de destino (toda la tarjeta es clic) ---------- */
.tm-destino__icono{width:54px;height:54px;border-radius:11px;background:var(--acento);display:grid;place-items:center;
  margin-bottom:12px}
.tm-destino__icono svg{width:36px;height:36px}
.tm-destino__titulo{font-family:var(--tm-cond);font-weight:700;font-size:1.55rem;line-height:1.1}
.tm-destino__texto{color:var(--tm-suave);margin:.3rem 0 0;min-height:3em;line-height:1.45}
[class*="st-key-destino_"]{position:relative;background:#fff;transition:transform .15s ease,border-color .15s ease}
[class*="st-key-destino_"]:hover{transform:translateY(-3px);border-color:var(--tm-grafito)}
[class*="st-key-destino_"] [data-testid="stElementContainer"]{position:static}
[class*="st-key-destino_"] [data-testid="stPageLink"] a::after{content:"";position:absolute;inset:0;border-radius:inherit}
[class*="st-key-destino_"] [data-testid="stPageLink"] p{font-weight:600}

/* ---------- animaciones de las escenas ---------- */
.tm-e-bus{animation:tm-llega-bus 1.25s cubic-bezier(.2,.8,.25,1) both}
.tm-e-estacion{animation:tm-aparece .4s ease both}
.tm-e-anden{animation:tm-sube .45s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box}
.tm-e-vidrio{animation:tm-crece-y .45s cubic-bezier(.2,.8,.2,1) .25s both;transform-box:fill-box;transform-origin:50% 100%}
.tm-e-techo{animation:tm-cae .5s cubic-bezier(.3,1.4,.5,1) .55s both;transform-box:fill-box}
.tm-e-puerta-a{animation:tm-abre-izq-e .5s ease 1.05s both}
.tm-e-puerta-b{animation:tm-abre-der-e .5s ease 1.05s both}
.tm-e-letrero{animation:tm-pop .45s cubic-bezier(.3,1.6,.5,1) .85s both;transform-box:fill-box;transform-origin:50% 100%}

.tm-e-tarjeta{animation:tm-tarjeta 1.5s cubic-bezier(.4,0,.2,1) both}
.tm-e-lector{animation:tm-lector-ok .2s ease .62s both}
.tm-e-onda{opacity:0;animation:tm-onda .6s ease-out .62s both;transform-box:fill-box;transform-origin:center}
.tm-e-chulo{stroke-dasharray:22;stroke-dashoffset:22;animation:tm-traza .3s ease .66s forwards}
.tm-e-brazos{animation:tm-gira-brazos .55s cubic-bezier(.4,0,.2,1) .95s both;transform-origin:168px 128px}
.tm-e-paso1,.tm-e-paso2,.tm-e-paso3,.tm-e-paso4{opacity:0;animation:tm-aparece .2s ease forwards}
.tm-e-paso1{animation-delay:1.15s}.tm-e-paso2{animation-delay:1.3s}.tm-e-paso3{animation-delay:1.45s}.tm-e-paso4{animation-delay:1.6s}

.tm-e-minutero{animation:tm-gira .35s linear infinite;transform-origin:84px 84px}
.tm-e-horero{animation:tm-gira 4.2s linear infinite;transform-origin:84px 84px}
.tm-e-caminante{animation:tm-camina-x 2.1s linear both}
.tm-e-caminante .tm-camina{animation:tm-rebota .26s ease-in-out infinite alternate}
.tm-e-caminante .tm-pierna-a{animation:tm-paso-a .26s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:50% 0}
.tm-e-caminante .tm-pierna-b{animation:tm-paso-b .26s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:50% 0}
.tm-e-c0{animation-delay:0s}.tm-e-c1{animation-delay:.12s}.tm-e-c2{animation-delay:.26s}.tm-e-c3{animation-delay:.36s}
.tm-e-c4{animation-delay:.5s}.tm-e-c5{animation-delay:.6s}.tm-e-c6{animation-delay:.74s}.tm-e-c7{animation-delay:.86s}

.tm-e-fila{animation:tm-voltea .5s cubic-bezier(.2,.9,.3,1.2) both;transform-box:fill-box;transform-origin:50% 0}
.tm-e-fila0{animation-delay:.2s}.tm-e-fila1{animation-delay:.45s}.tm-e-fila2{animation-delay:.7s}
.tm-e-tic{animation:tm-gira 1.6s steps(8) infinite;transform-origin:262px 50px}

.tm-e-nueva{animation:tm-cae-parada .7s cubic-bezier(.3,1.5,.5,1) .3s both;transform-box:fill-box}
.tm-e-une{stroke-dasharray:70;stroke-dashoffset:70;animation:tm-traza .35s ease .95s forwards}
.tm-e-deshacer{animation:tm-pop .45s cubic-bezier(.3,1.6,.5,1) 1.2s both;transform-box:fill-box;transform-origin:center}

.tm-e-curva{stroke-dasharray:260;stroke-dashoffset:260;animation:tm-traza 1s cubic-bezier(.4,0,.2,1) forwards}
.tm-e-curva2{animation-delay:.25s}.tm-e-curva3{animation-delay:.5s}
.tm-e-puntos{animation:tm-aparece .3s ease 1.4s both}

@keyframes tm-salir{to{opacity:0;visibility:hidden}}
@keyframes tm-aparece{from{opacity:0}to{opacity:1}}
@keyframes tm-llena{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes tm-gira{to{transform:rotate(360deg)}}
@keyframes tm-titila{from{opacity:1}to{opacity:.35}}
@keyframes tm-late{from{transform:scale(1)}to{transform:scale(1.25)}}
@keyframes tm-aguja{from{transform:rotate(-70deg)}to{transform:rotate(10deg)}}
@keyframes tm-abre-izq{to{transform:translateX(-4px)}}
@keyframes tm-abre-der{to{transform:translateX(4px)}}
@keyframes tm-abre-izq-f{from{transform:translateX(0)}to{transform:translateX(-13px)}}
@keyframes tm-abre-der-f{from{transform:translateX(0)}to{transform:translateX(13px)}}
@keyframes tm-abre-izq-e{to{transform:translateX(-22px)}}
@keyframes tm-abre-der-e{to{transform:translateX(22px)}}
@keyframes tm-baja-barrera{from{transform:translateY(-60px);opacity:0}to{transform:translateY(0);opacity:1}}
@keyframes tm-voltea{from{transform:perspective(300px) rotateX(-90deg);opacity:0}to{transform:none;opacity:1}}
@keyframes tm-crece{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes tm-crece-y{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes tm-sube{from{transform:translateY(24px);opacity:0}to{transform:none;opacity:1}}
@keyframes tm-cae{from{transform:translateY(-50px);opacity:0}to{transform:none;opacity:1}}
@keyframes tm-pop{from{transform:scale(0);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes tm-llega-bus{0%{transform:translateX(-330px)}82%{transform:translateX(5px)}100%{transform:translateX(0)}}
@keyframes tm-tarjeta{
  0%{transform:translate(250px,10px) rotate(-18deg);opacity:0}
  15%{opacity:1}
  40%{transform:translate(106px,63px) rotate(0)}
  62%{transform:translate(106px,63px) rotate(0)}
  100%{transform:translate(236px,4px) rotate(14deg);opacity:0}}
@keyframes tm-lector-ok{to{stroke:#12A26A}}
@keyframes tm-onda{0%{opacity:.9;transform:scale(1)}100%{opacity:0;transform:scale(2.4)}}
@keyframes tm-traza{to{stroke-dashoffset:0}}
@keyframes tm-gira-brazos{from{transform:rotate(0)}to{transform:rotate(120deg)}}
@keyframes tm-camina-x{from{transform:translateX(-30px)}to{transform:translateX(250px)}}
@keyframes tm-rebota{from{transform:translateY(0)}to{transform:translateY(-2.5px)}}
@keyframes tm-paso-a{from{transform:rotate(22deg)}to{transform:rotate(-22deg)}}
@keyframes tm-paso-b{from{transform:rotate(-22deg)}to{transform:rotate(22deg)}}
@keyframes tm-cae-parada{from{transform:translateY(-80px);opacity:0}to{transform:none;opacity:1}}
@keyframes tm-entra-parada{0%{transform:scale(0)}100%{transform:scale(1)}}
@keyframes tm-va-y-viene{from{transform:translateX(0)}to{transform:translateX(112px)}}
@keyframes tm-enciende{0%,30%{fill:#fff}70%,100%{fill:var(--tm-rojo)}}
@keyframes tm-barrido{from{background-position:100% 0}to{background-position:-100% 0}}
@keyframes tm-rayas{from{background-position:0 0}to{background-position:23px 0}}

@media (prefers-reduced-motion:reduce){
  .tm-bienvenida{display:none}
  .tm-escena *,.tm-ficha-dibujo *,.tm-tablero__hora,.tm-ranking__barra span,.tm-parada__punto,
  .tm-cargando *{animation:none!important}
  button[data-testid^="stBaseButton"]{transition:none}
}
</style>
"""


def aplicar_tema():
    """CSS global. Se llama una vez por ejecucion desde front/app.py."""
    st.html(_CSS)


# ------------------------------------------------------------------ encabezado
def encabezado(clave):
    """Letrero de la pagina y, si recien se entra a ella, su escena animada."""
    titulo, bajada, color, icono, escena, frase = PAGINAS[clave]
    entrada = ""
    if st.session_state.get("tm_pagina") != clave:
        st.session_state["tm_pagina"] = clave
        entrada = f"""
<div class="tm-bienvenida" style="--acento:{color}" aria-hidden="true">
  {escena(color)}
  <div class="tm-bienvenida__frase">{frase}</div>
  <div class="tm-bienvenida__barra"><span></span></div>
</div>"""
    html(f"""
{entrada}
<div class="tm-letrero" style="--acento:{color}">
  <div class="tm-letrero__icono">{dibujos.icono(icono, color)}</div>
  <div>
    <div class="tm-letrero__titulo" role="heading" aria-level="1">{titulo}</div>
    <p class="tm-letrero__bajada">{bajada}</p>
  </div>
</div>""")


# ------------------------------------------------------------------ cargas
def _cargador(mensaje):
    paradas = ""
    for k in range(5):
        paradas += (f'<circle class="tm-cargando__parada" cx="{14 + k * 35.5}" cy="22" r="5" fill="#fff" '
                    f'stroke="#262B33" stroke-width="3" style="animation-delay:{k * 0.3:.1f}s"/>')
    return f"""
<div class="tm-cargando" role="status">
  <svg viewBox="0 0 170 36" aria-hidden="true">
    <path d="M14 22 H156" stroke="#D3D8D1" stroke-width="6" stroke-linecap="round"/>
    {paradas}
    <g class="tm-cargando__bus"><g transform="translate(2 2) scale(.21)">{dibujos.bus()}</g></g>
  </svg>
  <span class="tm-cargando__texto">{texto(mensaje)}</span>
</div>"""


@contextmanager
def cargando(mensaje):
    """Muestra el bus de carga mientras corre el bloque `with`."""
    lugar = st.empty()
    with lugar.container():
        html(_cargador(mensaje))
    try:
        yield
    finally:
        lugar.empty()


# ------------------------------------------------------------------ piezas
def insignia(ruta):
    fondo, color = dibujos.color_ruta(ruta)
    return f'<span class="tm-ruta" style="background:{fondo};color:{color}">{texto(ruta)}</span>'


def chips(nombres, clase=""):
    partes = "".join(f'<span class="tm-chip {clase}">{texto(n)}</span>' for n in nombres)
    return f'<div class="tm-chips">{partes}</div>'


def ficha_estacion(nombre, estado):
    nombre_estado = {"ABIERTA": "Abierta", "CERRADA": "Cerrada"}.get(estado, "No existe")
    clase = estado if estado in ("ABIERTA", "CERRADA") else "NO"
    html(f"""
<div class="tm-ficha">
  {dibujos.estacion_estado(estado)}
  <div>
    <div class="tm-ficha__nombre">{texto(nombre)}</div>
    <span class="tm-estado tm-estado--{clase}">{nombre_estado}</span>
  </div>
</div>""")


def tablero(ruta, estacion, hora, detalle, color):
    html(f"""
<div class="tm-tablero" style="--acento:{color}">
  {insignia(ruta)}
  <span class="tm-tablero__hora">{texto(hora)}</span>
  <div class="tm-tablero__detalle">Próximo bus en <b>{texto(estacion)}</b><br>{detalle}</div>
</div>""")


def salidas(filas):
    """Tabla de salidas: filas = [(ruta, hora o None, nota)], una por ruta que pasa por la estacion."""
    items = ""
    for ruta, hora, nota in filas:
        clase = "" if hora else ' class="tm-salidas--vacia"'
        items += (f'<li{clase}>{insignia(ruta)}<span class="tm-salidas__hora">{texto(hora or "—")}</span>'
                  f'<span class="tm-salidas__nota">{texto(nota)}</span></li>')
    html(f'<ul class="tm-salidas">{items}</ul>')


def ranking(top, color):
    if not top:
        return
    mayor = top[0][1] if top[0][1] > 0 else 1
    filas = ""
    for i in range(len(top)):
        nombre, buses = top[i]
        filas += f"""
<li style="--i:{i}">
  <span class="tm-ranking__puesto">{i + 1}</span>
  <span class="tm-ranking__nombre">{texto(nombre)}</span>
  <span class="tm-ranking__barra"><span style="width:{100 * buses / mayor:.1f}%"></span></span>
  <span class="tm-ranking__valor">{f"{buses:,}".replace(",", ".")}</span>
</li>"""
    html(f'<ol class="tm-ranking" style="--acento:{color}">{filas}</ol>')


def linea_recorrido(paradas, color, nueva=None, cerradas=()):
    """Mapa de linea de una ruta: todas sus paradas en orden, de izquierda a derecha."""
    items = ""
    for i in range(len(paradas)):
        nombre = paradas[i]
        clases = "tm-parada"
        if i == 0 or i == len(paradas) - 1:
            clases += " tm-parada--extremo"
        if nombre == nueva:
            clases += " tm-parada--nueva"
        if nombre in cerradas:
            clases += " tm-parada--cerrada"
        items += (f'<li class="{clases}"><span class="tm-parada__punto"></span>'
                  f'<span class="tm-parada__nombre">{texto(nombre)}</span></li>')
    html(f'<div class="tm-linea" style="--acento:{color}"><ol>{items}</ol></div>')
