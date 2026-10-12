from __future__ import annotations

from datetime import date
from decimal import Decimal

from ejercicio.dominio.entidades import Prestamo
from ejercicio.dominio.errores import (
    EjemplarYaPrestado,
    LimiteDePrestamosAlcanzado,
    PrestamoNoEncontrado,
)
from ejercicio.dominio.valores import (
    CodigoDeEjemplar,
    CodigoDeSocio,
    FechaDePrestamo,
    Multa,
    MultaPorDia,
    PlazoDeDias,
)

class PrestamosDeSocio:

    def __init__(
        self,
        codigo: CodigoDeSocio,
        *,
        prestamos: tuple[Prestamo, ...] | list[Prestamo] = (),
        limite: int = 3,
        plazo: PlazoDeDias | None = None,
        multa_por_dia: MultaPorDia | None = None,
    ) -> None:
        self.codigo = codigo
        self.limite = limite
        self.plazo = plazo or PlazoDeDias(7)
        self.multa_por_dia = multa_por_dia or MultaPorDia(Decimal("1.00"))

        self._prestamos: list[Prestamo] = list(prestamos)

    @classmethod
    def crear(
        cls,
        codigo: CodigoDeSocio | str,
        *,
        limite: int = 3,
        plazo: PlazoDeDias | None = None,
        multa_por_dia: MultaPorDia | None = None,
    ) -> "PrestamosDeSocio":

        return cls(
            CodigoDeSocio(codigo) if isinstance(codigo, str) else codigo,
            limite=limite,
            plazo=plazo,
            multa_por_dia=multa_por_dia,
        )

    @property
    def prestamos(self) -> tuple[Prestamo, ...]:

        return tuple(sorted(self._prestamos, key=lambda p: (p.fecha_prestamo, p.ejemplar.valor)))

    def activos(self) -> tuple[Prestamo, ...]:

        return tuple(p for p in self.prestamos if p.esta_activo())

    def esta_activo(self, ejemplar: CodigoDeEjemplar) -> bool:

        return any(p.esta_activo() and p.ejemplar == ejemplar for p in self._prestamos)

    def total_multas(self) -> Multa:

        from decimal import Decimal

        return Multa(sum((p.multa.soles for p in self._prestamos), Decimal("0")))

    def prestar(self, ejemplar: CodigoDeEjemplar | str, hoy: date) -> Prestamo:

        raise NotImplementedError("TODO(alumno): implementar PrestamosDeSocio.prestar")

    def devolver(self, ejemplar: CodigoDeEjemplar | str, hoy: date) -> Multa:

        raise NotImplementedError("TODO(alumno): implementar PrestamosDeSocio.devolver")

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, PrestamosDeSocio):
            return NotImplemented
        return self.codigo == otro.codigo and self.prestamos == otro.prestamos

    def __repr__(self) -> str:
        return (
            f"PrestamosDeSocio({self.codigo}, activos={len(self.activos())}, "
            f"multas={self.total_multas()})"
        )
