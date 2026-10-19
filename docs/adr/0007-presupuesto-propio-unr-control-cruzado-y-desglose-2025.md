# 0007. Presupuesto propio de la UNR: control cruzado en todos los años y desglose solo en 2025

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

https://transparencia.unr.edu.ar/presupuesto/ publica las "Resoluciones distribución presupuestaria" de 2020 a 2025 (embebidas con EmbedPress) y un informe de ejecución con gráficos interactivos. El CLAUDE.md lo daba por no encontrado.

## Decisión

- **Control cruzado (todos los años):** el total de cada resolución se carga como Dato propio (`entidad: UNR`, documento: resolución de distribución) y se compara contra el crédito asignado del anexo de la ley del mismo año. La diferencia se muestra con las dos fichas, sin interpretarla. Así se cubren 2022, 2024 y 2025, que no tienen anexo.
- **Desglose interno (solo 2025):** distribución por dependencia (facultad) e inciso (personal, bienes de consumo, servicios, etc.). Si sobra tiempo, se extiende a otros años.

## Consecuencias

- El modelo agrega dos dimensiones de desglose: `dependencia` e `inciso`.
- Falta confirmar que las resoluciones traen el anexo con montos. Si solo traen el texto, el desglose no es posible y se registra un Evento de estado.
- Falta extraer las URL directas de los PDF embebidos.
- Probablemente aparezca la diferencia entre fuentes de financiamiento: el anexo de la ley es Tesoro Nacional y la resolución puede incluir recursos propios.

## Actualización (2026-10-19): el desglose pasa a 2023

Se abrieron las resoluciones (URL directas en https://transparencia.unr.edu.ar/wp-content/uploads/):

| Ejercicio | Resolución | Contenido |
|---|---|---|
| 2020 | `2024/10/RCS-621-19-2.pdf` | Escaneada (7 páginas, sin texto). Falta transcribir |
| 2021 | `2025/12/RCS-433-20.pdf` | Escaneada (10 páginas, sin texto). Falta transcribir |
| 2022 | `2024/10/CS-003-2022_firmado.pdf` | Solo homologa la Res. Rector 5679/2021; **no incluye anexo** |
| 2023 | `2025/12/CS-1016-22.pdf` (Res. C.S. 1016/2022) | Texto, más el Anexo I (presupuesto por rubro) y el Anexo II (gastos de funcionamiento por facultad y escuela), escaneados en las páginas 4 a 13 |
| 2024 | `2025/12/CS-405-23-2.pdf` (Res. C.S. 405/2023) | Prorroga el presupuesto 2023 (Res. C.S. 1016/2023), **sin montos** |
| 2025 | `2024/10/res-cs-721-2025.pdf` (Res. C.S. 721/2025, homologa la Res. Rector 8011/2024) | Prorroga el presupuesto 2024, **sin montos** |

**Decisión:** el desglose se hace sobre **2023**, porque los ejercicios 2024 y 2025 rigen ese mismo presupuesto prorrogado. En la interfaz se rotula: "2024 y 2025: rige el presupuesto 2023 prorrogado (Res. C.S. 405/2023 y 721/2025)". Cada prórroga es un Evento.

**Control cruzado verificado:** la Res. C.S. 1016/2022 cita textualmente "$34.259.832.336" para la UNR y "$752.482.394.720" para el conjunto del sistema (Ley 27.701). Ambos valores coinciden con el anexo de la ley sembrado en `data/`.

El Anexo I (página 4) trae, por ejemplo, Personal $31.432.794.131,80 (de los cuales Inciso 1: $31.053.340.986,00) sobre un total de $34.259.832.336,00. La transcripción se hace leyendo las imágenes y verificando que cada rubro sume su subtotal.

La ejecución presupuestaria está en un tablero SIU-Wichi (Pentaho) embebido en la página de presupuesto. Evaluarlo aparte.
