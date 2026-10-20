"""Construcción de los ejes de la página de inicio (ADR 0010).

Cada número que sale de acá es una `Cifra` que lleva los Datos de los que proviene y, si es
derivada, la fórmula con la que se calculó. Lo que no tiene datos va a `pendientes`, como texto.
"""

import re
from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal

from core import lentes
from core.carga import Repositorio
from core.lentes import Vigencia
from core.modelos import Dato, Evento

UNIVERSIDADES_NACIONALES = 61


@dataclass(frozen=True)
class Norma:
    """La norma que define un cálculo (no un dato): se muestra en la ficha con su cita textual (ADR 0023)."""
    texto: str
    url: str
    cita: str


BO_LEY_27795 = "https://www.boletinoficial.gob.ar/detalleAviso/primera/333139/20251021"
NORMA_ART3 = Norma("Ley 27.795, art. 3 (Boletín Oficial, 21-oct-2025)", BO_LEY_27795,
                   "«…actualizará al 1º de enero de 2025, según la variación acumulada del Índice de Precios al "
                   "Consumidor (IPC)… en el período comprendido entre el 1º de mayo al 31 de diciembre de 2024, el "
                   "monto de los gastos de funcionamiento de las universidades públicas…»")
NORMA_ART4 = Norma("Ley 27.795, art. 4 (Boletín Oficial, 21-oct-2025)", BO_LEY_27795,
                   "«…actualizará desde el 1º de enero hasta el 31 de diciembre de 2025, de forma bimestral, de acuerdo "
                   "al Índice de Precios al Consumidor (IPC)… Los aumentos otorgados y oportunamente efectivizados… "
                   "deberán tomarse a cuenta para el cálculo del presente artículo.»")
NORMA_REFERENCIA = Norma("Ley 27.795, art. 4, extendido a otro año: la ley no lo pide (referencia, ADR 0024)",
                         BO_LEY_27795, NORMA_ART4.cita)
NORMA_ART5 = Norma("Ley 27.795, art. 5 (Boletín Oficial, 21-oct-2025)", BO_LEY_27795,
                   "«…deberá actualizar los salarios… entre el período 1º/12/2023 hasta la sanción de la presente ley, "
                   "en un porcentaje que no puede ser inferior al Índice de Precios al Consumidor (IPC)… Este aumento se "
                   "hará efectivo al mes siguiente de la publicación… asegurando en todos los casos y tramos de la "
                   "negociación una actualización mensual no inferior a la inflación…»")


@dataclass(frozen=True)
class Cifra:
    clave: str
    etiqueta: str
    valor: Decimal
    unidad: str
    periodo: str
    fuentes: tuple[Dato, ...]
    calculo: str = ""
    aviso: str = ""  # p. ej. vigencia no confirmada de una grilla (ADR 0004)
    normas: tuple[Norma, ...] = ()  # la norma que define el cálculo, si la hay (ADR 0023)
    criterio: str = ""  # una elección del portal que la norma no fija (p. ej. el mes de la partida, ADR 0020)
    serie: tuple[tuple[str, Decimal], ...] = ()  # (período, valor) de donde se eligió la cifra, para la ficha

    @property
    def tipo_fuente(self) -> str:
        tipos = {d.tipo_fuente.value for d in self.fuentes}
        return tipos.pop() if len(tipos) == 1 else "mixta"


@dataclass
class Eje:
    clave: str
    titulo: str
    pregunta: str
    cifras: list[Cifra] = field(default_factory=list)
    eventos: list[Evento] = field(default_factory=list)
    supuestos: list[str] = field(default_factory=list)
    pendientes: list[str] = field(default_factory=list)
    serie: list[dict] = field(default_factory=list)
    detalle: dict = field(default_factory=dict)  # datos para el artículo "De dónde sale cada dato"

    @property
    def ultima_revision(self) -> date | None:
        fechas = [d.consultado for c in self.cifras for d in c.fuentes] + [e.consultado for e in self.eventos]
        return max(fechas, default=None)

    def cifra(self, clave: str) -> Cifra:
        return next(c for c in self.cifras if c.clave == clave)


def _directa(clave: str, etiqueta: str, dato: Dato) -> Cifra:
    return Cifra(clave, etiqueta, dato.valor, dato.unidad, dato.periodo, (dato,))


def _suma(clave: str, etiqueta: str, datos: list[Dato]) -> Cifra:
    return Cifra(clave, etiqueta, sum(d.valor for d in datos), datos[0].unidad, datos[0].periodo, tuple(datos),
                 calculo=f"Suma de {len(datos)} registros")


