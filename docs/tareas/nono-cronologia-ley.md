# Nono — Cronología de la Ley 27.795

**Sección:** 02 — `#ley`. **Archivos propios:** `data/eventos/ley.yaml`, `app/templates/_seccion_ley.html`, `eje_ley` en `core/ejes.py`, CSV nuevos `data/ley_*.csv`. **Rama:** `nono/cronologia-ley`. **ADR:** `0030`–`0034`.

Leer antes: [`docs/ESTANDAR.md`](../ESTANDAR.md), ADR 0014 y 0018.

## Estado actual

- 19 hitos, del veto de 2024 (antecedente) a la queja admitida por la Cámara el 15-oct-2026, y un evento de estado («Dónde está hoy»).
- **14 hitos con fuente primaria** (Boletín Oficial, actas de votación de las cámaras y textos de las resoluciones judiciales). Quedan 5 secundarios: el acuerdo del 10-jun (falta el acta firmada) y cuatro resoluciones judiciales sin texto disponible: suspensión de la cautelar (24-abr), concesión del recurso extraordinario (7-may), apelación de la sentencia (9-oct) y multa (14-oct).
- 81 notas de 28 medios, todas con el título verificado contra su `og:title` (`scripts/verificar_titulos.py`).

## Tareas

### 1. Pasar los hitos a fuente primaria
Reemplazar en cada evento `documento`, `url`, `pagina` y `tipo_fuente: primaria` cuando se consiga el original:
- [x] Ley 27.795 en el Boletín Oficial (21-oct-2025).
- [x] Decreto 647/2025, el veto (Boletín Oficial, 10-sep-2025).
- [x] Decreto 759/2025, la promulgación con suspensión (Boletín Oficial, 21-oct-2025). Cita la **Ley 24.629** en el art. 1 (no es errata); la 24.156 aparece en los considerandos.
- [x] Votaciones: sanción en el Senado (21-ago-2025), insistencia en Diputados (17-sep-2025) e insistencia en el Senado (2-oct-2025), desde los sitios de cada cámara.
- [ ] Resoluciones judiciales del expediente 39475/2025 — **hecho en parte**: cautelar, Cámara, Corte, 31-ago, sentencia de fondo y 15-oct (copias con firma digital publicadas por Class Actions Argentina, InfoGremiales y Palabras del Derecho; cij.gov.ar y csjn.gov.ar no las tienen). Faltan: 24-abr, 7-may, 9-oct y 14-oct. Diario Judicial publica algunos PDF detrás de un muro de pago. Detalle original: («CIN y otros c/ EN - PEN - Dto 759/2025 s/ Amparo»): cautelar del 23-dic-2025, Cámara del 31-mar-2026, recurso concedido del 7-may-2026, Corte Suprema del 25-jun-2026, intimación, sentencia de fondo del 6-oct-2026 y multa del 14-oct-2026. Buscar en el sitio del Poder Judicial (CIJ) o en el del CIN.

### 2. Verificar datos dudosos
- [x] Insistencia en Diputados: 174-67-2 confirmado en votaciones.hcdn.gob.ar/votacion/5766 (más 14 ausentes).
- [x] Intimaciones: hubo una intimación el 22-sep-2026; el 30-sep el juez rechazó la revocatoria, denegó la apelación y amplió los fundamentos (según la Cámara, 15-oct). Cargadas como dos hitos.
- [x] Fecha exacta en que el juez suspendió la ejecución de la cautelar: 24-abr-2026 (Diario Judicial, secundaria; falta el texto).

### 3. Completar la cobertura de prensa
- [x] El hito de la Cámara (31-mar-2026) no tiene noticias (ahora: Infobae, Página/12, La Capital).
- [x] Revisar que cada hito tenga al menos dos medios de líneas editoriales distintas (salvo el 31-ago, con una sola nota).
- [x] Títulos tal como se publicaron: `scripts/verificar_titulos.py` compara cada título con el `og:title` de la página.

### 4. Seguimiento (mantener al día)
- [ ] Resolución de la Cámara sobre la apelación de la sentencia de fondo.
- [ ] Apelación de la multa diaria. El 15-oct la Cámara concedió la apelación contra la intimación; no dice si suspende las multas (la prensa dice que sí).
- [ ] Actualizar el evento de estado (`estado-ley-27795-…`) cada vez que cambie la situación: se reemplaza por uno nuevo con la fecha del día.
- [x] Vigía de fuentes de la ley (ADR 0032): `data/fuentes.yaml`, `scripts/vigia_fuentes.py` y `.github/workflows/vigia.yml` avisan en el issue `vigia-ley`. Procedimiento para cargar un hecho: en el ADR 0032 y en cada aviso.
- [ ] Diputados (votaciones.hcdn.gob.ar) no se puede vigilar automáticamente (reCAPTCHA): revisar a mano cuando haya sesión sobre la ley.
- [ ] Registrar las copias que faltan en la Wayback Machine (16 notas de prensa): `.venv/bin/python scripts/archivar_fuentes.py --guardar`.

