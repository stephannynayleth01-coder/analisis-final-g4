#!/usr/bin/env python3
"""Prueba de humo: ¿tu portátil puede correr el pipeline con el modelo oficial?

Uso:  python prueba_humo.py            (usa LLM_PROVIDER del .env)
      python prueba_humo.py --proveedor groq
"""
import argparse
import sys
import tempfile
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from spec2code.llm import (modelos_ollama_instalados, nombre_modelo, ollama_url,  # noqa: E402
                           resolver_proveedor)
from spec2code.pipeline import ejecutar  # noqa: E402

SPEC = Path(__file__).parent / "specs" / "ejemplo_tienda_herrero.md"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proveedor", choices=["ollama", "groq"], default=None)
    a = ap.parse_args()

    try:
        prov = resolver_proveedor(a.proveedor)
    except RuntimeError as e:
        print("FALLA:", e)
        return 1
    modelo = nombre_modelo(prov)
    print(f"Proveedor: {prov} · Modelo: {modelo}")

    if prov == "ollama":
        instalados = modelos_ollama_instalados()
        if instalados is None:
            print(f"FALLA: Ollama no responde en {ollama_url()}. ¿Está abierto? Si tu equipo no lo soporta, usa Groq (ver README).")
            return 1
        if not any(n == modelo or n.startswith(modelo + ":") or n.split(":")[0] == modelo for n in instalados):
            print(f"FALLA: el modelo '{modelo}' no está descargado. Ejecuta:  ollama pull {modelo}")
            print("Modelos instalados:", ", ".join(instalados) or "(ninguno)")
            return 1

    with tempfile.TemporaryDirectory() as tmp:
        t0 = time.time()
        try:
            codigo = ejecutar(SPEC, Path(tmp), "ambos", prov, None, log=lambda *x: None)
        except Exception as e:  # noqa: BLE001
            print(f"FALLA al ejecutar el pipeline: {type(e).__name__}: {e}")
            return 1
        seg = time.time() - t0

    if codigo == 0:
        print(f"OK: el pipeline completo funcionó en {seg:.0f} s. Puedes trabajar con {prov}.")
        if seg > 300:
            print("Aviso: es lento (más de 5 min). Considera Groq como proveedor para ahorrar tiempo.")
        return 0
    print(f"FALLA: el modelo no produjo un resultado válido con la spec de referencia (código {codigo}).")
    print("Prueba de nuevo; si se repite, usa el proveedor de respaldo (Groq) y avisa al docente.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
