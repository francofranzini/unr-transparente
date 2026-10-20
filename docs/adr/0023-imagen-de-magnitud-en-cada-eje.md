# 0023. Cada eje muestra la magnitud con una imagen que se entiende de un vistazo y se puede verificar

- Estado: aceptada (pedido de Fran; a ratificar por el equipo)
- Fecha: 2026-10-19
- Generaliza: ADR 0022 (fajos en Transferencias). Modifica: `ESTANDAR.md` (nueva sección «Imagen de magnitud»).

## Contexto

Las pilas de fajos de Transferencias funcionaron: la diferencia entre lo que correspondía y lo que se transfirió se ve antes de leer un número. El equipo decidió que todo el sitio siga ese criterio: el dato tiene que entrar por los ojos y, a la vez, poder verificarse en cualquier momento.

## Decisión

Cada eje con una cifra central tiene una **imagen de magnitud** que cumple estas reglas:

1. **Proporcional.** La imagen es una transformación directa del dato, sin exagerar (fajos: altura proporcional; calendario: días = 30 × salario real). Si hay redondeo, la ficha muestra el valor exacto.
2. **Verificable.** Junto a la imagen va la cifra que la genera, y esa cifra abre su ficha (documento, página, cálculo, vigencia). Si la imagen cambia con un selector, cada estado tiene su propia cifra con ficha.
3. **Rojo = lo que falta según la Ley 27.795, solo desde que la ley rige** para ese dato. Antes, la misma brecha se muestra en gris (`--tenue`) y se rotula como referencia. No se usa el rojo para otra cosa.
4. **Animación con sentido**: muestra cómo se llega al dato (los fajos se apilan, los días se llenan) y se repite al cambiar de vista. Con «reducir movimiento», todo queda quieto. Sin JavaScript se ve el estado final.
5. **Celular**: lo que se compara queda lado a lado.
6. **Sin adjetivos**: la imagen produce el impacto; el texto describe.

## Salario: el calendario

- «Con el sueldo de {mes} se compra lo que en noviembre de 2023 alcanzaba para N días»: N = 30 × (básico del mes ÷ IPC del mes) ÷ (básico de nov-2023 ÷ IPC de nov-2023), en días completos. Agosto de 2026: 22,49 → 22 días; los otros 8, en rojo.
- Base noviembre de 2023: es el sueldo de partida del art. 5. Los días sin cubrir van en **rojo solo desde noviembre de 2025** y en gris antes (ver la corrección de abajo).
- Deslizador de noviembre de 2023 al último mes con IPC; cada mes es una cifra con ficha (`dias-AAAA-MM`, `faltan-AAAA-MM`) y lleva el aviso de vigencia si la escala no está publicada.
- «Un mes de 30 días» es una forma de leer la proporción, no un supuesto de gasto: la ficha dice el cálculo.

## Corrección (2026-10-19): la ley no rige hacia atrás mes a mes

La Ley 27.795 se publicó el 21-oct-2025. Cada artículo fija su alcance en el tiempo, y no es el mismo:

- **Art. 5 (salarios):** manda **un aumento** igual al IPC del 1-dic-2023 a la sanción, «efectivo al mes siguiente de la publicación» (**noviembre de 2025**), y desde ahí actualizaciones mensuales no inferiores a la inflación. **No** obliga a pagar cada mes desde diciembre de 2023. Por eso:
  - el gráfico de Salario muestra «Exige la ley» solo desde noviembre de 2025; antes, el sueldo de noviembre de 2023 ajustado por IPC es una **referencia** (línea punteada) y el tooltip dice «La ley todavía no regía». Está marcada la publicación. El gráfico se dibuja en `_seccion_salario.html` (el viejo `_grafico_salario.html`, congelado, ya no se incluye);
  - el calendario usa gris para los días sin cubrir antes de noviembre de 2025 («pérdida de poder de compra») y rojo desde entonces («lo que falta según la ley»);
  - la brecha de 33,4 % (agosto de 2026) no cambia: es posterior a noviembre de 2025.
- **Arts. 3 y 4 (funcionamiento):** el texto sí es retroactivo («desde el 1º de enero hasta el 31 de diciembre de 2025»). Lo correcto es «lo que la ley manda reconocer **por** 2025», no «lo que correspondía en enero». Como los aumentos se toman a cuenta, la comparación que fija la ley es el total del año; el acumulado mensual es una reconstrucción y así se rotula.
- Que la ley rija está además en disputa (Dec. 759/2025, sentencia del 6-oct-2026 y apelación); se usa la fecha de publicación y se enlazan ambos hechos.
