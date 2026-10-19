"""Carga y validación de `data/`. Una fila sin ficha completa es un error, no una advertencia."""

import csv
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from core.modelos import Dato, Evento

DIRECTORIO_DATOS = Path(__file__).resolve().parent.parent / "data"
CAMPOS_DATO = set(Dato.model_fields) - {"dimensiones"}


class ErrorDeCarga(Exception):
    def __init__(self, errores: list[str]):
        self.errores = errores
        super().__init__(f"{len(errores)} error(es) en data/:\n" + "\n".join(errores))


@dataclass
class Repositorio:
    datos: dict[str, Dato] = field(default_factory=dict)
    eventos: list[Evento] = field(default_factory=list)

    def buscar(self, **filtros: str) -> list[Dato]:
        """Filtra por campos de Dato o por dimensiones. Un filtro con valor "" exige dimensión vacía."""
        resultado = []
        for dato in self.datos.values():
            if all(_valor_de(dato, k) == v for k, v in filtros.items()):
                resultado.append(dato)
        return resultado

    def uno(self, **filtros: str) -> Dato:
        encontrados = self.buscar(**filtros)
        if len(encontrados) != 1:
            raise LookupError(f"Se esperaba un Dato para {filtros}, hay {len(encontrados)}")
        return encontrados[0]

    def eventos_de(self, eje: str) -> list[Evento]:
        return sorted((e for e in self.eventos if eje in e.ejes), key=lambda e: e.fecha)


def _valor_de(dato: Dato, campo: str) -> str:
    if campo in CAMPOS_DATO:
        return str(getattr(dato, campo))
    return dato.dimensiones.get(campo, "")


def _leer_csv(path: Path, errores: list[str]) -> list[Dato]:
    datos = []
    with path.open(encoding="utf-8") as f:
        for n, fila in enumerate(csv.DictReader(f), start=2):
            base = {k: v for k, v in fila.items() if k in CAMPOS_DATO and v != ""}
            dimensiones = {k: v for k, v in fila.items() if k not in CAMPOS_DATO and v}
            try:
                datos.append(Dato(**base, dimensiones=dimensiones))
            except ValidationError as e:
                for err in e.errors():
                    campo = ".".join(str(p) for p in err["loc"])
                    errores.append(f"{path.name}:{n}: {campo}: {err['msg']}")
    return datos


def _leer_eventos(path: Path, errores: list[str]) -> list[Evento]:
    eventos = []
    for n, crudo in enumerate(yaml.safe_load(path.read_text(encoding="utf-8")) or [], start=1):
        try:
            eventos.append(Evento(**crudo))
        except ValidationError as e:
            for err in e.errors():
                campo = ".".join(str(p) for p in err["loc"])
                errores.append(f"{path.parent.name}/{path.name}: evento {n} ({crudo.get('id')}): {campo}: {err['msg']}")
    return eventos


def cargar(directorio: Path = DIRECTORIO_DATOS) -> Repositorio:
    errores: list[str] = []
    repo = Repositorio()
    for path in sorted(directorio.glob("*.csv")):
        for dato in _leer_csv(path, errores):
            if dato.id in repo.datos:
                errores.append(f"{path.name}: id duplicado {dato.id}")
            repo.datos[dato.id] = dato
    # Un archivo de eventos por tema (data/eventos/*.yaml), para que cada responsable edite el suyo.
    archivos = sorted((directorio / "eventos").glob("*.yaml"))
    if (directorio / "eventos.yaml").exists():
        archivos.append(directorio / "eventos.yaml")
    for archivo in archivos:
        repo.eventos += _leer_eventos(archivo, errores)
    ids = [e.id for e in repo.eventos]
    errores += [f"eventos: id duplicado {i}" for i in sorted(set(ids)) if ids.count(i) > 1]
    if errores:
        raise ErrorDeCarga(errores)
    return repo
