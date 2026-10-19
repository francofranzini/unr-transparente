# 0004. Las grillas salariales rigen hasta la siguiente; no se interpola

- Estado: aceptada
- Fecha: 2026-10-19

## Contexto

Las grillas de COAD tienen huecos mensuales. El principio 1 ("ninguna cifra sin ficha") y el principio 7 ("el LLM nunca produce números") impiden inventar valores.

## Decisión

- Cada grilla es un Dato con `vigencia_desde`. Rige hasta que aparece la siguiente.
- Un mes sin grilla propia muestra la vigente y lo rotula: "grilla vigente desde jun-2026".
- La vigencia se considera **confirmada** solo si hay un Evento paritario que marca el siguiente cambio. Si no, el mes se rotula "vigencia no confirmada".
- No se interpola.
- **Cargo testigo:** profesor adjunto, dedicación exclusiva, sin antigüedad, nivel universitario.

## Consecuencias

- Hay que cargar los Eventos paritarios (actas o anuncios) junto con las grillas.
- Hay que abrir los PDFs anuales 2021-2023 de COAD para extraer los tramos mensuales que contengan.
