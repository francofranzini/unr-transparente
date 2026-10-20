# 0010. Ejes actualizables y vigía de fuentes

- Estado: aceptada; reemplazada en parte por el ADR 0036 (para la Ley 27.795 hay carga automática de lo verificable)
- Fecha: 2026-10-19

## Contexto

El entregable no puede ser una publicación de una sola vez. Tiene que indicar qué fuentes consultar para detectar cambios y mostrar el estado al día de hoy.

## Decisión

El portal se organiza en **ejes**. Cada eje tiene una pregunta, un indicador principal, una fuente vigilada y una frecuencia:

| Eje | Indicador principal | Fuente vigilada | Frecuencia |
|---|---|---|---|
| **Salario real** (prioritario) | Poder adquisitivo del salario del cargo testigo respecto de 2023 | Escalas de transparencia.unr.edu.ar + IPC (API de series de tiempo) | Con cada paritaria / mensual |
| **Asignado contra ejecutado** (prioritario) | Crédito vigente contra devengado, UNR y sistema, año en curso | Presupuesto Abierto (datos abiertos, CSV) | Mensual |
| **Control** (prioritario) | Auditorías y su estado | Transparencia UNR, AGN, SIGEN | Semestral |
| **Graduación** (prioritario) | Tasa de egreso con desfase (ADR 0009) | UNR en Números, anuario de la SPU | Anual |
| Pesos de hoy | Lentes de deflactación | API de series de tiempo (IPC) | Mensual |
| Ley de financiamiento | Línea de tiempo de Eventos con el estado vigente | Boletín Oficial, Senado, fallos judiciales | Con cada hecho |

Los cuatro ejes prioritarios encabezan la página de inicio.

Las fuentes no se cargan solas. Un **vigía de fuentes** (script) revisa cada una según su frecuencia y avisa si cambió algo: un CSV nuevo, un PDF nuevo, un mes nuevo de IPC. La carga sigue siendo manual y con ficha (principio 1). Cada eje muestra la fecha de su última revisión y si hay novedades sin cargar.

Sobre la ley de financiamiento: según el equipo, no se aplicó por distintas acciones judiciales, del Senado y del Poder Ejecutivo. Cada hecho se carga como Evento con su ficha. El portal no afirma "no se aplicó" sin esos Eventos.

## Consecuencias

- Se reemplaza "no hay scraping en el MVP" por "hay detección de cambios, pero no ingesta automática".
- Hace falta un registro de fuentes vigiladas (`data/fuentes.yaml`): URL, método de detección (hash, listado de archivos, último período de la API), frecuencia y fecha de la última revisión.
