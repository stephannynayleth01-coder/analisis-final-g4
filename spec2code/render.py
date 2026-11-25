"""ModeloAnalisis -> diagramas PlantUML y esqueleto de código (plantillas Jinja2)."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .schema import ModeloAnalisis, _ascii

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLAS = RAIZ / "plantillas"

TIPO_PY = {"texto": "str", "entero": "int", "decimal": "float", "booleano": "bool", "fecha": "date", "lista": "list"}
TIPO_JAVA = {"texto": "String", "entero": "int", "decimal": "double", "booleano": "boolean",
             "fecha": "LocalDate", "lista": "List<Object>"}
TIPO_UML = {"texto": "String", "entero": "int", "decimal": "double", "booleano": "boolean",
            "fecha": "Date", "lista": "List"}
TIPO_ER = {"texto": "varchar", "entero": "int", "decimal": "decimal", "booleano": "boolean",
           "fecha": "date", "lista": "json"}
ER_IZQ = {"1": "||", "0..1": "|o", "*": "}o", "0..*": "}o", "1..*": "}|"}
ER_DER = {"1": "||", "0..1": "o|", "*": "o{", "0..*": "o{", "1..*": "|{"}
FLECHA_UML = {"asociacion": "--", "agregacion": "o--", "composicion": "*--"}
MUCHOS = {"*", "0..*", "1..*"}


def _q(texto: object) -> str:
    return str(texto).replace('"', "'").replace("\n", " ").strip()


def _entorno() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(PLANTILLAS)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters["q"] = _q
    return env


def _camel(snake: str) -> str:
    partes = snake.split("_")
    return partes[0] + "".join(p[:1].upper() + p[1:] for p in partes[1:])


def _paquete(modulo: str) -> str:
    p = re.sub(r"[^a-z0-9]", "", _ascii(modulo).lower())
    return p if p and not p[0].isdigit() else "m" + p


def _vista_atributo(a) -> dict:
    return {"nombre": a.nombre, "camel": _camel(a.nombre), "tipo": a.tipo, "es_clave": a.es_clave,
            "py": TIPO_PY[a.tipo], "java": TIPO_JAVA[a.tipo], "uml": TIPO_UML[a.tipo], "er": TIPO_ER[a.tipo]}


def _vista_metodo(mt) -> dict:
    ret = mt.retorno
    return {"nombre": mt.nombre, "camel": _camel(mt.nombre), "descripcion": mt.descripcion.replace("\n", " "),
            "req_ids": mt.req_ids, "retorno": ret,
            "ret_py": "None" if ret == "ninguno" else TIPO_PY[ret],
            "ret_java": "void" if ret == "ninguno" else TIPO_JAVA[ret],
            "ret_uml": "" if ret == "ninguno" else TIPO_UML[ret]}


def _orden_herencia(m: ModeloAnalisis) -> list:
    """Padres antes que hijos (necesario para Python)."""
    por_nombre = {e.nombre: e for e in m.entidades}
    orden, hechos = [], set()

    def visitar(e) -> None:
        if e.nombre in hechos:
            return
        hechos.add(e.nombre)
        if e.hereda_de and e.hereda_de in por_nombre:
            visitar(por_nombre[e.hereda_de])
        orden.append(e)

    for e in m.entidades:
        visitar(e)
    return orden


def construir_vistas(m: ModeloAnalisis) -> dict:
    por_nombre = {e.nombre: e for e in m.entidades}

    def cadena(e) -> list:
        res = [e]
        while res[0].hereda_de and res[0].hereda_de in por_nombre and por_nombre[res[0].hereda_de] not in res:
            res.insert(0, por_nombre[res[0].hereda_de])
        return res

    entidades = []
    for e in _orden_herencia(m):
        ch = cadena(e)
        propios = [_vista_atributo(a) for a in e.atributos]
        heredados: list[dict] = []
        for padre in ch[:-1]:
            for a in padre.atributos:
                if a.nombre not in {x["nombre"] for x in heredados}:
                    heredados.append(_vista_atributo(a))
        nombres_heredados = {x["nombre"] for x in heredados}
        propios_sin_dup = [a for a in propios if a["nombre"] not in nombres_heredados]
        campos_rel = []
        for r in m.relaciones:
            if r.desde != e.nombre:
                continue
            muchos = r.multiplicidad_hasta in MUCHOS
            nombre = _camel_de_clase(r.hasta) + ("s" if muchos else "")
            campos_rel.append({
                "nombre": nombre, "snake": _snake_de_clase(r.hasta) + ("s" if muchos else ""),
                "clase": r.hasta, "muchos": muchos, "tipo_rel": r.tipo, "etiqueta": r.etiqueta,
                "req_ids": r.req_ids,
            })
        java_imports = set()
        todos = propios_sin_dup + heredados
        if any(a["tipo"] == "fecha" for a in propios_sin_dup):
            java_imports.add("java.time.LocalDate")
        if any(a["tipo"] == "lista" for a in propios_sin_dup) or any(c["muchos"] for c in campos_rel):
            java_imports.update({"java.util.List"})
        if any(c["muchos"] for c in campos_rel):
            java_imports.add("java.util.ArrayList")
        if any(_vista_metodo(mt)["ret_java"] == "LocalDate" for mt in e.metodos):
            java_imports.add("java.time.LocalDate")
        if any(_vista_metodo(mt)["ret_java"].startswith("List") for mt in e.metodos):
            java_imports.add("java.util.List")
        entidades.append({
            "nombre": e.nombre, "es_abstracta": e.es_abstracta, "hereda_de": e.hereda_de, "req_ids": e.req_ids,
            "atributos": propios_sin_dup, "heredados": heredados, "constructor": heredados + propios_sin_dup,
            "metodos": [_vista_metodo(mt) for mt in e.metodos], "campos_rel": campos_rel,
            "java_imports": sorted(java_imports),
            "usa_fecha_py": any(a["tipo"] == "fecha" for a in todos),
        })

    # Casos de uso
    alias_actor = {a.nombre: f"A{i}" for i, a in enumerate(m.actores, 1)}
    casos = [{
        "id": c.id, "alias": c.id.replace("-", "_"), "nombre": c.nombre,
        "actores": [alias_actor[a] for a in c.actores if a in alias_actor],
        "incluye": [x.replace("-", "_") for x in c.incluye],
        "extiende": [x.replace("-", "_") for x in c.extiende],
    } for c in m.casos_uso]
    actores = [{"nombre": a.nombre, "alias": alias_actor[a.nombre]} for a in m.actores]

    # Relaciones (clases y ER)
    relaciones = []
    for r in m.relaciones:
        relaciones.append({
            "desde": r.desde, "hasta": r.hasta, "etiqueta": r.etiqueta,
            "flecha": FLECHA_UML[r.tipo], "tipo": r.tipo,
            "mult_desde": r.multiplicidad_desde, "mult_hasta": r.multiplicidad_hasta,
            "er_izq": ER_IZQ[r.multiplicidad_desde], "er_der": ER_DER[r.multiplicidad_hasta],
            "n_a_m": r.multiplicidad_desde in MUCHOS and r.multiplicidad_hasta in MUCHOS,
        })

    # Secuencias
    nombres_actor = {a.nombre for a in m.actores}
    cu_por_id = {c.id: c for c in m.casos_uso}
    secuencias = []
    for s in m.secuencias:
        participantes: list[str] = []
        for msg in s.mensajes:
            for p in (msg.de, msg.a):
                if p not in participantes:
                    participantes.append(p)
        alias = {p: f"P{i}" for i, p in enumerate(participantes, 1)}
        cu = cu_por_id.get(s.caso_uso)
        secuencias.append({
            "caso_uso": s.caso_uso, "titulo": f"{s.caso_uso} {cu.nombre}" if cu else s.caso_uso,
            "participantes": [{"nombre": p, "alias": alias[p], "es_actor": p in nombres_actor} for p in participantes],
            "mensajes": [{"de": alias[x.de], "a": alias[x.a], "texto": x.texto} for x in s.mensajes],
        })

    return {"modulo": m.modulo, "paquete": _paquete(m.modulo), "actores": actores, "casos": casos,
            "entidades": entidades, "relaciones": relaciones, "secuencias": secuencias}


def _snake_de_clase(clase: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", clase).lower()


def _camel_de_clase(clase: str) -> str:
    return clase[:1].lower() + clase[1:]


def render_diagramas(m: ModeloAnalisis, destino: Path) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    env, v = _entorno(), construir_vistas(m)
    archivos: list[Path] = []

    def escribir(nombre: str, contenido: str) -> None:
        ruta = destino / nombre
        ruta.write_text(contenido, encoding="utf-8")
        archivos.append(ruta)

    escribir("01_casos_de_uso.puml", env.get_template("casos_uso.puml.j2").render(v=v))
    escribir("02_clases.puml", env.get_template("clases.puml.j2").render(v=v))
    escribir("03_er.puml", env.get_template("er.puml.j2").render(v=v))
    for s in v["secuencias"]:
        escribir(f"04_secuencia_{s['caso_uso']}.puml", env.get_template("secuencia.puml.j2").render(s=s))
    return archivos


def render_codigo(m: ModeloAnalisis, lenguaje: str, destino: Path) -> list[Path]:
    env, v = _entorno(), construir_vistas(m)
    archivos: list[Path] = []
    if lenguaje in ("python", "ambos"):
        d = destino / "python"
        d.mkdir(parents=True, exist_ok=True)
        ruta = d / "modelo.py"
        ruta.write_text(env.get_template("codigo_python.py.j2").render(v=v), encoding="utf-8")
        archivos.append(ruta)
    if lenguaje in ("java", "ambos"):
        d = destino / "java"
        d.mkdir(parents=True, exist_ok=True)
        for e in v["entidades"]:
            ruta = d / f"{e['nombre']}.java"
            ruta.write_text(env.get_template("codigo_java.java.j2").render(v=v, e=e), encoding="utf-8")
            archivos.append(ruta)
    return archivos


def renderizar_imagenes(puml: list[Path], log=print) -> bool:
    """Si PlantUML está instalado (comando `plantuml`), genera los SVG. Opcional."""
    exe = shutil.which("plantuml")
    if not exe:
        log("  · 'plantuml' no está instalado: abre los .puml con la extensión de VS Code o el servidor web de PlantUML.")
        return False
    try:
        subprocess.run([exe, "-tsvg", *map(str, puml)], check=True, capture_output=True, timeout=180)
        return True
    except (subprocess.SubprocessError, OSError) as e:
        log(f"  · No se pudo renderizar con PlantUML: {e}")
        return False
