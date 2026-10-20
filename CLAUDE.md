# CLAUDE.md — Portal de transparencia de la Universidad Pública

> Contexto para el agente que construye este proyecto en una hackatón (temática: Universidad Pública).
> Leer completo antes de escribir código. Lo marcado **[POR DEFINIR]** lo decide el equipo; si falta una decisión, preguntar en vez de suponer.
>
> **Estándar del sitio:** [`docs/ESTANDAR.md`](docs/ESTANDAR.md) fija la estética y las funcionalidades; es la base de cualquier modificación y no se cambia sin acuerdo del equipo y un ADR. El trabajo en curso está dividido en [`docs/tareas/`](docs/tareas/README.md).
>
> **Documentos relacionados:** `CONTEXT.md` es el glosario del dominio; usar esos términos en el código y en la interfaz. `docs/adr/` registra las decisiones tomadas y su porqué. Si este archivo y un ADR se contradicen, vale el ADR más reciente.

## 1. Qué es

> **Un monitor del financiamiento universitario frente a la Ley 27.795, con la fuente de cada número** (ADR 0024).

Alcance: **el sistema universitario nacional**; la Universidad Nacional de Rosario (UNR) queda como caso de detalle (ADR 0021). Se basa en **documentos oficiales** y está pensado para cualquier ciudadano, no solo para estudiantes.

**Tesis del producto:** el ruido sobre el financiamiento universitario no viene de datos distintos, sino de **elecciones metodológicas ocultas**: qué inflación se usa, contra qué año se compara, si se mide lo asignado o lo ejecutado, y si la cifra es de "educación", "educación superior" o "universidades". El portal **declara su lente, lo que exige la Ley 27.795, y hace explícitas las demás para que se puedan cambiar** (ADR 0024; antes la tesis era no elegir ninguna). El diferencial es seguir el conflicto: los gráficos suman períodos y estados de la ley a medida que hay datos nuevos, y muestran las mejoras con el mismo énfasis que las pérdidas.

Ejemplo real que motiva el proyecto. Las tres cifras salen del mismo presupuesto 2026:

| Quién | Afirmación | Qué mide en realidad |
|---|---|---|
| Gobierno (presentación en Diputados, oct-2025) | Educación +17,6 % nominal, ≈ +7 % real | Función *educación* completa, deflactada con la inflación **proyectada** del presupuesto (10,1 %) |
| Analytica (consultora) | Educación superior −12,8 % real | *Educación superior*, +9,9 % nominal, con una inflación **asumida** del 26 % |
| CEPA | Universidades −7,2 % vs 2025 y −34,3 % vs 2023; 0,47 % del PBI | *Universidades*, con otro deflactor y otro año base |

Las fuentes de estas afirmaciones están en la sección 9.

## 2. Principios no negociables

1. **Ninguna cifra sin ficha.** Cada número que se muestra tiene un registro con su fuente (ver la sección 4). Si un dato no tiene ficha, no se muestra.
2. **Sin adjetivos ni texto editorial.** Ni "recorte brutal" ni "aumento histórico". Se describe: "cayó 12,8 % en términos reales, deflactado con X, contra el año Y".
3. **Mostrar los indicadores que le importan a cada parte.** Evolución real del financiamiento *y* indicadores de eficiencia y control: egresados por ingresante, costo por estudiante, auditorías, ejecución. Si el portal solo muestra lo que le conviene a una de las partes, deja de ser neutral.
4. **Asignado ≠ ejecutado.** Siempre se rotula si la cifra es crédito asignado (ley), crédito vigente o devengado (lo efectivamente transferido).
5. **El atraso de los datos se muestra, no se esconde.** Cada cifra indica el período al que corresponde y la fecha de consulta.
6. **Primaria vs secundaria.** Una cifra tomada de la prensa o de un informe de terceros se marca como *secundaria* y cita a la fuente original que esa nota menciona.
7. **Ningún número sale de un LLM.** Todo número sale de un cálculo sobre datos con ficha.

