# Proyecto final · Análisis de Sistemas — De la especificación al código

Pipeline que toma **tu especificación** (Markdown) y produce, con ayuda de un LLM:

1. Diagramas **PlantUML**: casos de uso, clases, entidad-relación y secuencia.
2. Un **esqueleto de código** (Python y/o Java) con TODO, sin lógica de negocio.
3. Un borrador de **matriz de trazabilidad** (`trazabilidad_generada.csv`) y un `reporte.md`.

> Lo que se evalúa no es que el pipeline funcione: es **qué tan buena es tu spec** y **qué tan bien auditas** lo que genera. El modelo se equivoca; encontrar *por qué* es tu trabajo.

## Cómo funciona

```
specs/mi_spec.md ──► [revisión de la spec, sin IA] ──► [LLM → modelo.json validado]
                                                          │
                                  diagramas .puml ◄───────┤ (plantillas, sin IA)
                                  código base     ◄───────┘
```

El LLM **no escribe PlantUML ni código**: solo llena `modelo.json`. Los diagramas y el código salen de ese archivo con plantillas. Así, cualquier error visible en un diagrama nace en tu spec o en la interpretación del modelo, y puedes rastrearlo.

## 1. Requisitos del equipo

- Python 3.10 o superior.
- **Al menos un portátil por equipo** que corra Ollama (recomendado 16 GB de RAM; con 8 GB solo caben modelos pequeños y más lentos).
- ~6 GB libres en disco para el modelo (descárgalo con buena conexión **antes** de la clase).
- Para ver los diagramas: la extensión *PlantUML* de VS Code (requiere Java y Graphviz) o el servidor web de PlantUML.

## 2. Instalación

```bash
# 1) Instala Ollama desde https://ollama.com y descarga el modelo oficial
ollama pull qwen2.5:7b          # usa el modelo que indique el docente

# 2) Entorno de Python
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS
pip install -r requirements.txt

# 3) Configuración
copy .env.example .env          # Windows  (en Linux/macOS: cp .env.example .env)
```

## 3. Prueba de humo (hazla antes de empezar)

```bash
python prueba_humo.py
```

Ejecuta el pipeline completo con la spec de referencia. Si dice `OK`, tu equipo sirve. Si dice `FALLA`, sigue el mensaje; si Ollama no es viable en tu portátil, usa Groq (sección 6) **sin penalización en la nota**.

## 4. Uso

```bash
python generar.py specs/mi_spec.md --solo-revisar    # solo revisa la spec (rápido, sin IA)
python generar.py specs/mi_spec.md                   # pipeline completo
python generar.py specs/mi_spec.md --lenguaje java   # python | java | ambos
```

Parte de `specs/plantilla_spec.md`. El ejemplo resuelto está en `specs/ejemplo_tienda_herrero.md` (un módulo que **no** tiene ningún equipo: es un modelo de formato, no una solución).

## 5. Qué se genera en `salida/`

| Archivo | Para qué sirve |
|---|---|
| `diagramas/*.puml` | Propuesta de diagramas. **Audítalos contra la spec.** |
| `codigo/python/`, `codigo/java/` | Esqueleto con TODO. |
| `modelo.json` | Lo que el LLM entendió de tu spec. Aquí está la causa de muchos errores. |
| `trazabilidad_generada.csv` | Borrador: qué elementos *dice* el modelo que cubren cada requerimiento. **Verifícalo fila por fila.** |
| `reporte.md` | Revisión de la spec, intentos, errores de validación y cobertura. |

Sube `salida/` a GitHub en cada versión: es tu evidencia de proceso.

## 6. Groq como respaldo

1. Crea una cuenta gratuita en <https://console.groq.com> y genera una API key.
2. En tu `.env`: `GROQ_API_KEY=...` y `LLM_PROVIDER=groq` (o ejecuta con `--proveedor groq`).
3. Con `LLM_PROVIDER=auto` usa Ollama y, si no responde, pasa a Groq.

El `reporte.md` deja registrado qué proveedor y modelo usó cada corrida.

## 7. Reglas

- **El pipeline está congelado en `main`.** Solo puedes cambiar `specs/`, `auditoria/` y `salida/`. No modifiques `spec2code/`, `plantillas/`, `generar.py` ni `prueba_humo.py`: el docente lo verifica comparando con el repositorio base. Mejorar el pipeline es el **bonus**, en su propia rama (sección 8).
- **Nunca subas `.env` ni tu API key a GitHub.** Está en `.gitignore`; no lo fuerces.
- Corrige la **spec**, no los diagramas generados. Si editas a mano un diagrama, deja constancia en tu ADR.
- Sin commit visible, la sesión no cuenta.
- Los errores del modelo no se esconden: se documentan.

## 8. Bonus (opcional): mejorar el pipeline

Solo en la rama `bonus-pipeline`; `main` no se toca. Elige **una** opción:

| Opción | Qué haces | Archivos |
|---|---|---|
| **A. Nuevo diagrama** | Plantilla de diagrama de actividades o de estados generada desde `modelo.json` | `plantillas/`, `spec2code/render.py` |
| **B. Nueva validación** | Una regla que detecte un error de significado que hoy pasa (p. ej. un RN que no aparece en ningún método) | `spec2code/validar.py` |
| **C. Métodos con parámetros** | Extender el esquema para que los métodos tengan parámetros y reflejarlo en clases y código | `spec2code/schema.py`, `plantillas/` |

Requisitos: las pruebas siguen pasando y agregas al menos una nueva (`python -m unittest discover -s pruebas`), un `BONUS.md` que explique qué cambiaste y por qué, y la demostración con la spec de tu equipo en la sustentación.

## 9. Límites conocidos (parte de lo que puedes auditar)

- Los métodos generados no tienen parámetros y solo devuelven tipos básicos (no pueden devolver otra entidad).
- El ER no traduce la herencia ni crea tablas intermedias para relaciones N:M; el pipeline lo avisa con un comentario.
- No hay diagrama de arquitectura (C4): ese lo decides tú a partir de la spec.
- Un modelo pequeño puede omitir requerimientos o inventar relaciones; la validación solo detecta referencias rotas e IDs inexistentes, **no** errores de significado.

## 10. Pruebas del pipeline (para el docente)

```bash
python -m unittest discover -s pruebas -v
```

---
© Francisco Germán Cuéllar Méndez. Todos los derechos reservados.
