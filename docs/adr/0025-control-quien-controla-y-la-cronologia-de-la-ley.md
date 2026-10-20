# 0025. Control: quién controla a la UNR, plegado debajo de la pregunta, y la cronología de la ley sin sellos

- Estado: propuesta. Se adopta si el equipo la aprueba al integrar la rama `tero/auditorias`.
- Fecha: 2026-10-20
- Extiende: ADR 0030 y 0031 (cronología de la ley) a la sección Control.

## Contexto

La sección Control mostraba el recuadro del último control externo con todo su texto y una línea de tiempo simple, distinta de la de la ley (sin filtros, de lo más reciente a lo más antiguo, con «Ver N hechos anteriores»). Se pidió que lo de debajo de la pregunta explique quién controla a la UNR en lugar de repetir un hecho de la cronología, que no se vea completo de entrada, y que la cronología de auditorías sea igual a la de la ley.

## Decisión

- **Sin el recuadro «Último control externo publicado»**: repetía el hito del informe AGN 161/2022, que ya está en la línea de tiempo.
- **Debajo de la pregunta, en un desplegable** cuyo rótulo cambia de «Ver más» a «Ver menos» al abrirlo (solo CSS: funciona sin JavaScript): el texto del equipo sobre la autonomía y autarquía de las universidades (art. 75, inc. 19, de la Constitución) y quién las audita: la AGN, creada por la Ley 24.156 (art. 116, control externo, asiste al Congreso), y la SIGEN (art. 96, control interno del Poder Ejecutivo). La Constitución y la ley enlazan a InfoLEG. Sin cifras.
- **Cronología común.** La cronología de la ley pasa a una macro, `cronologia(...)` en `app/templates/_cronologia.html`, que usan las dos secciones: orden cronológico, recuadro con scroll, filtros y recorrido hecho por hecho. La sección de la ley se genera igual que antes.
- **Una cronología por universidad.** Bajo el título «Línea de tiempo», cada universidad tiene su recuadro desplegable («Universidad Nacional de Rosario (UNR) · 9 hechos desde 2021»), abierto por defecto, con su cronología adentro y una nota: algunos hechos (dictámenes de la Procuración, convenios del CIN) alcanzan a todas las universidades. Hoy solo está la UNR; para sumar otra se cargan sus hechos en `data/eventos/control_<sigla>.yaml` con `ejes: [control-<sigla>]` y se agrega a `UNIVERSIDADES_CONTROL`. Es la única excepción a «sin tarjetas» del estándar: un borde fino, sin fondo, para separar universidades.
- **Paso suave entre hechos (Control y ley).** En el recorrido, el hecho actual sale deslizándose hacia un lado, el nuevo entra desde el otro y el recuadro acompaña el cambio de alto (unos 0,45 s; los clics durante la animación se ignoran). En la ley, el sello se estampa cuando el hecho terminó de entrar, para que las dos animaciones no se pisen. Se activa con `transicion=True` en la macro (`data-transicion`). Con «reducir movimiento» el cambio es inmediato.
- **Actores de Control.** No se agregan colores: cada órgano toma el del poder del que depende. AGN, azul (Congreso); SIGEN y Procuración del Tesoro, naranja (Poder Ejecutivo); auditoría interna de la UNR, verde; convenios del CIN, amarillo. Se definen en `ACTORES_CONTROL` y `FILTROS_CONTROL` (`eje_control`); un evento sin actor es un error.
- **Sin sellos en Control.** Los sellos del recorrido son solo de la sección de la ley (ADR 0031); la macro los muestra únicamente si se le pasan.
- El evento de estado (informes individuales de la UAI no publicados) no va en la cronología; su ficha sigue disponible en `/ficha/evento/estado-uai-informes-individuales`.

## Consecuencias

- Archivos congelados que se tocan: `_cronologia_ley.html` (ahora llama a la macro), `_cronologia.html` (nuevo) y `estilo.css` (`.universidad`, el recuadro por universidad; `.si-cerrado` / `.si-abierto` para el rótulo «Ver más» / «Ver menos»; `.presentacion`: ancho de lectura del desplegable y espacio antes de la cronología; sin sellos, el recorrido no reserva su lugar). `interacciones.js`: ya manejaba cualquier `[data-cronologia]`; suma el paso suave para las que tienen `data-transicion` (animaciones `salir-*` y `entrar-*` en `estilo.css`).
- La línea de tiempo simple (`linea_tiempo` en `_macros.html`) queda sin uso en Control.
- Tests: hay un recuadro por universidad con su cronología adentro; la cronología de Control respeta el orden de los eventos, todo hecho tiene actor y no hay sellos; el texto va debajo de la pregunta, plegado, con el rótulo «Ver más» / «Ver menos», y no hay recuadro repetido.
