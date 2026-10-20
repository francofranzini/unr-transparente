# 0024. Identidad: un monitor del financiamiento universitario con una lente declarada, la Ley 27.795

- Estado: aceptada (propuesta de Fran; a ratificar por el equipo)
- Fecha: 2026-10-20
- Modifica: la tesis del `CLAUDE.md` §1 («el portal no elige una lente»). Complementa: ADR 0015 (eje central), 0021 (alcance nacional), 0023 (imagen de magnitud).

## Contexto

La tesis original era no elegir lente: mostrar que las cifras contradictorias salen de los mismos datos con supuestos distintos. En la práctica, el sitio se ordenó alrededor de una: lo que exige la Ley 27.795. Eso lo vuelve útil y deseable para quienes siguen el conflicto, pero puede convertirlo en un carrusel que solo funciona mientras existe el reclamo. La pregunta es qué pasa si la ley se aplica, se modifica o se resuelve en la Corte.

## Decisión

**Oración de identidad:**

> Un monitor del financiamiento universitario frente a la Ley 27.795, con la fuente de cada número.

Lo que la oración no dice va en el sitio: qué transfiere la Nación, qué hacen las universidades con eso y que se actualiza a medida que avanza el conflicto.

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

- Cambian el `CLAUDE.md` §1, el `ESTANDAR.md` §2 y la bajada de la portada (archivo congelado: por eso este ADR). La bajada dice: «Qué dice la Ley 27.795 de financiamiento universitario y qué pasó en realidad, con la fuente de cada número».
- Para poder decir «actualizado a medida que avanza el conflicto», hace falta el vigía de fuentes (ADR 0010) y una forma de cargar los períodos nuevos sin rehacer cada gráfico.
- Primer candidato: Transferencias 2026, con lo transferido y una referencia en gris, más el estado de la ley.

## Primera aplicación (2026-10-20): Transferencias 2026

- Selector «Año: 2025 / 2026» junto a «Ver: Todas / UNR». 2025 sigue como antes (lo que la ley manda reconocer; brecha en rojo).
- 2026: **referencia en gris y punteada** = la regla del art. 4 (partida de septiembre de 2024 × IPC del art. 3 × IPC al inicio de cada bimestre) extendida a 2026, rotulada «la ley no lo fija» (`lentes.referencia_art4`). Ventana: enero a septiembre de 2026, el último mes completo con referencia. Todas las universidades −34,7 %; UNR −52,0 %. La cifra no va en rojo.
- El texto de 2026 enlaza el estado de la ley a octubre de 2026. El título de la sección pasa a «¿Reciben las universidades lo que les corresponde por ley?», para que valga en cualquier año.
- Al publicarse un mes nuevo de Presupuesto Abierto y del IPC, la ventana se extiende sola.

## Actualización (2026-10-20): el piso como referencia de 2026 y los hechos del conflicto en el gráfico

- La referencia de 2026 pasa a ser el **piso de diciembre de 2025**: el monto mensual que el art. 4 fija para noviembre-diciembre de 2025, sin actualizar. Es la lectura más cercana a la ley, porque solo supone que lo que la ley ordenó para 2025 no se pierde. Enero a septiembre de 2026: todas −24,2 %; UNR −44,3 %. «Seguir actualizando por inflación» (−34,7 %; −52,0 %) queda en el desplegable «¿Y 2026?».
- El gráfico marca hechos del conflicto con su ficha: en 2025, sanción y publicación; en 2026, el acuerdo del 10 de junio (según la cobertura, un 20 % más para funcionamiento desde junio) y la sentencia de fondo del 6 de octubre.
- Queda fuera (se decidió no hacerlo por ahora): mostrar como cifra principal de 2026 la deuda de 2025 sin pagar.

## Actualización (2026-10-20): revisión de lo que no encajaba con la lente

- **La ley rige.** La Justicia confirmó varias veces que la suspensión del Dec. 759/2025 no vale; el rojo se mantiene sin matices.
- **Portada** (archivo congelado): «No te decimos qué pensar» era de la tesis vieja (no elegir lente). Pasa a «Lo que manda la ley, lo que llegó y la diferencia.» y «Medimos contra la Ley 27.795. Tocá cualquier número para ver el documento y la cuenta de donde sale.»
- **Control (04):** «¿Quién audita a la UNR?» pasa a «¿Quién audita a las universidades?», con un **historial de auditorías** de lo más antiguo a lo más reciente, en el mismo recuadro que la cronología de la ley (ADR 0030) y con el órgano de cada hecho (AGN · Congreso, SIGEN y Procuración · Poder Ejecutivo, convenios, auditoría interna de la UNR).
- **«Reproducí el titular» queda fuera** del proyecto. El punto 1 de este ADR deja de remitir a esa función; las otras lentes se explican en los desplegables de cada eje.
- **Transferencias:** «¿De dónde sale este número?» sigue la selección (Todas/UNR × 2025/2026): la cuenta, los desplegables y las tablas son los del número que se está viendo. La UNR tiene ahora los mismos detalles que el sistema (bimestres, mes a mes).
- Se dejan como están: el título de Transferencias para 2026, la cobertura de la lente (arts. 3, 4 y 5 son un recorte de lo que se presenta) y el peso visual de las mejoras.
