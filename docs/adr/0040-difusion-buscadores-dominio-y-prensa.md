# 0040. Difusión: buscadores, dominio propio y datos de prensa en el pie

- Estado: aceptada (pedido de Fran, 2026-10-29)
- Fecha: 2026-10-29
- Relacionado: ADR 0019 (una sola página), 0021 (nombre del sitio).

## Contexto

El sitio se mencionó en un programa de radio («estudiantes de LCC de la UNR») sin un enlace directo, y no aparecía en los buscadores. La dirección de Vercel (`unr-transparente-sigma.vercel.app`) no se puede dictar al aire.

## Decisión

- **Dominio propio:** `www.universidadtransparente.com.ar` es la dirección principal. El dominio sin `www` lo redirige Vercel (configuración del dominio), y la dirección vieja de Vercel redirige con 308, conservando la ruta, desde `vercel.json`. La dirección vive en la constante `SITIO` de `app/main.py`.
- **Buscadores:** `/robots.txt`, `/sitemap.xml` (solo la portada), URL canónica, datos estructurados `WebSite` y las etiquetas de verificación de Google Search Console (la del dominio propio y la de la dirección vieja, que hace falta para el cambio de dirección). Las fichas sueltas (`/ficha/...`) llevan `noindex, follow` para no competir con la portada.
- **Título de la pestaña:** «Universidad Transparente · Ley 27.795 de financiamiento universitario», con las palabras que se buscan. La vista previa al compartir sigue con «La universidad pública, a la vista».
- **Autoría:** el pie y la descripción dicen «estudiantes de (la Licenciatura en) Ciencias de la Computación de la UNR», como nos mencionan los medios. Sigue siendo un sitio independiente.
- **Ícono del sitio** (`favicon.ico` y versiones para celular): una «U» crema sobre azul marino, con la paleta y la tipografía del estándar.
- **IndexNow:** la clave se sirve en `/<clave>.txt` y `scripts/avisar_buscadores.py` avisa a Bing y a los demás buscadores de IndexNow que la portada cambió. Google se avisa desde Search Console.
- **Caché:** la portada se guarda 5 minutos en la CDN de Vercel (`s-maxage=300`), para que un pico de visitas no la recalcule en cada pedido.
- **Visitas:** Vercel Web Analytics (`/_vercel/insights/script.js`), sin cookies ni datos personales, para saber cuánta gente entra y desde dónde. Se activa en el panel de Vercel.
- **Prensa, en el pie y no en una página aparte** (se mantiene el ADR 0019): contacto, la imagen para notas y cómo citar un número. El pie tiene el ancla `#prensa`.

## Consecuencias

- Archivos congelados que se tocan: `app/main.py` (rutas de robots, sitemap, ícono e IndexNow; `SITIO`; caché de la portada), `base.html` (etiquetas para buscadores, ícono, autoría y prensa en el pie) y `pagina_ficha.html` (`noindex`).
- Si cambia la dirección del sitio, se cambia `SITIO` y se agrega la redirección desde la anterior.
- Después de publicar un cambio visible de la portada, correr `scripts/avisar_buscadores.py`.
