# Fran — Presupuesto y transferencias

**Sección:** 03 — `#transferencias`. **Archivos propios:** `data/ejecucion_programa26_*.csv`, `data/credito_asignado_ley.csv`, CSV nuevos `data/presupuesto_*.csv`, `app/templates/_seccion_transferencias.html`, `eje_ejecucion` en `core/ejes.py`, lentes nuevas en `core/lentes.py`. **Rama:** `fran/presupuesto`. **ADR:** `0020`–`0024`.

Leer antes: [`docs/ESTANDAR.md`](../ESTANDAR.md), ADR 0012, 0013, 0014 y 0015.

## Estado actual

- La sección muestra cuánto del crédito vigente 2026 se transfirió a la UNR: 88,0 % al 16-oct-2026, desde Presupuesto Abierto (`data/ejecucion_programa26_2026.csv`).
- Falta lo central para la disputa: **lo que exigen los arts. 3 y 4 de la Ley 27.795 frente a lo transferido.**

## Lo que ya se sabe (para no repetir trabajo)

- Datos abiertos de Presupuesto Abierto, mensuales: `https://dgsiaf-repo.mecon.gob.ar/repository/pa/datasets/<año>/credito-mensual-<año>.zip`. Filtrar por `programa_desc` = «Desarrollo de la Educacion Superior» y `subparcial_desc` = «Universidad Nacional de Rosario». El `programa_id` 26 se repite en otras subjurisdicciones: no filtrar solo por id. Los valores están en millones de pesos.
- En 2024 y 2025 la UNR tuvo **crédito vigente igual al presupuestado** (presupuesto 2023 prorrogado). Los aumentos se pagaron por fuera del crédito asignado a la UNR, a través de «Universidades sin Discriminar». Por eso la comparación con la ley se hace sobre lo **devengado**.
- Funcionamiento (actividad 14), devengado de la UNR en millones: total 2024 = 13.318 (≈283–679 por mes hasta mayo; **1.483 por mes desde junio**, después del aumento de mayo de 2024); total 2025 = 15.135, con montos mensuales irregulares (580 a 2.836).
- Cálculo exploratorio de lo que exigían los arts. 3 y 4 en 2025 (actividades 14, 15 y 16):
  - **Opción A** (monto de partida: nivel mensual vigente desde mayo de 2024): exigido 27.267, transferido 15.733, la ley exigía un **73 % más**.
  - **Opción B** (monto de partida: promedio mensual de todo 2024): exigido ~20.400, la ley exigía un **~31 % más**.
  - Recomendación previa: **A como principal y B visible**, igual que en Salario. Los arts. 3 y 4 no fijan fórmula para 2026: mostrar lo transferido en 2026 como dato, sin inventar un «exigido».

## Tareas

### 1. Decidir y registrar
- [x] Decidir el monto de partida (A o B) con el equipo y registrarlo en un ADR (`0020`).

### 2. Cargar los datos
- [x] Extender `scripts/extraer_presupuesto_abierto.py` (o crear uno nuevo) para la apertura **mensual** por actividad, y generar `data/presupuesto_unr_mensual_2024.csv` y `…_2025.csv` con la ficha completa.
- [x] Volver a extraer 2026 con la última actualización de Presupuesto Abierto (sigue siendo la del 16-oct-2026).

### 3. Calcular
- [x] Agregar en `core/lentes.py` la lente de los arts. 3 y 4: art. 3 (IPC de mayo a diciembre de 2024, al 1-ene-2025) y art. 4 (actualización bimestral por IPC durante 2025, tomando a cuenta los aumentos otorgados).
- [x] Tests con valores calculados a mano en `tests/test_lentes.py`.
- [x] Cifras nuevas en `eje_ejecucion` (`core/ejes.py`), con su cálculo explicado.

### 4. Mostrar (solo con componentes del estándar)
- [x] En `_seccion_transferencias.html`: fila de datos con lo que exigía la ley, lo transferido y la diferencia; la medición alternativa (B) visible; el 88 % frente al presupuesto pasa a segundo plano, dentro de un `mas-info`.
- [x] Un artículo «¿De dónde sale este número?» con pasos (`.articulo` / `.paso`), con el mismo tono que el de Salario.

