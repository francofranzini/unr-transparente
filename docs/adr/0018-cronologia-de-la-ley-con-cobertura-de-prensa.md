# 0018. Cronología de la Ley 27.795: línea de tiempo horizontal con cobertura de prensa

- Estado: aceptada
- Fecha: 2026-10-19

## Decisión

- La página `/ley` muestra los hitos en una **línea de tiempo horizontal** (vertical en pantallas angostas), con color y rótulo por actor: Congreso, Poder Ejecutivo, Justicia y Acuerdo. El veto de 2024 se incluye como antecedente.
- Cada `Evento` puede llevar `noticias` (medio, título, URL, fecha). Son **contexto para el lector, no la fuente del hecho**: la fuente sigue siendo la ficha del evento.
- Los títulos de las notas se guardan **tal como los publicó cada medio**, obtenidos de la propia página (`og:title`). No se redactan ni se resumen. El control de palabras valorativas excluye esos títulos, porque son citas.
- Se eligen medios de distintas líneas editoriales para cada hito.
- Cuando una fuente explica el argumento del Gobierno, se muestra en el mismo hito (principio 3).

## Corrección

El evento de estado anterior («no se encontró una decisión de la Corte Suprema») estaba desactualizado. La Corte rechazó el recurso extraordinario el 25-jun-2026 y la cautelar quedó firme. Se agregaron, además, los hitos: recurso concedido (7-may-2026), acuerdo salarial (10-jun-2026), intimación (30-sep-2026), apelación de la sentencia de fondo (9-oct-2026) y multa diaria (14-oct-2026).

## Pendiente

Reemplazar las fichas secundarias por fuentes primarias: Boletín Oficial (Ley 27.795, Decretos 647/2025 y 759/2025) y textos de las resoluciones judiciales.
