# 0019. Una sola página con secciones desplegables y estética de vidrio translúcido

- Estado: aceptada
- Fecha: 2026-10-19
- Reemplaza: ADR 0016 (una página por eje). Mantiene los ejes fijos del ADR 0017.

## Decisión

- **Una sola página (`/`)** con toda la información y poco texto. Cada eje es una «cápsula»: cerrada muestra número de orden, título, pregunta y dato clave; al tocarla se despliega con animación (`<details>` exclusivo, `::details-content` con `interpolate-size`). Las direcciones `/salario`, `/ley`, `/transferencias`, `/control` y `/graduacion` redirigen (301) a `/#eje` y abren esa sección.
- **Estética: transparencia como material.** Capas de vidrio esmerilado (`backdrop-filter`) sobre auras suaves y animadas con los tonos de la UNR (magenta, lila, celeste), a baja opacidad para no generar choque visual. Hay modo claro y oscuro. El rojo queda reservado para la brecha del art. 5.
- **Microinteracciones** (`app/static/interacciones.js`):
  - las cifras cuentan desde 0 al aparecer o al abrir su sección;
  - los bloques aparecen con un fundido al hacer scroll;
  - las líneas del gráfico se dibujan al abrir Salario;
  - un brillo sigue al cursor sobre el vidrio;
  - la navegación abre y desplaza hasta la sección.
- **Accesibilidad:** con «reducir movimiento» no hay animaciones. Sin JavaScript todo el contenido se ve, porque el fundido solo se aplica con la clase `js`. Las secciones se abren con teclado.
- **Lo que se mantiene:** cada número abre su ficha y el artículo de Salario queda en un desplegable «¿De dónde sale este número?».

## Actualización (2026-10-19): paleta de papel y tinta

- Las auras de colores se reemplazan por papel crema (#f2efe4, #ebe7d8) con una cuadrícula tenue, tinta azul marino (#141b34) y paneles crema translúcidos. La transparencia se mantiene en los paneles, que dejan ver la cuadrícula. En modo oscuro se invierte: fondo azul marino y tinta crema. Referencia: https://jcc.tera.ar/.
- El acento pasa a ser el azul marino; el rojo queda solo para la brecha del art. 5. Las series del gráfico se validaron contra el nuevo fondo: el naranja queda en 2,78:1 sobre crema y se compensa con su rótulo directo.
- La cronología de la Ley 27.795 pasa a ser vertical, de lo más reciente a lo más antiguo, con el año como separador.

## Actualización (2026-10-19): nombre, landing continua y cronología filtrable

- **Nombre del sitio: «UNR Transparente».** Siempre acompañado de «sitio independiente» en la barra y en el pie, para que no se confunda con un sitio oficial de la universidad.
- **Sin tarjetas.** El contenido es parte de la página, como en la referencia: secciones numeradas («01 — Salario docente») separadas por una línea fina; los datos van en una fila separada por líneas verticales, sin recuadros. Lo secundario (artículo de Salario, detalle de transferencias) queda detrás de un «ver más».
- **La motivación va justo después de la portada,** antes de los datos.
- **Cronología de la ley:**
  - filtros por actor (Congreso, Poder Ejecutivo, Justicia, Acuerdo), que se pueden combinar;
  - muestra los 4 hechos más recientes y un botón «Ver N hechos anteriores»;
  - cada hecho entra con una animación escalonada al aparecer en pantalla, y el detalle se despliega con transición;
  - los años sin hechos visibles se ocultan al filtrar;
  - sin JavaScript, se ve la cronología completa.