def _cociente(clave: str, etiqueta: str, num: Cifra, den: Cifra) -> Cifra:
    return Cifra(clave, etiqueta, num.valor / den.valor * 100, "porcentaje", num.periodo, num.fuentes + den.fuentes,
                 calculo=f"{num.etiqueta} ÷ {den.etiqueta} × 100")


def eje_ejecucion(repo: Repositorio, anio: str = "2026") -> Eje:
    eje = Eje("ejecucion", "Transferencias", "¿Reciben las universidades lo que les corresponde por ley?")

    def por_universidad(indicador: str) -> list[Dato]:
        return [d for d in repo.buscar(indicador=indicador, periodo=anio, actividad="")
                if d.dimensiones.get("universidad")]

    unr, sistema, no_asignado = {}, {}, {}
    for indicador in ("credito_asignado", "credito_vigente", "devengado"):
        filas = por_universidad(indicador)
        universidades = [d for d in filas if d.entidad in ("UNR", "OTRA_UNIVERSIDAD")]
        if len(universidades) != UNIVERSIDADES_NACIONALES:
            raise ValueError(f"{indicador} {anio}: se esperaban {UNIVERSIDADES_NACIONALES} universidades, "
                             f"hay {len(universidades)}")
        unr[indicador] = next(d for d in filas if d.entidad == "UNR")
        sistema[indicador] = universidades
        no_asignado[indicador] = next(d for d in filas if d.entidad == "CREDITO_NO_ASIGNADO")

    etiquetas = {"credito_asignado": "Crédito asignado (ley)", "credito_vigente": "Crédito vigente",
                 "devengado": "Devengado"}
    for indicador, etiqueta in etiquetas.items():
        eje.cifras.append(_directa(f"unr-{indicador}", f"UNR — {etiqueta}", unr[indicador]))
    eje.cifras.append(_cociente("unr-ejecucion", "UNR — Devengado sobre vigente",
                                eje.cifra("unr-devengado"), eje.cifra("unr-credito_vigente")))

    sis_vig = _suma("sistema-credito_vigente", "61 universidades — Crédito vigente", sistema["credito_vigente"])
    sis_dev = _suma("sistema-devengado", "61 universidades — Devengado", sistema["devengado"])
    eje.cifras += [sis_vig, sis_dev,
                   _cociente("sistema-ejecucion", "61 universidades — Devengado sobre vigente", sis_dev, sis_vig)]

    eje.cifras.append(_directa("no-asignado-credito_vigente",
                               "Crédito vigente no asignado a ninguna universidad", no_asignado["credito_vigente"]))
    eje.cifras.append(_directa("no-asignado-devengado",
                               "Devengado del crédito no asignado", no_asignado["devengado"]))

    corte = date.fromisoformat(unr["devengado"].dimensiones["fecha_corte"])
    dias_anio = (date(corte.year, 12, 31) - date(corte.year, 1, 1)).days + 1
    dia = corte.timetuple().tm_yday
    eje.cifras.append(Cifra("anio-transcurrido", f"Año transcurrido al {corte:%d/%m/%Y}",
                            Decimal(dia) / Decimal(dias_anio) * 100, "porcentaje", anio, (unr["devengado"],),
                            calculo=f"Día {dia} de {dias_anio} (fecha de corte del dato)"))

    _arts_3_4(repo, eje, anio, "SISTEMA_UNIVERSITARIO", "arts34-", "Todas las universidades", detalle=True)
    _arts_3_4(repo, eje, anio, "UNR", "unr-arts34-", "UNR", detalle=True)

    eje.supuestos = [
        "Transferencias del Tesoro (Programa 26); no incluye recursos propios.",
        "El año transcurrido es una referencia: las transferencias no son parejas mes a mes.",
        "El crédito sin universidad asignada va aparte (ADR 0013).",
        "Arts. 3 y 4: lo exigido se calcula sobre lo devengado, porque en 2024 y 2025 el crédito vigente de cada "
        "universidad fue el de 2023 prorrogado y los aumentos se pagaron por fuera (ADR 0020).",
        "Arts. 3 y 4: la cifra principal es la suma de las universidades nacionales; la UNR va como caso de detalle "
        "(ADR 0021).",
    ]
    _con_normas(eje, lambda c: _norma_transferencias(c.clave, anio))
    eje.pendientes = ["Los arts. 3 y 4 no fijan una fórmula para 2026: lo transferido en 2026 se muestra sin "
                      "un «exigido»."]
    return eje


