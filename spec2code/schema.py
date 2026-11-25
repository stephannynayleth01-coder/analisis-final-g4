"""Modelo de análisis intermedio (IR).

El LLM NO escribe PlantUML ni código: solo llena este modelo a partir de la spec.
Los diagramas y el código se generan después, de forma determinista, con plantillas.
Por eso cualquier defecto en los diagramas nace en este modelo (o en la spec).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

TipoDato = Literal["texto", "entero", "decimal", "booleano", "fecha", "lista"]
TipoRetorno = Literal["ninguno", "texto", "entero", "decimal", "booleano", "fecha", "lista"]
TipoRelacion = Literal["asociacion", "agregacion", "composicion"]
Multiplicidad = Literal["1", "0..1", "*", "0..*", "1..*"]

_PALABRAS_RESERVADAS = {
    "class", "def", "import", "from", "return", "int", "float", "new", "public", "private",
    "static", "void", "if", "else", "for", "while", "in", "is", "not", "and", "or", "none",
    "true", "false", "lambda", "global", "try", "except", "package", "interface", "default",
}


def _ascii(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def a_identificador(texto: str) -> str:
    """'poción mágica' -> 'PocionMagica' (nombre de clase válido)."""
    partes = re.findall(r"[A-Za-z0-9]+", _ascii(texto))
    ident = "".join(p[:1].upper() + p[1:] for p in partes)
    if ident and ident[0].isdigit():
        ident = "C" + ident
    return ident or "Sin_nombre"


def a_snake(texto: str) -> str:
    """'puntosDeVida' / 'Puntos de vida' -> 'puntos_de_vida'."""
    sin = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", _ascii(texto))
    partes = re.findall(r"[A-Za-z0-9]+", sin)
    snake = "_".join(p.lower() for p in partes) or "campo"
    if snake[0].isdigit():
        snake = "n_" + snake
    if snake in _PALABRAS_RESERVADAS:
        snake += "_"
    return snake


def norm_cu(valor: str) -> str:
    m = re.fullmatch(r"\s*CU[-_ ]?(\d+)\s*", valor, flags=re.I)
    return f"CU-{int(m.group(1)):02d}" if m else valor.strip()


def norm_req(valor: str) -> str:
    m = re.fullmatch(r"\s*(RNF|RF|RN)[-_ ]?(\d+)\s*", valor, flags=re.I)
    return f"{m.group(1).upper()}-{int(m.group(2)):02d}" if m else valor.strip()


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Trazable(_Base):
    req_ids: list[str] = Field(
        default_factory=list,
        description="IDs de la spec que justifican este elemento (p. ej. RF-01, RN-02). Solo IDs existentes.",
    )

    @field_validator("req_ids")
    @classmethod
    def _norm_reqs(cls, v: list[str]) -> list[str]:
        return list(dict.fromkeys(norm_req(x) for x in v))


class Actor(Trazable):
    nombre: str = Field(description="Nombre del actor tal como aparece en la spec")
    descripcion: str = ""


class CasoUso(Trazable):
    id: str = Field(description="Identificador CU-01, CU-02, ...")
    nombre: str = Field(description="Verbo + objeto, p. ej. 'Agregar objeto'")
    actores: list[str] = Field(description="Nombres de actores (deben existir en 'actores')")
    descripcion: str = ""
    incluye: list[str] = Field(default_factory=list, description="IDs de CU incluidos (<<include>>)")
    extiende: list[str] = Field(default_factory=list, description="IDs de CU que este extiende (<<extend>>)")

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        return norm_cu(v)

    @field_validator("incluye", "extiende")
    @classmethod
    def _ids(cls, v: list[str]) -> list[str]:
        return [norm_cu(x) for x in v]


class Atributo(_Base):
    nombre: str
    tipo: TipoDato = "texto"
    es_clave: bool = Field(default=False, description="True si identifica de forma única a la entidad")

    @field_validator("nombre")
    @classmethod
    def _n(cls, v: str) -> str:
        return a_snake(v)


class Metodo(Trazable):
    nombre: str = Field(description="Verbo en minúsculas con guiones bajos, p. ej. 'equipar_arma'")
    descripcion: str = ""
    retorno: TipoRetorno = "ninguno"

    @field_validator("nombre")
    @classmethod
    def _n(cls, v: str) -> str:
        return a_snake(v)


class Entidad(Trazable):
    nombre: str = Field(description="Sustantivo en singular, PascalCase, sin tildes")
    es_abstracta: bool = False
    hereda_de: Optional[str] = Field(default=None, description="Nombre de la entidad padre, si aplica")
    atributos: list[Atributo] = Field(default_factory=list)
    metodos: list[Metodo] = Field(default_factory=list)

    @field_validator("nombre")
    @classmethod
    def _n(cls, v: str) -> str:
        return a_identificador(v)

    @field_validator("hereda_de")
    @classmethod
    def _h(cls, v: Optional[str]) -> Optional[str]:
        return a_identificador(v) if v and v.strip() else None


class Relacion(Trazable):
    desde: str = Field(description="Entidad origen (en agregación/composición, el 'todo')")
    hasta: str = Field(description="Entidad destino")
    tipo: TipoRelacion = "asociacion"
    multiplicidad_desde: Multiplicidad = "1"
    multiplicidad_hasta: Multiplicidad = "1"
    etiqueta: str = ""

    @field_validator("desde", "hasta")
    @classmethod
    def _n(cls, v: str) -> str:
        return a_identificador(v)


class Mensaje(_Base):
    de: str
    a: str
    texto: str


class Secuencia(Trazable):
    caso_uso: str = Field(description="ID del caso de uso que ilustra, p. ej. CU-01")
    mensajes: list[Mensaje] = Field(description="Entre 3 y 8 mensajes en orden")

    @field_validator("caso_uso")
    @classmethod
    def _cu(cls, v: str) -> str:
        return norm_cu(v)


class ModeloAnalisis(_Base):
    modulo: str = Field(description="Nombre del módulo analizado")
    actores: list[Actor]
    casos_uso: list[CasoUso]
    entidades: list[Entidad]
    relaciones: list[Relacion] = Field(default_factory=list)
    secuencias: list[Secuencia] = Field(default_factory=list)

    def canonizar(self) -> "ModeloAnalisis":
        """Unifica mayúsculas/tildes entre referencias y nombres definidos (sin inventar nada)."""
        actores = {a.nombre.strip().casefold(): a.nombre.strip() for a in self.actores}
        entidades = {a_identificador(e.nombre): e.nombre for e in self.entidades}

        def actor(n: str) -> str:
            return actores.get(n.strip().casefold(), n.strip())

        def participante(n: str) -> str:
            if n.strip().casefold() in actores:
                return actores[n.strip().casefold()]
            return entidades.get(a_identificador(n), n.strip())

        for a in self.actores:
            a.nombre = a.nombre.strip()
        for cu in self.casos_uso:
            cu.actores = [actor(n) for n in cu.actores]
        for s in self.secuencias:
            for msg in s.mensajes:
                msg.de, msg.a = participante(msg.de), participante(msg.a)
        return self
