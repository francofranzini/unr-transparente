# 0032. Ficha breve: cómo se calcula y de dónde sale, con el detalle plegado

- Estado: propuesta (Fran). Se adopta si el equipo la aprueba al integrar el trabajo.
- Fecha: 2026-10-20
- Modifica: `docs/ESTANDAR.md` §3 («Cada número abre su ficha»).

## Contexto

Al tocar un número, la ficha mostraba todo a la vez: período, tipo de fuente, cálculo, la cita textual de cada artículo de la ley, el nombre completo de cada documento con su descarga y su cantidad de registros, notas e ids. En una cifra como «UNR: cuánto más correspondía que lo transferido» eran tres documentos, dos citas largas y 47 ids. No faltaba información: sobraba, y el cálculo quedaba perdido entre el resto. Tampoco se veía de qué se compone un total; por ejemplo, la partida de los arts. 3 y 4 mostraba «4 registros» y sus ids, pero no qué era cada uno.

## Decisión

La ficha se lee de arriba abajo en tres partes, y todo lo demás va detrás de un «Ver el detalle» (`<details>`, cerrado):

1. **El número**, en su forma corta («$ 1.529 millones», «73,3 %»), con el período al lado.
2. **Cómo se calcula**, en un recuadro: el cálculo en una frase. Si la cifra es la suma de pocos registros (hasta 12), debajo va cada sumando con su monto. Si la cifra depende de una elección del portal que la norma no fija, va en una línea (`Cifra.criterio`). La advertencia de vigencia de una grilla (`Cifra.aviso`) también va acá, porque cambia cómo leer el número.
3. **Sale de**: un renglón por documento, con su nombre corto (hasta el primer «:» o «(») y el enlace al sitio oficial; si dos documentos comparten nombre corto, se agrega su período. Las normas van como «Norma: Ley 27.795, art. 5», sin la cita. Al pie: tipo de fuente (primaria, secundaria o mixta) y fecha de consulta.

En «Ver el detalle»: el valor exacto, los montos exactos de cada sumando, la serie de donde se eligió la cifra (`Cifra.serie`), la cita textual de cada norma, los documentos completos con su descarga y cantidad de registros, las notas y los ids.

## Consecuencias

- Archivos congelados que se tocan: `_ficha_cifra.html`, `estilo.css` (`.ficha-calculo`, `.ficha-suma`, `.ficha-origen`, `.ficha-detalle` y afines; sin colores nuevos), `formato.py` (`pesos_corto`, `composicion`, `origenes`) y `main.py` (pasa la composición a la plantilla). `core/ejes.py` suma a `Cifra` los campos opcionales `criterio` y `serie`.
- La ficha de eventos (`_ficha_evento.html`) ya era breve y no cambia.
- El principio 1 no cambia: cada número sigue llevando documento, URL, período, tipo de fuente y fecha de consulta, y todo sigue a un clic.
- Los cálculos tienen que ser frases cortas y en castellano llano, porque son lo primero que se lee. Al agregar una cifra, escribir el `calculo` pensando en ese recuadro.
- `tests/test_app.py` verifica que la vista breve tiene el cálculo y el origen, y que citas e ids quedan en el detalle.
