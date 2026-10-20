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
3. **Rojo = lo que falta según la Ley 27.795.** No se usa para otra cosa.
4. **Animación con sentido**: muestra cómo se llega al dato (los fajos se apilan, los días se llenan) y se repite al cambiar de vista. Con «reducir movimiento», todo queda quieto. Sin JavaScript se ve el estado final.
5. **Celular**: lo que se compara queda lado a lado.
6. **Sin adjetivos**: la imagen produce el impacto; el texto describe.

## Salario: el calendario

- «Con el sueldo de {mes} se compra lo que en noviembre de 2023 alcanzaba para N días»: N = 30 × (básico del mes ÷ IPC del mes) ÷ (básico de nov-2023 ÷ IPC de nov-2023), en días completos. Agosto de 2026: 22,49 → 22 días; los otros 8, en rojo.
- Base noviembre de 2023: es el sueldo de partida del art. 5 (lo que la ley manda recuperar), así que los días en rojo son lo que falta según la ley.
- Deslizador de noviembre de 2023 al último mes con IPC; cada mes es una cifra con ficha (`dias-AAAA-MM`, `faltan-AAAA-MM`) y lleva el aviso de vigencia si la escala no está publicada.
- «Un mes de 30 días» es una forma de leer la proporción, no un supuesto de gasto: la ficha dice el cálculo.
