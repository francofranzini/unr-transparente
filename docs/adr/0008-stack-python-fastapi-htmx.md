# 0008. Stack: Python con FastAPI, Jinja y HTMX

- Estado: aceptada
- Fecha: 2026-10-19

## Decisión

- **Backend y páginas:** FastAPI con plantillas Jinja2. HTMX para la interactividad: el cambio de lente reemplaza solo el gráfico y el clic sobre una cifra abre su ficha.
- **Gráficos:** Plotly. Cada gráfico se acompaña de la lista de supuestos de la lente activa.
- **Esquema único:** modelos de Pydantic para Dato, Evento y el objeto de la afirmación (sección 6). Se usan para validar `data/` en el build y para validar la salida del LLM.
- **Datos:** `data/*.csv` (un archivo por indicador) y `data/eventos.yaml`. Un validador en la integración continua rechaza cualquier fila sin ficha completa.
- **Núcleo:** paquete `core/` (lentes y motor de "Reproducí el titular") sin dependencias web, probado con pytest y valores calculados a mano.
- **LLM:** SDK de Anthropic para Python, con salida estructurada, usado solo en el paso 1 de la sección 6. Si la llamada falla, se usa un formulario manual con los mismos campos.
- **Series externas** (IPC, PBI, RIPTE, REM): un script las descarga y las guarda versionadas en `data/` con su fecha de consulta. La demo no depende de APIs en vivo.
- **Despliegue:** local (`uvicorn`) para la demo. No hay hosting en el MVP.

## Alternativas descartadas

- **TypeScript + Vite + React:** el equipo se maneja más cómodo en Python.
- **Streamlit:** la estética de tablero de datos y las fichas por cifra quedaban forzadas.
