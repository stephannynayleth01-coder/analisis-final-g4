"""Prompts del pipeline. Léelos: son parte de lo que debes auditar.

El prompt no garantiza un resultado perfecto: el modelo puede omitir requerimientos,
inventar relaciones o malinterpretar una frase ambigua. Tu trabajo es encontrar esos
errores y rastrear su causa hasta la spec.
"""

SISTEMA = """Eres un analista de sistemas. Recibes la especificación de UN módulo de software \
y devuelves un modelo de análisis estructurado en JSON, siguiendo exactamente el esquema pedido.

Reglas:
1. Usa SOLO información presente en la especificación. No inventes funcionalidades, atributos \
ni reglas. Si algo es ambiguo o no está dicho, déjalo fuera en vez de suponerlo.
2. Cada actor, caso de uso, entidad, método, relación y secuencia debe llevar en "req_ids" los \
IDs de la spec que lo justifican. Usa únicamente IDs de la lista permitida.
3. Entidades en singular, PascalCase y sin tildes (p. ej. "Pocion"). Atributos y métodos en \
minúsculas con guiones bajos (p. ej. "puntos_vida", "equipar_arma").
4. Casos de uso con id CU-01, CU-02, ... Los actores de cada caso de uso deben existir en "actores".
5. La herencia se expresa SOLO con "hereda_de" (no la repitas en "relaciones").
6. Para los casos de uso más importantes genera una secuencia de 3 a 8 mensajes; los participantes \
deben ser actores o entidades del modelo.
7. Multiplicidades permitidas: "1", "0..1", "*", "0..*", "1..*".
8. Responde únicamente con el objeto JSON del esquema, sin texto adicional."""


def prompt_usuario(spec: str, ids: list[str]) -> str:
    return (
        f"IDs permitidos en req_ids: {', '.join(sorted(ids))}\n\n"
        "ESPECIFICACIÓN:\n"
        "```markdown\n"
        f"{spec.strip()}\n"
        "```"
    )


def prompt_correccion(errores: list[str], anterior_json: str | None) -> str:
    lista = "\n".join(f"- {e}" for e in errores)
    previo = f"\n\nTu respuesta anterior fue:\n{anterior_json}" if anterior_json else ""
    return (
        "Tu respuesta tiene problemas que impiden usarla:\n"
        f"{lista}{previo}\n\n"
        "Devuelve el objeto JSON COMPLETO y corregido, usando solo información de la spec."
    )
