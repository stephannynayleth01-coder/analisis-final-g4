# pruebas/test_bonus_parametros.py
"""Pruebas del bonus C: firmas tipadas en modelo, UML, Python y Java.

Entradas: modelo de referencia y fixture del equipo E4.
Salidas: aserciones sobre esquemas, validación y código que compila.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from spec2code.pipeline import ejecutar
from spec2code.render import render_codigo, render_diagramas
from spec2code.schema import ModeloAnalisis, Parametro
from spec2code.spec_lint import revisar_spec
from spec2code.validar import validar


class TestBonusParametros(unittest.TestCase):
    """Comprueba firmas de argumentos sin implementar ninguna regla del juego."""

    def setUp(self) -> None:
        """Carga el modelo original del profesor; sin parámetros inicialmente."""
        self.spec = RAIZ / 'specs' / 'ejemplo_tienda_herrero.md'
        data = (RAIZ / 'specs' / 'ejemplo_tienda_herrero.modelo.json').read_text(encoding='utf-8')
        self.modelo = ModeloAnalisis.model_validate_json(data).canonizar()
        self.ids = revisar_spec(self.spec.read_text(encoding='utf-8')).ids

    def test_modelos_antiguos_no_necesitan_parametros(self) -> None:
        """Entrada: modelo viejo; salida: firmas originales vacías y sin error."""
        met = self.modelo.entidades[1].metodos[0]
        self.assertEqual(met.parametros, [])
        self.assertEqual(validar(self.modelo, self.ids).errores, [])
        with tempfile.TemporaryDirectory() as tmp:
            render_diagramas(self.modelo, Path(tmp) / 'diagramas')
            render_codigo(self.modelo, 'ambos', Path(tmp) / 'codigo')
            uml = (Path(tmp) / 'diagramas/02_clases.puml').read_text(encoding='utf-8')
            java = (Path(tmp) / 'codigo/java/Tienda.java').read_text(encoding='utf-8')
            self.assertIn('listar_catalogo() : List', uml)
            self.assertIn('listarCatalogo()', java)

    def test_parametros_se_normalizan_y_renderizan_tipos(self) -> None:
        """Entrada: nombres y tipos; salida: firmas coherentes en los tres lenguajes."""
        met = self.modelo.entidades[1].metodos[1]
        met.parametros = [
            Parametro(nombre='personaje', tipo='Personaje'),
            Parametro(nombre='cantidad unidades', tipo='entero'),
            Parametro(nombre='fecha entrega', tipo='fecha'),
            Parametro(nombre='articulos', tipo='lista'),
            Parametro(nombre='disponible', tipo='booleano'),
        ]
        self.assertEqual(validar(self.modelo, self.ids).errores, [])
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            render_diagramas(self.modelo, tmp / 'd')
            render_codigo(self.modelo, 'ambos', tmp / 'c')
            uml = (tmp / 'd/02_clases.puml').read_text(encoding='utf-8')
            py = (tmp / 'c/python/modelo.py').read_text(encoding='utf-8')
            java = (tmp / 'c/java/Tienda.java').read_text(encoding='utf-8')
            self.assertIn('vender_a_personaje(personaje : Personaje, cantidad_unidades : int, fecha_entrega : Date, articulos : List, disponible : boolean)', uml)
            self.assertIn('def vender_a_personaje(self, personaje: Personaje, cantidad_unidades: int, fecha_entrega: date, articulos: list, disponible: bool)', py)
            self.assertIn('venderAPersonaje(Personaje personaje, int cantidadUnidades, LocalDate fechaEntrega, List<Object> articulos, boolean disponible)', java)
            self.assertIn('from datetime import date', py)
            self.assertIn('import java.time.LocalDate;', java)
            self.assertIn('import java.util.List;', java)
            subprocess.run([sys.executable, '-m', 'py_compile', str(tmp / 'c/python/modelo.py')], check=True)
            if shutil.which('javac'):
                code = list((tmp / 'c/java').glob('*.java'))
                res = subprocess.run(['javac', '-d', str(tmp / 'classes'), *map(str, code)], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, res.stderr)

    def test_esquema_y_prompt_explican_los_parametros(self) -> None:
        """Entrada: esquema Pydantic y prompt; salida: contrato visible para el LLM."""
        from spec2code.prompts import SISTEMA

        esquema = ModeloAnalisis.model_json_schema()
        metodo = esquema['$defs']['Metodo']['properties']
        self.assertIn('parametros', metodo)
        self.assertIn('Parametro', str(metodo['parametros']))
        self.assertIn('"parametros"', SISTEMA)
        self.assertIn('No inventes entradas', SISTEMA)

    def test_parametros_invalidos_se_rechazan(self) -> None:
        """Entrada: tipos inexistentes y nombres repetidos; salida: errores precisos."""
        met = self.modelo.entidades[1].metodos[1]
        met.parametros = [
            Parametro(nombre='costo', tipo='entero'),
            Parametro(nombre='Costo', tipo='entero'),
            Parametro(nombre='fantasma', tipo='EntidadFantasma'),
            Parametro(nombre='self', tipo='texto'),
        ]
        errors = ' '.join(validar(self.modelo, self.ids).errores)
        self.assertIn('repetido', errors)
        self.assertIn('EntidadFantasma', errors)
        self.assertIn('self', errors)

    def test_generacion_pipeline_e4_con_parametros(self) -> None:
        """Entrada: spec E4 y modelo enriquecido; salida: UML y código tipado correcto."""
        spec = RAIZ / 'specs/spec_final.md'
        fixture = RAIZ / 'pruebas/fixtures/modelo_e4_parametros.json'
        data = json.loads(fixture.read_text(encoding='utf-8'))
        self.assertEqual(data['modulo'], 'Misiones y progresión')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            self.assertEqual(ejecutar(spec, tmp / 'salida', 'ambos', sin_llm=fixture, log=lambda *x: None), 0)
            clases = (tmp / 'salida/diagramas/02_clases.puml').read_text(encoding='utf-8')
            py = (tmp / 'salida/codigo/python/modelo.py').read_text(encoding='utf-8')
            java = (tmp / 'salida/codigo/java/Personaje.java').read_text(encoding='utf-8')
            self.assertIn('aceptar_mision(mision : Mision)', clases)
            self.assertIn('registrar_avance(unidades : int)', clases)
            self.assertIn('def aceptar_mision(self, mision: Mision)', py)
            self.assertIn('def registrar_avance(self, unidades: int)', py)
            self.assertIn('aceptarMision(Mision mision)', java)
            self.assertIn('otorgarExperiencia(int puntos)', java)
            self.assertEqual(json.loads((tmp / 'salida/modelo.json').read_text(encoding='utf-8'))['modulo'], 'Misiones y progresión')
            subprocess.run([sys.executable, '-m', 'py_compile', str(tmp / 'salida/codigo/python/modelo.py')], check=True)
            if shutil.which('javac'):
                java_files = list((tmp / 'salida/codigo/java').glob('*.java'))
                proc = subprocess.run(['javac', '-d', str(tmp / 'clases'), *map(str, java_files)], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == '__main__':
    unittest.main()
