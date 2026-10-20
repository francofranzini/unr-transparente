# 0033. Más espacio entre secciones y entre las partes de cada sección

- Estado: propuesta (Fran). Se adopta si el equipo la aprueba al integrar el trabajo.
- Fecha: 2026-10-20
- Modifica: `docs/ESTANDAR.md` §2 (composición).

## Contexto

Las partes de cada sección (encabezado, cifras, imagen, gráfico, «ver más») aparecen con una animación al hacer scroll. Con 24 a 56 px entre ellas, varias entran en pantalla casi a la vez y la animación suma movimiento en lugar de guiar la lectura.

## Decisión

- Dos variables en `estilo.css`: `--entre-secciones` (`clamp(96px, 14vw, 160px)`) y `--entre-partes` (`clamp(48px, 7vw, 80px)`). En celular toman el mínimo.
- `.seccion` usa `--entre-secciones` arriba y la mitad abajo; el encabezado y cada parte de una sección (hijos directos de `.seccion` y del bloque de los arts. 3 y 4) se separan con `--entre-partes`. La portada (`.porque`) usa las mismas variables.
- Excepción: el selector «Ver:» de Transferencias queda a 24 px de las cifras que cambia, porque van juntos.

## Consecuencias

- Archivo congelado que se toca: `estilo.css`. No cambia ningún color, tipografía ni animación.
- Para ajustar el aire de toda la página alcanza con cambiar las dos variables.
