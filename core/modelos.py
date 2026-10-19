"""Modelos del dominio. Ver CONTEXT.md para el significado de cada término."""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PATRON_ID = r"^[a-z0-9][a-z0-9.-]*$"
PATRON_PERIODO = r"^\d{4}(-\d{2}(-\d{2})?)?$"
PATRON_URL = r"^https?://\S+$"

Unidad = Literal["ARS corrientes", "personas", "porcentaje", "índice"]


class TipoFuente(StrEnum):
    PRIMARIA = "primaria"
    SECUNDARIA = "secundaria"


class Ficha(BaseModel):
    """Procedencia de una cifra o un hecho. Sin ficha completa no se muestra nada."""

    model_config = ConfigDict(frozen=True)

    tipo_fuente: TipoFuente
    documento: str = Field(min_length=1)
    url: str = Field(pattern=PATRON_URL)
    pagina: int | None = None
    consultado: date
    nota: str = ""


class Dato(Ficha):
    id: str = Field(pattern=PATRON_ID)
    valor: Decimal
    unidad: Unidad
    entidad: str = Field(min_length=1)
    indicador: str = Field(min_length=1)
    periodo: str = Field(pattern=PATRON_PERIODO)
    # Columnas propias de cada archivo (rubro, dependencia, actividad, ...).
    dimensiones: dict[str, str] = Field(default_factory=dict)


class Noticia(BaseModel):
    """Cobertura periodística de un Evento. Es contexto para el lector, no la fuente del hecho."""

    model_config = ConfigDict(frozen=True)

    medio: str = Field(min_length=1)
    titulo: str = Field(min_length=1)
    url: str = Field(pattern=PATRON_URL)
    fecha: str = Field(default="", pattern=r"^(\d{4}-\d{2}-\d{2})?$")


TipoEvento = Literal["norma", "legislativo", "judicial", "dictamen", "auditoria", "convenio", "paritaria", "estado"]


class Evento(Ficha):
    """Hecho documentado sin cifra. Un evento de `tipo: estado` registra una ausencia."""

    id: str = Field(pattern=PATRON_ID)
    fecha: str = Field(pattern=PATRON_PERIODO)
    tipo: TipoEvento
    ejes: list[str] = Field(min_length=1)
    titulo: str = Field(min_length=1)
    # Meses sin grilla propia para los que este documento confirma que rige la anterior (ADR 0004).
    confirma_vigencia: list[str] = Field(default_factory=list)
    noticias: list[Noticia] = Field(default_factory=list)
