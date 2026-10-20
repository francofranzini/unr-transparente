# Estándar de Universidad Transparente

Este documento fija cómo se ve y cómo funciona el sitio. **Es la base de cualquier modificación.** A partir de acá el trabajo es sobre los **contenidos** (datos, eventos, textos), no sobre la presentación.

- Base: el estado de `main` después del commit «Rediseño: UNR Transparente…» y de la separación en archivos por sección (ver `git log`).
- Cambiar algo de este estándar requiere acuerdo del equipo y un ADR nuevo en `docs/adr/`. Nadie cambia la estética ni las funcionalidades por su cuenta.
- Si una tarea de contenido parece necesitar un cambio de presentación, se anota como **propuesta** en el archivo de tareas de quien la detecta y se discute al reunir el trabajo.

## 1. Qué archivos se pueden tocar

| Archivo | Estado | Quién |
|---|---|---|
| `data/**` (CSV y `data/eventos/*.yaml`) | Editable | Cada responsable, en los archivos de su tema |
| `data/eventos/ley.yaml`, `data/vigia/*.yaml`, `data/archivo_web.yaml` | Editable; además los escribe el workflow del vigía cada 3 horas (ADR 0036). A mano se mantienen `data/vigia/claves_ley.yaml` y el `ignorar` de `data/fuentes.yaml` | Responsable del eje ley |
| `app/templates/_seccion_<eje>.html` | Editable **solo el contenido**: textos, qué cifras se muestran, usando los componentes de la sección 4 | Responsable del eje |
| `core/ejes.py` | Editable **solo la función de su eje** (`eje_<eje>`): cifras, supuestos, pendientes | Responsable del eje |
| `core/lentes.py` | Se pueden **agregar** lentes nuevas, con tests calculados a mano. No se cambian las existentes sin acuerdo | Responsable del eje |
| `scripts/` | Se pueden agregar scripts de extracción | Cualquiera |
| `tests/` | Se agregan tests; no se borran ni se relajan los existentes | Cualquiera |
| `docs/tareas/<persona>.md` | Cada uno actualiza el suyo | Cada responsable |
| `CONTEXT.md` | Solo se **agregan** términos al final | Cualquiera |
| `app/static/estilo.css`, `app/static/interacciones.js` | **Congelado** | Nadie, sin acuerdo |
| `app/templates/base.html`, `inicio.html`, `_macros.html`, `_grafico_salario.html`, `_cronologia_ley.html`, `_ficha_*.html`, `pagina_ficha.html` | **Congelado** | Nadie, sin acuerdo |
| `app/main.py`, `app/formato.py`, `app/graficos.py`, `core/modelos.py`, `core/carga.py` | **Congelado** | Nadie, sin acuerdo |
| `CLAUDE.md` | Se actualiza al reunir el trabajo | Quien integra |

## 2. Identidad visual (congelada)

- **Identidad (ADR 0024):** «Un monitor del financiamiento universitario frente a la Ley 27.795, con la fuente de cada número». La lente de la ley se declara; las demás elecciones metodológicas quedan a la vista.
- **Nombre:** «Universidad Transparente» (ADR 0021), siempre con «sitio independiente» visible. No se usa el logo ni el escudo de ninguna universidad.
- **Alcance:** el sistema universitario nacional. La UNR aparece solo como caso de detalle donde un dato lo requiere, rotulada como tal.
- **Paleta de papel y tinta** (variables en `estilo.css`): fondo crema `#f2efe4` con cuadrícula tenue, papel `#ebe7d8`, tinta azul marino `#141b34`. En modo oscuro se invierte (fondo `#141b34`, tinta `#f2efe4`). No se agregan colores.
- **Rojo** (`--rojo`): reservado para lo que falta según la Ley 27.795, desde que la ley rige para ese dato: la brecha del art. 5 desde noviembre de 2025 (sueldo) y la de los arts. 3 y 4 por 2025 (funcionamiento). ADR 0022 y 0023. No se usa para nada más.
- **Colores de actores** (Congreso azul, Poder Ejecutivo naranja, Justicia verde, Acuerdo amarillo) y **series del gráfico** (pagado azul, exigido naranja): validados para daltonismo; no se cambian.
- **Tipografía:** Lato (400, 700, 900).
- **Composición:** una sola página, sin tarjetas. Secciones numeradas («01 — Salario docente») separadas por una línea fina; la pregunta como título; los datos sobre el papel. Lo secundario va detrás de un «ver más».
- **Espaciado (ADR 0033):** entre secciones, `--entre-secciones`; entre las partes de una sección (encabezado, cifras, imagen, gráfico, «ver más»), `--entre-partes`. Como cada parte aparece al hacer scroll, el aire hace que entren de a una. Un selector va pegado a lo que cambia.
- **Tono:** rioplatense, con voseo, frases cortas, sin jerga de datos. Acompaña al lector; no lo trata como una computadora.
- **Fechas y montos (ADR 0038):** en rótulos, tablas, gráficos y fichas, mes-año («ago-2026»; «ene-2026 a sep-2026»); en las frases, el mes en palabras («agosto de 2026»). Desde $ 10 millones, siempre en millones. Con «perdió» o «falta», la cifra va sin signo. Ningún texto visible nombra un ADR.

