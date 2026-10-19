# 0001. Ampliar el modelo para reproducir las tres afirmaciones de prueba

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

El criterio de aceptación exige analizar las tres afirmaciones de la sección 1 del CLAUDE.md (Gobierno, Analytica y CEPA). Con los datos sembrados (crédito asignado de la UNR y del sistema para 2021, 2023 y 2026), ninguna se puede reproducir: aluden a la función educación, a la educación superior, al año 2025 y al PBI.

## Decisión

Se amplía el modelo en lugar de recortar el criterio:

- Se agregan las entidades `ESTADO_NACIONAL` (función educación y cultura) y `PROGRAMA_26`, con crédito inicial 2025 y 2026 tomado del proyecto de ley de presupuesto 2026 (primaria).
- Para el total del sistema en 2025 se usa el crédito vigente desde Presupuesto Abierto (CSV), rotulado `credito_vigente`.
- Los supuestos de terceros (p. ej. inflación del 26 % de Analytica) se guardan como Dato `secundaria`, `indicador: inflacion_supuesta`, y se muestran como supuesto ajeno.
- El PBI nominal 2026 se toma del supuesto macro del proyecto de ley 2026.

## Consecuencias

- Hay más carga manual de datos antes de la demo.
- El motor tiene que distinguir supuestos oficiales de supuestos ajenos.
- Pasan a convivir conceptos distintos (asignado y vigente) en una misma comparación (ver la siguiente decisión).
