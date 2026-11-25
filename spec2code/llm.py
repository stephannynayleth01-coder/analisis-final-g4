"""Proveedores de LLM: Ollama (local, primera opción) y Groq (respaldo).

Todo se configura con variables de entorno (archivo .env). Los modelos por defecto son
solo un punto de partida: el docente fija el modelo oficial de la actividad.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OLLAMA_URL_DEFECTO = "http://localhost:11434"
OLLAMA_MODELO_DEFECTO = "qwen2.5:7b"          # confirma con `ollama list`
GROQ_MODELO_DEFECTO = "llama-3.3-70b-versatile"  # verifica vigencia en console.groq.com


def ollama_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", OLLAMA_URL_DEFECTO).rstrip("/")


def modelos_ollama_instalados(timeout: float = 3.0) -> list[str] | None:
    """Lista de modelos en el Ollama local, o None si no responde."""
    try:
        with urllib.request.urlopen(f"{ollama_url()}/api/tags", timeout=timeout) as r:
            datos = json.loads(r.read().decode("utf-8"))
        return [m.get("name", "") for m in datos.get("models", [])]
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, ValueError):
        return None


def resolver_proveedor(proveedor: str | None) -> str:
    """'auto' = Ollama si responde; si no, Groq cuando hay GROQ_API_KEY."""
    p = (proveedor or os.getenv("LLM_PROVIDER", "ollama")).lower()
    if p != "auto":
        return p
    if modelos_ollama_instalados() is not None:
        return "ollama"
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    raise RuntimeError(
        "Modo 'auto': Ollama no responde y no hay GROQ_API_KEY en el .env. "
        "Inicia Ollama o configura Groq."
    )


def nombre_modelo(proveedor: str, modelo: str | None = None) -> str:
    if modelo:
        return modelo
    if proveedor == "groq":
        return os.getenv("GROQ_MODEL", GROQ_MODELO_DEFECTO)
    return os.getenv("OLLAMA_MODEL", OLLAMA_MODELO_DEFECTO)


def crear_llm(proveedor: str, modelo: str | None = None):
    """Devuelve un chat model de LangChain listo para `with_structured_output`."""
    nombre = nombre_modelo(proveedor, modelo)
    if proveedor == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=nombre,
            base_url=ollama_url(),
            temperature=0,
            seed=42,
            num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "8192")),
            client_kwargs={"timeout": float(os.getenv("OLLAMA_TIMEOUT", "900"))},
        )
    if proveedor == "groq":
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("Falta GROQ_API_KEY en el archivo .env (nunca la subas a GitHub).")
        from langchain_groq import ChatGroq

        return ChatGroq(model=nombre, temperature=0, max_retries=2)
    raise ValueError(f"Proveedor desconocido: '{proveedor}'. Usa ollama, groq o auto.")
