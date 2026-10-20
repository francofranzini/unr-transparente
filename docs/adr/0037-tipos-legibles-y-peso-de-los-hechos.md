# 0037. Tipos de hecho legibles y con peso: el hecho principal va primero

- Estado: aceptada (2026-10-20)
- Fecha: 2026-10-20

## Contexto

La ficha de un evento mostraba su tipo con el valor interno («estado», «judicial», «legislativo»), que no le dice nada al lector. Además, «Dónde está hoy» mostraba siempre el resumen escrito a mano, aunque en esa fecha o después hubiera un hecho de más peso (una resolución judicial, una norma, una votación).

## Decisión

- **Un solo lugar para los tipos:** `TIPOS_EVENTO` en `core/ejes.py`, con la etiqueta que ve el lector y un peso. La ficha la usa a través de `fmt.tipo_evento`.

  | Tipo | Etiqueta | Peso |
  |---|---|---|
  | `judicial` | Resolución judicial | 3 |
  | `norma` | Norma (ley, decreto o resolución) | 3 |
  | `legislativo` | Votación o trámite en el Congreso | 3 |
  | `convenio` | Acuerdo o convenio | 2 |
  | `paritaria` | Acuerdo salarial | 2 |
  | `dictamen` | Dictamen | 2 |
  | `auditoria` | Informe de auditoría | 2 |
  | `estado` | Resumen de la situación a esa fecha | 1 |

- **Cronologías** (ley y Control): por fecha, de lo más antiguo a lo más reciente; en una misma fecha, de menor a mayor peso (`ordenar_cronologia`), así el hecho principal del día queda último.
- **«Dónde está hoy»:** si desde la fecha del resumen hay un hecho de más peso que el resumen, va primero (título, tipo y fecha, con su ficha) y el resumen queda debajo, en letra normal: «Resumen de la situación» si es del mismo día, o «Resumen del …, anterior a este hecho» si es anterior. Es el mismo hecho que cierra la línea de tiempo.
- **«Último hecho importante» en la línea de tiempo:** el hecho que destaca «Dónde está hoy» (o, si no hay, el último de más peso) lleva esa etiqueta y un punto más marcado. Desde el recuadro, «Ver en la línea de tiempo ↓» lleva a ese hecho: centra el recuadro, lo desplaza hasta el hecho y lo resalta un momento (en el recorrido, salta a ese hecho). Cada hecho tiene un ancla `#hito-<id>`; sin JavaScript, el enlace funciona como ancla común.
- **Una sola fecha** en el rótulo cuando el resumen está al día con la consulta de fuentes; las dos («resumen del … · fuentes consultadas el …») solo si el resumen quedó atrás (ADR 0036).

## Consecuencias

- Archivos congelados que se tocan: `_ficha_evento.html` (etiqueta del tipo), `_cronologia.html` (marca y anclas), `app/formato.py` (`tipo_evento`), `estilo.css` (`.hoy-resumen`, `.hito-etiqueta`, `.hito-importante`, resaltado) e `interacciones.js` (ir a un hecho).
- Un tipo de evento nuevo se agrega en `TIPOS_EVENTO`; si falta, la ficha muestra el valor interno y el peso es 0.
- Tests: etiqueta legible en todas las fichas de la ley, orden por peso en la misma fecha, el hecho destacado coincide con el último de la línea de tiempo, y hay un solo hecho marcado como «Último hecho importante».
