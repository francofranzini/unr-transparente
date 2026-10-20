# 0020. Arts. 3 y 4 de la Ley 27.795: devengado, monto de partida y alcance del sistema

- Estado: aceptada
- Fecha: 2026-10-19
- Relacionado: ADR 0014 (lente por artículo), 0015 (eje central), 0021 (alcance nacional).

## Contexto

Los arts. 3 y 4 de la Ley 27.795 mandan actualizar «el monto de los gastos de funcionamiento» de las actividades 14, 15, 16 y 25 del Programa 26: al 1-ene-2025 por el IPC del 1-may-2024 al 31-dic-2024 (art. 3) y de forma bimestral durante 2025, tomando a cuenta los aumentos otorgados (art. 4). La ley no dice de qué mes es «el monto».

En 2024 y 2025 rigió el presupuesto 2023 prorrogado: el crédito vigente de cada universidad no cambió y los aumentos se pagaron por fuera. El crédito no sirve como «lo que salió».

## Decisión

- **Lo transferido** es el devengado de Presupuesto Abierto (crédito mensual), actividades 14, 15, 16 y 25, todas las fuentes de financiamiento (en 2024 hay «Tesoro Nacional» y «Crédito Interno»).
- **Alcance (ADR 0021):** la cifra principal es la suma de todas las universidades nacionales. La UNR se calcula igual y se muestra como caso de detalle. «Universidades sin Discriminar» va aparte; en estas actividades tuvo devengado 0 en 2024 y 2025, así que no cambia la cuenta (si deja de ser 0, hay que revisar esta decisión).
- **Monto de partida, opción A (principal):** el devengado mensual de **septiembre de 2024**, cuando el monto del sistema ya es estable tras el aumento de mediados de 2024 (agosto y septiembre iguales; octubre y noviembre difieren menos del 1 %). Para la UNR da lo mismo que julio: el monto es igual de julio a noviembre. Mismo criterio que el art. 5: el último nivel vigente antes del período que actualiza la ley.
- **Opción B (visible al lado):** promedio mensual de los 12 meses de 2024.
- **Fórmula:** exigido 2025 = Σ por bimestre de partida × 2 × (IPC dic-24 ÷ IPC abr-24) × (IPC del último mes del bimestre anterior ÷ IPC dic-24); el primer bimestre usa diciembre de 2024. Se compara contra el devengado de todo 2025, porque los aumentos se toman a cuenta.
- **2026:** los arts. 3 y 4 no fijan fórmula; se muestra lo transferido sin un «exigido».

## Resultado al 2026-10-19

| | Exigido 2025 | Transferido 2025 | La ley exigía |
|---|---|---|---|
| Sistema, opción A | 606.157 M | 410.017 M | 47,8 % más |
| Sistema, opción B | 521.196 M | 410.017 M | 27,1 % más |
| UNR, opción A | 27.267 M | 15.733 M | 73,3 % más |

## Consecuencias

- Datos: `data/presupuesto_sistema_mensual_AAAA.csv` y `data/presupuesto_unr_mensual_AAAA.csv` (2024-2026), generados con `scripts/extraer_presupuesto_abierto_mensual.py`.
- El cálculo exploratorio previo de la opción B (≈ 20.400 M para la UNR) omitía la actividad 25; con ella da 20.702 M.

## Actualización (2026-10-19): fuente oficial y fuera el presupuesto

- **Texto de la ley:** se cita el Boletín Oficial del 21-oct-2025 (https://www.boletinoficial.gob.ar/detalleAviso/primera/333139/20251021). Los arts. 3 y 4 coinciden palabra por palabra con la copia del Consejo Profesional de Salta usada antes.
- **Dec. 759/2025** (https://www.boletinoficial.gob.ar/detalleAviso/primera/333140/20251021): promulga la ley «sin perjuicio de lo dispuesto por el artículo 5° de la Ley N° 24.629». La cita a la Ley 24.629 (normas complementarias para la ejecución del presupuesto) es correcta: no es una errata por la 24.156, como sospechaba el ADR 0014.
- **El presupuesto queda fuera de la sección:** se parte de la ley, y el presupuesto es lo que no la incluye. Se quita el desplegable «¿Cuánto del presupuesto 2026 llegó…?». Las cifras de crédito se siguen calculando en `eje_ejecucion` porque las usan tests existentes (ESTANDAR §1: no se borran tests).