def _norma_transferencias(clave: str, anio: str) -> tuple[Norma, ...]:
    if "arts34-" not in clave:
        return ()
    resto = clave.split("arts34-", 1)[1]
    if resto == "piso-mes":
        return (NORMA_ART3, NORMA_ART4)
    if resto.startswith(("ref-", "acum-piso-", "acum-ref-", "piso-", "relacion-piso-")) or resto == f"relacion-{anio}":
        return (NORMA_REFERENCIA,)
    if resto == "ipc-art3":
        return (NORMA_ART3,)
    if re.fullmatch(r"(exigido|brecha|relacion|faltante)(-b)?|exigido-bim\d|acum-exigido-\d\d", resto):
        return (NORMA_ART3, NORMA_ART4)
    return ()


def _con_normas(eje: Eje, regla) -> None:
    eje.cifras = [replace(c, normas=regla(c)) if regla(c) else c for c in eje.cifras]


CRITERIO_PARTIDA = {
    "nivel_sep_2024": ("La ley no dice de qué mes es el monto a actualizar. Tomamos septiembre de 2024, el último "
                       "nivel estable antes del período que actualiza la ley."),
    "promedio_2024": ("La ley no dice de qué mes es el monto a actualizar. Esta es la opción alternativa: el promedio "
                      "de 2024. La principal es septiembre de 2024."),
}