## 3. Alcance del MVP

**Forma de trabajo (ADR 0017):** los ejes son fijos y se actualizan de a uno. El foco es la disputa Universidades–Nación; en qué gasta internamente la UNR queda fuera por ahora. Cada página de eje termina con un artículo «De dónde sale cada dato».

**Navegación (ADR 0019):** una sola página en `/` («Universidad Transparente», ADR 0021) con secciones numeradas sin tarjetas; `/salario`, `/ley`, etc. redirigen a `/#eje`. Estética de vidrio translúcido sobre auras con los tonos de la UNR.

**Eje central (ADR 0015):** el conflicto Universidades–Nación, medido contra lo que exige la Ley 27.795. La portada muestra la brecha del art. 5 para el cargo testigo y el estado de la ley, con la posición del Poder Ejecutivo.

**Ejes prioritarios de la página de inicio (ADR 0010):** salario docente real respecto de 2023, asignado contra ejecutado, auditorías y graduación (valores absolutos hasta tener ingresantes). Cada eje muestra la fecha de su última revisión.

Cinco secciones, más una función diferencial:

- **Plata:** crédito asignado a la UNR por año, su participación en el total del sistema universitario, y la ejecución cuando exista. Con selector de lente. Incluye el control cruzado entre el anexo de la ley y la resolución de distribución propia de la UNR, y el desglose interno de 2023, que también rige en 2024 y 2025 por prórroga (ADR 0007). Los hitos de la negociación presupuestaria se marcan sobre el gráfico.
- **Salarios:** salario básico del cargo testigo (profesor adjunto, dedicación exclusiva, sin antigüedad), mes a mes, contra el IPC y contra lo que exige el art. 5 de la Ley 27.795, con los eventos paritarios (ADR 0003, 0004 y 0015).
- ~~**Gente:**~~ graduados y alumnos quedaron fuera del sitio (ADR 0024).
- **Ley 27.795:** lo que exige cada artículo (arts. 3, 4 y 5) contra lo que salió, para la UNR; estimaciones de costo de terceros como secundarias; línea de tiempo del estado de la ley (ADR 0014).
- **Control:** quién audita a la universidad (AGN, SIGEN, Unidad de Auditoría Interna) y una línea de tiempo de hechos documentados, incluida la negociación sobre el financiamiento (ADR 0005).
- **Funcionamiento (FCEIA):** concursos docentes, proyectos de investigación y tesinas, a partir de la API de la FCEIA (sección 5.4).
- **Diferencial: seguir el conflicto** (ADR 0024). «Reproducí el titular» quedó fuera del proyecto.

Fuera del MVP: otras universidades en detalle (solo el total del sistema como contexto), ingesta automática de datos (salvo lo verificable de la Ley 27.795, ADR 0036), login, edición por parte de usuarios.

## 4. Modelo de datos

Toda cifra es un registro `Dato`:

```yaml
id: unr-credito-2026-total
valor: 237298391675
unidad: ARS corrientes        # ARS corrientes | personas | porcentaje | índice
entidad: UNR                  # UNR | SISTEMA_UNIVERSITARIO | PROGRAMA_26 | ESTADO_NACIONAL | CARGO_TESTIGO | FCEIA
indicador: credito_asignado   # credito_asignado | credito_vigente | devengado | salario_bruto | inflacion_supuesta | egresados_grado | ...
desglose: total               # total | salud | educacion_cultura | ciencia_tecnica | <dependencia> | <inciso> | ...
periodo: "2026"               # año, o AAAA-MM para series mensuales
vigencia_desde: null          # solo grillas salariales: AAAA-MM desde el que rige (ADR 0004)
tipo_fuente: primaria         # primaria | secundaria
documento: "Universidades Nacionales — Presupuesto 2026 — Distribución de Créditos"
url: https://...
pagina: null                  # página del PDF, si aplica
consultado: 2026-10-19
nota: "Copia del anexo publicada por la UNT; buscar también la publicación oficial."
```

