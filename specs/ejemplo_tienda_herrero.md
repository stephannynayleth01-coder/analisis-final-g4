# Módulo: Tienda del herrero

## 1. Contexto y alcance

El RPG Manager es un sistema de consola para administrar personajes de rol. Este módulo permite que un Personaje compre y venda objetos en la tienda del herrero y repare sus armas pagando con oro. Queda fuera de alcance la creación de personajes, el inventario con límite de peso y el combate; se asume que el personaje ya existe y llega con su nombre y su oro.

## 2. Actores

- **Jugador**: persona que controla un personaje y usa la tienda.
- **Administrador del juego**: persona que mantiene el catálogo de la tienda.

## 3. Requerimientos funcionales

- **RF-01** El jugador puede consultar el catálogo de la tienda.
  - Criterio de aceptación: el catálogo muestra nombre, precio y unidades disponibles de cada artículo en venta.
- **RF-02** El jugador puede comprar un artículo del catálogo para su personaje.
  - Criterio de aceptación: tras la compra, el oro del personaje disminuye en el precio, el objeto queda entre los objetos del personaje y las unidades disponibles del artículo disminuyen en 1.
- **RF-03** El jugador puede vender a la tienda un objeto de su personaje.
  - Criterio de aceptación: tras la venta, el objeto deja de pertenecer al personaje y su oro aumenta según la regla RN-02.
- **RF-04** El jugador puede pagar al herrero para reparar un arma de su personaje.
  - Criterio de aceptación: tras la reparación, la durabilidad del arma es igual a su durabilidad máxima y el oro del personaje disminuye según la regla RN-04.
- **RF-05** El administrador del juego puede actualizar el precio y las unidades disponibles de un artículo del catálogo.
  - Criterio de aceptación: al consultar el catálogo después del cambio, el artículo muestra el precio y las unidades nuevos.

## 4. Requerimientos no funcionales

- **RNF-01** La consulta del catálogo responde en menos de 1 segundo con hasta 200 artículos.
- **RNF-02** Las reglas de negocio de este módulo tienen pruebas unitarias con al menos 70 % de cobertura.
- **RNF-03** Cada mensaje de error en español indica el código de la regla de negocio violada (por ejemplo, RN-01).

## 5. Reglas de negocio

- **RN-01** No se puede comprar un artículo si el oro del personaje es menor que su precio.
- **RN-02** El precio de venta de un objeto es el 50 % de su precio de compra, redondeado hacia abajo.
- **RN-03** No se puede comprar un artículo con 0 unidades disponibles.
- **RN-04** Reparar un arma cuesta 2 de oro por cada punto de durabilidad que le falte; no se puede reparar un arma que ya tiene su durabilidad máxima.

## 6. Supuestos y glosario

- **Oro**: moneda del juego; es un número entero mayor o igual a 0.
- **Objeto**: elemento con nombre y precio de compra. Los tipos de objeto son Arma y Poción.
- **Arma**: objeto con durabilidad actual y durabilidad máxima.
- **Poción**: objeto que restaura una cantidad fija de puntos de vida.
- **Artículo en venta**: un objeto del catálogo con sus unidades disponibles.