def _arts_3_4(repo: Repositorio, eje: Eje, anio: str, entidad: str, prefijo: str, quien: str,
              detalle: bool = False) -> None:
    """Ley 27.795, arts. 3 y 4: lo que correspondía transferir en 2025 frente a lo transferido (ADR 0020).

    `entidad` es SISTEMA_UNIVERSITARIO (cifra principal) o UNR (caso de detalle, ADR 0021). Con `detalle`, agrega
    la partida B, el IPC del art. 3, los bimestres y lo transferido en el año en curso, para el artículo."""
    ipc = lentes.serie_por_periodo(repo.buscar(indicador="ipc_nivel_general"))
    devengado = [d for d in repo.buscar(entidad=entidad, indicador="devengado") if "actividad_id" in d.dimensiones]
    transferido = lentes.transferido_arts_3_4(devengado, "2025")
    eje.cifras.append(Cifra(f"{prefijo}transferido", f"{quien}: transferido en 2025",
                            transferido.valor, "ARS corrientes", "2025", transferido.fuentes,
                            calculo="Devengado de enero a diciembre, actividades 14, 15, 16 y 25"))

    serie_2024 = tuple((mes, sum((d.valor for d in lentes._de_actividades(devengado) if d.periodo == mes), Decimal(0)))
                       for mes in lentes._meses("2024-01", "2024-12"))
    opciones = (("nivel_sep_2024", ""), ("promedio_2024", "-b")) if detalle else (("nivel_sep_2024", ""),)
    for opcion, sufijo in opciones:
        partida = lentes.partida_arts_3_4(devengado, opcion)
        nombre = lentes.PARTIDAS_ARTS_3_4[opcion]
        eje.cifras.append(Cifra(f"{prefijo}partida{sufijo}", f"{quien}: {nombre}", partida.valor,
                                "ARS corrientes", lentes.MES_PARTIDA_ARTS_3_4 if opcion == "nivel_sep_2024" else "2024",
                                partida.fuentes, criterio=CRITERIO_PARTIDA[opcion], serie=serie_2024,
                                calculo=("Lo transferido en septiembre de 2024 para gastos de funcionamiento: la suma "
                                         "de las cuatro actividades del Programa 26 que nombra la ley"
                                         if opcion == "nivel_sep_2024" else
                                         "Lo transferido en 2024 para gastos de funcionamiento (las cuatro actividades "
                                         "del Programa 26 que nombra la ley), dividido por 12")))
        exigido = lentes.exigido_arts_3_4(partida, ipc)
        eje.cifras.append(Cifra(f"{prefijo}exigido{sufijo}",
                                f"{quien}: correspondían en 2025 según la ley" + (" (partida: promedio de 2024)" if sufijo else ""),
                                exigido.valor, "ARS corrientes", "2025", exigido.fuentes,
                                calculo="Partida mensual × inflación de mayo a diciembre de 2024 (art. 3) × inflación acumulada al inicio de cada bimestre de 2025 (art. 4), sumado mes a mes."))
        eje.cifras.append(Cifra(f"{prefijo}brecha{sufijo}",
                                f"{quien}: cuánto más correspondía que lo transferido" + (" (partida: promedio de 2024)" if sufijo else ""),
                                (exigido.valor / transferido.valor - 1) * 100, "porcentaje", "2025",
                                exigido.fuentes + transferido.fuentes,
                                calculo="(Correspondía ÷ transferido − 1) × 100"))
        eje.cifras.append(Cifra(f"{prefijo}relacion{sufijo}",
                                f"{quien}: lo transferido frente a lo que correspondía"
                                + (" (partida: promedio de 2024)" if sufijo else ""),
                                (transferido.valor / exigido.valor - 1) * 100, "porcentaje", "2025",
                                exigido.fuentes + transferido.fuentes,
                                calculo="(Transferido ÷ correspondía − 1) × 100"))
        eje.cifras.append(Cifra(f"{prefijo}faltante{sufijo}",
                                f"{quien}: diferencia en 2025" + (" (partida: promedio de 2024)" if sufijo else ""),
                                exigido.valor - transferido.valor, "ARS corrientes", "2025",
                                exigido.fuentes + transferido.fuentes, calculo="Correspondía − transferido"))

    # Acumulado mes a mes de 2025, para el gráfico y su tabla (cada punto es una Cifra con ficha).
    partida = lentes.partida_arts_3_4(devengado, "nivel_sep_2024")
    meses = lentes._meses("2025-01", "2025-12")
    acum_exigido = acum_transferido = Decimal(0)
    fuentes_exigido: tuple[Dato, ...] = ()
    fuentes_transferido: tuple[Dato, ...] = ()
    serie = []
    for mes, exigido_mes in zip(meses, lentes.meses_art4(partida, ipc)):
        datos_mes = tuple(d for d in transferido.fuentes if d.periodo == mes)
        acum_exigido += exigido_mes.valor
        acum_transferido += sum(d.valor for d in datos_mes)
        fuentes_exigido = tuple({d.id: d for d in fuentes_exigido + exigido_mes.fuentes}.values())
        fuentes_transferido += datos_mes
        hasta = f"enero a {MESES_LARGOS[int(mes[5:]) - 1]} de 2025" if mes != "2025-01" else "enero de 2025"
        eje.cifras.append(Cifra(f"{prefijo}acum-exigido-{mes[5:]}", f"{quien}: la ley manda reconocer por {hasta}",
                                acum_exigido, "ARS corrientes", mes, fuentes_exigido,
                                calculo="Partida mensual × inflación de mayo a diciembre de 2024 (art. 3) × inflación acumulada al inicio de cada bimestre de 2025 (art. 4), sumado mes a mes."))
        eje.cifras.append(Cifra(f"{prefijo}acum-transferido-{mes[5:]}", f"{quien}: transferido, {hasta}",
                                acum_transferido, "ARS corrientes", mes, fuentes_transferido,
                                calculo="Devengado acumulado, actividades 14, 15, 16 y 25"))
        serie.append({"mes": mes_legible(mes), "exigido": float(acum_exigido) / 1e6,
                      "transferido": float(acum_transferido) / 1e6})
    eje.detalle.setdefault("acumulado", {})[prefijo] = serie

    # Año en curso: la ley no fija cuánto corresponde. Referencia en gris: la regla del art. 4 extendida (ADR 0024).
    referencia = lentes.referencia_art4(partida, ipc, anio)
    del_anio = [d for d in devengado if d.periodo.startswith(f"{anio}-")
                and d.dimensiones.get("actividad_id") in lentes.ACTIVIDADES_ARTS_3_4]
    completos = sorted({d.periodo for d in del_anio if "Mes en curso" not in d.nota})
    ventana = lentes._meses(f"{anio}-01", f"{anio}-12")[:min(len(referencia), len(completos))]
    if anio != "2025" and ventana:
        hasta = mes_largo(ventana[-1])
        # Piso: el monto mensual que la ley fija para fin de 2025 (último bimestre del art. 4), sin actualizar.
        ultimo_bim = lentes.bimestres_art4(partida, ipc)[-1]
        piso_mes = ultimo_bim.valor / 2
        acum_ref = acum_tr = acum_piso = Decimal(0)
        f_ref: tuple[Dato, ...] = ()
        f_tr: tuple[Dato, ...] = ()
        serie_anio = []
        for mes, ref_mes in zip(ventana, referencia):
            datos_mes = tuple(d for d in del_anio if d.periodo == mes)
            acum_ref += ref_mes.valor
            acum_piso += piso_mes
            acum_tr += sum(d.valor for d in datos_mes)
            f_ref = tuple({d.id: d for d in f_ref + ref_mes.fuentes}.values())
            f_tr += datos_mes
            etiqueta = f"enero a {MESES_LARGOS[int(mes[5:]) - 1]} de {anio}" if mes[5:] != "01" else f"enero de {anio}"
            eje.cifras.append(Cifra(f"{prefijo}acum-ref-{mes}", f"{quien}: referencia, {etiqueta}", acum_ref,
                                    "ARS corrientes", mes, f_ref, calculo=CALC_REFERENCIA))
            eje.cifras.append(Cifra(f"{prefijo}acum-tr-{mes}", f"{quien}: transferido, {etiqueta}", acum_tr,
                                    "ARS corrientes", mes, f_tr, calculo="Devengado acumulado, actividades 14, 15, 16 y 25"))
            eje.cifras.append(Cifra(f"{prefijo}acum-piso-{mes}", f"{quien}: piso de diciembre de 2025, {etiqueta}",
                                    acum_piso, "ARS corrientes", mes, ultimo_bim.fuentes,
                                    calculo="Monto mensual de noviembre-diciembre de 2025 según el art. 4, sin actualizar, sumado mes a mes."))
            serie_anio.append({"mes": mes_legible(mes), "exigido": float(acum_piso) / 1e6,
                               "transferido": float(acum_tr) / 1e6})
        eje.cifras.append(Cifra(f"{prefijo}ref-{anio}", f"{quien}: referencia, enero a {hasta}", acum_ref,
                                "ARS corrientes", anio, f_ref, calculo=CALC_REFERENCIA))
        eje.cifras.append(Cifra(f"{prefijo}tr-{anio}", f"{quien}: transferido, enero a {hasta}", acum_tr,
                                "ARS corrientes", anio, f_tr, calculo="Devengado de los meses completos"))
        eje.cifras.append(Cifra(f"{prefijo}relacion-{anio}",
                                f"{quien}: lo transferido frente a la referencia, enero a {hasta}",
                                (acum_tr / acum_ref - 1) * 100, "porcentaje", anio, f_ref + f_tr,
                                calculo="(Transferido ÷ referencia − 1) × 100. La referencia no es un monto que fije la ley."))
        eje.detalle.setdefault("acumulado_actual", {})[prefijo] = serie_anio
        eje.detalle["ventana_actual"] = f"enero a {hasta}"
        eje.detalle["meses_actual"] = [m[5:] for m in ventana]
        eje.cifras.append(Cifra(f"{prefijo}piso-mes", f"{quien}: monto mensual de noviembre-diciembre de 2025 según la ley",
                                piso_mes, "ARS corrientes", "2025-12", ultimo_bim.fuentes,
                                calculo="Último bimestre del art. 4 ÷ 2"))
        # Lectura principal para el año en curso (ADR 0024): el piso de diciembre de 2025, sin actualizar.
        piso = acum_piso
        eje.cifras.append(Cifra(f"{prefijo}piso-{anio}", f"{quien}: piso de diciembre de 2025, enero a {hasta}", piso,
                                "ARS corrientes", anio, ultimo_bim.fuentes,
                                calculo=f"Monto mensual de noviembre-diciembre de 2025 según el art. 4 × {len(ventana)} "
                                        "meses, sin actualizar. La ley no lo pide: es otra lectura posible (ADR 0024)."))
        eje.cifras.append(Cifra(f"{prefijo}relacion-piso-{anio}",
                                f"{quien}: lo transferido frente al piso de diciembre de 2025, enero a {hasta}",
                                (acum_tr / piso - 1) * 100, "porcentaje", anio, ultimo_bim.fuentes + f_tr,
                                calculo="(Transferido ÷ piso − 1) × 100. El piso no es un monto que fije la ley."))

    if not detalle:
        return

    f3 = lentes.factor_art3(ipc)
    eje.cifras.append(Cifra(f"{prefijo}ipc-art3", "Inflación de mayo a diciembre de 2024",
                            (f3.valor - 1) * 100, "porcentaje", "2024-12", f3.fuentes,
                            calculo="IPC de diciembre de 2024 ÷ IPC de abril de 2024 − 1"))

    partida = lentes.partida_arts_3_4(devengado, "nivel_sep_2024")
    meses_2025 = lentes._meses("2025-01", "2025-12")
    for i, bimestre in enumerate(lentes.bimestres_art4(partida, ipc), start=1):
        meses = meses_2025[2 * i - 2:2 * i]
        etiqueta = f"{MESES_LARGOS[int(meses[0][5:]) - 1]} y {MESES_LARGOS[int(meses[1][5:]) - 1]} de 2025"
        eje.cifras.append(Cifra(f"{prefijo}exigido-bim{i}", f"{quien}: correspondía, {etiqueta}", bimestre.valor,
                                "ARS corrientes", meses[1], bimestre.fuentes,
                                calculo="Partida × 2 meses × inflación acumulada al inicio del bimestre"))
        datos = [d for d in transferido.fuentes if d.periodo in meses]
        eje.cifras.append(Cifra(f"{prefijo}transferido-bim{i}", f"{quien}: transferido, {etiqueta}",
                                sum(d.valor for d in datos), "ARS corrientes", meses[1], tuple(datos),
                                calculo="Devengado de los dos meses"))

    # Transferido mes a mes en 2025 y en el año en curso: si en el año en curso se pagó algo a cuenta de 2025,
    # no entra en la comparación (que es por ejercicio); la tabla deja ver los saltos (ADR 0020).
    meses_tabla = []
    for a in ("2025", anio):
        for mes in lentes._meses(f"{a}-01", f"{a}-12"):
            datos = tuple(d for d in devengado if d.periodo == mes
                          and d.dimensiones.get("actividad_id") in lentes.ACTIVIDADES_ARTS_3_4)
            if not datos:
                continue
            parcial = any("Mes en curso" in d.nota for d in datos)
            eje.cifras.append(Cifra(f"{prefijo}mes-{mes}", f"{quien}: transferido en {mes_largo(mes)}",
                                    sum(d.valor for d in datos), "ARS corrientes", mes, datos,
                                    calculo="Devengado del mes, actividades 14, 15, 16 y 25",
                                    aviso="Mes en curso a la fecha de corte del dato." if parcial else ""))
            if mes[5:] not in meses_tabla:
                meses_tabla.append(mes[5:])
    eje.detalle["meses_tabla"] = meses_tabla

    actual = lentes.transferido_arts_3_4(devengado, anio)
    if actual.fuentes:
        corte = actual.fuentes[0].dimensiones["fecha_corte"]
        eje.cifras.append(Cifra(f"{prefijo}transferido-actual",
                                f"{quien}: transferido en {anio}, hasta el {corte}",
                                actual.valor, "ARS corrientes", anio, actual.fuentes,
                                calculo="Devengado del año, actividades 14, 15, 16 y 25"))
        eje.detalle["corte_actual"] = mes_largo(corte[:7])

    sin_asignar = [d for d in repo.buscar(entidad="CREDITO_NO_ASIGNADO", indicador="devengado")
                   if d.dimensiones.get("actividad_id") in lentes.ACTIVIDADES_ARTS_3_4 and d.periodo.startswith("2025-")]
    if sin_asignar and entidad == "SISTEMA_UNIVERSITARIO":
        eje.cifras.append(Cifra(f"{prefijo}sin-asignar", "Transferido en 2025 sin universidad asignada", sum(d.valor for d in sin_asignar), "ARS corrientes", "2025",
                                tuple(sin_asignar), calculo="Devengado de «Universidades sin Discriminar», actividades 14, 15, 16 y 25"))


