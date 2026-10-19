# 0006. Base de precios: último mes disponible por defecto; proyección del REM como lente extra

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

Al 2026-10-19, el último IPC publicado es el de ago-2026. Ni el promedio anual de 2026 ni dic-2026 existen todavía, así que la lente "real con IPC observado" no se puede calcular para 2026 con los parámetros previstos.

## Decisión

- El parámetro **base de precios** tiene tres valores: `promedio_anual`, `dic_dic` y `ultimo_mes`.
- Para la serie que incluye el año en curso, el valor por defecto es `ultimo_mes`, rotulado "a precios de ago-2026".
- Para comparar años cerrados, el valor por defecto es `promedio_anual`, porque el crédito se ejecuta a lo largo del año.
- Hay una lente extra, **IPC observado + proyección del REM (BCRA)**, que completa los meses faltantes con las expectativas del mercado, rotuladas como supuesto ajeno.
- "Reproducí el titular" recorre los tres valores de la base de precios.

## Consecuencias

- Resuelve el pendiente "promedio anual o diciembre contra diciembre" de la sección 10 del CLAUDE.md.
- Hay que cargar las series del REM con ficha (fecha de la encuesta).
