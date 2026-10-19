# 0005. Auditorías: metadatos, datos categóricos textuales y eventos de estado

- Estado: aceptada
- Fecha: 2026-10-19

## Decisión

Cada informe de auditoría se registra como un Evento con:

- órgano (`AGN`, `SIGEN` o `UAI_UNR`), objeto auditado, período auditado, fecha de emisión y URL;
- tipo de dictamen **tal como figura en el informe**;
- cantidad de observaciones, como Dato con página;
- cita literal de la conclusión, entre comillas y con página.

No hay resúmenes propios ni generados por el LLM (principios 2 y 7).

Cuando no se encuentran informes, se registra un **Evento de estado** ("no se encontraron informes publicados al AAAA-MM-DD"), cuya ficha son las búsquedas realizadas (dónde se buscó y cuándo).

## Hallazgos de la búsqueda inicial (2026-10-19)

- **Unidad de Auditoría Interna de la UNR:** la página https://unr.edu.ar/auditoria-interna/ solo lista autoridades y contacto. El portal https://transparencia.unr.edu.ar/ publica un **resumen de la UAI 2019-2024** (8 páginas; metadatos del PDF: 26-dic-2024): https://transparencia.unr.edu.ar/wp-content/uploads/2025/11/RESUMEN-INFORME-UAI-2019_2024.pdf. Los informes individuales no están publicados, lo que corresponde a un Evento de estado. Datos del resumen:
  - Informes por año (Anexo I): 2019: 21 · 2020: 10 · 2021: 14 · 2022: 18 · 2023: 20 · 2024: 12, con un total de 95. Instructivos de trabajo de la SIGEN: 65. **Inconsistencia interna:** el texto dice "89 informes de auditoría", pero la tabla suma 95. Se muestran ambas cifras con su página y no se elige una.
  - Último informe de la AGN sobre la UNR: **161/2022**, referido al ejercicio 2017.
  - Informes de la SIGEN sobre el control interno de la UNR: IF-2021-70799304-APN-GCSS#SIGEN (jul-2021) e IF-2022-50136522-APN-GCSS#SIGEN (jul-2022), con "95% de cumplimiento" (cita textual).
  - Cronología: dictamen de la Procuración del Tesoro del 28-nov-2022 (art. 100 de la LAF no aplicable a las universidades) → Res. SIGEN 299/2023 (20-jul-2023) → convenio marco CIN–SIGEN del 08-sep-2023, que la UNR no suscribió → Res. UNR 4424/2023 (adopta los manuales de la SIGEN) → convenio CIN–AGN del 07-ago-2024 → dictamen IF-2024-112489009-APN-PTN del 15-oct-2024, que revierte el de 2022.
  - El Anexo II lista las observaciones más frecuentes. Se muestran como cita literal, sin resumir.
- **AGN:** hay un antecedente de una auditoría de la AGN sobre la UNR (ambiente de control y ejecución presupuestaria), referida en un proyecto de resolución de Diputados de dic-2009: https://www3.hcdn.gob.ar/dependencias/dcomisiones/periodo-128/128-105.pdf. Falta el informe original en auditoria.gov.ar.
- **SIGEN:** auditó universidades hasta 2022. Un dictamen de la Procuración del Tesoro de 2022 (Zannini) derivó el control a la AGN, y el de oct-2024 (Barra) habilitó otra vez a la SIGEN. Una nota de Cadena 3 anticipa una auditoría a la UNR "en los próximos meses", sin fecha. Según iProfesional (28-jun-2026), la SIGEN prepara cronogramas para las 61 universidades. No se encontró un informe de la SIGEN sobre la UNR.
- **Prensa:** el rector Bartolacci declaró que la UNR tiene "dos auditorías externas y varios controles internos" (Conclusión; no se pudo abrir la nota, HTTP 403).
- **SISAC:** desde el 31-jul-2023 las unidades de auditoría interna de las universidades dejaron de cargar sus productos en el SISAC de la SIGEN, salvo el informe mensual (resolución de la UNMdP). Esto puede explicar por qué no hay informes publicados.

## Consecuencias

- La sección 5.5 del CLAUDE.md queda incompleta: la frase "la AGN no estaba constituida" hay que contrastarla con el dictamen de 2022 que le asignó el control. Es una secuencia de Eventos que hay que cargar con ficha.
