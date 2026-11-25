# Módulo: Misiones y progresión

## 1. Contexto y alcance

RPG Manager administra personajes de un juego de rol. Este módulo permite al jugador consultar misiones disponibles, aceptarlas, conocer su avance, completarlas o abandonarlas, recibir experiencia, subir de nivel y consultar el historial de intentos cerrados. También recibe eventos de avance del motor del juego, representado como una entrada simulada del propio módulo.

El módulo trabaja con un catálogo de misiones predefinido. Cada misión tiene un identificador único, nombre, nivel requerido, objetivo total y recompensa fija de experiencia. Cada personaje tiene identificador único, nombre, nivel y experiencia disponible hacia el siguiente nivel. Para conservar el historial, cada aceptación de una misión genera un intento independiente asociado a un personaje y una misión.

Quedan fuera de alcance la creación y edición de personajes, la administración del catálogo de misiones, el combate, el inventario, el equipamiento, la autenticación de cuentas y las integraciones con módulos de otros equipos. El motor del juego solo entrega al módulo el identificador del intento activo y la cantidad de unidades de avance; la fuente real de esas acciones no se implementa aquí. No se requiere una base de datos ni una interfaz gráfica como parte de esta especificación.

Esta primera versión parte de US01 a US08 del backlog de Scrum, incorporando la funcionalidad de abandonar misiones y el registro de avance como operación mínima necesaria para consultar y completar objetivos.

## 2. Actores

- **Jugador**: persona que controla un personaje y consulta, acepta, completa o abandona misiones, además de consultar su experiencia, nivel e historial.
- **Motor del juego**: origen simulado de eventos que registran las unidades de avance de un intento de misión activa; no requiere integración real con otros módulos.

## 3. Requerimientos funcionales

- **RF-01** El jugador puede consultar el catálogo de misiones disponibles para su personaje. Una misión está disponible cuando el personaje cumple el nivel requerido y no tiene un intento activo ni uno completado de esa misión; los intentos abandonados no la bloquean.
  - Criterio de aceptación: dado un personaje de nivel 2, cuando consulta las misiones disponibles, entonces se muestran únicamente las misiones con nivel requerido menor o igual a 2 que no estén activas ni completadas por ese personaje, detallando identificador, nombre, nivel requerido, objetivo total y recompensa de experiencia.

- **RF-02** El jugador puede aceptar una misión disponible para su personaje y comenzar un nuevo intento.
  - Criterio de aceptación: dado un personaje con menos de 3 misiones activas y nivel suficiente, cuando acepta una misión que no está activa ni completada, entonces se crea un intento con identificador propio, avance 0, estado `activa` y fecha de inicio; si infringe RN-01, RN-02 o RN-07, no se crea el intento y se informa la regla incumplida.

- **RF-03** El jugador puede consultar el avance de un intento activo de misión de su personaje, expresado en unidades y en porcentaje entero.
  - Criterio de aceptación: dado el identificador de un personaje y el identificador de una misión con un intento activo que tiene 2 unidades completadas de 5, cuando el jugador consulta su progreso, entonces se muestran 2 de 5 unidades y 40 % de avance; si no existe un intento activo de esa misión para el personaje, no se modifica ningún dato y se informa el motivo.

- **RF-04** El jugador puede completar una misión cuando su intento activo alcanza la totalidad del objetivo.
  - Criterio de aceptación: dado un intento activo con avance igual al objetivo total, cuando el jugador solicita completarlo, entonces el intento cambia a estado `completada`, registra fecha de cierre y dispara automáticamente RF-05 una sola vez; si el avance es inferior al objetivo o el intento no está activo, la operación se rechaza sin modificar datos.

- **RF-05** El sistema otorga automáticamente al personaje la recompensa fija de experiencia correspondiente a una misión completada mediante RF-04.
  - Criterio de aceptación: dada una misión con recompensa de 60 puntos y una finalización válida ejecutada desde RF-04, cuando el sistema procesa la recompensa, entonces la experiencia disponible del personaje aumenta en 60 puntos y dispara automáticamente RF-07; si ese personaje ya fue recompensado por completar la misma misión, no se suman puntos adicionales.

- **RF-06** El jugador puede consultar el nivel actual, la experiencia disponible, la experiencia requerida para el siguiente nivel y la experiencia faltante de su personaje.
  - Criterio de aceptación: dado un personaje de nivel 2 con 50 puntos de experiencia disponibles hacia el siguiente nivel, cuando consulta su progresión, entonces se muestran nivel 2, experiencia disponible 50, umbral requerido 200 y experiencia faltante 150.

- **RF-07** El sistema aumenta automáticamente el nivel del personaje cuando la experiencia disponible alcanza o supera el umbral del nivel actual tras ejecutar RF-05.
  - Criterio de aceptación: dado un personaje de nivel 1 con 90 puntos de experiencia, cuando recibe una recompensa válida de 20 puntos, entonces sube a nivel 2 y conserva 10 puntos; dado un personaje de nivel 1 con experiencia 0 que obtiene 350 puntos, entonces alcanza nivel 3 con 50 puntos sobrantes.

- **RF-08** El jugador puede consultar el historial de intentos de misión completados o abandonados de su personaje.
  - Criterio de aceptación: dado un personaje con intentos cerrados, cuando consulta su historial, entonces se muestra cada intento cerrado con identificador, nombre de misión, estado y fecha de cierre, ordenados desde el cierre más reciente al más antiguo (y por identificador de intento descendente en caso de empate en la fecha); los intentos activos no se incluyen y, si no existen intentos cerrados, se muestra una lista vacía.

