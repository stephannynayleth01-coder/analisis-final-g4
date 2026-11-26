# Módulo: Misiones y progresión

## 1. Contexto y alcance

RPG Manager administra personajes de un juego de rol. Este módulo permite al jugador consultar misiones disponibles, aceptarlas, conocer su avance, completarlas o abandonarlas, recibir experiencia, subir de nivel y consultar el historial de intentos cerrados. También recibe eventos de avance del motor del juego, representado como una entrada simulada del propio módulo.

El módulo trabaja con un catálogo de misiones predefinido. Cada misión tiene un identificador único, nombre, nivel requerido, objetivo total y recompensa fija de experiencia. Cada personaje tiene identificador único, nombre, nivel y experiencia disponible hacia el siguiente nivel. Para conservar el historial, cada aceptación de una misión genera un intento independiente asociado a un personaje y una misión. Un personaje recién creado comienza sin intentos de misión asociados (0 intentos).

Quedan fuera de alcance la creación y edición de personajes, la administración del catálogo de misiones, el combate, el inventario, el equipamiento, la autenticación de cuentas y las integraciones con módulos de otros equipos. El motor del juego solo entrega al módulo el identificador del intento activo y la cantidad de unidades de avance; la fuente real de esas acciones no se implementa aquí. No se requiere una base de datos ni una interfaz gráfica como parte de esta especificación.

Esta versión final refina la especificación tras auditar la primera corrida del pipeline, explicitando los tipos de retorno de cada consulta, la asignación de responsabilidades entre `Personaje` e `IntentoMision`, la encapsulación de la progresión (otorgar experiencia y subir de nivel) y las multiplicidades entre entidades.

## 2. Actores

- **Jugador**: persona que controla un personaje y ejecuta las operaciones de consultar misiones disponibles, aceptar misión, consultar avance, completar misión, abandonar misión, consultar progresión y consultar historial. No ejecuta directamente operaciones internas de suma de experiencia ni de ascenso de nivel.
- **Motor del juego**: origen simulado de eventos que invoca exclusivamente el registro de unidades de avance sobre un intento de misión activo; no requiere integración real con otros módulos.

## 3. Requerimientos funcionales

- **RF-01** El jugador puede consultar el catálogo de misiones disponibles para su personaje mediante la operación `Personaje.consultar_misiones_disponibles()`, que retorna una lista de objetos `Mision`. Una misión es disponible si cumple `Personaje.nivel >= Mision.nivel_requerido` y el personaje no tiene ningún `IntentoMision` en estado `activa` ni `completada` para esa misión (los intentos `abandonada` no bloquean).
  - Criterio de aceptación: dado un personaje de nivel 2, cuando consulta las misiones disponibles, entonces el sistema retorna una lista con las misiones de nivel requerido menor o igual a 2 que no estén activas ni completadas por ese personaje, incluyendo identificador, nombre, nivel requerido, objetivo total y recompensa de experiencia; si ninguna cumple, retorna una lista vacía.

- **RF-02** El jugador puede aceptar una misión disponible para su personaje mediante `Personaje.aceptar_mision(mision)`, operación que valida RN-01, RN-02 y RN-07 y retorna el nuevo objeto `IntentoMision` creado en estado `activa` con avance 0 y fecha de inicio actual.
  - Criterio de aceptación: dado un personaje con menos de 3 intentos en estado `activa` y nivel mayor o igual al requerido, cuando acepta una misión sin intento activo ni completado previo, entonces se crea y retorna un `IntentoMision` con identificador propio, avance 0, estado `activa` y fecha de inicio; si incumple RN-01, RN-02 o RN-07, no se crea el intento y se lanza un error indicando la regla incumplida.

