# Nono — Cronología de la Ley 27.795

**Sección:** 02 — `#ley`. **Archivos propios:** `data/eventos/ley.yaml`, `app/templates/_seccion_ley.html`, `eje_ley` en `core/ejes.py`, CSV nuevos `data/ley_*.csv`. **Rama:** `nono/cronologia-ley`. **ADR:** `0030`–`0034`.

Leer antes: [`docs/ESTANDAR.md`](../ESTANDAR.md), ADR 0014 y 0018.

## Estado actual

- 15 hitos, del veto de 2024 (antecedente) a la multa del 14-oct-2026, y un evento de estado («Dónde está hoy»).
- **Todos los hitos son fuente secundaria**: se basan en una copia de la ley publicada por un tercero, en el informe de ACIJ y en la prensa.
- 33 notas de unos 20 medios, con los títulos tal como se publicaron.

## Tareas

### 1. Pasar los hitos a fuente primaria
Reemplazar en cada evento `documento`, `url`, `pagina` y `tipo_fuente: primaria` cuando se consiga el original:
- [ ] Ley 27.795 en el Boletín Oficial (21-oct-2025).
- [ ] Decreto 647/2025, el veto (Boletín Oficial, 10-sep-2025).
- [ ] Decreto 759/2025, la promulgación con suspensión (Boletín Oficial, 21-oct-2025). Verificar si cita la «Ley 24.629» o la 24.156: la copia que usamos dice 24.629, posible errata.
- [ ] Votaciones: sanción en el Senado (21-ago-2025), insistencia en Diputados (17-sep-2025) e insistencia en el Senado (2-oct-2025), desde los sitios de cada cámara.
- [ ] Resoluciones judiciales del expediente 39475/2025 («CIN y otros c/ EN - PEN - Dto 759/2025 s/ Amparo»): cautelar del 23-dic-2025, Cámara del 31-mar-2026, recurso concedido del 7-may-2026, Corte Suprema del 25-jun-2026, intimación, sentencia de fondo del 6-oct-2026 y multa del 14-oct-2026. Buscar en el sitio del Poder Judicial (CIJ) o en el del CIN.

### 2. Verificar datos dudosos
- [ ] Insistencia en Diputados: el resultado 174-67-2 sale de una sola fuente (La Voz de San Justo). Confirmar con la Cámara.
- [ ] Intimaciones: Perfil informa una del ~22-sep-2026 y Minutouno, otra del 30-sep-2026. Confirmar si son dos y cargar ambas.
- [ ] Fecha exacta en que el juez suspendió la ejecución de la cautelar mientras estaba el recurso extraordinario.

### 3. Completar la cobertura de prensa
- [ ] El hito de la Cámara (31-mar-2026) no tiene noticias.
- [ ] Revisar que cada hito tenga al menos dos medios de líneas editoriales distintas.
- [ ] Títulos tal como se publicaron: tomar el `og:title` de la página de la nota (sin el sufijo con el nombre del medio).

### 4. Seguimiento (mantener al día)
- [ ] Resolución de la Cámara sobre la apelación de la sentencia de fondo.
- [ ] Apelación de la multa diaria.
- [ ] Actualizar el evento de estado (`estado-ley-27795-…`) cada vez que cambie la situación: se reemplaza por uno nuevo con la fecha del día.

### 5. Coordinar
- [ ] El art. 8 de la ley asigna a la AGN el control de las universidades. Acordar con Tero si se carga como evento con `ejes: [ley, control]` y en qué archivo.
- [ ] El acuerdo salarial del 10-jun-2026 aparece en `ley.yaml` y en `salario.yaml` (instructivo). Mantener ambos consistentes.

## Avances

_(Completar a medida que se avanza: qué se hizo, con qué fuente y en qué commit.)_

## Propuestas de presentación

_(Anotar acá, sin implementarlas, las ideas que requerirían cambiar el estándar.)_
