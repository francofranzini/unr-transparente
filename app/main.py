"""Portal de transparencia de la UNR. Ejecutar con: .venv/bin/uvicorn app.main:app --reload"""

from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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
templates.env.globals.update(fmt=formato)


def _render(request: Request, parcial: str, contexto: dict) -> HTMLResponse:
    """Con HTMX devuelve solo el fragmento; sin JavaScript, la página completa."""
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, parcial, contexto)
    return templates.TemplateResponse(request, "pagina_ficha.html", {**contexto, "parcial": parcial})


# Todo el contenido vive en la portada; las direcciones de cada eje llevan a su sección, abierta.
PAGINAS = {"salario": "salario", "ley": "ley", "transferencias": "ejecucion", "control": "control"}
templates.env.globals.update(paginas={v: k for k, v in PAGINAS.items()})


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    ejes = construir_ejes(repo)
    formatos = [graficos.salario_contra_ley(ejes["salario"].serie, f) for f in graficos.FORMATOS]
    return templates.TemplateResponse(request, "inicio.html", {"ejes": ejes, "graficos_salario": formatos})


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