- **RF-03** El jugador puede consultar el avance de un intento activo de misión mediante `Personaje.consultar_avance(mision)`, operación que localiza el `IntentoMision` en estado `activa` de esa misión para el personaje y retorna una estructura de resumen con las unidades completadas, el objetivo total y el porcentaje entero calculado como `parte_entera(100 * avance / objetivo_total)`.
  - Criterio de aceptación: dado un personaje con un intento activo en una misión de objetivo total 5 con 2 unidades completadas, cuando consulta el avance, entonces el sistema retorna 2 unidades, objetivo 5 y 40 % de avance; si no existe un intento en estado `activa` de esa misión para el personaje, no se modifica ningún dato y se informa el motivo.

- **RF-04** El jugador puede completar una misión mediante `Personaje.completar_mision(mision)`, que delega en `IntentoMision.completar()` tras verificar RN-04, cambia el estado del intento a `completada`, registra la fecha de cierre, invoca internamente `Personaje.otorgar_experiencia(puntos)` una única vez y retorna el intento actualizado.
  - Criterio de aceptación: dado un intento en estado `activa` cuyo avance es igual al objetivo total, cuando el jugador solicita completarlo, entonces el intento cambia a estado `completada`, registra fecha de cierre, invoca la entrega única de experiencia (RF-05) y retorna el intento cerrado; si el intento no está en estado `activa` o su avance es menor al objetivo total, la operación se rechaza por RN-04 o RN-05 sin modificar datos.

- **RF-05** El sistema otorga automáticamente al personaje la recompensa fija de experiencia mediante la operación interna `Personaje.otorgar_experiencia(puntos)`, invocada exclusivamente desde `IntentoMision.completar()` al validar una finalización única por misión (RN-05), sumando los puntos a `Personaje.experiencia_disponible` e invocando inmediatamente `Personaje.verificar_subida_nivel()`.
  - Criterio de aceptación: dada una misión con recompensa de 60 puntos completada por primera vez por el personaje, cuando se ejecuta `otorgar_experiencia(60)`, entonces `experiencia_disponible` aumenta en 60 puntos y se ejecuta automáticamente la verificación de ascenso (RF-07); si la misión ya fue completada previamente por ese personaje, se rechaza cualquier otorgamiento adicional por RN-05.

- **RF-06** El jugador puede consultar su estado de progresión mediante `Personaje.consultar_progresion()`, operación que calcula `umbral_siguiente = 100 * nivel` y `experiencia_faltante = umbral_siguiente - experiencia_disponible`, retornando nivel actual, experiencia disponible, umbral requerido y experiencia faltante.
  - Criterio de aceptación: dado un personaje de nivel 2 con 50 puntos de experiencia disponible, cuando consulta su progresión, entonces el sistema retorna nivel 2, experiencia disponible 50, umbral requerido 200 y experiencia faltante 150.

- **RF-07** El sistema aumenta automáticamente el nivel del personaje mediante la operación interna `Personaje.verificar_subida_nivel()`, ejecutada al final de `Personaje.otorgar_experiencia(puntos)`, descontando `100 * nivel` de `experiencia_disponible` e incrementando `nivel` en 1 de forma iterativa mientras `experiencia_disponible >= 100 * nivel` (RN-03).
  - Criterio de aceptación: dado un personaje de nivel 1 con 90 puntos de experiencia, cuando recibe 20 puntos mediante RF-05, entonces sube a nivel 2 y conserva 10 puntos de experiencia disponible; dado un personaje de nivel 1 con 0 puntos que recibe 350 puntos, entonces alcanza nivel 3 y conserva 50 puntos sobrantes.

- **RF-08** El jugador puede consultar el historial de intentos cerrados mediante `Personaje.consultar_historial()`, operación que filtra únicamente los `IntentoMision` del personaje en estado `completada` o `abandonada` (excluyendo `activa`), los ordena por fecha de cierre descendente (y por identificador de intento descendente en caso de empate) y retorna dicha lista.
  - Criterio de aceptación: dado un personaje con intentos cerrados y activos, cuando consulta su historial, entonces el sistema retorna una lista únicamente con los intentos en estado `completada` o `abandonada` (incluyendo identificador, nombre de misión, estado y fecha de cierre) ordenados del cierre más reciente al más antiguo; si no tiene intentos cerrados, retorna una lista vacía.

