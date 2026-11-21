// Recorrido de una ruta que se puede tocar (Parte E).
//   data.paradas : [{n: nombre, c: cerrada?, nueva: recien agregada?}]  en el orden que se ve
//   data.color   : color de la ruta
//   data.elegido : indice del tramo elegido (entre paradas[i] y paradas[i+1]) o -1
// Al pasar el mouse sobre un tramo aparece un "+"; al hacer clic se avisa a Python
// con setTriggerValue("tramo", {a, b}) para que ofrezca agregar una parada ahi.
const NS = "http://www.w3.org/2000/svg";
function el(tag, attrs, padre) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (padre) padre.appendChild(e);
  return e;
}
function partir(nombre) {
  if (nombre.length <= 15) return [nombre];
  const palabras = nombre.split(" ");
  let mejor = [nombre], peor = 1e9;
  for (let i = 1; i < palabras.length; i++) {
    const a = palabras.slice(0, i).join(" "), b = palabras.slice(i).join(" ");
    const m = Math.max(a.length, b.length);
    if (m < peor) { peor = m; mejor = [a, b]; }
  }
  return mejor;
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  const raiz = parentElement.querySelector(".linea");
  let guardado = parentElement.__tm;
  if (!guardado) guardado = parentElement.__tm = { clics: 0 };

  function dibujar() {
    raiz.innerHTML = "";
    const P = data.paradas, N = P.length;
    const ancho = raiz.clientWidth || 900;
    const K = ancho < 520 ? 3 : (ancho < 820 ? 5 : 8);
    const W = ancho < 520 ? 460 : (ancho < 820 ? 720 : 1000);
    const MARGEN = ancho < 520 ? 70 : 80, FILA = 132, ARRIBA = 72, RADIO = FILA / 2;
    const filas = Math.max(1, Math.ceil(N / K));
    let paso = K > 1 ? (W - 2 * MARGEN) / (K - 1) : 0;
    let corr = 0;
    if (N <= K) {
      paso = Math.min(paso, N > 1 ? (W - 2 * MARGEN) / (N - 1) : 0, 170);
      corr = (W - 2 * MARGEN - paso * (N - 1)) / 2;
    }
    P.forEach((p, i) => {
      const fila = Math.floor(i / K);
      let col = i % K;
      if (fila % 2 === 1) col = K - 1 - col;
      p.x = MARGEN + corr + col * paso;
      p.y = ARRIBA + fila * FILA;
      p.borde = filas > 1 && (col === 0 || col === K - 1) ? (col === 0 ? "izq" : "der") : "";
    });
    const H = ARRIBA + (filas - 1) * FILA + 78;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "group",
                            "aria-label": "Recorrido de la ruta. Cada tramo entre dos paradas se puede tocar para agregar una parada." });
    raiz.appendChild(svg);

    const capaTramos = el("g", {}, svg);
    const capaParadas = el("g", {}, svg);
    const capaGlobos = el("g", {}, svg);
    const pista = document.createElement("div");
    pista.className = "pista";
    pista.textContent = N > 1 ? "Pasa el mouse por la línea entre dos paradas y haz clic para agregar una parada ahí."
                              : "";

    for (let s = 0; s < N - 1; s++) {
      const a = P[s], b = P[s + 1];
      let d;
      if (Math.abs(a.y - b.y) < 1) d = `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
      else d = `M ${a.x} ${a.y} A ${RADIO} ${RADIO} 0 0 ${a.borde === "der" ? 1 : 0} ${b.x} ${b.y}`;
      const g = el("g", { class: "tramo" + (s === data.elegido ? " elegido" : ""), tabindex: 0, role: "button",
                          "aria-label": `Agregar una parada entre ${a.n} y ${b.n}` }, capaTramos);
      el("path", { d: d, class: "base" }, g);
      const pint = el("path", { d: d, class: "pintada", stroke: data.color }, g);
      el("path", { d: d, class: "zona" }, g);
      const m = pint.getPointAtLength(pint.getTotalLength() / 2);
      const lugar = el("g", { transform: `translate(${m.x} ${m.y})` }, g);   // el CSS anima .mas: la posicion va afuera
      const mas = el("g", { class: "mas" }, lugar);
      el("circle", { cx: 0, cy: 0, r: 17 }, mas);
      el("path", { d: "M -7 0 H 7 M 0 -7 V 7" }, mas);

      // globo con la instruccion
      const texto = `Agregar una parada entre ${a.n} y ${b.n}`;
      const gl = el("g", { class: "globo" }, g);
      const t = el("text", { x: 0, y: 0 }, gl);
      t.textContent = texto;
      const w = Math.min(texto.length * 7.2 + 24, W - 20);
      const xx = Math.min(Math.max(m.x, w / 2 + 6), W - w / 2 - 6);
      const r = el("rect", { x: -w / 2, y: -17, width: w, height: 28, rx: 8 }, gl);
      gl.insertBefore(r, t);
      el("path", { d: `M ${m.x - xx - 6} 11 L ${m.x - xx} 18 L ${m.x - xx + 6} 11 Z`, fill: "#262B33" }, gl);
      gl.setAttribute("transform", `translate(${xx} ${m.y - 40})`);

      const elegir = () => {
        guardado.clics += 1;
        setTriggerValue("tramo", { a: a.n, b: b.n, n: guardado.clics });
      };
      g.addEventListener("pointerenter", () => g.classList.add("hover"));
      g.addEventListener("pointerleave", () => g.classList.remove("hover"));
      g.addEventListener("focus", () => g.classList.add("hover"));
      g.addEventListener("blur", () => g.classList.remove("hover"));
      g.addEventListener("click", elegir);
      g.addEventListener("keydown", ev => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); elegir(); } });
    }

    P.forEach((p, i) => {
      const extremo = i === 0 || i === N - 1;
      const g = el("g", { class: "parada" + (extremo ? " extremo" : "") + (p.c ? " cerrada" : "") + (p.nueva ? " nueva" : "") },
                   capaParadas);
      el("circle", { cx: p.x, cy: p.y, r: extremo ? 14 : 9 }, g);
      const lineas = partir(p.n);
      let x = p.x, anclaje = "middle";
      if (p.borde === "der") { anclaje = "end"; x = p.x + 14; }
      if (p.borde === "izq") { anclaje = "start"; x = p.x - 14; }
      const t = el("text", { x: x, y: p.y + 34, "text-anchor": anclaje,
                             class: "nombre" + (p.c ? " cerrada" : "") + (p.nueva ? " nueva" : "") }, g);
      lineas.forEach((linea, k) => {
        const ts = el("tspan", { x: x, dy: k === 0 ? 0 : 16 }, t);
        ts.textContent = linea;
      });
    });
    raiz.appendChild(pista);
  }

  dibujar();
  let anterior = raiz.clientWidth;
  const obs = new ResizeObserver(() => {
    const w = raiz.clientWidth;
    if (Math.abs(w - anterior) > 40) { anterior = w; dibujar(); }
  });
  obs.observe(raiz);
  return () => obs.disconnect();
}
