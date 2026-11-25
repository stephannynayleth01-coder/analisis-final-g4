"""Pruebas de las partes deterministas del pipeline (no necesitan un LLM real).

Ejecutar:  python -m unittest discover -s pruebas -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from spec2code.extract import extraer_modelo  # noqa: E402
from spec2code.pipeline import ejecutar  # noqa: E402
from spec2code.render import render_codigo, render_diagramas  # noqa: E402
from spec2code.schema import ModeloAnalisis, a_identificador, a_snake, norm_cu, norm_req  # noqa: E402
from spec2code.spec_lint import revisar_spec  # noqa: E402
from spec2code.validar import validar  # noqa: E402

SPEC = RAIZ / "specs" / "ejemplo_tienda_herrero.md"
MODELO = RAIZ / "specs" / "ejemplo_tienda_herrero.modelo.json"


def modelo_ref() -> ModeloAnalisis:
    return ModeloAnalisis.model_validate_json(MODELO.read_text(encoding="utf-8")).canonizar()


class LLMSimulado:
    """Imita la parte de LangChain que usa el pipeline: with_structured_output(...).invoke(...)."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = 0
        self.mensajes = []

    def with_structured_output(self, esquema, include_raw=False):
        padre = self

        class _Runnable:
            def invoke(self, mensajes):
                padre.llamadas += 1
                padre.mensajes.append(mensajes)
                return padre.respuestas.pop(0)

        return _Runnable()


def respuesta(modelo=None, error=None):
    return {"raw": None, "parsed": modelo, "parsing_error": error}


class TestNormalizacion(unittest.TestCase):
    def test_nombres(self):
        self.assertEqual(a_identificador("poción mágica"), "PocionMagica")
        self.assertEqual(a_snake("Puntos de Vida"), "puntos_de_vida")
        self.assertEqual(a_snake("puntosVida"), "puntos_vida")
        self.assertEqual(norm_req("rf-1"), "RF-01")
        self.assertEqual(norm_req(" RNF_3 "), "RNF-03")
        self.assertEqual(norm_cu("cu-7"), "CU-07")


class TestSpecLint(unittest.TestCase):
    def test_spec_de_referencia_limpia(self):
        inf = revisar_spec(SPEC.read_text(encoding="utf-8"))
        self.assertEqual(inf.errores, [])
        self.assertEqual(inf.advertencias, [])
        self.assertEqual(len(inf.definiciones), 12)

    def test_detecta_problemas(self):
        malo = "# M\n\n## Actores\n- **A**: x\n\n## Requerimientos funcionales\n- **RF-1** hace algo rápido\n- **RF-02** otra cosa\n"
        inf = revisar_spec(malo)
        texto = " ".join(inf.errores + inf.advertencias)
        self.assertIn("Falta la sección", texto)
        self.assertIn("mal formado", texto)
        self.assertIn("criterio", texto.lower())
        self.assertIn("ambiguo", texto)


class TestValidacion(unittest.TestCase):
    def test_referencia_valida(self):
        ids = revisar_spec(SPEC.read_text(encoding="utf-8")).ids
        self.assertEqual(validar(modelo_ref(), ids).errores, [])

    def test_detecta_alucinaciones_y_referencias_rotas(self):
        ids = revisar_spec(SPEC.read_text(encoding="utf-8")).ids
        m = modelo_ref()
        m.casos_uso[0].req_ids.append("RF-99")
        m.casos_uso[1].actores = ["Fantasma"]
        m.relaciones[0].hasta = "NoExiste"
        errores = " | ".join(validar(m, ids).errores)
        self.assertIn("RF-99", errores)
        self.assertIn("Fantasma", errores)
        self.assertIn("NoExiste", errores)


class TestExtraccion(unittest.TestCase):
    def setUp(self):
        self.texto = SPEC.read_text(encoding="utf-8")
        self.ids = revisar_spec(self.texto).ids

    def test_reintenta_hasta_obtener_modelo_valido(self):
        malo = modelo_ref()
        malo.casos_uso[0].req_ids = ["RF-99"]
        llm = LLMSimulado([respuesta(malo), respuesta(None, ValueError("json roto")), respuesta(modelo_ref())])
        ext = extraer_modelo(self.texto, self.ids, llm, max_reintentos=2, log=lambda *a: None)
        self.assertTrue(ext.ok)
        self.assertEqual(ext.intentos, 3)
        self.assertEqual(len(ext.historial), 2)
        self.assertIn("RF-99", " ".join(ext.historial[0]))
        # el mensaje de corrección incluye los errores del intento anterior
        self.assertIn("RF-99", str(llm.mensajes[1][-1]))

    def test_falla_si_agota_reintentos(self):
        malo = modelo_ref()
        malo.casos_uso[0].req_ids = ["RF-99"]
        llm = LLMSimulado([respuesta(malo)] * 3)
        ext = extraer_modelo(self.texto, self.ids, llm, max_reintentos=2, log=lambda *a: None)
        self.assertFalse(ext.ok)
        self.assertEqual(llm.llamadas, 3)


