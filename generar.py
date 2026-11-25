#!/usr/bin/env python3
"""CLI: python generar.py specs/mi_spec.md"""
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from spec2code.pipeline import ejecutar  # noqa: E402
from spec2code.spec_lint import revisar_spec  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="De la spec a diagramas PlantUML y esqueleto de código.")
    p.add_argument("spec", type=Path, help="Archivo Markdown con la especificación")
    p.add_argument("--salida", type=Path, default=Path("salida"), help="Carpeta de salida (por defecto: salida)")
    p.add_argument("--lenguaje", choices=["python", "java", "ambos"], default="ambos")
    p.add_argument("--proveedor", choices=["ollama", "groq", "auto"], default=None,
                   help="Por defecto, LLM_PROVIDER del .env (ollama). 'auto' = Ollama y, si no responde, Groq")
    p.add_argument("--modelo", default=None, help="Nombre del modelo (por defecto, el del .env)")
    p.add_argument("--reintentos", type=int, default=2, help="Reintentos automáticos si el modelo falla")
    p.add_argument("--solo-revisar", action="store_true", help="Solo revisa la spec (sin LLM) y termina")
    p.add_argument("--sin-llm", type=Path, default=None, metavar="MODELO.JSON",
                   help="Genera desde un modelo.json ya existente (para probar plantillas)")
    p.add_argument("--imagenes", action="store_true", help="Renderiza SVG si 'plantuml' está instalado")
    a = p.parse_args()

    if a.solo_revisar:
        inf = revisar_spec(a.spec.read_text(encoding="utf-8"))
        for e in inf.errores:
            print("❌", e)
        for w in inf.advertencias:
            print("⚠️ ", w)
        print(f"{len(inf.definiciones)} requerimientos; {len(inf.errores)} error(es), {len(inf.advertencias)} advertencia(s).")
        return 1 if inf.errores else 0

    return ejecutar(a.spec, a.salida, a.lenguaje, a.proveedor, a.modelo, a.sin_llm, a.imagenes, a.reintentos)


if __name__ == "__main__":
    sys.exit(main())
