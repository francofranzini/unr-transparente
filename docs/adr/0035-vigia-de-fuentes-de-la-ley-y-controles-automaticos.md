# 0035. Vigía de fuentes de la ley y controles automáticos

- Estado: propuesta (Nono). Se adopta si el equipo la aprueba al integrar la rama `feat/automate-news`.
- Fecha: 2026-10-20
- Implementa: ADR 0010 (vigía de fuentes) para el eje ley.

## Contexto

La cronología de la Ley 27.795 se actualiza con cada hecho (ADR 0010), pero hasta ahora todo dependía de que alguien se acordara de buscar novedades y de correr los controles. El repositorio no tenía integración continua, y varias reglas de verificación no se controlaban solas: hechos secundarios con una sola nota, notas cargadas en el hito equivocado, enlaces caídos. Al pasar los hitos a fuente primaria aparecieron errores de la prensa (votos, montos, fechas) que una carga automática habría publicado.

## Decisión

**1. El vigía detecta y avisa; nunca publica.**
- `data/fuentes.yaml` registra las fuentes vigiladas: InfoLEG (normas que modifican la ley), actas del Senado, noticias del CIN y Google Noticias (causa CIN y aviso temprano de prensa). Diputados se revisa a mano porque su portal tiene reCAPTCHA; Class Actions Argentina rechaza pedidos automáticos y se sigue a través de Google Noticias.
- `scripts/vigia_fuentes.py` informa como novedad:
  - en páginas sin fecha, un enlace que no está citado en ningún evento ni en el `ignorar` de la fuente;
  - en feeds, lo publicado desde la última revisión cargada (la fecha del evento de `estado`) que no está citado; las notas de Google Noticias se reconocen también por el título.
- **El estado vive en los datos versionados**, no en un bot: cuando se carga un hecho, sus enlaces dejan de ser novedad; lo que no corresponde se agrega a `ignorar` en un pull request.
- `.github/workflows/vigia.yml` lo corre todos los días y escribe en un único issue abierto con la etiqueta `vigia-ley`.

**2. Controles en cada cambio.** `.github/workflows/validar.yml` corre `scripts/validar_datos.py` y `pytest` en cada push y pull request a `main`, sin red.

**3. Reglas de verificación como tests** (`tests/test_eventos_ley.py`, solo eje ley):
- un hecho `secundaria` tiene al menos dos medios distintos;
- toda noticia tiene fecha, y ninguna es anterior al hecho por más de un día;
- hay un solo evento de `estado` y su fecha alcanza al último hecho.

**4. Enlaces y copias.** Los lunes, el workflow corre `verificar_titulos.py` y `verificar_enlaces.py` (solo cuentan como caídos 404, 410 o un dominio inexistente; los sitios que rechazan pedidos automáticos se listan aparte) y avisa si algo falla. `scripts/archivar_fuentes.py` registra en `data/archivo_web.yaml` la copia de cada fuente en la Wayback Machine, primero las fichas de los eventos.

**5. El atraso se muestra.** «Dónde está hoy» dice «revisado el …», con la fecha del evento de estado.

## Procedimiento para cargar un hecho nuevo

1. Buscar el original: Boletín Oficial, acta de votación de la cámara o texto de la resolución.
2. Si no hay original: `tipo_fuente: secundaria`, con 2 o más medios de líneas editoriales distintas y la nota «Texto de la resolución: pendiente».
3. Copiar las citas literales del documento, no de la prensa.
4. Cargar el evento en `data/eventos/ley.yaml`; si corresponde, su sello en `SELLOS_LEY` (sin cifras, ADR 0031).
5. Reemplazar el evento de `estado` con la fecha del día.
6. Correr `scripts/validar_datos.py`, `pytest`, `scripts/verificar_titulos.py` y `scripts/archivar_fuentes.py --guardar`.
7. Abrir un pull request para que lo revise otra persona y cerrar el issue del vigía.

## Consecuencias

- Hace falta que el dueño del repositorio habilite GitHub Actions; la etiqueta `vigia-ley` la crea el workflow. Conviene marcar `validar.yml` como obligatorio para fusionar en `main`.
- El vigía es genérico: los otros ejes pueden sumar fuentes en `data/fuentes.yaml` con su `eje` y correr `vigia_fuentes.py --eje <eje>`.
- Google Noticias es solo un aviso temprano: nunca es la fuente de un hecho.
- Queda como propuesta mostrar en la página la copia archivada cuando el original se cae: requiere un campo nuevo en `Ficha` o `Noticia` (`core/modelos.py`, congelado).
