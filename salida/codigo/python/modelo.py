"""Esqueleto generado por spec2code. Módulo: Misiones y progresión

NO es una solución: son clases y firmas con TODO. Completa la lógica, audita cada
clase contra la spec y corrige la SPEC (no este archivo) cuando el error venga de ella.
"""
from __future__ import annotations

from datetime import date


class Personaje:
    """Personaje. Trazabilidad: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08."""

    def __init__(self, identificador: int, nombre: str, nivel: int, experiencia_disponible: int) -> None:
        self.identificador: int = identificador  # TODO: encapsulamiento (propiedades)
        self.nombre: str = nombre  # TODO: encapsulamiento (propiedades)
        self.nivel: int = nivel  # TODO: encapsulamiento (propiedades)
        self.experiencia_disponible: int = experiencia_disponible  # TODO: encapsulamiento (propiedades)
        self.intento_misions: list[IntentoMision] = []  # asociacion: tiene ()

    def consultar_misiones_disponibles(self) -> None:
        """consultar_misiones_disponibles (RF-01)."""
        raise NotImplementedError("TODO: implementar Personaje.consultar_misiones_disponibles")

    def aceptar_mision(self) -> None:
        """aceptar_mision (RF-02)."""
        raise NotImplementedError("TODO: implementar Personaje.aceptar_mision")

    def consultar_avance(self) -> None:
        """consultar_avance (RF-03)."""
        raise NotImplementedError("TODO: implementar Personaje.consultar_avance")

    def completar_mision(self) -> None:
        """completar_mision (RF-04)."""
        raise NotImplementedError("TODO: implementar Personaje.completar_mision")

    def consultar_progresion(self) -> None:
        """consultar_progresion (RF-06)."""
        raise NotImplementedError("TODO: implementar Personaje.consultar_progresion")

    def consultar_historial(self) -> None:
        """consultar_historial (RF-08)."""
        raise NotImplementedError("TODO: implementar Personaje.consultar_historial")

    def abandonar_mision(self) -> None:
        """abandonar_mision (RF-09)."""
        raise NotImplementedError("TODO: implementar Personaje.abandonar_mision")


class Mision:
    """Mision. Trazabilidad: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08."""

    def __init__(self, identificador: int, nombre: str, nivel_requerido: int, objetivo_total: int, recompensa_experiencia: int) -> None:
        self.identificador: int = identificador  # TODO: encapsulamiento (propiedades)
        self.nombre: str = nombre  # TODO: encapsulamiento (propiedades)
        self.nivel_requerido: int = nivel_requerido  # TODO: encapsulamiento (propiedades)
        self.objetivo_total: int = objetivo_total  # TODO: encapsulamiento (propiedades)
        self.recompensa_experiencia: int = recompensa_experiencia  # TODO: encapsulamiento (propiedades)

    def consultar_disponibilidad(self) -> None:
        """consultar_disponibilidad (RF-01)."""
        raise NotImplementedError("TODO: implementar Mision.consultar_disponibilidad")


class IntentoMision:
    """IntentoMision. Trazabilidad: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08."""

    def __init__(self, identificador: int, personaje: int, mision: int, estado: str, avance: int, fecha_inicio: date, fecha_cierre: date) -> None:
        self.identificador: int = identificador  # TODO: encapsulamiento (propiedades)
        self.personaje: int = personaje  # TODO: encapsulamiento (propiedades)
        self.mision: int = mision  # TODO: encapsulamiento (propiedades)
        self.estado: str = estado  # TODO: encapsulamiento (propiedades)
        self.avance: int = avance  # TODO: encapsulamiento (propiedades)
        self.fecha_inicio: date = fecha_inicio  # TODO: encapsulamiento (propiedades)
        self.fecha_cierre: date = fecha_cierre  # TODO: encapsulamiento (propiedades)
        self.mision: Mision | None = None  # asociacion: pertenece_a ()

    def registrar_avance(self) -> None:
        """registrar_avance (RF-10)."""
        raise NotImplementedError("TODO: implementar IntentoMision.registrar_avance")

    def completar(self) -> None:
        """completar (RF-04)."""
        raise NotImplementedError("TODO: implementar IntentoMision.completar")

    def abandonar(self) -> None:
        """abandonar (RF-09)."""
        raise NotImplementedError("TODO: implementar IntentoMision.abandonar")
