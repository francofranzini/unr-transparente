# 0024. Identidad: un monitor del financiamiento universitario con una lente declarada, la Ley 27.795

- Estado: aceptada (propuesta de Fran; a ratificar por el equipo)
- Fecha: 2026-10-20
- Modifica: la tesis del `CLAUDE.md` §1 («el portal no elige una lente»). Complementa: ADR 0015 (eje central), 0021 (alcance nacional), 0023 (imagen de magnitud).

## Contexto

La tesis original era no elegir lente: mostrar que las cifras contradictorias salen de los mismos datos con supuestos distintos. En la práctica, el sitio se ordenó alrededor de una: lo que exige la Ley 27.795. Eso lo vuelve útil y deseable para quienes siguen el conflicto, pero puede convertirlo en un carrusel que solo funciona mientras existe el reclamo. La pregunta es qué pasa si la ley se aplica, se modifica o se resuelve en la Corte.

## Decisión

**Oración de identidad:**

> Un monitor público del financiamiento universitario, medido contra la Ley 27.795: qué dice la ley, qué transfiere la Nación y qué hacen las universidades con eso, con la fuente de cada número y actualizado a medida que avanza el conflicto.

1. **La lente se conserva y se declara.** La Ley 27.795 es la referencia central, y se dice así en la portada y en cada eje. Las demás elecciones metodológicas (inflación, año base, etapa presupuestaria, alcance) siguen a la vista y, donde se pueda, se pueden cambiar. «Reproducí el titular» sigue siendo el lugar donde se comparan las otras lentes.
2. **El diferencial es seguir el conflicto.** Los gráficos son variables: suman períodos (2026, 2027…) y estados de la ley a medida que hay datos o hechos nuevos. No son una foto.
3. **Reglas para extender un gráfico a un período nuevo:**
   - Si la ley fija qué corresponde en ese período, se calcula y lo que falta va en rojo (ADR 0023).
   - Si no lo fija (los arts. 3 y 4 solo regulan 2025), no se inventa un «exigido». Se muestra lo transferido y, como mucho, una **referencia** en gris (por ejemplo, lo de 2025 ajustado por inflación), rotulada como tal.
   - Si aparece una norma o una sentencia que fija un monto (presupuesto 2027, orden judicial), se carga como Evento y pasa a ser la referencia, con su ficha.
   - Cada eje muestra el **estado de la ley a la fecha del dato**: suspendida, rige y se cumple, o rige y no se cumple.
4. **Que funcione si la brecha se cierra.** Las imágenes de magnitud muestran mejoras con el mismo lenguaje: el calendario se llena hasta 30, las pilas se igualan. Si la ley se cumple, el sitio lo dice con el mismo énfasis.
5. **El nombre se mantiene** («Universidad Transparente»). La parte «qué hacen las universidades con eso» (control, graduación, costo por estudiante) es parte de la identidad y queda como deuda: hoy está menos desarrollada que la parte de la ley.

## Consecuencias

- Cambian el `CLAUDE.md` §1, el `ESTANDAR.md` §2 y la bajada de la portada (archivo congelado: por eso este ADR). La bajada dice solo lo que el sitio ya cumple: «Qué dice la Ley 27.795 de financiamiento universitario y qué pasó en realidad, con la fuente de cada número».
- Para poder decir «actualizado a medida que avanza el conflicto», hace falta el vigía de fuentes (ADR 0010) y una forma de cargar los períodos nuevos sin rehacer cada gráfico.
- Primer candidato: Transferencias 2026, con lo transferido y una referencia en gris, más el estado de la ley.
