# 0015. El conflicto Universidades–Nación es el eje central; la referencia es la Ley 27.795

- Estado: aceptada
- Fecha: 2026-10-19
- Reemplaza en parte: ADR 0010 (orden de ejes) y la portada basada en el ADR 0013.

## Contexto

Para el equipo, lo central no es cuánto recibió la UNR de lo que fija la ley de presupuesto, sino la distancia entre lo que se paga o transfiere y lo que exige la Ley 27.795 de Financiamiento Universitario.

## Decisión

1. **Portada:** brecha entre el salario pagado y el que exige el art. 5 de la Ley 27.795 para el cargo testigo, en el último mes con IPC publicado. Junto a ella va siempre el estado de la ley: ejecución suspendida por el Dec. 759/2025, fallo del 6-oct-2026 y posición del Gobierno (principio 3).
2. **Asignado contra ejecutado** (ley de presupuesto) pasa a segundo plano. Se reemplaza por "lo que exigen los arts. 3 y 4 contra lo transferido" en cuanto se carguen los datos de Presupuesto Abierto 2024-2025.
3. **Indicador salarial:** `salario_basico` (sin antigüedad ni adicionales), no "salario bruto". Las sumas no remunerativas de los instructivos son solo para el personal no docente, y la garantía salarial empieza en la franja del 20 % de antigüedad.
4. **Art. 5, salario exigido en el mes m** = básico de nov-2023 × IPC(m) / IPC(nov-2023). El art. 5 manda compensar el IPC desde el 1-dic-2023 hasta la sanción y, después, actualizar mensualmente al menos por la inflación. El salario de partida es el último vigente antes del 1-dic-2023. La alternativa (partir de dic-2023) se declara en los supuestos.
5. **Mes de la portada:** el último con IPC publicado. Si ese mes no tiene grilla propia, se muestra la vigente con su rótulo de vigencia (ADR 0004).

## Validación

Con estos supuestos, la brecha de ago-2026 da 33,40 %, la misma cifra de recomposición que reclaman los gremios (Tiempo Argentino / Misiones Online, sep-2026). Es el primer caso de prueba de "Reproducí el titular" sobre la Ley 27.795.

## Fuentes

- **Grillas:** instructivos de liquidación de la SPU publicados en https://transparencia.unr.edu.ar/escalas-salariales/ (carpetas de Google Drive por mes). Para cada mes vale el documento más reciente que lo cubre; los valores reemplazados quedan en la nota.
- **IPC:** API de series de tiempo, serie 148.3_INIVELNAL_DICI_M_26 (`scripts/descargar_ipc.py`).
