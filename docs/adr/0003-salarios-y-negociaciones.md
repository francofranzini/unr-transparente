# 0003. Incluir salarios docentes (cargo testigo) y la negociación presupuestaria

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

Además del presupuesto, la discusión pública gira en torno a dos cosas: la pérdida de poder adquisitivo del salario docente y la secuencia política alrededor del financiamiento (ley de financiamiento universitario, veto, insistencia del Congreso, suspensión, refuerzos para gastos de funcionamiento).

## Decisión

1. **Salarios (A).** Una serie mensual del salario bruto de un **cargo testigo**, comparada contra el IPC. Fuente: grillas de COAD (https://coad.org.ar/salarios/), en PDF, de 2021 a oct-2026. Se cargan como `secundaria` hasta encontrar la resolución oficial o el acta paritaria.
2. **Negociaciones (B).** Hitos con ficha (Boletín Oficial, votaciones, actas del CIN) en la línea de tiempo de la sección Control, que además se marcan sobre el gráfico de Plata.

## Consecuencias

- Nueva entidad `CARGO_TESTIGO` y nuevo indicador `salario_bruto`.
- Nuevo tipo de registro **Evento**, separado de Dato, porque no es una cifra.
- El índice de COAD tiene huecos: faltan ene-feb y jul-sep de 2026, 2024 aparece por semestres y 2021-2023 por años. Hay que definir cómo se tratan (siguiente pregunta).

## Actualización (2026-10-19)

El portal de transparencia de la UNR publica escalas salariales oficiales 2023-2026 (Docente, NoDocente y "Superior", en carpetas de Google Drive): https://transparencia.unr.edu.ar/escalas-salariales/. Para 2023 en adelante son **fuente primaria** y reemplazan a COAD. COAD queda como fuente secundaria para 2021-2022 y como respaldo.