class TestRender(unittest.TestCase):
    def test_diagramas_y_codigo(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            puml = render_diagramas(modelo_ref(), tmp / "d")
            self.assertEqual(len(puml), 5)
            clases = (tmp / "d" / "02_clases.puml").read_text(encoding="utf-8")
            self.assertIn("Objeto <|-- Arma", clases)
            self.assertIn('Tienda "1" *-- "0..*" ArticuloEnVenta', clases)
            er = (tmp / "d" / "03_er.puml").read_text(encoding="utf-8")
            self.assertIn("Tienda ||--o{ ArticuloEnVenta", er)
            for p in puml:
                t = p.read_text(encoding="utf-8")
                self.assertTrue(t.startswith("@startuml") and t.rstrip().endswith("@enduml"))

            archivos = render_codigo(modelo_ref(), "ambos", tmp / "c")
            py = tmp / "c" / "python" / "modelo.py"
            subprocess.run([sys.executable, "-I", "-m", "py_compile", str(py)], check=True)
            self.assertGreaterEqual(len(archivos), 6)

    @unittest.skipUnless(shutil.which("javac"), "javac no está instalado")
    def test_java_compila(self):
        with tempfile.TemporaryDirectory() as tmp:
            render_codigo(modelo_ref(), "java", Path(tmp) / "c")
            fuentes = [str(p) for p in (Path(tmp) / "c" / "java").glob("*.java")]
            r = subprocess.run(["javac", "-d", str(Path(tmp) / "out"), *fuentes], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_incluye_extiende_y_nm(self):
        m = modelo_ref()
        m.casos_uso[1].incluye = ["CU-01"]
        m.casos_uso[2].extiende = ["CU-01"]
        m.relaciones[1].multiplicidad_hasta = "*"
        with tempfile.TemporaryDirectory() as tmp:
            render_diagramas(m, Path(tmp))
            cu = (Path(tmp) / "01_casos_de_uso.puml").read_text(encoding="utf-8")
            self.assertIn("CU_02 .> CU_01 : <<include>>", cu)
            self.assertIn("CU_03 .> CU_01 : <<extend>>", cu)
            self.assertIn("N:M", (Path(tmp) / "03_er.puml").read_text(encoding="utf-8"))


class TestPipelineCompleto(unittest.TestCase):
    def test_con_llm_simulado(self):
        with tempfile.TemporaryDirectory() as tmp:
            llm = LLMSimulado([respuesta(modelo_ref())])
            cod = ejecutar(SPEC, Path(tmp), "ambos", "ollama", llm=llm, log=lambda *a: None)
            self.assertEqual(cod, 0)
            for nombre in ("modelo.json", "reporte.md", "trazabilidad_generada.csv"):
                self.assertTrue((Path(tmp) / nombre).exists(), nombre)

    def test_modelo_invalido_no_genera_diagramas(self):
        malo = modelo_ref()
        malo.casos_uso[0].req_ids = ["RF-99"]
        with tempfile.TemporaryDirectory() as tmp:
            cod = ejecutar(SPEC, Path(tmp), "python", "ollama", llm=LLMSimulado([respuesta(malo)] * 3), log=lambda *a: None)
            self.assertEqual(cod, 2)
            self.assertFalse((Path(tmp) / "diagramas").exists())
            self.assertTrue((Path(tmp) / "reporte.md").exists())

    def test_spec_con_errores(self):
        with tempfile.TemporaryDirectory() as tmp:
            malo = Path(tmp) / "mala.md"
            malo.write_text("# vacío\n", encoding="utf-8")
            self.assertEqual(ejecutar(malo, Path(tmp) / "s", log=lambda *a: None), 1)


class TestIntegracionLangChain(unittest.TestCase):
    """Verifica que las clases reales de LangChain aceptan nuestra configuración (sin conectarse)."""

    def test_ollama(self):
        try:
            from spec2code.llm import crear_llm
            llm = crear_llm("ollama", "qwen2.5:7b")
        except ImportError:
            self.skipTest("langchain-ollama no está instalado")
        self.assertIsNotNone(llm.with_structured_output(ModeloAnalisis, include_raw=True))

    def test_groq(self):
        try:
            from spec2code.llm import crear_llm
            with mock.patch.dict(os.environ, {"GROQ_API_KEY": "clave-falsa-de-prueba"}):
                llm = crear_llm("groq")
        except ImportError:
            self.skipTest("langchain-groq no está instalado")
        self.assertIsNotNone(llm.with_structured_output(ModeloAnalisis, include_raw=True))


if __name__ == "__main__":
    unittest.main()
