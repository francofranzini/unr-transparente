// Microinteracciones. Todo es opcional: sin JavaScript la página se lee completa.
(() => {
  const menosMovimiento = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Ficha: se abre cuando HTMX trae su contenido.
  document.addEventListener("htmx:afterSwap", (e) => {
    if (e.detail.target.id === "ficha-contenido") document.getElementById("ficha").showModal();
  });

  // Cifras que cuentan desde 0 hasta su valor, con formato rioplatense.
  const formato = (valor, decimales) =>
    valor.toLocaleString("es-AR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });

  function contar(el) {
    if (el.dataset.contado) return;
    el.dataset.contado = "1";
    const final = el.textContent.trim();
    const m = final.match(/^(.*?)(−?)(\d[\d.]*(?:,\d+)?)(.*)$/);
    if (!m || menosMovimiento) return;
    const [, antes, signo, numero, despues] = m;
    const decimales = (numero.split(",")[1] || "").length;
    const objetivo = parseFloat(numero.replace(/\./g, "").replace(",", "."));
    const inicio = performance.now(), duracion = 1300;
    const paso = (t) => {
      const p = Math.min((t - inicio) / duracion, 1), suave = 1 - Math.pow(1 - p, 3);
      el.textContent = antes + signo + formato(objetivo * suave, decimales) + despues;
      if (p < 1) requestAnimationFrame(paso); else el.textContent = final;
    };
    requestAnimationFrame(paso);
  }

  // Aparición al hacer scroll: bloques, cifras, gráfico y cada hecho de las cronologías.
  const observador = new IntersectionObserver((entradas) => {
    for (const { target, isIntersecting } of entradas) {
      if (!isIntersecting) continue;
      target.classList.add("visible");
      target.querySelectorAll("[data-contar]").forEach(contar);
      observador.unobserve(target);
    }
  }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
  const observar = (el) => observador.observe(el);
  document.querySelectorAll(".revelar, .hito, .tiempo li").forEach(observar);

  // Cronología de la ley: filtros por actor; lista con scroll propio (ADR 0030) o recorrido hecho por hecho con
  // sellos (ADR 0031). Sin JavaScript se ve la lista completa.
  document.querySelectorAll("[data-cronologia]").forEach((crono) => {
    const hitos = [...crono.querySelectorAll(".hito")];
    const anios = [...crono.querySelectorAll(".anio")];
    const botones = [...crono.querySelectorAll("[data-filtro]")];
    const recuadro = crono.querySelector("[data-cronologia-scroll]");
    const modos = crono.querySelector("[data-modos]");
    const botonModo = crono.querySelector("[data-modo]");
    const pista = crono.querySelector("[data-pista-lista]");
    const nav = crono.querySelector("[data-nav]");
    const contador = crono.querySelector("[data-contador]");
    const [anterior, siguiente] = nav.querySelectorAll("[data-paso]");
    const escalon = 4; // en la lista, los hechos aparecen de a grupos de 4 al entrar en el recuadro
    let carrusel = false, actual = 0, coinciden = [];
    modos.hidden = false;

    // El sello se vuelve a estampar cada vez que su hecho aparece en el recorrido.
    function sellar(hito) {
      const sello = hito.querySelector(".sello");
      if (!sello || menosMovimiento) return;
      sello.classList.remove("estampar");
      recuadro.classList.remove("golpe");
      void sello.offsetWidth;
      sello.classList.add("estampar");
      recuadro.classList.add("golpe");
    }

    function aplicar(conSello = true) {
      const activos = botones.filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.dataset.filtro);
      coinciden = hitos.filter((h) => !activos.length || activos.includes(h.dataset.actor));
      hitos.forEach((h) => { h.hidden = true; h.classList.remove("visible", "actual"); });
      if (carrusel) {
        actual = Math.min(Math.max(actual, 0), coinciden.length - 1);
        const hito = coinciden[actual];
        if (hito) {
          hito.hidden = false;
          hito.classList.add("visible", "actual");
          if (conSello) sellar(hito);
        }
        anios.forEach((a) => { a.hidden = true; });
        contador.textContent = coinciden.length ? `Hecho ${actual + 1} de ${coinciden.length}` : "Ningún hecho con este filtro";
        anterior.disabled = actual <= 0;
        siguiente.disabled = actual >= coinciden.length - 1;
        return;
      }
      coinciden.forEach((h, i) => {
        h.hidden = false;
        h.style.setProperty("--i", i % escalon);
        observar(h);
      });
      // Un año se muestra solo si tiene algún hecho visible.
      anios.forEach((a) => {
        let sig = a.nextElementSibling, alguno = false;
        while (sig && !sig.classList.contains("anio")) { if (!sig.hidden) alguno = true; sig = sig.nextElementSibling; }
        a.hidden = !alguno;
      });
    }

    // Con data-transicion (ADR 0025), el hecho actual sale hacia un lado, el nuevo entra desde el otro y el recuadro
    // acompaña el cambio de alto; si tiene sello, se estampa cuando el hecho terminó de entrar. Sin data-transicion, o
    // con «reducir movimiento», el cambio es inmediato.
    const conTransicion = "transicion" in crono.dataset && !menosMovimiento;
    const SALIDA = 180, ENTRADA = 280;
    let animando = false;

    function mover(paso) {
      if (!carrusel || animando) return;
      const nuevo = Math.min(Math.max(actual + paso, 0), coinciden.length - 1);
      if (nuevo === actual) return;
      if (!conTransicion) {
        actual = nuevo;
        aplicar();
        return;
      }
      animando = true;
      const viejo = coinciden[actual];
      const altoAntes = recuadro.offsetHeight;
      viejo.classList.add(paso > 0 ? "sale-izq" : "sale-der");
      setTimeout(() => {
        viejo.classList.remove("sale-izq", "sale-der");
        actual = nuevo;
        aplicar(false);
        const entrante = coinciden[actual];
        entrante.classList.add(paso > 0 ? "entra-der" : "entra-izq");
        const altoDespues = recuadro.offsetHeight;
        recuadro.style.overflow = "hidden";
        recuadro.style.height = `${altoAntes}px`;
        void recuadro.offsetHeight;
        recuadro.style.transition = `height ${ENTRADA}ms ease`;
        recuadro.style.height = `${altoDespues}px`;
        setTimeout(() => {
          entrante.classList.remove("entra-der", "entra-izq");
          recuadro.style.removeProperty("height");
          recuadro.style.removeProperty("transition");
          recuadro.style.removeProperty("overflow");
          animando = false;
          sellar(entrante);
        }, ENTRADA);
      }, SALIDA);
    }

    botones.forEach((b) => b.addEventListener("click", () => {
      b.setAttribute("aria-pressed", b.getAttribute("aria-pressed") === "true" ? "false" : "true");
      actual = 0;
      aplicar();
      recuadro.scrollTop = 0;
    }));
    botonModo.addEventListener("click", () => {
      carrusel = !carrusel;
      actual = 0;
      botonModo.setAttribute("aria-pressed", String(carrusel));
      botonModo.textContent = carrusel ? "Ver toda la lista" : "Recorrer hecho por hecho ▸";
      recuadro.classList.toggle("modo-carrusel", carrusel);
      nav.hidden = !carrusel;
      pista.hidden = carrusel;
      recuadro.scrollTop = 0;
      aplicar();
    });
    // Ir a un hecho desde otra parte de la página (p. ej. «Ver en la línea de tiempo», ADR 0037): se centra el recuadro,
    // se desplaza hasta el hecho y se lo resalta un momento. En el recorrido, se salta a ese hecho.
    crono.addEventListener("ir-a-hito", (e) => {
      const hito = e.detail;
      recuadro.scrollIntoView({ behavior: menosMovimiento ? "auto" : "smooth", block: "center" });
      if (carrusel) {
        const i = coinciden.indexOf(hito);
        if (i >= 0) { actual = i; aplicar(); }
      } else {
        recuadro.scrollTo({ top: hito.offsetTop - 48, behavior: menosMovimiento ? "auto" : "smooth" });
      }
      hito.classList.remove("resaltado");
      void hito.offsetWidth;
      hito.classList.add("resaltado");
    });
    anterior.addEventListener("click", () => mover(-1));
    siguiente.addEventListener("click", () => mover(1));
    crono.addEventListener("keydown", (e) => {
      if (!carrusel || e.target.closest("summary, a")) return;
      if (e.key === "ArrowRight") { e.preventDefault(); mover(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); mover(-1); }
    });
    aplicar();
  });

  // Enlaces a un hecho de una cronología (#hito-<id>): los resuelve la propia cronología, que sabe dónde está.
  document.addEventListener("click", (e) => {
    const enlace = e.target.closest('a[href^="#hito-"]');
    const hito = enlace && document.getElementById(enlace.getAttribute("href").slice(1));
    const crono = hito && hito.closest("[data-cronologia]");
    if (!crono) return;
    e.preventDefault();
    crono.dispatchEvent(new CustomEvent("ir-a-hito", { detail: hito }));
  });

  // Mapa de quién audita (ADR 0034): un panel por órgano; «Ver sus hechos» filtra la línea de tiempo de la sección.
  document.querySelectorAll("[data-mapa-control]").forEach((mapa) => {
    const botones = [...mapa.querySelectorAll("[data-organo]")];
    const paneles = [...mapa.querySelectorAll("[data-panel-organo]")];
    const elegir = (clave) => {
      botones.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.organo === clave)));
      paneles.forEach((p) => { p.hidden = p.dataset.panelOrgano !== clave; });
    };
    botones.forEach((b) => b.addEventListener("click", () => elegir(b.dataset.organo)));
    elegir(botones[0].dataset.organo);
    const seccion = mapa.closest("section");
    if (!seccion.querySelector("[data-cronologia]")) return;
    mapa.querySelectorAll("[data-ver-hechos]").forEach((b) => {
      b.hidden = false;
      b.addEventListener("click", () => {
        // La cronología de la universidad elegida en el selector «Ver:».
        const crono = [...seccion.querySelectorAll("[data-cronologia]")].find((c) => !c.closest("[hidden]"));
        crono.querySelectorAll("[data-filtro]").forEach((f) => {
          if ((f.getAttribute("aria-pressed") === "true") !== (f.dataset.filtro === b.dataset.verHechos)) f.click();
        });
        crono.scrollIntoView({ behavior: menosMovimiento ? "auto" : "smooth", block: "start" });
      });
    });
  });

  // Línea de tiempo de Control: el selector «Ver:» elige la universidad (ADR 0034). Sin JavaScript se ven todas.
  document.querySelectorAll("[data-universidades]").forEach((bloque) => {
    const botones = [...bloque.querySelectorAll("[data-universidad]")];
    const paneles = [...bloque.querySelectorAll("[data-panel-universidad]")];
    const elegir = (sigla) => {
      botones.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.universidad === sigla)));
      paneles.forEach((p) => { p.hidden = p.dataset.panelUniversidad !== sigla; });
    };
    botones.forEach((b) => b.addEventListener("click", () => elegir(b.dataset.universidad)));
    if (botones.length) elegir(botones[0].dataset.universidad);
  });

  // Luz que sigue al cursor sobre el vidrio.
  if (!menosMovimiento) document.addEventListener("pointermove", (e) => {
    const vidrio = e.target.closest(".luz");
    if (!vidrio) return;
    const r = vidrio.getBoundingClientRect();
    vidrio.style.setProperty("--mx", `${e.clientX - r.left}px`);
    vidrio.style.setProperty("--my", `${e.clientY - r.top}px`);
  });
})();
