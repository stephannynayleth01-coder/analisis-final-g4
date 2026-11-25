"""Spec (Markdown) -> ModeloAnalisis, con validación y reintento automático."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .prompts import SISTEMA, prompt_correccion, prompt_usuario
from .schema import ModeloAnalisis
from .validar import Validacion, validar


@dataclass
class Extraccion:
    modelo: ModeloAnalisis | None
    validacion: Validacion | None
    intentos: int
    historial: list[list[str]] = field(default_factory=list)  # errores de cada intento fallido
    segundos: float = 0.0

    @property
    def ok(self) -> bool:
        return self.modelo is not None and self.validacion is not None and not self.validacion.errores


def extraer_modelo(spec: str, ids: set[str], llm, max_reintentos: int = 2, log=print) -> Extraccion:
    estructurado = llm.with_structured_output(ModeloAnalisis, include_raw=True)
    base = [("system", SISTEMA), ("human", prompt_usuario(spec, sorted(ids)))]
    mensajes = list(base)
    historial: list[list[str]] = []
    ultimo: ModeloAnalisis | None = None
    ultima_val: Validacion | None = None
    t0 = time.time()

    for intento in range(1, max_reintentos + 2):
        log(f"  · Llamando al modelo (intento {intento} de {max_reintentos + 1})...")
        res = estructurado.invoke(mensajes)
        parsed, error = res.get("parsed"), res.get("parsing_error")

        if parsed is None or error:
            errores = [f"La salida no cumple el esquema JSON: {str(error)[:400]}"]
            ultimo, ultima_val = None, None
            anterior = None
        else:
            ultimo = parsed.canonizar()
            ultima_val = validar(ultimo, ids)
            errores = ultima_val.errores
            anterior = ultimo.model_dump_json()
            if not errores:
                return Extraccion(ultimo, ultima_val, intento, historial, time.time() - t0)

        historial.append(errores)
        log(f"    ✗ {len(errores)} problema(s) en el intento {intento}")
        mensajes = base + [("human", prompt_correccion(errores, anterior))]

    return Extraccion(ultimo, ultima_val, max_reintentos + 1, historial, time.time() - t0)