- **RF-09** El jugador puede abandonar una misión activa mediante `Personaje.abandonar_mision(mision)`, operación que valida que el intento esté en estado `activa` (RN-06), invoca `IntentoMision.abandonar()` para cambiar su estado a `abandonada` y registrar la fecha de cierre sin otorgar experiencia ni registrar avance, liberando el cupo activo y retornando el intento cerrado.
  - Criterio de aceptación: dado un intento en estado `activa`, cuando el jugador solicita abandonarlo, entonces cambia a estado `abandonada`, registra fecha de cierre, otorga 0 puntos de experiencia, libera un cupo activo y retorna el intento cerrado sin invocar ningún registro de avance; un nuevo intento posterior de esa misión comienza con avance 0.

- **RF-10** El motor del juego puede registrar unidades de avance sobre un intento activo mediante `IntentoMision.registrar_avance(unidades)`, operación que valida RN-08 (unidades enteras mayores que 0, intento en estado `activa` y `avance + unidades <= objetivo_total`), suma las unidades a `avance` y retorna el intento actualizado sin completarlo ni otorgar experiencia.
  - Criterio de aceptación: dado un intento en estado `activa` con avance 2 de 5, cuando el motor ejecuta `registrar_avance(1)`, entonces el avance pasa a 3 de 5 y retorna el intento actualizado; si `unidades <= 0`, `avance + unidades > objetivo_total` o el estado no es `activa`, se rechaza por RN-08 sin modificar el avance.

## 4. Requerimientos no funcionales

- **RNF-01** La consulta de misiones disponibles (`consultar_misiones_disponibles`) y la consulta de historial (`consultar_historial`) deben responder en 2 segundos o menos en al menos 95 de cada 100 solicitudes de prueba, con un catálogo de hasta 200 misiones y hasta 100 intentos registrados por personaje.

- **RNF-02** Las operaciones de aceptar, completar, abandonar y registrar avance deben responder en 2 segundos o menos en al menos 95 de cada 100 solicitudes de prueba, con un catálogo de hasta 200 misiones y hasta 100 intentos registrados por personaje.

- **RNF-03** La suite de pruebas unitarias debe incluir al menos 2 casos de prueba por cada una de las 8 reglas de negocio (RN-01 a RN-08), cubriendo un escenario válido y un escenario rechazado o límite, alcanzando el 100 % de pruebas aprobadas sobre la lógica implementada.

## 5. Reglas de negocio

- **RN-01** El personaje solo puede aceptar una misión cuando `Personaje.nivel >= Mision.nivel_requerido`. Se verifica dentro de `Personaje.aceptar_mision(mision)` antes de crear el intento.

- **RN-02** Un personaje puede mantener como máximo 3 registros de `IntentoMision` en estado `activa` simultáneamente (`0` a `3` intentos activos; un personaje puede tener `0` intentos totales al iniciar). Los intentos en estado `completada` y `abandonada` no ocupan cupo activo. Se verifica dentro de `Personaje.aceptar_mision(mision)`.

- **RN-03** Para pasar del nivel `N` al nivel `N+1` se requieren exactamente `100 * N` puntos de `experiencia_disponible`, con `N` entero mayor o igual a 1. Dentro de `Personaje.verificar_subida_nivel()`, mientras `experiencia_disponible >= 100 * nivel`, se descuenta `100 * nivel` de `experiencia_disponible` y se incrementa `nivel` en 1, conservando el sobrante.

- **RN-04** Una misión solo puede completarse mediante `IntentoMision.completar()` si existe un intento del personaje en estado `activa` y `IntentoMision.avance == Mision.objetivo_total`. Completar cambia el estado a `completada` y registra la fecha de cierre.

