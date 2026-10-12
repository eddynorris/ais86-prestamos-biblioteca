from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from ejercicio.dominio.errores import ValorInvalido

_FORMATO_SOCIO = re.compile(r"^S-\d{4}$")
_FORMATO_EJEMPLAR = re.compile(r"^E-\d{4}$")

@dataclass(frozen=True, slots=True, order=True)
class CodigoDeSocio:

    valor: str

    def __post_init__(self) -> None:
        normalizado = str(self.valor).strip().upper()
        if not _FORMATO_SOCIO.match(normalizado):
            raise ValorInvalido("Código de socio", self.valor, "S-9999 (p. ej. S-0001)")
        object.__setattr__(self, "valor", normalizado)

    def __str__(self) -> str:
        return self.valor

@dataclass(frozen=True, slots=True, order=True)
class CodigoDeEjemplar:

    valor: str

    def __post_init__(self) -> None:
        normalizado = str(self.valor).strip().upper()
        if not _FORMATO_EJEMPLAR.match(normalizado):
            raise ValorInvalido("Código de ejemplar", self.valor, "E-9999 (p. ej. E-0001)")
        object.__setattr__(self, "valor", normalizado)

    def __str__(self) -> str:
        return self.valor

@dataclass(frozen=True, slots=True, order=True)
class FechaDePrestamo:

    fecha: date

    def __post_init__(self) -> None:
        if isinstance(self.fecha, datetime):
            raise ValorInvalido("Fecha de préstamo", self.fecha, "una date sin hora")
        if not isinstance(self.fecha, date):
            raise ValorInvalido("Fecha de préstamo", self.fecha, "una date")
        object.__setattr__(self, "fecha", self.fecha)

    def __str__(self) -> str:
        return self.fecha.isoformat()

@dataclass(frozen=True, slots=True)
class PlazoDeDias:

    dias: int

    def __post_init__(self) -> None:
        if isinstance(self.dias, bool) or not isinstance(self.dias, int):
            raise ValorInvalido("Plazo", self.dias, "un número entero de días")
        if self.dias <= 0:
            raise ValorInvalido("Plazo", self.dias, "un entero mayor que 0")
        object.__setattr__(self, "dias", self.dias)

    def vence(self, desde: FechaDePrestamo) -> date:

        from datetime import timedelta

        return desde.fecha + timedelta(days=self.dias)

    def __str__(self) -> str:
        return f"{self.dias} días"

@dataclass(frozen=True, slots=True)
class MultaPorDia:

    soles: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.soles, Decimal):
            object.__setattr__(self, "soles", Decimal(str(self.soles)))
        if self.soles < 0:
            raise ValorInvalido("Multa por día", self.soles, "un monto mayor o igual a 0")
        object.__setattr__(self, "soles", self.soles.quantize(Decimal("0.01")))

    def __str__(self) -> str:
        return f"S/ {self.soles}"

@dataclass(frozen=True, slots=True)
class Multa:

    soles: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.soles, Decimal):
            object.__setattr__(self, "soles", Decimal(str(self.soles)))
        object.__setattr__(self, "soles", self.soles.quantize(Decimal("0.01")))

    def es_cero(self) -> bool:
        return self.soles == 0

    def __str__(self) -> str:
        return f"S/ {self.soles}"