Los hechos sin cifra son registros `Evento` (fecha, tipo, descripción literal y la misma ficha de fuente). Tipos: hitos de negociación (leyes, vetos, decretos, acuerdos del CIN, paritarias), dictámenes, auditorías y **eventos de estado**, que registran la ausencia de información a una fecha ("no se encontraron informes publicados al 2026-10-19"), con las búsquedas realizadas como ficha.

- Almacenamiento: `data/*.csv` (un archivo por indicador) y `data/eventos/*.yaml`, versionados. Un validador en la integración continua (`.github/workflows/validar.yml`) rechaza cualquier fila sin ficha completa. El **vigía de fuentes** (`data/fuentes.yaml` + `scripts/vigia_fuentes.py`) detecta cambios y avisa en el issue `vigia-ley` (ADR 0010 y 0035). La carga es manual, con una excepción: lo verificable de la Ley 27.795 (normas de InfoLEG, votaciones del Senado y notas de prensa que coinciden con un único hito) lo carga `scripts/actualizar_ley.py` cada 3 horas y, si pasan la validación y los tests, se commitea en `main` (ADR 0036). Los hechos que solo cuenta la prensa nunca entran solos.
- Las lentes (sección 5.2) son funciones puras `(serie, parámetros) → serie`, y cada resultado lleva consigo la lista de supuestos aplicados para mostrarlos en pantalla.

## 5. Fuentes

### 5.1 Plata

| Fuente | Qué da | Estado |
|---|---|---|
| Anexo de distribución de créditos de las universidades nacionales (ley de presupuesto, capítulo II) | Crédito por universidad y por función (Salud, Educación y Cultura, Ciencia y Técnica) | 2021, 2023 y 2026 encontrados (ver sección 9). **Falta 2022**. **Verificar 2024 y 2025**: probablemente rigió el presupuesto 2023 prorrogado y no hay anexo nuevo |
| Comentario a la ejecución presupuestaria: universidades nacionales (Cuenta de Inversión) | Ejecutado 2024: transferencias por universidad, ingresos, gastos y resultado de las 61 universidades | Encontrado el de 2024. Buscar otros años |
| Presupuesto Abierto (presupuestoabierto.gob.ar) | Ejecución nacional mensual del programa 26 (Desarrollo de la Educación Superior) | La API requiere registro; también hay datos abiertos descargables en CSV |
| Presupuesto propio de la UNR ("Resoluciones distribución presupuestaria") | Distribución interna por rubro y por facultad | **Encontrado** en https://transparencia.unr.edu.ar/presupuesto/. El único con anexo de montos es **2023** (Res. C.S. 1016/2022, anexos escaneados en las páginas 4-13). 2024 y 2025 prorrogan el de 2023. 2020 y 2021 están escaneados y falta transcribirlos. La ejecución está en un tablero SIU-Wichi embebido. Detalle y URL en el ADR 0007 |
| Proyecto de ley de presupuesto 2026 | Crédito inicial 2025 y 2026 de la función educación y cultura y del programa 26; supuesto macro (inflación 10,1 %, PBI nominal) | Por cargar (ADR 0001) |
| Presupuesto Abierto (CSV) | Crédito vigente 2025 del sistema universitario (año sin ley; rigió 2023 prorrogado) | Por cargar, rotulado `credito_vigente` (ADR 0001 y 0002) |

### 5.2 Lentes (deflactores y bases)

