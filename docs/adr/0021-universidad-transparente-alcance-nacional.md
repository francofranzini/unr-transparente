# 0021. «Universidad Transparente»: el alcance es el sistema universitario nacional

- Estado: aceptada
- Fecha: 2026-10-19
- Reemplaza: el nombre fijado en el ADR 0019 y el «piloto: UNR» del `CLAUDE.md` §1.

## Contexto

Lo que el portal discute (la Ley 27.795, el salario del cargo testigo, las transferencias del Programa 26, la auditoría de la SIGEN y la AGN) es igual para todas las universidades nacionales. La escala salarial la fija la Secretaría de Políticas Universitarias para todo el sistema, y la disputa es entre las universidades y la Nación. Llamar al sitio «UNR Transparente» lo presenta como un portal sobre una sola universidad.

## Decisión

- El sitio se llama **«Universidad Transparente»**, siempre con «sitio independiente» visible. Bajada: «La universidad pública, a la vista».
- El alcance es el **sistema universitario nacional**. La UNR deja de ser el sujeto de cada sección y aparece solo como **caso de detalle** donde un dato lo requiere (por ejemplo, su presupuesto interno o sus auditorías internas), rotulada como tal.
- No se usa el logo ni el escudo de ninguna universidad. El pie aclara que el sitio no tiene afiliación con ninguna universidad.

## Consecuencias

- Cambian el nombre, la portada y el pie (archivos congelados, por eso este ADR) y el `ESTANDAR.md`.
- Queda pendiente reorientar el contenido de cada sección (preguntas, cifras principales y artículos) al sistema; lo hace cada responsable en su frente. Hasta entonces, las secciones que hablan de la UNR siguen siendo válidas como caso de detalle.
- Los `id` de los datos y las entidades (`UNR`, `SISTEMA_UNIVERSITARIO`) no cambian.
