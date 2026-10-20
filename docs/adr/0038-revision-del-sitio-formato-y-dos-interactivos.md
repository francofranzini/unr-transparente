# 0038. Revisión del sitio: formato unificado, textos más claros y dos interactivos

- Estado: aceptada en formato y textos (decisión de Fran en la revisión del 2026-10-20); el recorrido de la ley y la cascada, a prueba.
- Fecha: 2026-10-20
- Modifica: `docs/ESTANDAR.md` §2 (tono: formato de fechas) y §3 (cronología de la ley); ADR 0025 (texto de presentación de Control).

## Contexto

Una revisión completa del sitio encontró incoherencias de lectura (la misma palabra para dos cifras distintas, dobles negativos, dos nombres para una misma referencia, montos y fechas en varios formatos), jerga interna a la vista del lector («ADR 0024» en fichas) y dos lugares donde había que leer mucho para entender algo que se puede ver: dónde está la ley y cómo se llega a lo que correspondía en 2025.

## Decisión

**Coherencia y formato**
- **Salario:** el billete ya no dice «Le falta −25,0 %». Dice «Perdió 25,0 % de poder de compra» y conecta esa cifra con el aumento que la recupera: «para comprar lo mismo que en nov-2023… el sueldo tiene que subir 33,4 %», la misma cifra de la portada. Para eso hay dos cifras por mes, `perdida-<mes>` (sin signo) y `subir-<mes>` (1 ÷ lo que compra − 1). La del último mes coincide con la brecha del art. 5, y un test lo verifica.
- **Sin signos dobles:** con «perdió» o «falta» la cifra va sin signo.
- **Transferencias 2026:** «referencia» es el monto mensual de fines de 2025 sin actualizar; «referencia actualizada por inflación» es la otra lectura. Ya no se usa «piso».
- **Fechas:** en rótulos, tablas, gráficos y fichas, **mes-año** («ago-2026»; un período de varios meses, «ene-2026 a sep-2026»). En las frases, el mes va en palabras. Las fechas con día no cambian («20 oct 2026»).
- **Montos:** desde $ 10 millones, siempre en millones («$ 28 millones»), para que una columna no mezcle formatos. Los sueldos se muestran exactos.
- **Fichas:** los cálculos van en castellano llano, no como fórmula. Ninguna ficha nombra un ADR, y un test lo verifica.
- **Tablas mensuales:** un mes sin devengado dice «sin transferencias en el mes». El mes en curso dice «mes en curso, datos al…».
- **Enlaces a la ficha de un hecho:** siempre «Ver ficha →».
- **Instrucción «Tocá un número…»:** queda solo en el lema del principio. La sección 05 pasa a «¿Qué muestra cada ficha?» y su ejemplo usa el formato de la ficha real (ADR 0032).
- **Control:** el «Ver más» queda solo con la autonomía y la autarquía (art. 75, inc. 19, de la Constitución). Lo de quién audita ya lo muestra el mapa (ADR 0034).

**Recorrido de la ley** (sección 03, arriba de «Dónde está hoy»)
- Una línea con un paso por cada sello del ADR 0031, en orden: de «Sancionada» a la última resolución. Cada paso tiene el color de su actor, con el mismo mapa por tipo de hecho que la línea de tiempo (`ACTORES_LEY` en `core/ejes.py`). El antecedente de 2024 queda solo en la línea de tiempo.
- Los rótulos alternan arriba y abajo de la línea. El último paso dice «hoy» y late.
- Cada paso lleva a su hecho en la línea de tiempo (`#hito-<id>`, ADR 0037).
- La línea se dibuja al aparecer y los pasos entran en orden. En pantallas angostas el recorrido se desplaza de costado y arranca en el último paso. Con «reducir movimiento», todo queda quieto.

**Cascada de los arts. 3 y 4** (Transferencias, «¿De dónde sale este número?», 2025)
- Reemplaza la tabla de la cuenta por cuatro pasos con barras proporcionales:
  1. la partida mensual (sep-2024);
  2. la partida actualizada por el art. 3, que es una cifra nueva, `partida-art3`, con ficha y norma;
  3. los seis bimestres del art. 4, cada uno con dos barras: lo que manda la ley (naranja) y lo recibido (azul), con sus montos. El eje empieza en un valor redondo debajo del menor de los dos (`fmt.piso_eje`), no en cero, y lo indica solo el rótulo del eje;
  4. lo que correspondía en el año frente a lo recibido, con lo que falta en rojo.
- Cada barra es una cifra con ficha. Las barras crecen al abrir el desplegable. En celular, los bimestres pasan a barras horizontales.

## Consecuencias

- Archivos congelados que se tocan: `estilo.css` (`.camino*`, `.cascada*`, ficha de ejemplo, notas de tablas), `interacciones.js` (el recorrido arranca en el último paso), `formato.py` (millones desde $ 10 millones, mes-año), `base.html`, `inicio.html`, `_cronologia.html` y `_cronologia_ley.html` («Ver ficha →», actores desde `ACTORES_LEY`).
- Tests nuevos: sin dobles negativos en el billete; el aumento del billete coincide con la brecha del art. 5; ninguna ficha menciona un ADR; las tablas de Transferencias están en millones; «Ver ficha →»; un paso del recorrido por sello; la cascada con sus fichas. Dos tests existentes cambian solo el formato de fecha que esperan.
- Sellos nuevos en `SELLOS_LEY` suman un paso al recorrido sin tocar la plantilla.
