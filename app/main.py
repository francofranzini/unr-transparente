"""Portal de transparencia de la UNR. Ejecutar con: .venv/bin/uvicorn app.main:app --reload"""

from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import formato, graficos
from core.carga import cargar
from core.ejes import construir_ejes

RAIZ = Path(__file__).resolve().parent

# Si data/ tiene una fila sin ficha, la aplicación no arranca (principio 1).
repo = cargar()

app = FastAPI(title="Portal de transparencia — UNR")
app.mount("/static", StaticFiles(directory=RAIZ / "static"), name="static")
templates = Jinja2Templates(directory=RAIZ / "templates")
# Dirección pública: los buscadores y las vistas previas al compartir necesitan URL absolutas.
SITIO = "https://www.universidadtransparente.com.ar"
# Clave de IndexNow: con ella Bing y otros buscadores aceptan avisos de cambios (scripts/avisar_buscadores.py).
INDEXNOW_CLAVE = "0e91086c2ca35921727ad800d2b59988"
templates.env.globals.update(fmt=formato, sitio=SITIO)


def _render(request: Request, parcial: str, contexto: dict) -> HTMLResponse:
    """Con HTMX devuelve solo el fragmento; sin JavaScript, la página completa."""
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, parcial, contexto)
    return templates.TemplateResponse(request, "pagina_ficha.html", {**contexto, "parcial": parcial})


# Todo el contenido vive en la portada; las direcciones de cada eje llevan a su sección, abierta.
PAGINAS = {"salario": "salario", "ley": "ley", "transferencias": "ejecucion", "control": "control"}
templates.env.globals.update(paginas={v: k for k, v in PAGINAS.items()})


# HEAD también: algunos lectores de vista previa (LinkedIn, WhatsApp) lo piden antes del GET
@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def inicio(request: Request):
    ejes = construir_ejes(repo)
    formatos = [graficos.salario_contra_ley(ejes["salario"].serie, f) for f in graficos.FORMATOS]
    respuesta = templates.TemplateResponse(request, "inicio.html", {"ejes": ejes, "graficos_salario": formatos})
    # La CDN de Vercel guarda la portada 5 minutos; así un pico de visitas no recalcula la página en cada pedido.
    respuesta.headers["Cache-Control"] = "public, max-age=0, s-maxage=300, stale-while-revalidate=86400"
    return respuesta


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITIO}/sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap():
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"  <url><loc>{SITIO}/</loc></url>\n"
           "</urlset>\n")
    return Response(xml, media_type="application/xml")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(RAIZ / "static" / "favicon.ico")


@app.get(f"/{INDEXNOW_CLAVE}.txt", response_class=PlainTextResponse)
def indexnow_clave():
    return INDEXNOW_CLAVE


@app.get("/{pagina}")
def pagina_eje(pagina: str):
    if pagina not in PAGINAS:
        raise HTTPException(404, "No existe esa página")
    return RedirectResponse(f"/#{pagina}", status_code=301)


@app.get("/ficha/cifra/{eje}/{clave}", response_class=HTMLResponse)
def ficha_cifra(request: Request, eje: str, clave: str):
    ejes = construir_ejes(repo)
    try:
        cifra = ejes[eje].cifra(clave)
    except (KeyError, StopIteration):
        raise HTTPException(404, "No existe esa cifra")
    documentos = Counter((d.documento, d.url, d.pagina, d.tipo_fuente.value, d.consultado) for d in cifra.fuentes)
    notas = sorted({d.nota for d in cifra.fuentes if d.nota})
    return _render(request, "_ficha_cifra.html", {"cifra": cifra, "documentos": documentos, "notas": notas,
                                                  "composicion": formato.composicion(cifra)})


@app.get("/ficha/evento/{evento_id}", response_class=HTMLResponse)
def ficha_evento(request: Request, evento_id: str):
    evento = next((e for e in repo.eventos if e.id == evento_id), None)
    if evento is None:
        raise HTTPException(404, "No existe ese evento")
    return _render(request, "_ficha_evento.html", {"evento": evento})