- **RN-05** Cada misión otorga su recompensa de experiencia (`Mision.recompensa_experiencia`) una sola vez por personaje, exclusivamente al completarse por primera vez mediante `IntentoMision.completar()` e invocar `Personaje.otorgar_experiencia(puntos)`. Si el personaje ya posee un intento `completada` para esa misión o intenta completarla nuevamente, no se otorga experiencia.

- **RN-06** Abandonar una misión mediante `IntentoMision.abandonar()` solo se permite si el intento está en estado `activa`; registra el estado `abandonada`, asigna la fecha de cierre y otorga 0 puntos de experiencia (nunca invoca `registrar_avance` ni `otorgar_experiencia`). El personaje puede volver a aceptar la misión creando un nuevo `IntentoMision` con avance 0 mientras conserva el intento abandonado en el historial.

- **RN-07** Un personaje no puede aceptar una misión si ya tiene un `IntentoMision` en estado `activa` o `completada` para esa misma misión. Un intento previo en estado `abandonada` no impide una nueva aceptación conforme a RN-06. Se verifica dentro de `Personaje.aceptar_mision(mision)`.

- **RN-08** La operación `IntentoMision.registrar_avance(unidades)` exige que `unidades` sea un número entero mayor que 0, que el intento esté en estado `activa` y que `avance + unidades <= Mision.objetivo_total`. Registrar avance modifica únicamente `avance` y nunca cambia el estado a `completada` ni otorga experiencia.

## 6. Supuestos y glosario

- **Personaje**: entidad mínima del módulo con atributos `id_personaje`, `nombre`, `nivel` (entero, inicia en 1) y `experiencia_disponible` (entero, inicia en 0). Tiene una relación de uno a muchos opcional (`1` a `0..*`) con `IntentoMision`.
- **Misión**: definición del catálogo con atributos `id_mision`, `nombre`, `nivel_requerido` (entero >= 1), `objetivo_total` (entero >= 1) y `recompensa_experiencia` (entero > 0). Tiene una relación de uno a muchos opcional (`1` a `0..*`) con `IntentoMision`.
- **Intento de misión (`IntentoMision`)**: registro independiente creado al aceptar una misión; contiene `id_intento`, referencia a `Personaje`, referencia a `Mision`, `estado` (`activa`, `completada` o `abandonada`), `avance` (entero >= 0, inicia en 0), `fecha_inicio` y `fecha_cierre` (nula mientras esté `activa`).
- **Estados de un intento**: enumeración cerrada con valores `activa`, `completada` y `abandonada`. Solo se permiten las transiciones de `activa` a `completada` (vía `completar()`) o de `activa` a `abandonada` (vía `abandonar()`).
- **Misión disponible**: misión del catálogo donde `Personaje.nivel >= Mision.nivel_requerido` y no existe ningún `IntentoMision` del personaje con esa misión en estado `activa` ni `completada`.
- **Avance**: número entero de unidades de objetivo completadas, acotado entre `0` y `Mision.objetivo_total`. El porcentaje se calcula como la parte entera de `100 * avance / objetivo_total`.
- **Experiencia disponible**: puntos enteros no negativos acumulados hacia el siguiente nivel después de descontar los umbrales `100 * N` de niveles superados. No representa experiencia total histórica.
- **Recompensa de experiencia**: cantidad fija positiva definida en cada misión (`recompensa_experiencia`). Se aplica una sola vez por personaje al completar la misión.
- **Historial de misiones**: lista de `IntentoMision` de un personaje cuyo estado es `completada` o `abandonada` (excluyendo `activa`), ordenada por `fecha_cierre` descendente y `id_intento` descendente.
- **Motor del juego**: actor simulado que invoca únicamente `IntentoMision.registrar_avance(unidades)`; no requiere implementación de combate ni conexión a sistemas de otros equipos.
- **Límites y errores**: cualquier operación que incumpla una regla de negocio (RN-01 a RN-08) lanza una excepción o error identificando la regla incumplida y mantiene intacto el estado de `Personaje`, `Mision` e `IntentoMision`.
