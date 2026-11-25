"""Revisión determinista de la especificación (sin LLM).

Detecta problemas típicos de una spec antes de gastar una corrida del modelo:
secciones faltantes, IDs mal formados o repetidos, requerimientos sin criterio de
aceptación y lenguaje ambiguo. Es un apoyo: no sustituye tu criterio de analista.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

SECCIONES = {
    "actores": "Actores",
    "requerimientos funcionales": "Requerimientos funcionales",
    "requerimientos no funcionales": "Requerimientos no funcionales",
    "reglas de negocio": "Reglas de negocio",
}

AMBIGUAS = [
    "rápido", "rapido", "fácil", "facil", "amigable", "adecuado", "adecuada", "eficiente",
    "apropiado", "apropiada", "flexible", "robusto", "robusta", "intuitivo", "intuitiva",
    "óptimo", "optimo", "buen rendimiento", "lo antes posible", "cuando sea necesario",
    "según corresponda", "segun corresponda", "etc", "y/o",
]

_DEF = re.compile(r"^\s*[-*+]\s+\*{0,2}(RF|RNF|RN)-(\d+)\*{0,2}[\s:.\-–]*(.*)$")
_ID = re.compile(r"\b(RNF|RF|RN)-(\d+)\b")


def _norm(texto: str) -> str:
    sin = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", " ", sin.lower()).strip()


@dataclass
class InformeSpec:
    definiciones: dict[str, str] = field(default_factory=dict)  # id -> texto
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def ids(self) -> set[str]:
        return set(self.definiciones)


def revisar_spec(texto: str) -> InformeSpec:
    inf = InformeSpec()
    lineas = texto.splitlines()

    # 1) Secciones
    titulos = [_norm(re.sub(r"^#+", "", ln)) for ln in lineas if ln.lstrip().startswith("#")]
    for clave, nombre in SECCIONES.items():
        if not any(clave in t for t in titulos):
            inf.errores.append(f"Falta la sección '{nombre}'.")

    # 2) Definiciones de requerimientos (y su bloque de texto)
    actual = None
    bloques: dict[str, list[str]] = {}
    for ln in lineas:
        m = _DEF.match(ln)
        if m:
            tipo, num, resto = m.groups()
            rid = f"{tipo}-{num}"
            if len(num) != 2:
                inf.errores.append(f"ID mal formado '{rid}': usa siempre dos dígitos (p. ej. {tipo}-01).")
            if rid in inf.definiciones:
                inf.errores.append(f"ID repetido: {rid}.")
            inf.definiciones[rid] = resto.strip()
            bloques[rid] = [resto]
            actual = rid
        elif ln.lstrip().startswith("#"):
            actual = None
        elif actual is not None:
            bloques[actual].append(ln)

    if not any(i.startswith("RF-") for i in inf.definiciones):
        inf.errores.append("No se encontró ningún requerimiento funcional (formato: '- **RF-01** texto').")

    # 3) IDs referenciados pero nunca definidos
    for rid in sorted({f"{t}-{n}" for t, n in _ID.findall(texto)} - set(inf.definiciones)):
        inf.advertencias.append(f"Se menciona {rid} pero no está definido como requerimiento.")

    # 4) Criterios de aceptación, ambigüedad y métricas
    for rid, partes in bloques.items():
        cuerpo = "\n".join(partes)
        if rid.startswith("RF-") and not re.search(r"criterio", cuerpo, flags=re.I):
            inf.advertencias.append(f"{rid} no tiene 'Criterio de aceptación'.")
        if rid.startswith("RNF-") and not re.search(r"\d", cuerpo):
            inf.advertencias.append(f"{rid} no tiene una métrica medible (ningún número).")
        for palabra in AMBIGUAS:
            if re.search(rf"(?<!\w){re.escape(palabra)}(?!\w)", cuerpo, flags=re.I):
                inf.advertencias.append(f"{rid} usa lenguaje ambiguo: '{palabra}'.")
                break
    return inf
