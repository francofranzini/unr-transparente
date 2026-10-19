# 0012. "Ejecutado": transferencias de la Nación (principal) y ejecución propia de la UNR (segundo nivel)

- Estado: aceptada
- Fecha: 2026-10-19

## Decisión

- **Indicador principal del eje "asignado contra ejecutado":** crédito presupuestado, vigente y devengado de las transferencias del Programa 26 a la UNR.
- **Segundo nivel:** la ejecución propia de la UNR (tablero SIU-Wichi de transparencia.unr.edu.ar), solo si permite exportar los datos. Si no, se registra un Evento de estado.

## Verificación de la fuente (2026-10-19)

Datos abiertos de Presupuesto Abierto, crédito anual 2026: https://dgsiaf-repo.mecon.gob.ar/repository/pa/datasets/2026/credito-anual-2026.zip. El archivo tiene la leyenda "Última actualización del ejercicio 2026: 16 Octubre 2026". También existe `credito-mensual-2026.zip`, con apertura mensual.

- **Filtro:** `programa_desc` = "Desarrollo de la Educacion Superior" y `parcial_desc` empieza con "Transferencias a universidades nacionales". El valor de `subparcial_desc` identifica a la universidad (62 valores: 61 universidades más "Universidades sin Discriminar").
- **Ojo:** el `programa_id` 26 se repite en otras subjurisdicciones del Ministerio de Capital Humano (p. ej. "Prestacion Alimentar"). Hay que filtrar por descripción o por subjurisdicción, nunca solo por id.
- **Unidad:** millones de pesos. Fuente de financiamiento: Tesoro Nacional.
- **UNR, 2026:** presupuestado 237.298,391675 · vigente 237.298,391675 · devengado 208.839,493671 (millones). El presupuestado **coincide exactamente** con el anexo de la ley sembrado en `data/` (237.298.391.675).
- **Desglose de la UNR por actividad:** salario docente, salario no docente, funcionamiento, hospitales, ciencia y técnica, FUNDAR.

## Hallazgo a resolver (siguiente pregunta)

Las 61 universidades tienen vigente = presupuestado. Todo el aumento del crédito vigente del sistema está en **"Universidades sin Discriminar"**: presupuestado 149.439,4, vigente 1.457.463,7 y devengado 0 (millones). Por eso el cociente devengado/vigente del sistema (68,9 %) depende de si se incluye esa línea.