CALC_REFERENCIA = ("La regla del art. 4 extendida a este año: partida de septiembre de 2024 × inflación de mayo a "
                   "diciembre de 2024 × inflación acumulada al inicio de cada bimestre. La ley no lo pide: es una "
                   "referencia (ADR 0024).")


MESES_ABREV = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
                "noviembre", "diciembre"]


def mes_legible(periodo: str) -> str:
    """Forma compacta, para ejes de gráficos y tooltips: «ago-2026»."""
    anio, mes = periodo.split("-")
    return f"{MESES_ABREV[int(mes) - 1]}-{anio}"


def mes_largo(periodo: str) -> str:
    """Forma para leer en un texto: «agosto de 2026»."""
    anio, mes = periodo.split("-")
    return f"{MESES_LARGOS[int(mes) - 1]} de {anio}"


def _aviso_vigencia(punto: lentes.Punto) -> str:
    if punto.vigencia == Vigencia.PROPIA:
        return ""
    mes, desde = mes_largo(punto.periodo), mes_largo(punto.fuentes[0].periodo)
    if punto.vigencia == Vigencia.CONFIRMADA:
        return f"Para {mes} rige la escala de {desde}: un documento confirma que no hubo cambios."
    return (f"No hay escala publicada para {mes}. Usamos la de {desde}, la última disponible; "
            f"si hubo un aumento en el medio, este número cambia.")


