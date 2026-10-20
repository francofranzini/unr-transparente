# 0039. Salario: lo que dejó de cobrar el cargo testigo desde que rige el art. 5

- Estado: aceptada (pedido de Fran, 2026-10-20)
- Fecha: 2026-10-20
- Relacionado: ADR 0003, 0004 y 0011 (cargo testigo y vigencia de las grillas), 0015 (art. 5), 0032 (ficha breve).

## Contexto

La sección de Salario muestra cuánto falta en un mes (la brecha del art. 5) y cuánto poder de compra se perdió, pero no cuánta plata dejó de cobrar el cargo testigo en total.

## Decisión

- **Una cifra nueva**, `no-cobrado` en `eje_salario`, calculada con la lente `no_cobrado_art5` de `core/lentes.py`, que tiene tests a mano.
- **Cómo se calcula:** cada mes, lo que exige el art. 5 (el básico de nov-2023 actualizado por IPC) menos el básico cobrado. Se suma desde **nov-2025**, el mes siguiente a la publicación de la ley, que es cuando el art. 5 manda pagar el aumento, hasta el último mes con IPC publicado.
- **Qué incluye:** va en pesos de cada mes, sin ajustar, y solo cuenta el básico: sin aguinaldo, antigüedad ni adicionales. Un mes en que se cobrara más de lo exigido suma 0 y no compensa otros meses. Los meses sin escala publicada usan la vigente y la ficha lo avisa (ADR 0004).
- **Dónde va:** en su propia fila, debajo de las cifras de Salario, como cifra destacada. Su ficha muestra el criterio, el aviso de vigencia, la norma y el detalle mes a mes (`Cifra.serie`, con su nota en `Cifra.serie_nota`).
- **«Sale de» en las fichas:** cuando hay más de dos documentos con el mismo nombre corto (los instructivos de la SPU), van en un solo renglón con la cantidad y el rango de meses; el detalle sigue en «Ver el detalle».

## Consecuencias

- Archivos congelados que se tocan: `formato.py` (agrupación en `origenes`) y `_ficha_cifra.html` (nota de la serie).
- Cuando se publique la escala de un mes que hoy usa la vigente, la cifra cambia sola.