| Lente | Fuente | Detalle |
|---|---|---|
| Nominal | — | Pesos corrientes |
| Real con IPC observado | API de series de tiempo de datos.gob.ar, id `148.3_INIVELNAL_DICI_M_26` (IPC nacional, base dic-2016, mensual) | Verificado: responde sin registro, último dato agosto de 2026. URL: `https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&format=json` |
| Real con inflación presupuestada | Supuesto macro de cada ley de presupuesto | Carga manual, un valor por año (2026: 10,1 %) |
| Real con IPC observado + proyección | IPC observado; los meses faltantes se completan con el REM del BCRA | Supuesto ajeno, rotulado como tal (ADR 0006) |
| Real con supuesto de terceros | P. ej. inflación del 26 % asumida por Analytica | Dato `secundaria`, `indicador: inflacion_supuesta` (ADR 0001) |
| Participación en el sistema | Total general del mismo anexo | No depende de la inflación: es la lente más robusta para comparar años |
| % del PBI | PBI nominal (INDEC, misma API de series) | Solo para totales del sistema |
| Por estudiante | Matrícula del mismo año (sección 5.3) | Solo si hay matrícula del mismo período |
| En salarios | RIPTE (misma API de series) | Opcional |

**Parámetros de cada lente:** año base y **base de precios** (`promedio_anual`, `dic_dic` o `ultimo_mes`). La base de precios, por sí sola, cambia resultados, así que va en la interfaz y en la ficha. Valores por defecto (ADR 0006): `ultimo_mes` para series que incluyen el año en curso (hoy, "a precios de ago-2026"), y `promedio_anual` para comparar años cerrados.

**Etapa presupuestaria:** cada serie de Plata muestra una sola etapa por defecto. Las comparaciones mixtas (p. ej. asignado 2026 contra vigente 2025) están permitidas y siempre llevan advertencia (ADR 0002).

### 5.3 Gente