- **RF-09** El jugador puede abandonar una misión con intento activo.
  - Criterio de aceptación: dado un intento activo, cuando el jugador lo abandona, entonces cambia a estado `abandonada`, registra fecha de cierre, otorga 0 puntos de experiencia y libera el cupo activo; un nuevo intento posterior de esa misión comienza con avance 0.

- **RF-10** El motor del juego puede registrar unidades de avance sobre un intento de misión activo.
  - Criterio de aceptación: dado un intento activo con avance 2 de 5, cuando el motor registra 1 unidad, entonces el avance queda en 3 de 5; si la cantidad es menor o igual a 0, supera el objetivo total o el intento no está activo, la operación se rechaza sin modificar el avance.

## 4. Requerimientos no funcionales

- **RNF-01** La consulta de misiones disponibles y la consulta de historial deben responder en 2 segundos o menos en al menos 95 de cada 100 solicitudes de prueba, con un catálogo de hasta 200 misiones y hasta 100 intentos registrados por personaje.

- **RNF-02** Las operaciones de aceptar, completar, abandonar y registrar avance deben responder en 2 segundos o menos en al menos 95 de cada 100 solicitudes de prueba, con un catálogo de hasta 200 misiones y hasta 100 intentos registrados por personaje.

- **RNF-03** La suite de pruebas unitarias debe incluir al menos 2 casos de prueba por cada una de las 8 reglas de negocio (RN-01 a RN-08), cubriendo un escenario válido y un escenario rechazado o límite, alcanzando el 100 % de pruebas aprobadas sobre la lógica implementada.

## 5. Reglas de negocio

- **RN-01** El personaje solo puede aceptar una misión cuando su nivel actual es mayor o igual que el nivel requerido por esa misión.

- **RN-02** Un personaje puede mantener como máximo 3 intentos de misión en estado `activa` al mismo tiempo. Los intentos en estado `completada` y `abandonada` no ocupan cupo activo.

- **RN-03** Para pasar del nivel N al nivel N+1 se requieren 100 × N puntos de experiencia disponible, con N entero mayor o igual a 1. Al subir de nivel se descuenta ese umbral y la experiencia sobrante se conserva; el proceso se repite mientras alcance para otro nivel.

- **RN-04** Una misión solo puede completarse si existe un intento del personaje en estado `activa` y su avance es exactamente igual al objetivo total. Completar registra el estado `completada` y la fecha de cierre.

- **RN-05** Cada misión otorga su recompensa de experiencia una sola vez por personaje, exclusivamente al completarse de forma válida. Solicitar nuevamente la finalización no vuelve a otorgar experiencia.

- **RN-06** Abandonar una misión solo se permite si el intento está en estado `activa`; al abandonarla no se otorga experiencia. El personaje puede volver a aceptarla si cumple las demás reglas, pero cada nueva aceptación crea otro intento con avance 0 y conserva el intento abandonado en el historial.

- **RN-07** Un personaje no puede aceptar una misión si ya tiene un intento activo o un intento completado de esa misma misión. Una misión abandonada puede volver a aceptarse conforme a RN-06.

- **RN-08** Un registro de avance debe indicar un número entero de unidades mayor que 0, aplicarse únicamente a un intento en estado `activa` y no superar el objetivo total de la misión. Registrar avance no completa automáticamente la misión ni otorga experiencia.

## 6. Supuestos y glosario

- **Personaje**: entidad mínima del módulo con identificador único, nombre, nivel actual y experiencia disponible. Inicia en nivel 1 con 0 puntos de experiencia; sus demás atributos pertenecen a otros módulos.
- **Misión**: definición del catálogo con identificador único, nombre, nivel requerido mayor o igual a 1, objetivo total entero mayor o igual a 1 y recompensa fija de experiencia entera mayor que 0. El catálogo está predefinido y su administración queda fuera de alcance.
- **Intento de misión**: registro independiente creado cada vez que un personaje acepta una misión; contiene identificador propio, referencia al personaje y la misión, estado, avance actual, fecha de inicio y fecha de cierre si corresponde.
- **Estados de un intento**: `activa`, `completada` y `abandonada`. Solo se permiten las transiciones de `activa` a `completada` o de `activa` a `abandonada`. Una nueva aceptación crea un nuevo intento, no reactiva el anterior.
- **Misión disponible**: misión del catálogo que cumple el nivel del personaje y que ese personaje no tiene activa ni completada. Un intento abandonado no impide una nueva aceptación.
- **Avance**: número entero de unidades de objetivo completadas, desde 0 hasta el objetivo total. El porcentaje se calcula como la parte entera de 100 × avance / objetivo total.
- **Experiencia disponible**: puntos enteros no negativos acumulados hacia el siguiente nivel después de descontar los umbrales de niveles superados. No se representa como experiencia total histórica.
- **Recompensa de experiencia**: cantidad fija positiva definida en cada misión. Se aplica una vez por personaje al completar la misión.
- **Historial de misiones**: conjunto de intentos cerrados de un personaje, incluidos los completados y abandonados; se presenta del más reciente al más antiguo.
- **Motor del juego**: actor simulado que envía el identificador de intento y un incremento de unidades de avance; no requiere implementación de combate ni conexión a sistemas de otros equipos.
- **Límites y errores**: las operaciones que incumplen una regla no modifican el estado del personaje, la misión ni el intento. Para evitar ambigüedad, el motivo del rechazo identifica la regla RN correspondiente.
