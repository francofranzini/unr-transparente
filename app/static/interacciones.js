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

  // Cronología de la ley: filtros por actor y «ver anteriores».
  document.querySelectorAll("[data-cronologia]").forEach((crono) => {
    const hitos = [...crono.querySelectorAll(".hito")];
    const anios = [...crono.querySelectorAll(".anio")];
    const botones = [...crono.querySelectorAll("[data-filtro]")];
    const verMas = crono.querySelector("[data-ver-mas]");
    const limite = Number(crono.dataset.visibles || 4);
    let completa = false;

    function aplicar() {
      const activos = botones.filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.dataset.filtro);
      const coinciden = hitos.filter((h) => !activos.length || activos.includes(h.dataset.actor));
      hitos.forEach((h) => { h.hidden = true; h.classList.remove("visible"); });
      coinciden.forEach((h, i) => {
        if (completa || i < limite) {
          h.hidden = false;
          h.style.setProperty("--i", i % limite);
          observar(h);
        }
      });
      // Un año se muestra solo si tiene algún hecho visible.
      anios.forEach((a) => {
        let sig = a.nextElementSibling, alguno = false;
        while (sig && !sig.classList.contains("anio")) { if (!sig.hidden) alguno = true; sig = sig.nextElementSibling; }
        a.hidden = !alguno;
      });
      const resto = coinciden.length - limite;
      verMas.hidden = resto <= 0;
      verMas.textContent = completa ? "Ver menos" : `Ver ${resto} ${resto === 1 ? "hecho anterior" : "hechos anteriores"}`;
    }

    botones.forEach((b) => b.addEventListener("click", () => {
      b.setAttribute("aria-pressed", b.getAttribute("aria-pressed") === "true" ? "false" : "true");
      aplicar();
    }));
    verMas.addEventListener("click", () => {
      completa = !completa;
      aplicar();
      if (!completa) crono.scrollIntoView({ behavior: menosMovimiento ? "auto" : "smooth", block: "start" });
    });
    aplicar();
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
