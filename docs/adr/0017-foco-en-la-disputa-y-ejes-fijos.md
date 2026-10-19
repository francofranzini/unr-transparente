# 0017. Foco en la disputa Universidades–Nación; ejes fijos que se actualizan de a uno

- Estado: aceptada
- Fecha: 2026-10-19
- Modifica: ADR 0007 (desglose interno) y ADR 0012 (segundo nivel: ejecución propia de la UNR).

## Decisión

- **Fuera de foco por ahora:** en qué gasta internamente la UNR. Esto incluye el desglose por rubro y por facultad (ADR 0007) y la ejecución propia del tablero SIU-Wichi (ADR 0012). Los datos ya transcritos (`data/unr_presupuesto_2023_*.csv`) quedan versionados, pero no se muestran.
- **Ejes fijos:** salario, Ley 27.795, transferencias, control y graduación. No se agregan ejes nuevos; cada uno se actualiza de a uno.
- **Cada página de eje termina con un artículo "De dónde sale cada dato":** fuentes con enlace, cómo se calcula cada número y qué no incluye. Las cantidades que menciona (meses con grilla, último IPC, meses sin grilla) se calculan desde `data/`, para que el texto no quede desactualizado.

## Excepción (2026-10-19)

La página `/ley` no lleva artículo: a pedido del equipo, la cronología se explica sola. La procedencia de cada hecho está en el enlace «De dónde sale este dato» de cada hito y del recuadro «Dónde está hoy».
