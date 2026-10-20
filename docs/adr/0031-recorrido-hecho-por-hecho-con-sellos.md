# 0031. Cronología de la ley: título, recorrido hecho por hecho y sellos

- Estado: propuesta (Nono). Se adopta si el equipo la aprueba al integrar la rama `nono/cronologia-ley`, junto con el ADR 0030.
- Fecha: 2026-10-19
- Modifica: `docs/ESTANDAR.md` §2 (composición) y §3 (cronología de la ley).

## Contexto

Con 19 hechos, la lista con scroll propio (ADR 0030) sirve para buscar, pero no para contar la historia. Se pidió poder pasar los hechos de a uno, como en un carrusel, y marcar con un sello los momentos en que cambia el estado de la ley (por ejemplo, «VETADA»).

## Decisión

- La cronología lleva un título propio, **«Línea de tiempo»**, con la guía «De lo más antiguo a lo más reciente: del veto de 2024 a hoy.»
- Un botón **«Recorrer hecho por hecho»** cambia la lista por un recorrido de a un hecho, con «Anterior», «Siguiente» y el contador «Hecho N de M». Funciona también con las flechas del teclado y respeta los filtros por actor. «Ver toda la lista» vuelve a la lista.
- En el recorrido, algunos hechos muestran un **sello** que se estampa al aparecer. Los sellos:
  - **nombran el acto, no lo califican** («Vetada», «Es ley», «Cautelar firme», «Inconstitucional»), con un detalle que evita leerlos fuera de contexto («Suspensión del Dto. 759/2025 · 1.ª instancia»);
  - **se reparten entre los actores**: Congreso (sanción, veto rechazado, es ley), Poder Ejecutivo (vetada, promulgada y suspendida, apelada), Justicia (cautelar admitida, suspendida, firme, inconstitucional, multa diaria) y Acuerdo;
  - **no llevan cifras**, porque toda cifra va con su ficha;
  - toman el **color del actor** del hecho; no se agregan colores y el rojo sigue reservado para la brecha del art. 5;
  - se definen en `SELLOS_LEY`, en `core/ejes.py` (`eje_ley`), por id de evento. Si un id no existe en `ley.yaml`, `eje_ley` da error y los tests fallan.
- Accesibilidad: el sello es decorativo (`aria-hidden`), porque el título del hecho ya dice lo mismo. El contador se anuncia (`aria-live`). Con «reducir movimiento» el sello aparece sin animación. Sin JavaScript, los controles no se muestran y se ve la lista completa.

## Consecuencias

- Archivos congelados que se tocan: `_cronologia_ley.html` (título, controles, sellos), `estilo.css` (`.cronologia-titulo`, `.recorrido-*`, `.sello`, animaciones `estampar` y `golpe`) e `interacciones.js` (modo recorrido).
- `tests/test_app.py` verifica que los controles nacen ocultos y que cada sello corresponde a un evento existente.
- Para agregar un sello a un hecho nuevo, se suma su id a `SELLOS_LEY` con el mismo criterio: describir el acto y mantener el reparto entre actores.