### 5. Coordinar
- [ ] El art. 8 de la ley asigna a la AGN el control de las universidades. Acordar con Tero si se carga como evento con `ejes: [ley, control]` y en qué archivo.
- [ ] Pedir a Fran que habilite GitHub Actions en el repositorio y marque `validar.yml` como obligatorio para fusionar en `main`.
- [ ] Proponer a Fran y Tero sumar sus fuentes a `data/fuentes.yaml` (Presupuesto Abierto, AGN, SIGEN) con su `eje`.
- [x] El acuerdo salarial del 10-jun-2026 aparece en `ley.yaml` y en `salario.yaml` (instructivo). Consistentes: 1.520.087,32 ÷ 1.252.853,64 = +21,33 %.

## Avances

**2026-10-19**
- Fuentes primarias para el veto firme de 2024, sanción, veto, insistencias y promulgación (BO, senado.gob.ar, votaciones.hcdn.gob.ar). Veto firme de 2024: el registro oficial da 160-84-5 (Chequeado había informado 159-85-5); corregido. La nota de la promulgación decía «$ 2 billones para 2026» como costo de la ley: según los decretos, $ 2.008.377.852.000 es solo la recomposición salarial 2026; el costo total estimado es $ 1.069.644.600.000 para 2025. Corregido.
- Hitos judiciales con texto primario: cautelar, Cámara, Corte (la cita anterior no era literal; reemplazada), 31-ago, intimación 22-sep, ampliación 30-sep, sentencia de fondo y queja del 15-oct. Nuevos hitos: 24-abr, 31-ago, 30-sep y 15-oct.
- 48 notas nuevas y 14 fechas completadas; la nota de Perfil del 6-oct pasó de «apelación» a «sentencia de fondo».
- Evento de estado actualizado: multas con efecto en discusión tras el 15-oct.
- Cronología de lo más antiguo a lo más reciente, con scroll propio (ADR 0030, propuesta).

**2026-10-20** (rama `feat/automate-news`, ADR 0032)
- Controles automáticos en cada pull request (`.github/workflows/validar.yml`).
- Reglas de verificación como tests (`tests/test_eventos_ley.py`). Al escribirlas apareció un error: el hito del 30-sep tenía las tres notas del 22-sep y le faltaba la de Minutouno. Corregido.
- «Dónde está hoy · revisado el …», calculado desde el evento de estado.
- Vigía de fuentes con tests sin red (`tests/test_vigia.py`), control de enlaces (`scripts/verificar_enlaces.py`) y copias en la Wayback Machine (`scripts/archivar_fuentes.py`, `data/archivo_web.yaml`: 76 de 92 enlaces, con todas las fichas de los eventos).

**Pendiente detectado**
- Media sanción en Diputados (6-ago-2025, 158-75-5): hoy está en la nota de la sanción; podría ser un hito propio.
- Recusación de los jueces de la Corte (4-jun-2026) y causa acumulada de la UBA (cautelar del 1-sep-2026): sin cargar.
- El 5-ago-2026 la Sala III habría declarado abstracta la apelación del CIN contra la suspensión: falta la fecha exacta.

## Propuestas de presentación

- **Copia archivada en la página (propuesta, no implementada):** cuando el enlace original de una ficha o noticia se cae, mostrar la copia de `data/archivo_web.yaml`. Requiere un campo nuevo en `Ficha` o `Noticia` (`core/modelos.py`, congelado).
- **ADR 0031 (implementada en la rama, pendiente de aprobación):** título «Línea de tiempo», recorrido hecho por hecho con «Anterior»/«Siguiente» y sellos animados que nombran el acto (VETADA, ES LEY, CAUTELAR FIRME…), repartidos entre actores y con el color de cada uno.
- **ADR 0030 (implementada en la rama, pendiente de aprobación):** cronología en orden cronológico dentro de un recuadro con scroll propio, año fijo arriba, sin «Ver N hechos anteriores». Toca `_cronologia_ley.html`, `estilo.css` e `interacciones.js`.
