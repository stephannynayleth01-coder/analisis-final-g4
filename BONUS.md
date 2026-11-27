# Bonus C — Métodos con parámetros

## 1. Qué mejoramos

Durante la primera y segunda corrida del módulo **Misiones y progresión**, encontramos que el pipeline generaba los métodos sin parámetros, aunque estos estuvieran definidos en nuestra especificación. Por ejemplo, RF-02 establece `aceptar_mision(mision)` y RF-10 define `registrar_avance(unidades)`, pero el código generado originalmente mostraba `aceptarMision()` y `registrarAvance()`.

Por esta razón, elegimos la **opción C del bonus**, con el objetivo de mejorar el pipeline para que los métodos puedan recibir parámetros y estos se representen correctamente en el diagrama de clases y en el código Python y Java.

La mejora permite que el modelo intermedio (`modelo.json`) incluya los nombres y tipos de los parámetros de cada método.

## 2. Archivos que modificamos

| Archivo | Cambio realizado |
|---|---|
| `spec2code/schema.py` | Agregamos la clase `Parametro` con nombre y tipo, y permitimos que cada método tenga una lista de parámetros, vacía por defecto. |
| `spec2code/render.py` | Adaptamos la conversión de los tipos de parámetros para PlantUML, Python y Java. También incorporamos los imports necesarios para fechas y listas. |
| `spec2code/validar.py` | Agregamos validaciones para detectar parámetros repetidos, nombres incorrectos y referencias a tipos que no existen. |
| `spec2code/prompts.py` | Ajustamos las instrucciones para que la IA identifique los parámetros definidos en la especificación sin inventar información. |
| `plantillas/clases.puml.j2` | Incorporamos los nombres y tipos de los parámetros en los métodos del diagrama de clases. |
| `plantillas/codigo_python.py.j2` | Modificamos la generación de métodos para incluir parámetros tipados y comentarios sobre los datos de entrada. |
| `plantillas/codigo_java.java.j2` | Incorporamos parámetros tipados y comentarios JavaDoc con sus respectivos `@param`. |
| `pruebas/test_bonus_parametros.py` | Agregamos cinco pruebas unitarias para comprobar la generación de parámetros, sus tipos, las validaciones y la compatibilidad con modelos anteriores. |
| `pruebas/fixtures/modelo_e4_parametros.json` | Preparamos un modelo de demostración basado en la segunda corrida de nuestro módulo, agregando los parámetros definidos en `spec_final.md`. |

El archivo `modelo_e4_parametros.json` nos permite comprobar la mejora sin depender de una nueva respuesta de Ollama. Este archivo se utiliza únicamente para las pruebas del bonus y no reemplaza el `modelo.json` de nuestra entrega principal.

## 3. Ejemplo del resultado

Con los cambios realizados, la operación para aceptar una misión ahora se representa de la siguiente manera:

| Artefacto | Método generado |
|---|---|
| PlantUML | `aceptar_mision(mision : Mision)` |
| Python | `def aceptar_mision(self, mision: Mision) -> None:` |
| Java | `public void aceptarMision(Mision mision)` |

También conseguimos que la operación para registrar avance incluya el parámetro `unidades`:

| Artefacto | Método generado |
|---|---|
| PlantUML | `registrar_avance(unidades : int)` |
| Python | `def registrar_avance(self, unidades: int) -> None:` |
| Java | `public void registrarAvance(int unidades)` |

La mejora admite tipos como `string`, `int`, `decimal`, `bool`, `date`, `list` y referencias a entidades existentes dentro del modelo. Además, incorporamos validaciones para impedir que se generen parámetros duplicados o que hagan referencia a clases inexistentes.

## 4. Resultados obtenidos

Después de incorporar los cambios, ejecutamos las pruebas unitarias y generamos nuevamente los artefactos del módulo E4 utilizando nuestro modelo de demostración.

Obtuvimos los siguientes resultados:

- **20 pruebas unitarias aprobadas**, sin errores y sin pruebas omitidas. Las 15 pruebas originales del pipeline y las 5 nuevas pruebas del bonus finalizaron correctamente.
- El pipeline generó **11 diagramas y 4 archivos de código**, correspondientes a un archivo Python y tres clases Java.
- Los parámetros aparecieron correctamente en el diagrama de clases y en las firmas de los métodos generados en ambos lenguajes.
- El código Python pasó la comprobación de sintaxis mediante `py_compile`.
- Las tres clases Java generadas compilaron correctamente utilizando `javac`.
- Comprobamos que los modelos anteriores que no tienen parámetros siguen funcionando sin cambios. Con el ejemplo original del herrero se conservaron los mismos 5 diagramas y 7 archivos de código del pipeline inicial.
- El validador detectó correctamente parámetros repetidos y referencias a tipos inexistentes.

Las pruebas unitarias se ejecutaron con `python -m unittest discover -s pruebas -v`, mientras que la generación de nuestro módulo se realizó con `generar.py`, utilizando `spec_final.md`.