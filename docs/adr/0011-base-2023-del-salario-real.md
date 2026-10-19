# 0011. Salario real: base promedio de 2023, con nov-2023 y dic-2023 siempre visibles

- Estado: modificada por el ADR 0016 (en pantalla solo se muestra la base nov-2023)
- Fecha: 2026-10-19

## Contexto

El eje prioritario "salario real" compara contra 2023. Dentro de ese año, el mes base cambia mucho el resultado. A confirmar con la serie del INDEC guardada en `data/`: en dic-2023 hubo una devaluación y una inflación mensual muy alta (del orden del 25 %), y los salarios de ese mes no se habían ajustado. Elegir una única base equivale a tomar posición.

## Decisión

- **Parámetro `base_salario`:** `promedio_2023` (por defecto), `nov_2023` o `dic_2023`.
- Debajo de la cifra principal se muestra siempre: "Con base nov-2023: X %. Con base dic-2023: Y %."
- Para `promedio_2023`, el salario base es el promedio de las 12 grillas mensuales vigentes en 2023 (ADR 0004), deflactado con el IPC del mismo mes.
- "Reproducí el titular" recorre las tres bases.

## Consecuencias

- Hacen falta las 12 grillas mensuales de 2023 del cargo testigo (escalas de la UNR 2023, primarias) y el IPC mensual de 2023.
