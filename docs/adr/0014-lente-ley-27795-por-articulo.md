# 0014. Lente "Ley 27.795": lo que exige cada artículo contra lo que salió, solo para la UNR

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

La Ley 27.795 de Financiamiento de la Educación Universitaria y Recomposición del Salario Docente (sancionada el 21-ago-2025, vetada por el Dec. 647/2025, confirmada el 2-oct-2025, publicada en el BO el 21-oct-2025 y suspendida en su ejecución por el Dec. 759/2025) fija obligaciones calculables con el IPC del INDEC y las actividades del Programa 26.

Texto consultado: https://www.consejosalta.org.ar/wp-content/uploads/Ley-27.795-y-Dec-759-2025.pdf (copia de un tercero). **Pendiente:** cargar la fuente primaria del Boletín Oficial.

## Decisión

Se crea una lente por artículo, calculada solo para la UNR y solo con Datos que tienen ficha:

| Artículo | "Correspondería" | "Salió" | Datos |
|---|---|---|---|
| Art. 3 | Actividades 14, 15, 16 y 25 del Programa 26, actualizadas al 1-ene-2025 por el IPC may-2024 → dic-2024 | Crédito vigente / devengado 2025 de esas actividades | Presupuesto Abierto 2024 y 2025 (`subparcial_desc` = UNR) + IPC |
| Art. 4 | Las mismas actividades, actualizadas bimestralmente por IPC durante 2025 (los aumentos otorgados se toman a cuenta) | Devengado 2025 por bimestre | Presupuesto Abierto mensual 2025 + IPC |
| Art. 5 | Salario del cargo testigo, aumentado al menos por el IPC entre el 1-dic-2023 y la fecha de corte | Salario efectivamente vigente | Escalas de la UNR + IPC |

- **Parámetro `fecha_corte_art5`:** `2025-08-21` (sanción; por defecto), `2025-10-02` (confirmación) o `2025-10-21` (publicación). Las tres se muestran siempre.
- El art. 6 (becas) queda fuera de alcance porque no es un dato de la UNR. El art. 8 (control por la AGN) se vincula al eje de Control.
- **Estimaciones de costo total de terceros** (OPC $1,96 billones a precios de 2024; Poder Ejecutivo ~$2,5 billones según la prensa; CIEN ~$3,1 billones; ACIJ ~$3,4 billones; CIN ~$7,2 billones de necesidad 2026): se muestran como Datos `secundaria`, cada uno con su método, sin elegir uno.
- El estado de la ley es una línea de tiempo de Eventos: sanción, veto, insistencias, promulgación con suspensión, cautelar del 23-dic-2025, Cámara del 31-mar-2026, suspensión de la cautelar por el recurso extraordinario, fallo del 6-oct-2026 que declara inconstitucional el Dec. 759/2025, y Corte Suprema pendiente.
- "Reproducí el titular" recorre las tres fechas de corte. Caso de prueba: la recomposición del 33,4 % que reclaman los gremios.

## Consecuencias

- Hay que descargar Presupuesto Abierto 2024 y 2025 (anual y mensual), además del 2026 ya verificado.
- Hay que verificar en el BO el texto del Dec. 759/2025: la copia consultada menciona la "Ley 24.629", posible errata por la 24.156.
