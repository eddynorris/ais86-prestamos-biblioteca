from __future__ import annotations

from typing import Protocol, runtime_checkable

from ejercicio.dominio.prestamos import PrestamosDeSocio
from ejercicio.dominio.valores import CodigoDeSocio

@runtime_checkable
class RepositorioDePrestamos(Protocol):

    def buscar(self, codigo: CodigoDeSocio) -> PrestamosDeSocio | None:

        ...

    def guardar(self, prestamos: PrestamosDeSocio) -> None:

        ...

    def socios_registrados(self) -> tuple[CodigoDeSocio, ...]:

        ...
