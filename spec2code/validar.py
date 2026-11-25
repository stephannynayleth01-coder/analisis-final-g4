"""Validación determinista del modelo que devolvió el LLM.

Los ERRORES provocan un reintento automático (se le devuelven al modelo).
Las ADVERTENCIAS no bloquean: son pistas para tu auditoría.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .schema import ModeloAnalisis


@dataclass
class Validacion:
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)


def _duplicados(items: list[str]) -> list[str]:
    vistos, dup = set(), []
    for i in items:
        if i in vistos and i not in dup:
            dup.append(i)
        vistos.add(i)
    return dup


def validar(m: ModeloAnalisis, ids_spec: set[str]) -> Validacion:
    v = Validacion()
    actores = {a.nombre for a in m.actores}
    cus = {c.id for c in m.casos_uso}
    entidades = {e.nombre: e for e in m.entidades}

    if not m.actores:
        v.errores.append("No hay actores.")
    if not m.casos_uso:
        v.errores.append("No hay casos de uso.")
    if not m.entidades:
        v.errores.append("No hay entidades.")

    for d in _duplicados([a.nombre for a in m.actores]):
        v.errores.append(f"Actor repetido: {d}.")
    for d in _duplicados([c.id for c in m.casos_uso]):
        v.errores.append(f"Id de caso de uso repetido: {d}.")
    for d in _duplicados([e.nombre for e in m.entidades]):
        v.errores.append(f"Entidad repetida: {d}.")

    # Referencias cruzadas
    for cu in m.casos_uso:
        if not cu.actores:
            v.errores.append(f"{cu.id} no tiene actores.")
        for a in cu.actores:
            if a not in actores:
                v.errores.append(f"{cu.id} usa el actor '{a}', que no está en 'actores'.")
        for ref in cu.incluye + cu.extiende:
            if ref not in cus:
                v.errores.append(f"{cu.id} referencia el caso de uso inexistente {ref}.")
            if ref == cu.id:
                v.errores.append(f"{cu.id} se referencia a sí mismo.")
    for e in m.entidades:
        if e.hereda_de and e.hereda_de not in entidades:
            v.errores.append(f"{e.nombre} hereda de '{e.hereda_de}', que no existe.")
        for d in _duplicados([a.nombre for a in e.atributos]):
            v.advertencias.append(f"{e.nombre}: atributo repetido '{d}'.")
    for e in m.entidades:  # ciclos de herencia
        visto, actual = {e.nombre}, e
        while actual.hereda_de and actual.hereda_de in entidades:
            actual = entidades[actual.hereda_de]
            if actual.nombre in visto:
                v.errores.append(f"Ciclo de herencia que involucra a {e.nombre}.")
                break
            visto.add(actual.nombre)
    for r in m.relaciones:
        for extremo in (r.desde, r.hasta):
            if extremo not in entidades:
                v.errores.append(f"Relación {r.desde}->{r.hasta}: la entidad '{extremo}' no existe.")
    for s in m.secuencias:
        if s.caso_uso not in cus:
            v.errores.append(f"Una secuencia apunta al caso de uso inexistente {s.caso_uso}.")
        if len(s.mensajes) < 2:
            v.advertencias.append(f"La secuencia de {s.caso_uso} tiene menos de 2 mensajes.")
        conocidos = actores | set(entidades)
        for msg in s.mensajes:
            for p in (msg.de, msg.a):
                if p not in conocidos:
                    v.advertencias.append(f"Secuencia {s.caso_uso}: '{p}' no es actor ni entidad del modelo.")

    # Trazabilidad: IDs inventados
    def revisar(nombre: str, req_ids: list[str]) -> None:
        for r in req_ids:
            if r not in ids_spec:
                v.errores.append(f"{nombre} cita '{r}', que no existe en la spec.")

    for c in m.casos_uso:
        revisar(c.id, c.req_ids)
        if not c.req_ids:
            v.errores.append(f"{c.id} no indica req_ids (trazabilidad).")
    for e in m.entidades:
        revisar(f"Entidad {e.nombre}", e.req_ids)
        if not e.req_ids:
            v.errores.append(f"Entidad {e.nombre} no indica req_ids (trazabilidad).")
        for mt in e.metodos:
            revisar(f"{e.nombre}.{mt.nombre}", mt.req_ids)
    for a in m.actores:
        revisar(f"Actor {a.nombre}", a.req_ids)
    for r in m.relaciones:
        revisar(f"Relación {r.desde}->{r.hasta}", r.req_ids)
    for s in m.secuencias:
        revisar(f"Secuencia {s.caso_uso}", s.req_ids)

    return v


def cobertura(m: ModeloAnalisis) -> dict[str, list[str]]:
    """req_id -> elementos del modelo que DICEN cubrirlo (afirmación del LLM, por verificar)."""
    c: dict[str, list[str]] = {}

    def anotar(req_ids: list[str], etiqueta: str) -> None:
        for r in req_ids:
            c.setdefault(r, []).append(etiqueta)

    for a in m.actores:
        anotar(a.req_ids, f"Actor {a.nombre}")
    for cu in m.casos_uso:
        anotar(cu.req_ids, f"CasoUso {cu.id}")
    for e in m.entidades:
        anotar(e.req_ids, f"Entidad {e.nombre}")
        for mt in e.metodos:
            anotar(mt.req_ids, f"Metodo {e.nombre}.{mt.nombre}")
    for r in m.relaciones:
        anotar(r.req_ids, f"Relacion {r.desde}->{r.hasta}")
    for s in m.secuencias:
        anotar(s.req_ids, f"Secuencia {s.caso_uso}")
    return c
