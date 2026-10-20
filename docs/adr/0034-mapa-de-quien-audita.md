# 0034. Control: quién audita a las universidades, y una línea de tiempo por universidad con selector

- Estado: propuesta (Fran). Se adopta si el equipo la aprueba; en especial Tero, responsable de la sección 04.
- Fecha: 2026-10-20
- Relacionado: ADR 0005 (qué se muestra de cada auditoría), 0023 (imagen de magnitud en cada eje), 0025 (Control).
- Modifica: ADR 0025 (pregunta de la sección y recuadro desplegable por universidad).

## Contexto

Salario y Transferencias tienen una imagen que se entiende sin leer (billete, fajos; ADR 0023). Control tenía solo texto plegado y la línea de tiempo. Control no tiene una cifra central, así que no corresponde una imagen de magnitud; lo que hay que ver es una relación: quién controla a las universidades y desde dónde. Además, la pregunta era «¿Quién audita a la UNR?», pero quién audita es igual para todas las universidades nacionales; lo propio de la UNR son sus hechos, en la línea de tiempo.

## Decisión

- La pregunta de la sección pasa a **«¿Quién audita a las universidades?»**.
- Entre el «Ver más» y la línea de tiempo, un **mapa**: al centro, las universidades nacionales; a la izquierda la **AGN** (control externo, color del Congreso, línea continua) y a la derecha la **SIGEN** (control interno del Poder Ejecutivo, color del Ejecutivo, línea punteada). Íconos de línea propios (lupa, escudo, edificio), sin logos de ningún organismo.
- Cada órgano es un botón que abre su panel: función según la norma citada, a quién responde y los hechos de `control.yaml` que **alcanzan a todas las universidades** (convenios del CIN, dictámenes de la Procuración del Tesoro, resoluciones), cada uno con su ficha. Se eligen por id en `ORGANOS_CONTROL` (`core/ejes.py`); si un id no existe, `eje_control` da error. «Ver sus hechos en la línea de tiempo» aplica el filtro del órgano en la cronología de la universidad elegida.
- La línea punteada de la SIGEN es una convención de estilo para distinguir los dos lados; no indica que el control sea más débil. Lo que define su alcance está en el panel.
- **Línea de tiempo por universidad:** en lugar de un recuadro desplegable por universidad, un selector «Ver:» como el de Transferencias, con la universidad elegida marcada. Hoy solo está la UNR; para sumar otra alcanza con cargar sus hechos y agregarla a `UNIVERSIDADES_CONTROL`, y aparece como un botón más.
- Animación: al aparecer, las universidades y los órganos entran escalonados, las líneas se dibujan hacia el centro y un punto viaja por cada una. Con «reducir movimiento», todo quieto. Sin JavaScript se ven los dos paneles y todas las líneas de tiempo, y el botón de filtro no aparece.

## Consecuencias

- Archivos congelados que se tocan: `estilo.css` (`.mapa-*`, `.organo*`, `.unr-icono`, `.universidad-titulo`, animaciones `viaje`, `viaje-izq`, `panel-entra`; sin colores nuevos) e `interacciones.js` (paneles, filtro y selector de universidad).
- `_seccion_control.html` y `eje_control` son de Tero: este cambio entra en su sección.
- **Cambian tests existentes del ADR 0025 (requiere el acuerdo de Tero):** la pregunta nueva; el recuadro desplegable por universidad pasa a selector; y el nombre «Sindicatura General de la Nación» ya no se exige solo plegado (ahora se verifica que el texto de presentación siga plegado), porque el mapa nombra a cada órgano a la vista.
- Para sumar un órgano al mapa: una entrada en `ORGANOS_CONTROL`, con su prefijo en `ACTORES_CONTROL`, y su botón en el mapa.
