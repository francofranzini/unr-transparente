# 0033. Carga automática de lo verificable de la Ley 27.795, publicada en Vercel

- Estado: propuesta (Nono). Requiere acuerdo del equipo: reemplaza en parte el ADR 0010 («hay detección de cambios, pero no ingesta automática») y el ADR 0032 («el vigía detecta y avisa; nunca publica»).
- Fecha: 2026-10-20

## Contexto

Se quiere que la sección de la ley se actualice sola, con la mayor veracidad posible, a partir de lo que el vigía encuentra todos los días. Al pasar la cronología a fuentes primarias se vio que la prensa se equivoca (votos, montos, fechas, notas en el hito equivocado): cargar todo lo que trae la prensa publicaría esos errores. Además, el sitio corría solo en local: aunque los datos cambiaran en GitHub, la página no.

## Decisión

**Se publica solo lo que se puede verificar sin intervención humana** (`scripts/actualizar_ley.py`):

| Qué | Verificación | Cómo entra |
|---|---|---|
| Normas que InfoLEG vincula a la Ley 27.795 (`carga: norma`) | Registro oficial | Hito `primaria`, con número, dependencia, fecha y descripción tal como figuran |
| Votaciones del Senado sobre la ley (`carga: votacion`) | Acta oficial | Hito `primaria`, con resultado, mayoría y votos del acta |
| Notas de prensa (`carga: prensa`: feeds de sección y mapas de noticias de medios de líneas distintas) | Título leído de la página de la nota; nota de hasta 3 días después de un hito; coincide con las claves de ese hito y de ningún otro (`data/vigia/claves_ley.yaml`) | Se suma a «Cómo lo contaron»; nunca es la fuente del hecho |
| Fecha de consulta de las fuentes | — | `data/vigia/estado_ley.yaml`, una vez por día |

**No se publica solo** (va al issue `vigia-ley`, una sola vez cada cosa): hechos nuevos que solo cuenta la prensa, notas que no coinciden con un único hito, títulos que no se pudieron leer, fuentes que no responden. Google Noticias y el CIN quedan como aviso (`carga: aviso`): no dan el enlace original o son una de las partes.

**El atraso se muestra.** «Dónde está hoy» dice «resumen del …» (evento de estado, escrito por una persona) y «fuentes consultadas el …» (automática). Si hay hechos cargados después del resumen, la página lo dice: «Después de este resumen hubo un hecho nuevo: …». La regla «el estado alcanza al último hecho» (ADR 0032) se reemplaza por esta.

**Publicación.** `.github/workflows/vigia.yml` corre cada 3 horas: carga, `validar_datos.py` y `pytest`; si pasan y hubo cambios en `data/`, hace commit en `main`. Vercel (`vercel.json`, `api/index.py`) vuelve a publicar con cada commit. Si la validación o los tests fallan, se descartan los cambios y se avisa en el issue: nada se publica sin pasar los mismos controles que un cambio manual (ficha completa, sin palabras valorativas, dos medios para un hecho secundario, notas no anteriores al hecho).

## Consecuencias

- El dueño del repositorio tiene que: habilitar GitHub Actions con permiso de escritura; si `main` está protegida, permitir que el workflow haga push (o cambiar el último paso por un pull request con fusión automática); conectar el repositorio a Vercel.
- Las claves de cada hito se mantienen a mano en `data/vigia/claves_ley.yaml` cuando se carga un hito a mano; los que carga el script suman las suyas solos.
- **Segunda etapa (no implementada):** hechos nuevos que solo cuenta la prensa, publicados como `secundaria` «pendiente de verificación» cuando medios de líneas distintas coinciden. Necesita un modelo de lenguaje para agrupar notas y redactar un título neutral sin cifras (principio 7), y una clave de la API guardada como secreto.
- Pendiente: feeds de Página/12, Clarín y Perfil que traigan estas notas (los de portada rotan en pocas horas).