| Fuente | Estado |
|---|---|
| Síntesis o anuario de estadísticas universitarias de la Secretaría de Políticas Universitarias | Última encontrada: 2021-2022. Tiene atraso, y hay que mostrarlo |
| Datos del rectorado de la UNR | Solo encontrados citados en prensa (fuente **secundaria**). Egresados de grado: 3.043 (2023), 3.380 (2024), 3.419 (2025) |
| UNR en Números (https://transparencia.unr.edu.ar/unr-en-numeros/), "Datos correspondientea al año 2024" | **Primaria.** Alumnos 2024: grado 101.018 · posgrado 7.468 · pregrado y tecnicaturas 3.339 · preuniversitario 3.485 · Escuela de Oficios 1.484 · adultos mayores 1.552. Los valores están en atributos `data-to-value` del HTML (contadores animados). No trae ingresantes ni egresados |
| Ingresantes de la UNR | **[POR DEFINIR]**: hacen falta desde 2016 o 2017 para la tasa de egreso con n = 8. Buscar en el anuario de la SPU o pedirlos al rectorado. (Consulta de Graduados es un buscador individual de títulos, no da totales) |

**Tasa de egreso (ADR 0009):** egresados(t) / ingresantes(t − n), con n = 5, 6 u 8 como parámetro visible. La comparación del mismo año (n = 0) no se muestra en Gente; solo la usa "Reproducí el titular" para reconocer titulares, con la advertencia "compara cohortes distintas". La cohorte real queda como evento de estado (no hay datos públicos).

### 5.3 bis Salarios

| Fuente | Estado |
|---|---|
| Escalas salariales de la UNR, 2023-2026 (Docente, NoDocente, "Superior") | **Primaria.** https://transparencia.unr.edu.ar/escalas-salariales/ (carpetas de Google Drive por mes con los instructivos de liquidación de la SPU). Cargadas en `data/salario_cargo_testigo.csv` (43 meses, ene-2023 a oct-2026; faltan ene-2024, que está confirmado por documento, y jul/ago-2026) |
| Grillas de COAD, 2021 a oct-2026 (universitario y preuniversitario, en PDF) | **Secundaria**, para 2021-2022 y como respaldo. https://coad.org.ar/salarios/ |

Cargo testigo: profesor adjunto, dedicación exclusiva, sin antigüedad, nivel universitario. Salario real respecto de 2023: base promedio 2023 por defecto, con nov-2023 y dic-2023 siempre visibles (ADR 0011). Cada grilla rige hasta la siguiente; no se interpola. Un mes sin grilla muestra la vigente rotulada ("grilla vigente desde jun-2026"). Si no hay un evento paritario que confirme el siguiente cambio, el mes se rotula "vigencia no confirmada" (ADR 0004).

### 5.4 Funcionamiento: API de la FCEIA

`https://fceia-api.ariloc.ar` (documentación en `/docs`, spec en `/openapi.json`, fuentes en `/api/v1/info`). Es de solo lectura y sin autenticación; está curada con IA más revisión manual. **No tiene datos financieros ni de matrícula.**

Endpoints útiles para este portal:
- `GET /api/v1/contests`: concursos docentes (estado, dedicación, departamento)
- `GET /api/v1/research/projects`: proyectos de investigación por año
- `GET /api/v1/theses`: tesinas (fecha de defensa), un indicador indirecto de egreso de la LCC
- `GET /api/v1/teachers`, `GET /api/v1/careers`

Hay que confirmar con el autor de la API que se puede usar, y darle crédito en el portal.

### 5.5 Control

Fuente principal: el resumen de la Unidad de Auditoría Interna (UAI) de la UNR 2019-2024, https://transparencia.unr.edu.ar/wp-content/uploads/2025/11/RESUMEN-INFORME-UAI-2019_2024.pdf. El detalle está en el ADR 0005.

- **Control externo (AGN):** el último informe sobre la UNR es el **161/2022**, referido al ejercicio 2017. Hay un antecedente en 2009 (ambiente de control y ejecución presupuestaria). Convenio CIN–AGN del 07-ago-2024.
- **SIGEN:** informes IF-2021-70799304-APN-GCSS#SIGEN (jul-2021) e IF-2022-50136522-APN-GCSS#SIGEN (jul-2022) sobre el control interno de la UNR.
- **Cronología:** dictamen de la Procuración del Tesoro del 28-nov-2022 (el control interno de la LAF no se aplica a las universidades) → Res. SIGEN 299/2023 (20-jul-2023) → convenio marco CIN–SIGEN del 08-sep-2023, que la UNR no suscribió → Res. UNR 4424/2023 (adopta los manuales de la SIGEN) → dictamen IF-2024-112489009-APN-PTN del 15-oct-2024, que revierte el de 2022.
- **UAI de la UNR:** informes por año (2019-2024): 21, 10, 14, 18, 20 y 12; además, 65 instructivos de trabajo de la SIGEN. El texto del resumen dice "89 informes", pero la tabla suma 95: se muestran ambas cifras con su página. Los informes individuales no están publicados (evento de estado).
- **Qué se muestra de cada auditoría:** metadatos, tipo de dictamen tal como figura en el informe, cantidad de observaciones y cita literal de la conclusión. Ningún resumen propio ni generado por el LLM.

### 5.6 Datos ya verificados (sembrar en `data/`)

| Período | UNR: crédito asignado (total) | Total del sistema | Participación de la UNR |
|---|---|---|---|
| 2021 | 10.541.057.489 | 222.500.294.595 | 4,74 % |
| 2023 | 34.259.832.336 | 752.482.394.720 | 4,55 % |
| 2026 | 237.298.391.675 | 4.785.117.662.765 | 4,96 % |

Desglose por función de la UNR:
- **2021:** Salud 85.569.887 · Educación y Cultura 10.440.013.216 · Ciencia y Técnica 15.474.386
- **2023:** Salud 240.424.308 · Educación y Cultura 33.969.366.224 · Ciencia y Técnica 50.041.804
- **2026:** Salud 333.597.580 · Educación y Cultura 236.720.170.001 · Ciencia, Tecnología e Innovación 244.624.094

Las fuentes están en la sección 9. Antes de la demo, volver a abrir cada PDF y verificar estos valores contra el original.

## 6. "Reproducí el titular" (fuera del proyecto, ADR 0024)

> Se conserva como registro de la idea original; no se implementa.

El usuario pega una afirmación, por ejemplo: *"El presupuesto universitario cayó 30 % desde 2023"*.

1. **El LLM la interpreta** y la convierte en un objeto validado, sin producir ningún número propio:
   ```json
   {"valor_afirmado": -30, "unidad": "porcentaje", "alcance": "universidades|educacion_superior|educacion|UNR",
    "concepto": "asignado|devengado|desconocido", "periodo_desde": "2023", "periodo_hasta": "2026|desconocido",
    "lente": "real|nominal|pbi|desconocida"}
   ```
2. **El motor enumera** todas las combinaciones de lentes y parámetros compatibles con los campos desconocidos, y calcula cada una con datos que tienen ficha.
3. **Resultado:** las combinaciones que reproducen la cifra dentro de una tolerancia (±1 punto porcentual) y las que no. Cada combinación lleva sus **advertencias**:
   - **de alcance:** el alcance de la frase no coincide con el del dato citado, por ejemplo cuando se habla de "universidades" con una cifra de "educación";
   - **de comparación mixta:** compara etapas presupuestarias distintas, por ejemplo asignado 2026 contra vigente 2025 (ADR 0002);
   - **de supuesto ajeno:** usa un parámetro de terceros (inflación del 26 % de Analytica, REM).

   El motor enumera también la etapa presupuestaria, la base de precios y, para la tasa de egreso, el desfase n (incluido n = 0).
4. Si ninguna combinación reproduce la cifra: "No se puede reproducir con los datos oficiales disponibles", junto con lo que faltaría para hacerlo.

La tabla de la sección 1 son los casos de prueba de esta función: las tres afirmaciones tienen que poder analizarse.

## 7. Stack (ADR 0008)

- **Python con FastAPI y Jinja2.** HTMX para la interactividad: el cambio de lente reemplaza solo el gráfico y el clic sobre una cifra abre su ficha.
- **Gráficos con Plotly.** Cada gráfico se acompaña de la lista de supuestos de la lente activa.
- **Pydantic como esquema único** para Dato, Evento y el objeto de la sección 6. Valida `data/` en el build y la salida del LLM.
- **`core/`:** lentes y ejes, sin dependencias web, probados con pytest y valores calculados a mano.
- **Series externas** (IPC, PBI, RIPTE, REM): un script las descarga y las guarda versionadas en `data/` con su fecha de consulta. La demo no depende de APIs en vivo.
- **Despliegue:** local (`uvicorn`) y Vercel (`vercel.json`, `api/index.py`), que vuelve a publicar con cada commit en `main` (ADR 0036).
- **Automatización (ADR 0035 y 0036):** `validar.yml` corre el validador y los tests en cada push y pull request; `vigia.yml` corre la carga automática de la ley cada 3 horas y, los lunes, la verificación de títulos y enlaces. **Como un bot commitea en `main`, hacer `git pull` antes de empezar a trabajar.**

**Cómo correr:**
```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validar_datos.py      # toda fila de data/ con ficha completa
.venv/bin/python -m pytest -q                   # lentes, carga, ejes y app
.venv/bin/uvicorn app.main:app --reload --reload-include '*.yaml' --reload-include '*.csv'   # http://127.0.0.1:8000
```

**Estructura:** `core/modelos.py` (Dato, Evento), `core/carga.py` (lee y valida `data/`), `core/ejes.py` (cada número es una `Cifra` con sus Datos de origen), `app/` (FastAPI, plantillas Jinja + HTMX), `scripts/extraer_presupuesto_abierto.py` (propone filas del Programa 26 por universidad a partir del CSV de Presupuesto Abierto, para revisar antes de versionar), `scripts/vigia_fuentes.py` y `scripts/actualizar_ley.py` (vigía y carga automática de la ley; su estado en `data/vigia/`), `scripts/verificar_enlaces.py` y `scripts/archivar_fuentes.py` (enlaces caídos y copias en la Wayback Machine, en `data/archivo_web.yaml`).

## 8. Criterios de aceptación de la demo

- [ ] Cada cifra en pantalla abre su ficha (documento, URL, período, asignado o ejecutado, primaria o secundaria).
- [ ] Salario y Transferencias se miden contra lo que manda la Ley 27.795, con la selección (Todas/UNR, año) aplicada también a «¿De dónde sale este número?».
- [ ] La serie salarial del cargo testigo se muestra contra el IPC, con la vigencia de cada grilla rotulada.
- [ ] La sección Control muestra la cronología de dictámenes y auditorías, incluidos los eventos de estado.
- [ ] Ningún texto del portal usa adjetivos valorativos.
- [ ] Hay tests de las lentes con valores calculados a mano.

**Guion sugerido (3 minutos):** la cifra de la portada (lo que le falta al sueldo docente para cumplir la ley) → el billete que se achica → las pilas de Transferencias, de todas las universidades a la UNR, de 2025 a 2026 → tocar un número y abrir su ficha y su cuenta → cierre con "medimos contra la ley; cada número muestra de dónde sale".

## 9. Fuentes consultadas

- Presupuesto 2026, distribución de créditos por universidad (copia publicada por la UNT): https://www.unt.edu.ar/wp-content/uploads/2026/03/ANEXO-UNIVERSIDADES.pdf
- Presupuesto 2023, distribución de créditos (copia publicada por la UNDEF): https://undef.edu.ar/wp-content/uploads/2025/06/Anexo-Universidades2023.pdf
- Presupuesto 2021, distribución de créditos (copia publicada por El Tucumano): https://www.eltucumano.com/adjunto/2022/04/22/presupuesto%20universidades%20(1).pdf
- Comentario a la ejecución presupuestaria 2024, universidades nacionales: https://www.argentina.gob.ar/sites/default/files/comentario_universidades_2024.pdf
- API de series de tiempo (IPC): https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&format=json
- Presupuesto Abierto, registro de la API: https://www.presupuestoabierto.gob.ar/sici/api-pac
- Síntesis de Información Universitaria (SPU): https://www.argentina.gob.ar/node/253411
- Egresados de la UNR (secundaria, datos del rectorado): https://www.lacapital.com.ar/la-ciudad/en-alza-crecio-un-22-el-numero-graduados-la-unr-n10260518.html
- Posición del Gobierno sobre el presupuesto 2026 y la ley de financiamiento: https://www.diariodecuyo.com.ar/argentina/presupuesto-2026-el-gobierno-ratifico-que-no-aplicara-la-ley-de-financiamiento-universitario-1792999.html
- Análisis de Analytica: https://www.mdzol.com/dinero/motosierra-el-gasto-publico-que-paso-las-universidades-nacionales-n1408689
- Estimaciones de CEPA: https://www.lavozdesanjusto.com.ar/el-presupuesto-universitario-para-el-2026-sera-el-mas-bajo-en-los-ultimos-20-anos
- Auditorías de la SIGEN: https://www.iprofesional.com/legales/415319-decision-clave-gobierno-javier-milei-permitira-auditar-a-fondo-universidades-publicas
- Ejemplo de presupuesto propio publicado por una universidad (UNRC): https://www.unrc.edu.ar/unrc/transparencia/docs/presupuesto/2025/RR0003-2025-ROVERA.pdf
- Portal de transparencia de la UNR: https://transparencia.unr.edu.ar/ (presupuesto, escalas salariales, auditoría interna, UNR en Números)
- Resumen de la auditoría interna de la UNR 2019-2024: https://transparencia.unr.edu.ar/wp-content/uploads/2025/11/RESUMEN-INFORME-UAI-2019_2024.pdf
- Página de la Unidad de Auditoría Interna de la UNR: https://unr.edu.ar/auditoria-interna/
- Antecedente de una auditoría de la AGN sobre la UNR (proyecto de resolución, Diputados, 2009): https://www3.hcdn.gob.ar/dependencias/dcomisiones/periodo-128/128-105.pdf
- Grillas salariales de COAD: https://coad.org.ar/salarios/
- Plan de auditorías de la SIGEN sobre las 61 universidades (iProfesional, 28-jun-2026): https://www.iprofesional.com/impuestos/415928-uba-maxima-tension-que-contratos-quiere-auditar-sigen-gobierno-javier-milei

## 10. Pendientes **[POR DEFINIR]**

- [x] Stack y despliegue local (ADR 0008).
- [ ] Anexo de distribución 2022. Para 2024 y 2025 se usa el crédito vigente (ADR 0001 y 0002) y el total de la resolución de distribución de la UNR (ADR 0007).
- [ ] Ubicar la fuente oficial de cada anexo; hoy se usan copias publicadas por terceros.
- [x] Anexos de la Res. C.S. 1016/2022 (presupuesto 2023) transcritos a `data/unr_presupuesto_2023_anexo1.csv` y `data/unr_presupuesto_2023_anexo2_facultades.csv`, verificados por `tests/test_presupuesto_unr_2023.py`. Las páginas 9-11 (obras proyectadas) no traen montos.
- [ ] ~~Transcribir los presupuestos internos 2020 y 2021~~: fuera de foco (ADR 0017).
- [ ] ~~Evaluar el tablero SIU-Wichi~~: fuera de foco (ADR 0017).
- [ ] Una fuente primaria para ingresantes (desde 2016) y egresados.
- [ ] Inflación presupuestada de cada año. (Base de precios por defecto: resuelto en el ADR 0006.)
- [ ] Informe 161/2022 de la AGN: ubicar el original en auditoria.gov.ar.
- [ ] Eventos paritarios (actas o anuncios) para confirmar la vigencia de las grillas salariales.
- [ ] Series del REM del BCRA, con la fecha de cada encuesta.
- [x] Presupuesto Abierto 2026 cargado en `data/ejecucion_programa26_2026.csv` (corte 16-oct-2026).
- [ ] Descargar Presupuesto Abierto 2024 y 2025 (anual y mensual) para la lente Ley 27.795 (ADR 0014).
- [x] Vigía de fuentes y carga automática para la Ley 27.795 (ADR 0035 y 0036).
- [ ] Vigía de fuentes para los demás ejes: IPC y Presupuesto Abierto primero (`data/fuentes.yaml` con su `eje`).
- [ ] Habilitar GitHub Actions con permiso de escritura y conectar el repositorio a Vercel (ADR 0036).
- [x] IPC mensual (`data/ipc.csv`, `scripts/descargar_ipc.py`) y grillas del cargo testigo 2023-2026 cargados. La brecha del art. 5 en ago-2026 (33,40 %) reproduce el reclamo gremial.
- [ ] Instructivos de jul-2026 y ago-2026 (no publicados en el portal de la UNR).
- [ ] Lente arts. 3 y 4 (gastos de funcionamiento) para reemplazar "asignado contra ejecutado" (ADR 0015).
- [ ] Texto de la Ley 27.795 y de los Decs. 647/2025 y 759/2025 desde el Boletín Oficial, y textos de las resoluciones judiciales (fuente primaria; ADR 0018).
- [x] Cronología de la ley con cobertura de prensa (ADR 0018). Para actualizarla: agregar el Evento en `data/eventos/ley.yaml` con su ficha y sus `noticias` (títulos tal como se publicaron).
- [ ] Permiso y crédito para la API de la FCEIA.
- [x] Nombre del portal: «Universidad Transparente», siempre con «sitio independiente» (ADR 0019, renombrado en el ADR 0021).
- [ ] Reorientar el contenido de cada sección al sistema universitario nacional; la UNR queda como caso de detalle (ADR 0021).