### 5. Verificar datos existentes
- [ ] `data/credito_asignado_ley.csv`: reverificar contra los PDF los valores de 2021 y 2026 (tienen la nota «reverificar»), y reemplazar las copias de terceros (UNT, El Tucumano) por la publicación oficial.
- [ ] Buscar el acto (decisión administrativa) que creó el crédito vigente de «Universidades sin Discriminar» en 2026 (1,46 billones, con 0 devengado) y cargarlo como evento. Ver si se relaciona con el acuerdo del 10-jun-2026.

## Avances

**2026-10-19**
- Opción A como principal y B visible (ADR 0020). La partida A pasó de julio a **septiembre de 2024**: en el sistema, julio todavía está por debajo del nivel estable; para la UNR da lo mismo.
- Con el cambio de alcance (ADR 0021), la sección muestra **el sistema universitario** y la UNR como caso de detalle.
- Datos: `data/presupuesto_sistema_mensual_{2024,2025,2026}.csv` (actividades 14, 15, 16 y 25, suma de las universidades más «sin asignar» aparte) y `data/presupuesto_unr_mensual_{2024,2025,2026}.csv` (todas las actividades de la UNR). Script: `scripts/extraer_presupuesto_abierto_mensual.py {unr|sistema} …`.
- Resultado 2025, sistema: exigido 606.157 M, transferido 410.017 M → **47,8 % más** (B: 27,1 %). UNR: 27.267 M contra 15.733 M → 73,3 % más.
- «Universidades sin Discriminar» tuvo devengado 0 en estas actividades en 2024 y 2025: la duda sobre si sumarlo no aplica.
- En 2024 parte de las partidas se financió con «Crédito Interno»; se suman todas las fuentes y la nota de cada fila lo detalla.
- El 88 % del presupuesto 2026 pasó a un «ver más», ahora con las 61 universidades primero.

- **El caso de la UNR** tiene bloque propio con gráfico acumulado de 2025 (exigido contra transferido), selector UNR / todas las universidades, tooltip por mes y tabla mes a mes con fichas (ADR 0022). Revisado en claro, oscuro y a 390 px de ancho.

**Pendiente**
- **¿Pagos en 2026 a cuenta de 2025?** Los arts. 3 y 4 mandan reconocer todo 2025, pero la ley se publicó en octubre: parte podría haberse pagado en 2026, fuera de la comparación (que es por ejercicio). Junio (82.265 M) y septiembre de 2026 (122.176 M) casi triplican lo habitual, después de un julio en 0. Buscar en el Boletín Oficial las resoluciones de la Secretaría de Educación o decisiones administrativas de 2026 que asignan fondos de funcionamiento; si alguna es a cuenta de la Ley 27.795 o de 2025, cargarla como evento y recalcular la brecha.
- Tarea 5 (reverificar `credito_asignado_ley.csv` contra los PDF oficiales, y el acto que creó el crédito de «Universidades sin Discriminar» 2026).

## Propuestas de presentación

- **Para Nono (`data/eventos/ley.yaml`):** los eventos de sanción, veto e insistencia del Senado citan la copia del Consejo de Salta; la ley oficial está en el Boletín Oficial (https://www.boletinoficial.gob.ar/detalleAviso/primera/333139/20251021) y el Dec. 759/2025 en https://www.boletinoficial.gob.ar/detalleAviso/primera/333140/20251021.
- **Para Salario (`_articulo_salario.html`):** el enlace a la ley apunta a la misma copia; cambiarlo por el del Boletín Oficial.
- Quitar de `eje_ejecucion` las cifras de crédito y su test si el equipo acuerda que el presupuesto queda fuera del portal.
- **Para Salario (art. 5):** el mismo problema de «exige»: la ley es de octubre de 2025 y actualiza desde diciembre de 2023, con el aumento efectivo «al mes siguiente de la publicación». Revisar el verbo y marcar sanción y publicación en su gráfico, como en Transferencias (ADR 0022).
- Las fichas son legibles si los rótulos, cálculos y notas son cortos; sugerir el mismo criterio a los demás ejes.
- Si se adopta el gráfico del ADR 0022, mover su geometría a `app/graficos.py` y el sombreado a `estilo.css` (archivos congelados).
- Un selector de universidad para la línea de detalle: los datos mensuales por universidad están en Presupuesto Abierto.
