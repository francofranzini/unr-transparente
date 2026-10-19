# 0002. Se permiten comparaciones entre etapas presupuestarias, siempre rotuladas

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

En 2024 y 2025 no hubo ley de presupuesto y rigió el de 2023 prorrogado. Para comparar 2026 (crédito asignado) contra 2025 solo existe el crédito vigente o el devengado. Algunas afirmaciones públicas, como el −7,2 % de CEPA, probablemente mezclan etapas.

## Decisión

- La etapa (asignado, vigente o devengado) es una dimensión más que el motor de "Reproducí el titular" combina.
- Toda combinación que compare etapas distintas lleva una advertencia de **comparación mixta** ("compara asignado 2026 con vigente 2025"), con el mismo peso visual que la advertencia de alcance.
- En la sección Plata, cada serie muestra una sola etapa por defecto. La mezcla solo aparece si el usuario la elige explícitamente.

## Consecuencias

- El motor enumera más combinaciones, así que hay que ordenarlas para que la lista no sea ruido.
- El objetivo del portal queda explícito: desarmar las afirmaciones sobre cuánto se asigna, cuánto se ejecuta y cuánto se perdió en poder adquisitivo.
