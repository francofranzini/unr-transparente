# 0016. Una página por eje, portada de presentación y una sola medición salarial visible

- Estado: reemplazada por el ADR 0019
- Fecha: 2026-10-19
- Modifica: ADR 0011 (las tres bases dejan de mostrarse) y ADR 0014 (las tres fechas de corte dejan de mostrarse).

## Decisión

- **Portada (`/`):** presenta el objetivo del sitio (datos oficiales con la fuente de cada número). Destaca la brecha del art. 5 en rojo y enlaza a cada eje. No carga gráficos ni tablas.
- **Una página por eje:** `/salario`, `/ley`, `/transferencias`, `/control`, `/graduacion`. Cada una lleva su título, su pregunta, la fecha de revisión y su contenido; los supuestos y los pendientes van plegados.
- **Salario:** solo se muestra la medición frente a nov-2023. Las bases promedio-2023 y dic-2023, y las fechas de corte del art. 5, siguen en `core/lentes.py` para "Reproducí el titular", pero no se muestran.
- **Cifra destacada:** "33,4 %" en rojo, rotulada "aumento que falta". No se muestra "−33,4 %": la versión negativa de la misma brecha es −25,0 % (pagado ÷ exigido − 1). Mostrar 33,4 con signo menos sería un dato incorrecto.

## Actualización (2026-10-19): estética y tono

- Se toma la estética del sitio de la UNR: barra magenta (#990077), tipografía Lato y acentos en magenta. **No** se usa el logo institucional y la barra dice «sitio independiente», para que el sitio no se confunda con uno oficial.
- La cifra destacada sigue en rojo.
- Los artículos de cada eje acompañan al lector paso a paso, con los meses escritos en palabras («agosto de 2026») y sin jerga de datos («vigencia no confirmada» pasa a «escala todavía no publicada»).
- Los subtítulos van en el color del texto, no en gris.