def _desde_resultado(clave: str, etiqueta: str, unidad: str, periodo: str, r: lentes.Resultado, calculo: str,
                     aviso: str = "") -> Cifra:
    return Cifra(clave, etiqueta, r.valor, unidad, periodo, r.fuentes, calculo, aviso)


def eje_salario(repo: Repositorio) -> Eje:
    eje = Eje("salario", "Salario docente", "¿Cuánto cobra un docente frente a lo que exige la ley?")
    grillas = repo.buscar(entidad="CARGO_TESTIGO", indicador="salario_basico")
    ipc = lentes.serie_por_periodo(repo.buscar(indicador="ipc_nivel_general"))
    confirmados = {m for e in repo.eventos_de("salario") for m in e.confirma_vigencia}
    ultimo_ipc = max(ipc)
    puntos = {p.periodo: p for p in lentes.serie_vigente(grillas, ultimo_ipc, confirmados)}
    mes, legible = ultimo_ipc, mes_largo(ultimo_ipc)
    pagado = puntos[mes]
    aviso = _aviso_vigencia(pagado)

    eje.cifras.append(_desde_resultado("brecha-art5", f"Aumento necesario para cumplir el art. 5 ({legible})",
                                       "porcentaje", mes, lentes.brecha_art5(puntos, ipc, mes),
                                       "(salario exigido ÷ básico pagado − 1) × 100", aviso))
    eje.cifras.append(Cifra("pagado", f"Básico pagado ({legible})", pagado.valor, "ARS corrientes", mes,
                            pagado.fuentes, aviso=aviso))
    eje.cifras.append(_desde_resultado("exigido", f"Salario que exige el art. 5 ({legible})", "ARS corrientes", mes,
                                       lentes.salario_art5(puntos, ipc, mes),
                                       "básico nov-2023 × IPC del mes ÷ IPC nov-2023"))
    base = puntos[lentes.MES_PREVIO_ART5]
    eje.cifras.append(Cifra("basico-nov2023", "Básico de noviembre de 2023", base.valor, "ARS corrientes",
                            lentes.MES_PREVIO_ART5, base.fuentes))
    eje.cifras.append(Cifra("aumento-basico", f"Aumento del básico, de noviembre de 2023 a {legible}",
                            (pagado.valor / base.valor - 1) * 100, "porcentaje", mes, pagado.fuentes + base.fuentes,
                            f"(básico {legible} ÷ básico nov-2023 − 1) × 100", aviso))
    eje.cifras.append(Cifra("aumento-ipc", f"Aumento de precios (IPC), de noviembre de 2023 a {legible}",
                            (ipc[mes].valor / ipc[lentes.MES_PREVIO_ART5].valor - 1) * 100, "porcentaje", mes,
                            (ipc[mes], ipc[lentes.MES_PREVIO_ART5]), f"(IPC {legible} ÷ IPC nov-2023 − 1) × 100"))
    eje.cifras.append(_desde_resultado("real-nov_2023", f"Salario real de {legible} frente a noviembre de 2023", "porcentaje",
                                       mes, lentes.variacion_real(puntos, ipc, mes, "nov_2023"),
                                       "(salario real del mes ÷ salario real de nov-2023 − 1) × 100", aviso))

    # Billete: cuánto compra el sueldo de cada mes frente al de nov-2023 (ADR 0023).
    billete = []
    base_ipc = ipc[lentes.MES_PREVIO_ART5]
    for periodo in sorted(p for p in puntos if lentes.MES_PREVIO_ART5 <= p <= mes):
        punto, nombre = puntos[periodo], mes_largo(periodo)
        variacion = lentes.variacion_real(puntos, ipc, periodo, "nov_2023")
        aviso_mes = _aviso_vigencia(punto)
        rige = periodo >= lentes.MES_VIGENCIA_ART5
        fuentes = variacion.fuentes + (base_ipc,)
        calculo = (f"(básico de {nombre} ÷ IPC de {nombre}) ÷ (básico de noviembre de 2023 ÷ IPC de noviembre "
                   f"de 2023)")
        eje.cifras.append(Cifra(f"compra-{periodo}", f"Lo que compra el sueldo de {nombre}, frente al de noviembre de 2023",
                                100 + variacion.valor, "porcentaje", periodo, fuentes, f"{calculo} × 100", aviso_mes))
        eje.cifras.append(Cifra(f"poder-{periodo}", f"Poder de compra del sueldo de {nombre} frente a noviembre de 2023",
                                variacion.valor, "porcentaje", periodo, fuentes, f"({calculo} − 1) × 100", aviso_mes))
        billete.append({"periodo": periodo, "mes": nombre, "corto": mes_legible(periodo),
                        "proporcion": float(1 + variacion.valor / 100), "rige": rige, "aviso": aviso_mes})

    for p in puntos.values():
        # «referencia»: el sueldo de nov-2023 actualizado por IPC, para todos los meses desde nov-2023.
        # «exigido»: lo mismo, pero solo desde que el art. 5 rige (nov-2025).
        referencia = (lentes.salario_art5(puntos, ipc, p.periodo).valor
                      if p.periodo >= lentes.MES_PREVIO_ART5 else None)
        exigido = referencia if p.periodo >= lentes.MES_VIGENCIA_ART5 else None
        eje.serie.append({"periodo": p.periodo, "pagado": p.valor, "exigido": exigido, "referencia": referencia,
                          "vigencia": p.vigencia.value})

    sin_grilla = [p for p in puntos.values() if p.vigencia != Vigencia.PROPIA]
    ultima_grilla = max(grillas, key=lambda d: d.periodo)
    eje.detalle = {
        "desde": mes_largo(min(puntos)), "hasta_grilla": mes_largo(ultima_grilla.periodo),
        "meses_con_grilla": len(grillas),
        "sin_grilla": [(mes_largo(p.periodo), p.vigencia.value, mes_largo(p.fuentes[0].periodo))
                       for p in sin_grilla],
        "ultima_grilla": ultima_grilla, "ipc": ipc[mes], "ultimo_ipc": legible,
        "grillas_sin_ipc": [mes_largo(d.periodo) for d in grillas if d.periodo > mes],
        "billete": billete,
        "vigencia_art5": mes_largo(lentes.MES_VIGENCIA_ART5),
    }
    _con_normas(eje, lambda c: (NORMA_ART5,) if c.clave in ("brecha-art5", "exigido") or (
        c.clave.startswith("poder-") and c.periodo >= lentes.MES_VIGENCIA_ART5) else ())
    eje.eventos = repo.eventos_de("salario")
    eje.supuestos = [
        "Profesor adjunto, dedicación exclusiva, sin antigüedad: salario básico.",
        "Lo que exige el art. 5: el básico de nov-2023 actualizado por IPC.",
        "Último mes con IPC publicado.",
    ]
    eje.pendientes = ["Instructivos de jul-2026 y ago-2026 (no publicados en el portal de la UNR)."]
    return eje


