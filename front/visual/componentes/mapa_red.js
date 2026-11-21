// Mapa esquematico de la red (Parte E). Se dibuja con los datos que manda Python:
//   data.estaciones : [{n: nombre, x, y, r: [indices de rutas], c: true si esta cerrada}]
//   data.rutas      : [[nombre, color de fondo, color del texto], ...]
//   data.aristas    : [[i, j], ...]   estaciones consecutivas en alguna ruta
//   data.viaje      : [{color, paradas: [indices]}, ...]   el viaje elegido (puede ir vacio)
//   data.origen / data.destino : indice de la estacion o -1
// Cuando se hace clic en una estacion se avisa a Python con setTriggerValue("estacion", ...).
const NS = "http://www.w3.org/2000/svg";

function el(tag, attrs, padre) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (padre) padre.appendChild(e);
  return e;
}
function div(clase, texto, padre) {
  const d = document.createElement("div");
  if (clase) d.className = clase;
  if (texto !== undefined) d.textContent = texto;
  if (padre) padre.appendChild(d);
  return d;
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  const raiz = parentElement.querySelector(".mapa");
  const W = data.ancho, H = data.alto;
  const sinMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // lo que se conserva entre un dibujo y el siguiente (zoom, posicion, clics)
  let guardado = parentElement.__tm;
  const primera = !guardado;
  if (!guardado) guardado = parentElement.__tm = { vista: { x: 0, y: 0, w: W, h: H }, clics: 0 };
  const vista = guardado.vista;

  raiz.innerHTML = "";
  const marco = div("marco", undefined, raiz);
  const papel = div("papel", undefined, marco);
  if (primera && !sinMovimiento) {
    papel.classList.add("desenrollando");
    setTimeout(() => papel.classList.remove("desenrollando"), 1700);
  }
  const svg = el("svg", { role: "img", preserveAspectRatio: "xMidYMid meet",
                          "aria-label": "Mapa esquemático de las estaciones de TransMilenio" });
  papel.appendChild(svg);
  div("rollo rollo--arriba", undefined, papel);
  div("rollo rollo--abajo", undefined, papel);
  const globo = div("globo", undefined, papel);
  const leyenda = div("leyenda", "Rueda: acercar · Arrastra: mover el mapa", papel);
  const controles = div("controles", undefined, papel);
  const pie = div("pie", undefined, marco);
  pie.setAttribute("aria-live", "polite");

  const E = data.estaciones;
  const viajeIdx = new Set();
  (data.viaje || []).forEach(t => t.paradas.forEach(i => viajeIdx.add(i)));

  // ------------------------------------------------------------ vias
  const capaVias = el("g", {}, svg);
  data.aristas.forEach(([a, b]) => {
    el("line", { x1: E[a].x, y1: E[a].y, x2: E[b].x, y2: E[b].y, class: "via",
                 "vector-effect": "non-scaling-stroke" }, capaVias);
  });
  const capaViaje = el("g", {}, svg);
  (data.viaje || []).forEach(t => {
    for (let k = 0; k < t.paradas.length - 1; k++) {
      const a = E[t.paradas[k]], b = E[t.paradas[k + 1]];
      const l = el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: "via via--viaje",
                             "vector-effect": "non-scaling-stroke" }, capaViaje);
      l.style.stroke = t.color;      // el CSS de .via pinta de gris: el color del viaje va en style
    }
  });

  // ------------------------------------------------------------ estaciones
  const capaEst = el("g", {}, svg);
  const capaNombres = el("g", {}, svg);
  const capaCarteles = el("g", {}, svg);
  const circulos = [];
  const nombres = [];
  let hoverIdx = -1;

  E.forEach((s, i) => {
    let clase = "est";
    if (s.c) clase += " cerrada";
    if (viajeIdx.has(i)) clase += " viaje";
    if (i === data.origen || i === data.destino) clase += " extremo";
    const c = el("circle", { cx: s.x, cy: s.y, r: 6, class: clase, tabindex: 0, role: "button",
                             "aria-label": s.n + (s.c ? " (cerrada)" : "") }, capaEst);
    c.setAttribute("vector-effect", "non-scaling-stroke");
    circulos.push(c);
    const t = el("text", { x: s.x + 9, y: s.y + 4, class: "nombre" }, capaNombres);
    t.textContent = s.n;
    if (viajeIdx.has(i) || i === data.origen || i === data.destino) t.classList.add("fijo");
    nombres.push(t);

    c.addEventListener("pointerenter", () => mostrarGlobo(i));
    c.addEventListener("pointerleave", () => ocultarGlobo());
    c.addEventListener("focus", () => mostrarGlobo(i));
    c.addEventListener("blur", () => ocultarGlobo());
    c.addEventListener("click", ev => elegir(i, ev.shiftKey));
    c.addEventListener("keydown", ev => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); elegir(i, ev.shiftKey); } });
  });

  // carteles de origen y destino
  function cartel(i, texto, color) {
    if (i < 0) return;
    const s = E[i];
    const g = el("g", { class: "cartel", transform: `translate(${s.x} ${s.y - 22})` }, capaCarteles);
    const t = el("text", { x: 0, y: 5 }, g);
    t.textContent = texto;
    const w = texto.length * 7.4 + 16;
    const r = el("rect", { x: -w / 2, y: -11, width: w, height: 22, rx: 6, fill: color }, g);
    g.insertBefore(r, t);
    el("path", { d: "M -5 11 L 0 18 L 5 11 Z", fill: color }, g);
    g.dataset.i = i;
  }
  cartel(data.origen, "Origen", "#2E7D32");
  cartel(data.destino, "Destino", "#D42A20");
  if (data.destino >= 0) {
    const p = el("circle", { cx: E[data.destino].x, cy: E[data.destino].y, r: 10, class: "pulso" }, capaCarteles);
    p.setAttribute("vector-effect", "non-scaling-stroke");
  }

  // ------------------------------------------------------------ zoom y movimiento
  function aplicarVista() {
    svg.setAttribute("viewBox", `${vista.x} ${vista.y} ${vista.w} ${vista.h}`);
    const k = vista.w / W;                       // 1 = todo el mapa; menos = acercado
    papel.classList.toggle("cerca", k < 0.42);
    const radio = 6.2 * Math.pow(k, 0.55);
    circulos.forEach((c, i) => {
      const grande = i === data.origen || i === data.destino;
      c.setAttribute("r", (grande ? 1.45 : 1) * radio);
    });
    const tam = 13 * Math.pow(k, 0.8);
    nombres.forEach((t, i) => {
      t.style.fontSize = tam + "px";
      t.setAttribute("x", E[i].x + 1.4 * radio + 2);
      t.setAttribute("y", E[i].y + tam * 0.32);
      t.style.strokeWidth = (tam * 0.3) + "px";
    });
    Array.from(capaCarteles.querySelectorAll(".cartel")).forEach(g => {
      const s = E[+g.dataset.i];
      const esc = Math.max(0.55, Math.pow(k, 0.6));
      g.setAttribute("transform", `translate(${s.x} ${s.y - 2.2 * radio - 4 * esc}) scale(${esc})`);
    });
    capaCarteles.querySelectorAll(".pulso").forEach(p => p.setAttribute("r", 1.8 * radio));
  }
  function ajustar() {
    // mantiene la proporcion del cuadro para que "meet" no deje bordes raros
    const caja = svg.getBoundingClientRect();
    if (!caja.width || !caja.height) return;
    const pro = caja.width / caja.height;
    if (Math.abs(vista.w / vista.h - pro) > 0.001) {
      const cx = vista.x + vista.w / 2, cy = vista.y + vista.h / 2;
      vista.h = vista.w / pro;
      vista.x = cx - vista.w / 2;
      vista.y = cy - vista.h / 2;
    }
  }
  function limitar() {
    const margen = 0.15;
    vista.x = Math.min(Math.max(vista.x, -W * margen), W * (1 + margen) - vista.w);
    vista.y = Math.min(Math.max(vista.y, -H * margen), H * (1 + margen) - vista.h);
  }
  function aEspacio(px, py) {
    const caja = svg.getBoundingClientRect();
    return [vista.x + (px - caja.left) / caja.width * vista.w, vista.y + (py - caja.top) / caja.height * vista.h];
  }
  function zoom(factor, px, py) {
    const caja = svg.getBoundingClientRect();
    if (px === undefined) { px = caja.left + caja.width / 2; py = caja.top + caja.height / 2; }
    const [ex, ey] = aEspacio(px, py);
    const nw = Math.min(W * 1.3, Math.max(W / 9, vista.w * factor));
    const f = nw / vista.w;
    vista.x = ex - (ex - vista.x) * f;
    vista.y = ey - (ey - vista.y) * f;
    vista.w = nw; vista.h = vista.h * f;
    limitar(); aplicarVista(); ocultarGlobo();
  }
  function reiniciarVista() {
    // todo el mapa a la vista, centrado, con la proporcion del cuadro
    const caja = svg.getBoundingClientRect();
    const pro = caja.width && caja.height ? caja.width / caja.height : W / H;
    if (W / H > pro) { vista.w = W; vista.h = W / pro; } else { vista.h = H; vista.w = H * pro; }
    vista.x = (W - vista.w) / 2; vista.y = (H - vista.h) / 2;
    aplicarVista();
  }

  [["+", "Acercar", () => zoom(0.7)], ["−", "Alejar", () => zoom(1 / 0.7)], ["⌂", "Ver todo el mapa", reiniciarVista]]
    .forEach(([txt, etiqueta, fn]) => {
      const b = document.createElement("button");
      b.type = "button"; b.textContent = txt; b.title = etiqueta; b.setAttribute("aria-label", etiqueta);
      b.addEventListener("click", fn);
      controles.appendChild(b);
    });

  papel.addEventListener("wheel", ev => {
    ev.preventDefault();
    zoom(Math.pow(1.0017, ev.deltaY), ev.clientX, ev.clientY);
  }, { passive: false });

  let arrastre = null;
  let seMovio = false;
  papel.addEventListener("pointerdown", ev => {
    if (ev.button !== 0) return;
    arrastre = { x: ev.clientX, y: ev.clientY, vx: vista.x, vy: vista.y };
    seMovio = false;
  });
  papel.addEventListener("pointermove", ev => {
    if (!arrastre) return;
    const dx = ev.clientX - arrastre.x, dy = ev.clientY - arrastre.y;
    if (!seMovio && Math.hypot(dx, dy) > 5) { seMovio = true; papel.classList.add("arrastrando"); ocultarGlobo(); }
    if (!seMovio) return;
    const caja = svg.getBoundingClientRect();
    vista.x = arrastre.vx - dx / caja.width * vista.w;
    vista.y = arrastre.vy - dy / caja.height * vista.h;
    limitar(); aplicarVista();
  });
  const soltar = () => { arrastre = null; papel.classList.remove("arrastrando"); setTimeout(() => { seMovio = false; }, 0); };
  papel.addEventListener("pointerup", soltar);
  papel.addEventListener("pointerleave", soltar);

  // ------------------------------------------------------------ globo
  function mostrarGlobo(i) {
    if (seMovio) return;
    hoverIdx = i;
    const s = E[i];
    globo.innerHTML = "";
    div("globo__nombre", s.n, globo);
    if (s.r.length) {
      div("globo__sub", s.r.length === 1 ? "Bus que pasa por aquí:" : `Buses que pasan por aquí (${s.r.length}):`, globo);
      const lista = div("globo__buses", undefined, globo);
      const MAX = 14;
      s.r.slice(0, MAX).forEach(r => {
        const b = div("bus", data.rutas[r][0], lista);
        b.style.background = data.rutas[r][1];
        b.style.color = data.rutas[r][2];
      });
      if (s.r.length > MAX) { const m = div("bus", `+${s.r.length - MAX} más`, lista); m.style.background = "#E0E3DD"; }
    } else {
      div("globo__sub", "Ninguna ruta pasa por aquí.", globo);
    }
    let accion, tecla = null, clase = "globo__accion";
    if (s.c) { accion = "Estación cerrada: no se puede viajar desde ni hacia ella."; clase += " globo__accion--no"; }
    else if (i === data.origen) { accion = "Es tu estación de origen."; clase += " globo__accion--no"; }
    else if (data.origen < 0) accion = "Haz clic para salir desde esta estación.";
    else { accion = "Haz clic para cambiar tu ruta a esta estación."; tecla = "Shift + clic: usarla como origen."; }
    div(clase, accion, globo);
    if (tecla) div("globo__tecla", tecla, globo);

    // posicion: encima de la estacion; si no cabe, debajo
    const cp = papel.getBoundingClientRect(), ce = circulos[i].getBoundingClientRect();
    let x = ce.left + ce.width / 2 - cp.left;
    let y = ce.top - cp.top - 8;
    const ancho = globo.offsetWidth, alto = globo.offsetHeight;
    x = Math.min(Math.max(x, ancho / 2 + 8), cp.width - ancho / 2 - 8);
    globo.style.transform = "";
    if (y - alto < 8) { y = ce.bottom - cp.top + 8 + alto; }
    globo.style.left = x + "px";
    globo.style.top = y + "px";
    globo.classList.add("visible");
    circulos[i].classList.add("hover");
  }
  function ocultarGlobo() {
    globo.classList.remove("visible");
    if (hoverIdx >= 0) circulos[hoverIdx].classList.remove("hover");
    hoverIdx = -1;
  }

  // ------------------------------------------------------------ clic
  function elegir(i, comoOrigen) {
    if (seMovio) return;
    const s = E[i];
    if (s.c) { pie.textContent = ""; const b = document.createElement("b"); b.textContent = s.n;
               pie.append(b, " está cerrada: no se puede viajar desde ni hacia ella."); return; }
    guardado.clics += 1;
    setTriggerValue("estacion", { nombre: s.n, origen: !!comoOrigen, n: guardado.clics });
  }

  // texto de abajo
  if (data.origen >= 0 && data.destino >= 0) {
    pie.append("Tu viaje va de ");
    const a = document.createElement("b"); a.textContent = E[data.origen].n;
    const b = document.createElement("b"); b.textContent = E[data.destino].n;
    pie.append(a, " a ", b, ". Haz clic en otra estación para cambiar el destino.");
  } else if (data.origen >= 0) {
    const a = document.createElement("b"); a.textContent = E[data.origen].n;
    pie.append("Sales de ", a, ". Haz clic en la estación a la que quieres llegar.");
  } else {
    pie.textContent = "Pasa el mouse por una estación para ver qué buses pasan. Haz clic para elegir de dónde sales.";
  }

  if (primera) reiniciarVista(); else { ajustar(); limitar(); aplicarVista(); }
  let ancho0 = 0;
  const obs = new ResizeObserver(() => {
    const w = papel.clientWidth;
    if (!ancho0) { ancho0 = w; if (primera) reiniciarVista(); return; }
    ajustar(); limitar(); aplicarVista();
  });
  obs.observe(papel);
  return () => obs.disconnect();
}