## 3. Funcionalidades (congeladas)

- **Orden y anclas de las secciones:** `#salario` (01), `#transferencias` (02), `#ley` (03), `#control` (04), «Cómo leer los números» (05). Graduación quedó fuera (ADR 0024). Las direcciones `/salario`, `/ley`, etc. redirigen a su ancla.
- **Cada número abre su ficha** (documento, página, fecha de consulta, tipo de fuente, cálculo). Se escribe siempre con `num(eje, clave)`; nunca un número a mano en una plantilla.
- **La ficha es breve (ADR 0032):** a la vista, el número con su período, «Cómo se calcula» y «Sale de»; el valor exacto, las citas de la ley, los documentos completos y los ids van en «Ver el detalle». Por eso el `calculo` de cada `Cifra` es una frase corta en castellano llano. Si la cifra depende de una elección del portal que la norma no fija, se dice en `criterio`; si se eligió de una serie, la serie va en `serie`.
- **Cifras que cuentan desde 0:** `num(eje, clave, true)` en las filas de datos.
- **Cronología de la ley:** «Línea de tiempo», vertical, de lo más antiguo a lo más reciente, dentro de un recuadro con scroll propio y el año fijo arriba; filtros por actor; detalle desplegable con «Cómo lo contaron»; recorrido «hecho por hecho» con sellos que nombran el acto (ADR 0030 y 0031, propuestas).
- **Cronología de Control:** una por universidad, cada una en un recuadro desplegable (hoy, la UNR), con la misma plantilla que la de la ley (`_cronologia.html`), con los actores AGN, SIGEN y Procuración, auditoría interna de la UNR y convenios; debajo de la pregunta, un desplegable «Ver más» / «Ver menos» con la autarquía de las universidades y quién las audita (AGN y SIGEN), sin recuadro aparte; sin sellos, que son solo de la ley (ADR 0025, propuesta).
- **Accesibilidad:** con «reducir movimiento» no hay animaciones; sin JavaScript se ve todo el contenido; todo se usa con teclado.
- **Recorrido de la ley (ADR 0038, a prueba):** arriba de «Dónde está hoy», un paso por sello, con el color de su actor; cada paso lleva a su hecho en la línea de tiempo.
- **Tipos de hecho (ADR 0037):** cada tipo tiene una etiqueta legible y un peso en `TIPOS_EVENTO`. En una misma fecha, el hecho de más peso va último en la línea de tiempo; «Dónde está hoy» lo muestra primero si es posterior al resumen, y lleva la marca «Último hecho importante».
- **Actualización de la ley (ADR 0035 y 0036):** el vigía avisa las novedades en el issue `vigia-ley`. Lo verificable (normas de InfoLEG, votaciones del Senado, notas que coinciden con un único hito) se carga solo y se publica si pasa la validación y los tests; lo demás se carga a mano con el procedimiento del ADR 0035. «Dónde está hoy» muestra la fecha del resumen y la de consulta de las fuentes.
- **Validación:** si una fila de `data/` no tiene ficha completa, la aplicación no arranca. La integración continua corre el validador y los tests en cada push y pull request a `main`.

## 4. Componentes disponibles para el contenido

Se usan tal como están; no se crean clases ni estilos nuevos.

