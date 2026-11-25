"""Orquesta: leer spec -> revisar -> LLM (o modelo.json) -> validar -> generar archivos."""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path

from .extract import extraer_modelo
from .llm import crear_llm, nombre_modelo, resolver_proveedor
from .render import render_codigo, render_diagramas, renderizar_imagenes
from .schema import ModeloAnalisis
from .spec_lint import revisar_spec
from .validar import cobertura, validar


def _escribir_trazabilidad(destino: Path, definiciones: dict[str, str], cob: dict[str, list[str]]) -> None:
    with open(destino, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["req_id", "tipo", "texto_en_la_spec", "elementos_que_el_modelo_dice_cubrirlo",
                    "cobertura_declarada", "verificado_por_el_equipo (si/no/parcial)", "observaciones_del_equipo"])
        for rid in sorted(definiciones):
            tipo = rid.split("-")[0]
            elems = cob.get(rid, [])
            if elems:
                estado = "declarada"
            elif tipo == "RNF":
                estado = "sin elementos (los RNF suelen no verse en los diagramas: revisar a mano)"
            else:
                estado = "SIN COBERTURA"
            w.writerow([rid, tipo, definiciones[rid], "; ".join(elems), estado, "", ""])


def _reporte(meta: dict, lint, ext, val, cob, definiciones) -> str:
    L = ["# Reporte de la corrida", ""]
    L += [f"- Fecha: {meta['fecha']}", f"- Spec: `{meta['spec']}`",
          f"- Origen del modelo: {meta['origen']}", f"- Intentos al LLM: {meta['intentos']}",
          f"- Duración de la extracción: {meta['segundos']:.1f} s", ""]
    L += ["## Revisión de la spec (sin LLM)", ""]
    L += [f"- ❌ {e}" for e in lint.errores] or []
    L += [f"- ⚠️ {a}" for a in lint.advertencias] or []
    if not lint.errores and not lint.advertencias:
        L.append("- Sin observaciones.")
    L += ["", "## Validación del modelo generado", ""]
    if ext is not None and ext.historial:
        for i, errs in enumerate(ext.historial, 1):
            L.append(f"Intento {i} fallido:")
            L += [f"  - {e}" for e in errs]
    L += [f"- ❌ {e}" for e in val.errores]
    L += [f"- ⚠️ {a}" for a in val.advertencias]
    if not val.errores and not val.advertencias and not (ext and ext.historial):
        L.append("- Sin observaciones.")
    L += ["", "## Cobertura declarada por el modelo", ""]
    sin = [r for r in sorted(definiciones) if not cob.get(r) and not r.startswith("RNF")]
    L.append(f"- Requerimientos con elementos asociados: {sum(1 for r in definiciones if cob.get(r))} de {len(definiciones)}")
    L += [f"- ⚠️ Sin cobertura: {', '.join(sin)}" if sin else "- Todos los RF y RN tienen algún elemento asociado."]
    L += ["", "> Que el modelo *declare* cubrir un requerimiento no significa que lo cubra bien.",
          "> Verifica cada fila de `trazabilidad_generada.csv` contra la spec y los diagramas."]
    return "\n".join(L) + "\n"


def ejecutar(spec: Path, salida: Path, lenguaje: str = "ambos", proveedor: str | None = None,
             modelo_llm: str | None = None, sin_llm: Path | None = None, imagenes: bool = False,
             max_reintentos: int = 2, log=print, llm=None) -> int:
    """Devuelve 0 si todo salió bien, 1 si la spec tiene errores, 2 si el modelo no pasó la validación."""
    texto = spec.read_text(encoding="utf-8")
    lint = revisar_spec(texto)
    log(f"Spec: {spec.name} — {len(lint.definiciones)} requerimientos")
    for e in lint.errores:
        log(f"  ❌ {e}")
    for a in lint.advertencias:
        log(f"  ⚠️  {a}")
    salida.mkdir(parents=True, exist_ok=True)
    if lint.errores:
        log("La spec tiene errores de formato. Corrígelos y vuelve a ejecutar.")
        return 1

    ext = None
    t0 = time.time()
    if sin_llm:
        modelo = ModeloAnalisis.model_validate_json(sin_llm.read_text(encoding="utf-8")).canonizar()
        val = validar(modelo, lint.ids)
        origen, intentos, ok = f"archivo {sin_llm.name} (sin LLM)", 0, not val.errores
    else:
        prov = resolver_proveedor(proveedor)
        nombre = nombre_modelo(prov, modelo_llm)
        log(f"LLM: {prov} / {nombre}")
        llm = llm or crear_llm(prov, modelo_llm)
        ext = extraer_modelo(texto, lint.ids, llm, max_reintentos=max_reintentos, log=log)
        modelo, val, ok = ext.modelo, ext.validacion, ext.ok
        origen, intentos = f"LLM {prov} / {nombre}", ext.intentos

    meta = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "spec": str(spec), "origen": origen,
            "intentos": intentos, "segundos": time.time() - t0}

    if not ok:
        log("✗ El modelo no pasó la validación tras los reintentos. Revisa reporte.md.")
        if modelo is not None:
            (salida / "modelo_invalido.json").write_text(modelo.model_dump_json(indent=2), encoding="utf-8")
        vacio = val if val is not None else validar(ModeloAnalisis(modulo="?", actores=[], casos_uso=[], entidades=[]), lint.ids)
        (salida / "reporte.md").write_text(_reporte(meta, lint, ext, vacio, {}, lint.definiciones), encoding="utf-8")
        return 2

    cob = cobertura(modelo)
    (salida / "modelo.json").write_text(modelo.model_dump_json(indent=2), encoding="utf-8")
    puml = render_diagramas(modelo, salida / "diagramas")
    codigo = render_codigo(modelo, lenguaje, salida / "codigo")
    _escribir_trazabilidad(salida / "trazabilidad_generada.csv", lint.definiciones, cob)
    (salida / "reporte.md").write_text(_reporte(meta, lint, ext, val, cob, lint.definiciones), encoding="utf-8")
    if imagenes:
        renderizar_imagenes(puml, log)

    log(f"✓ Listo en {salida}/: {len(puml)} diagramas, {len(codigo)} archivo(s) de código, "
        f"trazabilidad_generada.csv, modelo.json y reporte.md")
    return 0
