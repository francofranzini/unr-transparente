# División del trabajo

Tres frentes en paralelo, sobre la base fijada en [`docs/ESTANDAR.md`](../ESTANDAR.md). Cada uno modifica **contenidos** de su tema; nadie cambia la presentación.

| Persona | Frente | Sección del sitio | Archivo de tareas |
|---|---|---|---|
| **Nono** | Cronología de la Ley 27.795 | 02 — `#ley` | [`nono-cronologia-ley.md`](nono-cronologia-ley.md) |
| **Fran** | Presupuesto y transferencias | 03 — `#transferencias` | [`fran-presupuesto.md`](fran-presupuesto.md) |
| **Tero** | Auditorías y control | 04 — `#control` | [`tero-auditorias.md`](tero-auditorias.md) |

Salario (01) lo toma Fran (rama `fran/salario`, calendario de días de sueldo, ADR 0023). Graduación (05) no tiene responsable por ahora; sus pendientes están al final de este archivo.

## Qué archivos son de cada uno

Para no pisarnos al reunir el trabajo, cada archivo tiene un solo dueño:

| Archivo | Nono | Fran | Tero |
|---|---|---|---|
| `data/eventos/ley.yaml` | ✔ | | |
| `data/eventos/control.yaml` | | | ✔ |
| `app/templates/_seccion_ley.html` | ✔ | | |
| `app/templates/_seccion_transferencias.html` | | ✔ | |
| `app/templates/_seccion_control.html` | | | ✔ |
| `core/ejes.py` → `eje_ley` / `eje_ejecucion` / `eje_control` | `eje_ley` | `eje_ejecucion` | `eje_control` |
| `data/ejecucion_programa26_*.csv`, `data/credito_asignado_ley.csv` | | ✔ | |
| CSV nuevos | `data/ley_*.csv` | `data/presupuesto_*.csv` | `data/control_*.csv` |
| `core/lentes.py` | | ✔ (lente de los arts. 3 y 4) | |

Si alguien necesita tocar un archivo de otro (por ejemplo, Tero quiere que un evento de control aparezca también en la cronología de la ley), lo pide a su dueño o lo anota como propuesta.

**Numeración de ADR** (para que no choquen): Fran `0020`–`0024`, Tero `0025`–`0029`, Nono `0030`–`0034`.

## Cómo trabajar

1. Partir de `main` actualizado: `git switch main && git pull`.
2. Una rama por persona: `nono/cronologia-ley`, `fran/presupuesto`, `tero/auditorias`.
3. Commits chicos y descriptivos. Cada dato o evento nuevo, con su ficha completa.
4. Antes de abrir el pull request, cumplir la definición de terminado del estándar (§7).
5. Abrir un pull request a `main`. La plantilla trae la lista de control.

## Cómo reunimos todo

1. Se integra en este orden, porque Fran toca código de cálculo y conviene que sea lo último sobre una base estable: **Tero (control) → Nono (ley) → Fran (presupuesto)**.
2. Después de cada integración: tests, validación de datos y una revisión de la página en claro, oscuro y celular.
3. Quien integra actualiza `CLAUDE.md` (pendientes resueltos) y revisa las **propuestas de presentación** anotadas en los archivos de tareas, para decidir en conjunto si se adopta alguna (con su ADR).

## Pendientes sin asignar

**Salario (01)**
- Conseguir los instructivos de julio y agosto de 2026: la UNR no los publicó. Se pueden pedir por el [formulario de acceso a la información](https://transparencia.unr.edu.ar/formulario-informacion/).
- Actualizar el IPC cuando el INDEC publique septiembre de 2026: `.venv/bin/python scripts/descargar_ipc.py`.

**Graduación (05)**
- Ingresantes de la UNR desde 2016, para la tasa de egreso con desfase (ADR 0009). Fuentes: anuario de la SPU o pedido al rectorado.
- Reemplazar los egresados de prensa (secundaria) por una fuente primaria de la UNR.