| Componente | Uso en una plantilla de sección |
|---|---|
| Encabezado de sección | `{{ encabezado("03", "Transferencias", "¿Pregunta?") }}` |
| Fila de datos | `<div class="datos revelar"><div class="dato dato-grande"><small>Rótulo</small>{{ num(eje, "clave", true) }}</div>…</div>` (una sola `dato-grande` por fila) |
| Nota aclaratoria | `<p class="aviso">…</p>` |
| Recuadro de estado | `<div class="hoy revelar"><small>Rótulo</small><p>…</p><a class="enlace" …>Ver ficha →</a></div>` |
| Desplegable | `<details class="mas-info"><summary>¿De dónde sale…?</summary>…</details>` |
| Tabla | `<table class="tabla">` con `data-r` en cada `<td>` (para celulares) |
| Línea de tiempo simple | `{{ linea_tiempo(eje, 4) }}` |
| Pasos de un artículo | `<section class="articulo"><div class="paso"><h3><span>1</span>Título</h3><p>…</p></div></section>` |
| Enlace a la ficha de un evento | `<a href="/ficha/evento/ID" hx-get="/ficha/evento/ID" hx-target="#ficha-contenido">…</a>` |
| Gráfico acumulado con selector (solo sección 02, ADR 0022) | Ver `_seccion_transferencias.html`: SVG con las series `exigido`/`pagado`, botones `.actor` y tabla con fichas |

## 4 bis. Imagen de magnitud (ADR 0023)

Cada eje con una cifra central la muestra también con una imagen que se entiende sin leer números: pilas de fajos (Transferencias), billete que se achica según el poder de compra (Salario). Reglas: proporcional al dato; la cifra que la genera está al lado y abre su ficha (también en cada estado de un selector); rojo solo para lo que falta según la Ley 27.795 y solo desde que la ley rige para ese dato (antes, gris y rotulado como referencia); animación que muestra cómo se llega al dato, quieta con «reducir movimiento» y completa sin JavaScript; en celular, lo que se compara va lado a lado.

## 5. Reglas de contenido

Son los principios del `CLAUDE.md` (§2), que siguen vigentes:

1. **Ninguna cifra sin ficha.** Todo número sale de un `Dato` en `data/` con documento, URL, período, tipo de fuente y fecha de consulta.
2. **Sin adjetivos ni texto editorial.** Se describe el hecho («cayó 25,0 % frente a noviembre de 2023»), no se lo califica.
3. **Las dos partes.** Cuando una fuente explica el argumento del Gobierno o el de las universidades, se muestra (en `nota` del evento, empezando con «Argumento del Gobierno…» para que aparezca en la cronología).
4. **Asignado ≠ vigente ≠ devengado.** Siempre rotulado.
5. **El atraso se muestra.** Cada dato lleva su período y su fecha de consulta.
6. **Primaria o secundaria.** La prensa y los informes de terceros son `secundaria` y citan la fuente original.
7. **Títulos de noticias tal como se publicaron**, tomados de la página de la nota (`og:title`); sin el nombre del medio que algunas páginas agregan al final. Para cada hito, medios de líneas editoriales distintas.

## 6. Formato de los datos

- **Cifras:** un CSV por tema en `data/`, con las columnas base de `Dato` (`id, valor, unidad, entidad, indicador, periodo, tipo_fuente, documento, url, pagina, consultado, nota`). Las columnas extra pasan a `dimensiones`. `id` en minúsculas con guiones, único en todo `data/`.
- **Eventos:** `data/eventos/<tema>.yaml` (`ley.yaml`, `control.yaml`, `salario.yaml`). Campos: `id, fecha, tipo, ejes, titulo, tipo_fuente, documento, url, pagina, consultado, nota, noticias`. Los tipos son `norma`, `legislativo`, `judicial`, `dictamen`, `auditoria`, `convenio`, `paritaria` y `estado`; un tipo nuevo se agrega en `TIPOS_EVENTO` con su etiqueta y su peso (ADR 0037). Un evento de `estado` registra una ausencia o la situación a una fecha; se reemplaza cuando cambia.
- **Noticias:** `{medio, titulo, url, fecha}` dentro del evento.

## 7. Antes de proponer un cambio (definición de terminado)

- [ ] `git pull` antes de empezar: el vigía commitea en `main` cada 3 horas.

- [ ] `.venv/bin/python scripts/validar_datos.py` da OK.
- [ ] `.venv/bin/python -m pytest -q` pasa completo.
- [ ] Ningún archivo congelado modificado (`git diff --stat main` lo muestra).
- [ ] Cada número nuevo se ve en la página y abre su ficha.
- [ ] Los textos nuevos pasan el control de palabras valorativas (`tests/test_app.py`) y siguen el tono de la sección 2.
- [ ] Se revisó la página en modo claro, oscuro y en celular.
- [ ] El archivo de tareas propio está actualizado (qué se hizo, qué quedó pendiente, qué propuestas surgieron).
