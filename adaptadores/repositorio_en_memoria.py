from __future__ import annotations

from ejercicio.dominio.prestamos import PrestamosDeSocio
from ejercicio.dominio.valores import CodigoDeSocio

class PrestamosEnMemoria:

    def __init__(self) -> None:
        self._datos: dict[CodigoDeSocio, PrestamosDeSocio] = {}

    def buscar(self, codigo: CodigoDeSocio) -> PrestamosDeSocio | None:
        clave = codigo if isinstance(codigo, CodigoDeSocio) else CodigoDeSocio(codigo)
        return self._datos.get(clave)

    def guardar(self, prestamos: PrestamosDeSocio) -> None:
        self._datos[prestamos.codigo] = prestamos

    def socios_registrados(self) -> tuple[CodigoDeSocio, ...]:
        return tuple(sorted(self._datos))

    def __repr__(self) -> str:
        return f"PrestamosEnMemoria({len(self._datos)} socio(s))"
