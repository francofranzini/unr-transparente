# Tero — Auditorías y control

**Sección:** 04 — `#control`. **Archivos propios:** `data/eventos/control.yaml`, CSV nuevos `data/control_*.csv`, `app/templates/_seccion_control.html`, `eje_control` en `core/ejes.py`. **Rama:** `tero/auditorias`. **ADR:** `0025`–`0029`.

Leer antes: [`docs/ESTANDAR.md`](../ESTANDAR.md) y el ADR 0005 (qué se muestra de cada auditoría).

## Estado actual

- 10 eventos en `control.yaml`, casi todos tomados del **resumen de la Unidad de Auditoría Interna (UAI) de la UNR 2019-2024**: https://transparencia.unr.edu.ar/wp-content/uploads/2025/11/RESUMEN-INFORME-UAI-2019_2024.pdf
- La sección muestra el último control externo (informe AGN 161/2022, sobre el ejercicio 2017) y una línea de tiempo simple.
- Ningún informe de auditoría está cargado con su contenido: solo sabemos que existen.

## Formato de cada auditoría (ADR 0005)

Por cada informe: un evento con órgano, objeto auditado, período auditado, fecha y URL; **tipo de dictamen tal como figura**; **cantidad de observaciones** (como `Dato` con página, en `data/control_*.csv`); y la **cita literal** de la conclusión con su página. Nada de resúmenes propios. Si no se encuentra un documento, se carga un evento de `estado` con dónde se buscó y cuándo.

## Tareas

### 1. Control externo (AGN)
- [ ] Ubicar el informe AGN 161/2022 en https://www.agn.gob.ar y cargar dictamen, observaciones y conclusión.
- [ ] Buscar otros informes de la AGN sobre la UNR (el antecedente de 2009 está citado en un proyecto de Diputados: https://www3.hcdn.gob.ar/dependencias/dcomisiones/periodo-128/128-105.pdf).
- [ ] Convenio CIN–AGN del 07-ago-2024: texto original.
- [ ] Art. 8 de la Ley 27.795 (la AGN controla a las universidades y remite los informes al Congreso): acordar con Nono cómo se carga, por ejemplo como evento con `ejes: [ley, control]`.

### 2. Control interno (SIGEN y UAI)
- [ ] Informes SIGEN IF-2021-70799304-APN-GCSS#SIGEN e IF-2022-50136522-APN-GCSS#SIGEN. Son expedientes GDE: intentar obtenerlos; si no, evento de `estado`.
- [ ] Resolución SIGEN 299/2023 (Boletín Oficial) y Convenio Marco CIN–SIGEN del 08-sep-2023.
- [ ] Dictámenes de la Procuración del Tesoro del 28-nov-2022 y del 15-oct-2024 (IF-2024-112489009-APN-PTN): textos originales.
- [ ] Plan de auditorías de la SIGEN sobre las 61 universidades (iProfesional, 28-jun-2026) y cualquier auditoría de la SIGEN a la UNR en 2025-2026.

### 3. Unidad de Auditoría Interna de la UNR
- [ ] El resumen 2019-2024 dice «89 informes» en el texto, pero su tabla suma 95. Consultar a la UAI cuál es correcto (hoy se muestran ambos).
- [ ] Pedir los informes individuales por el [formulario de acceso a la información](https://transparencia.unr.edu.ar/formulario-informacion/) y registrar el pedido como evento de `estado` (fecha del pedido, número de trámite).
- [ ] Cargar como `Dato` los informes por año (2019: 21, 2020: 10, 2021: 14, 2022: 18, 2023: 20, 2024: 12) con la página del resumen, para que se muestren con ficha.

### 4. Noticias
- [ ] Los eventos de control pueden llevar `noticias` (igual que los de la ley), pero la línea de tiempo simple de esta sección **no las muestra**. Cargarlas igual, y anotar en «Propuestas» si conviene usar en Control el mismo componente que la cronología de la ley.

## Avances

**2026-10-20** (ADR 0025, propuesta)
- Se quitó el recuadro «Último control externo publicado»: repetía el hito del informe AGN, que está en la línea de tiempo.
- Debajo de la pregunta, un desplegable «Ver más» / «Ver menos» con el texto del equipo: autonomía y autarquía de las universidades (art. 75, inc. 19, de la Constitución) y quién las audita (AGN, Ley 24.156, y SIGEN), con enlaces a InfoLEG.
- La línea de tiempo de Control usa la misma cronología que la ley (macro `_cronologia.html`): orden cronológico, scroll propio, filtros por órgano y recorrido hecho por hecho (`ACTORES_CONTROL` y `FILTROS_CONTROL` en `eje_control`). Sin sellos: son solo de la sección de la ley.
- La línea de tiempo va dentro de un recuadro desplegable «Universidad Nacional de Rosario (UNR)». Para sumar otra universidad: sus hechos en `data/eventos/control_<sigla>.yaml` con `ejes: [control-<sigla>]` y una línea en `UNIVERSIDADES_CONTROL` (`core/ejes.py`).
- Para cada evento nuevo de `control.yaml`: si su id no empieza con `agn`, `sigen`, `ptn` o `uai` (ni es un `convenio`), sumar su actor en `_actor_control`.

## Propuestas de presentación

- **ADR 0025 (implementada en la rama, pendiente de aprobación):** quién controla a la UNR, plegado debajo de la pregunta, y la cronología de la ley (sin sellos) en Control. Toca `_cronologia_ley.html`, `_cronologia.html` (nuevo) y `estilo.css`.
