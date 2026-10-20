# 0030. Cronología de la ley: de lo más antiguo a lo más reciente, en un recuadro con scroll propio

- Estado: propuesta (Nono). Se adopta si el equipo la aprueba al integrar la rama `nono/cronologia-ley`.
- Fecha: 2026-10-19
- Modifica: ADR 0019 (cronología con 4 hechos y «Ver N hechos anteriores») y `docs/ESTANDAR.md` §3.

## Contexto

La cronología se mostraba de lo más reciente a lo más antiguo, con 4 hechos visibles y un botón para ver el resto. Con 15 hechos, al desplegarla ocupaba buena parte de la página: para llegar a Transferencias o Control había que recorrerla entera. Además, la historia de la ley se entiende mejor en el orden en que ocurrió (sanción → veto → insistencias → promulgación con suspensión → Justicia).

## Decisión

- Los hechos van **de lo más antiguo (arriba) a lo más reciente (abajo)**.
- La lista vive en un **recuadro con scroll propio** (`.cronologia-scroll`, alto máximo `min(60vh, 36rem)`): la página sigue de largo y la cronología se recorre adentro. Se muestran todos los hechos; desaparece el botón «Ver N hechos anteriores».
- El **año queda fijo arriba** del recuadro mientras se recorren sus hechos.
- Una línea guía sobre el recuadro: «De lo más antiguo a lo más reciente. Desplazate dentro del recuadro para llegar a hoy.» El estado actual sigue arriba, en «Dónde está hoy».
- Los filtros por actor no cambian; al cambiar un filtro el recuadro vuelve al principio.
- Accesibilidad: el recuadro es una región con nombre y foco de teclado (`tabindex="0"`), así que se desplaza con las flechas. Sin JavaScript se ve todo y el scroll funciona igual (es CSS).

## Consecuencias

- Archivos congelados que se tocan: `_cronologia_ley.html`, `estilo.css` (se agregan `.cronologia-guia` y `.cronologia-scroll`, `.anio` pasa a `sticky`, se quita `.ver-mas` y el antecedente de 2024 usa el mismo círculo lleno que los demás hechos: lo distingue el rótulo «Antecedente») e `interacciones.js` (sin límite de hechos; la entrada escalonada usa grupos de 4).
- `tests/test_app.py` verifica el orden cronológico.
- Mientras el puntero está sobre el recuadro, la rueda del mouse lo desplaza a él; al llegar al final, sigue la página. Por eso el alto máximo es menor que la pantalla.