def eje_control(repo: Repositorio) -> Eje:
    eje = Eje("control", "Control", "¿Quién audita a las universidades?")
    eje.eventos = repo.eventos_de("control")
    eje.pendientes = ["Informe AGN 161/2022 (original).", "Informes individuales de la Unidad de Auditoría Interna."]
    return eje


# Sellos del recorrido «hecho por hecho» (ADR 0031): nombran el acto, no lo califican, y se reparten entre
# Congreso, Poder Ejecutivo y Justicia. El detalle evita leer el sello fuera de contexto; sin cifras, que van con ficha.
SELLOS_LEY = {
    "ley-2024-veto-firme": ("Veto firme", "Ley 27.757 · 2024"),
    "ley-27795-sancion": ("Sancionada", "Senado"),
    "ley-27795-veto": ("Vetada", "Decreto 647/2025"),
    "ley-27795-insistencia-diputados": ("Veto rechazado", "Diputados, por dos tercios"),
    "ley-27795-insistencia-senado": ("Es ley", "Senado, por dos tercios"),
    "ley-27795-promulgacion": ("Promulgada y suspendida", "Decreto 759/2025"),
    "ley-27795-cautelar": ("Cautelar admitida", "Arts. 5 y 6"),
    "ley-27795-suspension-cautelar": ("Cautelar suspendida", "Mientras se tramita el recurso"),
    "ley-27795-acuerdo-junio-2026": ("Acuerdo firmado", "Gobierno, CIN y gremios"),
    "ley-27795-corte": ("Cautelar firme", "Corte Suprema"),
    "ley-27795-fallo-fondo": ("Inconstitucional", "Suspensión del Dto. 759/2025 · 1.ª instancia"),
    "ley-27795-apelacion": ("Apelada", "Sentencia de fondo"),
    "ley-27795-multa": ("Multa diaria", "Jefatura de Gabinete"),
}


def eje_ley(repo: Repositorio) -> Eje:
    eje = Eje("ley", "Ley 27.795", "¿En qué estado está la ley de financiamiento universitario?")
    eje.eventos = repo.eventos_de("ley")
    ids = {e.id for e in eje.eventos}
    faltan = set(SELLOS_LEY) - ids
    if faltan:
        raise ValueError(f"Sellos de eventos que no existen en ley.yaml: {sorted(faltan)}")
    eje.detalle = {"sellos": SELLOS_LEY}
    eje.supuestos = []
    eje.pendientes = ["Lente por artículo (arts. 3, 4 y 5) para la UNR: requiere Presupuesto Abierto 2024-2025, "
                      "IPC y grillas salariales.",
                      "Textos de las resoluciones judiciales del expediente 39475/2025."]
    return eje


CONSTRUCTORES = {
    "salario": eje_salario,
    "ley": eje_ley,
    "ejecucion": eje_ejecucion,
    "control": eje_control,
}


def construir_eje(repo: Repositorio, clave: str) -> Eje:
    return CONSTRUCTORES[clave](repo)


def construir_ejes(repo: Repositorio) -> dict[str, Eje]:
    return {clave: construir(repo) for clave, construir in CONSTRUCTORES.items()}
