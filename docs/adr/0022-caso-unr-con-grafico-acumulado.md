# 0022. El caso de la UNR en Transferencias: bloque propio y gráfico acumulado con selector

- Estado: aceptada (pedido de Fran; a ratificar por el equipo al integrar)
- Fecha: 2026-10-19
- Modifica: `ESTANDAR.md` §4 (componentes), que no preveía un segundo gráfico.

## Contexto

Con el alcance nacional (ADR 0021), la cifra principal de la sección 03 es la del sistema (47,8 %). El caso de la UNR (73,3 %) quedaba como una nota al pie, y es donde se ve la diferencia entre universidades.

## Decisión

- Dentro de la sección 03, debajo de la fila del sistema, un bloque «El caso de la UNR» con su propia fila de datos (brecha de la UNR como `dato-grande`, exigido, recibido y el valor de todo el sistema para comparar).
- Un **gráfico acumulado de 2025**, mes a mes: lo exigido por los arts. 3 y 4 (serie naranja, `exigido`) contra lo devengado (serie azul, `pagado`), con el espacio entre ambas sombreado con el mismo naranja al 14 %. No se usa rojo (reservado al art. 5).
- **Interacción:** selector «UNR / Todas las universidades» (botones `.actor` de la cronología, `aria-pressed`) y cruz con tooltip por mes, como en el gráfico de Salario. Cada vista tiene su propio eje: se comparan formas y brechas, no montos.
- **Accesibilidad:** rótulos directos al final de cada línea, leyenda, y una tabla «Ver los números mes a mes» con cada valor enlazado a su ficha. Sin JavaScript se ve la UNR y la tabla con ambos.
- El SVG se calcula en la plantilla de la sección (`_seccion_transferencias.html`) a partir de `eje.detalle["acumulado"]`, sin tocar `app/graficos.py` ni `estilo.css`. Única regla nueva: el sombreado (`fill-opacity` en línea).

## Consecuencias

- Lo exigido por mes es la mitad del bimestre (`lentes.meses_art4`); el acumulado de diciembre coincide con el total anual (test).
- Si el equipo adopta el patrón, conviene mover la geometría a `app/graficos.py` y la regla del sombreado a `estilo.css`.

## Actualización (2026-10-19): «correspondían» y textos cortos

- **Verbo:** «según la ley, correspondían», no «la ley exigía». La ley es de octubre de 2025 y manda actualizar desde enero de ese año; antes de la sanción no exigía nada, y la exigibilidad está en disputa (Dec. 759/2025, sentencia del 6-oct-2026 y apelación). Debajo de la cifra se enlazan ambos eventos.
- **Gráfico:** líneas punteadas en la sanción (21-ago-2025) y la publicación (21-oct-2025).
- **Artículo:** la explicación es una cuenta de cinco renglones; el resto va en desplegables de una pregunta (`.mas`).
- **Fichas:** rótulos de una línea, cálculo en una frase, nota única por archivo. El detalle por fuente de financiamiento y la cantidad de universidades pasan a columnas (`fuentes_financiamiento`, `universidades`), que no se muestran en la ficha.
