# Glosario del dominio

Términos acordados para el portal. Si el código o la interfaz usan una palabra distinta para el mismo concepto, se corrige el código, no el glosario.

- **Dato**: registro atómico de una cifra con su ficha (fuente, período, concepto, tipo de fuente). Sin ficha, no hay dato.
- **Ficha**: metadatos de procedencia de un Dato (documento, URL, página, fecha de consulta, nota).
- **Entidad**: a quién corresponde la cifra. Valores: `UNR`, `SISTEMA_UNIVERSITARIO` (total del anexo de distribución), `PROGRAMA_26` (Desarrollo de la Educación Superior), `ESTADO_NACIONAL` (con `desglose` = función, p. ej. `educacion_cultura`), `FCEIA`.
- **Alcance**: la entidad o el agregado del que habla una afirmación (`UNR`, `universidades`, `educacion_superior`, `educacion`). La advertencia de alcance aparece cuando el alcance de la frase no coincide con el del dato que la reproduce.
- **Concepto** (etapa presupuestaria): `credito_asignado` (crédito inicial de la ley), `credito_vigente` (asignado más modificaciones), `devengado` (lo ejecutado).
- **Tipo de fuente**: `primaria` (documento oficial) o `secundaria` (prensa o informe de terceros, que cita su fuente original).
- **Supuesto ajeno**: parámetro que no sale de una fuente oficial, sino de un tercero (p. ej. la inflación del 26 % asumida por Analytica). Se guarda como Dato `secundaria` con `indicador: inflacion_supuesta` y se rotula como tal en pantalla.
- **Lente**: función pura `(serie, parámetros) → serie` que lleva consigo la lista de supuestos aplicados.
- **Comparación mixta**: comparación entre Datos de distinta etapa presupuestaria (p. ej. asignado 2026 contra vigente 2025). Está permitida y siempre se rotula.
- **Advertencia**: aviso que acompaña a un resultado del motor. Tipos: de alcance, de comparación mixta y de supuesto ajeno.
- **Auditoría**: informe de control sobre la universidad, emitido por un órgano externo (SIGEN, AGN) o interno (unidad de auditoría interna de la UNR). Es un hecho documentado con ficha.
- **Cargo testigo**: un único cargo docente de referencia, con dedicación y antigüedad fijas, cuyo salario bruto se sigue mes a mes para medir el poder adquisitivo.
- **Evento**: hecho documentado con fecha y ficha, pero sin cifra (p. ej. veto de la ley de financiamiento, dictamen de la Procuración, publicación de una auditoría). Se muestra en líneas de tiempo, nunca como número.
- **Negociación**: secuencia de Eventos sobre el financiamiento (leyes, vetos, decretos, acuerdos con el CIN) o sobre salarios (paritarias).
- **Vigencia**: período durante el cual rige una grilla salarial, desde `vigencia_desde` hasta la siguiente grilla. Es *confirmada* si un Evento paritario marca el siguiente cambio, y *no confirmada* en caso contrario.
- **Evento de estado**: Evento que registra la *ausencia* de información a una fecha ("no se encontraron informes publicados al 2026-10-19"), con las búsquedas realizadas como ficha.
- **Tipo de dictamen**: calificación de una auditoría tal como figura en el informe (p. ej. "con salvedades"). Se transcribe y nunca se parafrasea.
- **Base de precios**: mes o promedio de precios al que se expresa una serie real: `promedio_anual`, `dic_dic` o `ultimo_mes`.
- **Instructivo de trabajo**: proyecto de auditoría acotado que pide la SIGEN. Se cuenta aparte de los informes de auditoría.
- **Resolución de distribución**: acto de la UNR que reparte su presupuesto entre dependencias e incisos. Es una fuente distinta del anexo de la ley de presupuesto nacional.
- **Inciso**: clasificación del gasto por objeto (1 Personal, 2 Bienes de consumo, 3 Servicios no personales, 4 Bienes de uso, 5 Transferencias).
- **Dependencia**: unidad interna de la UNR (facultad, escuela, rectorado) que recibe una parte del presupuesto.
- **Tasa de egreso con desfase**: egresados(t) / ingresantes(t − n). n es un parámetro visible (5, 6 u 8). No es una tasa por cohorte real.
- **Eje**: pregunta pública que el portal responde, con un indicador principal, una fuente vigilada y una frecuencia de actualización.
- **Vigía de fuentes**: proceso que detecta cambios en las fuentes vigiladas y avisa. No carga datos: la carga es manual y con ficha.
- **Base salarial**: período contra el que se mide el salario real: `promedio_2023` (por defecto), `nov_2023` o `dic_2023`. Las tres se muestran siempre.
- **Crédito no asignado**: crédito vigente del Programa 26 imputado a "Universidades sin Discriminar", es decir, sin universidad de destino. Se muestra aparte y nunca se mezcla en los cocientes por universidad.
- **Lente Ley 27.795**: cálculo, por artículo, de lo que correspondería según la ley, contrastado con lo asignado o devengado. Solo para la UNR, con Datos que tienen ficha.
- **Fecha de corte (art. 5)**: fin del período de IPC que el art. 5 manda compensar: `2025-08-21` (por defecto), `2025-10-02` o `2025-10-21`.
- **Salario exigido (art. 5)**: básico de nov-2023 × IPC(m) / IPC(nov-2023). Es lo que correspondería según la Ley 27.795 en el mes m.
- **Brecha art. 5**: cuánto habría que aumentar el básico pagado para alcanzar el salario exigido, en %.
