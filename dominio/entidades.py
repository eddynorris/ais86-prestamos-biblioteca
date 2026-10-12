from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from ejercicio.dominio.valores import (
    CodigoDeEjemplar,
    FechaDePrestamo,
    Multa,
    MultaPorDia,
    PlazoDeDias,
)

class Prestamo:

    __slots__ = ("_ejemplar", "_fecha_prestamo", "_plazo", "_fecha_devolucion", "_multa")

    def __init__(
        self,
        ejemplar: CodigoDeEjemplar,
        fecha_prestamo: FechaDePrestamo,
        plazo: PlazoDeDias,
    ) -> None:
        self._ejemplar = ejemplar
        self._fecha_prestamo = fecha_prestamo
        self._plazo = plazo
        self._fecha_devolucion: date | None = None
        self._multa = Multa(Decimal("0"))

    @property
    def ejemplar(self) -> CodigoDeEjemplar:
        return self._ejemplar

    @property
    def fecha_prestamo(self) -> FechaDePrestamo:
        return self._fecha_prestamo

    @property
    def plazo(self) -> PlazoDeDias:
        return self._plazo

    @property
    def fecha_devolucion(self) -> date | None:
        return self._fecha_devolucion

    @property
    def multa(self) -> Multa:
        return self._multa

    def esta_activo(self) -> bool:
        return self._fecha_devolucion is None

    def vence(self) -> date:

        return self._plazo.vence(self._fecha_prestamo)

    def dias_de_atraso(self, hoy: date) -> int:

        return (hoy - self.vence()).days

    def _registrar_devolucion(self, hoy: date, multa_por_dia: MultaPorDia) -> Multa:

        self._fecha_devolucion = hoy
        atraso = max(0, self.dias_de_atraso(hoy))
        self._multa = Multa(multa_por_dia.soles * atraso)
        return self._multa

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Prestamo):
            return NotImplemented
        return (self._ejemplar, self._fecha_prestamo) == (otro._ejemplar, otro._fecha_prestamo)

    def __hash__(self) -> int:
        return hash((self._ejemplar, self._fecha_prestamo))

    def __repr__(self) -> str:
        estado = "activo" if self.esta_activo() else f"devuelto {self._fecha_devolucion}"
        return f"Prestamo({self._ejemplar}, {self._fecha_prestamo}, {estado})"
