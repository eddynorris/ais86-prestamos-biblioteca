from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ejercicio.dominio.entidades import Prestamo
from ejercicio.dominio.errores import SocioSinPrestamos
from ejercicio.dominio.prestamos import PrestamosDeSocio
from ejercicio.dominio.repositorios import RepositorioDePrestamos
from ejercicio.dominio.valores import (
    CodigoDeEjemplar,
    CodigoDeSocio,
    Multa,
    MultaPorDia,
    PlazoDeDias,
)

def _como_socio(codigo: CodigoDeSocio | str) -> CodigoDeSocio:
    return codigo if isinstance(codigo, CodigoDeSocio) else CodigoDeSocio(codigo)

def _cargar(repositorio: RepositorioDePrestamos, codigo: CodigoDeSocio) -> PrestamosDeSocio | None:
    return repositorio.buscar(codigo)

@dataclass
class PrestarEjemplar:

    repositorio: RepositorioDePrestamos
    limite: int = 3
    plazo: PlazoDeDias | None = None
    multa_por_dia: MultaPorDia | None = None

    def ejecutar(
        self, *, socio: CodigoDeSocio | str, ejemplar: CodigoDeEjemplar | str, hoy: date
    ) -> Prestamo:
        codigo = _como_socio(socio)
        prestamos = _cargar(self.repositorio, codigo)
        if prestamos is None:
            prestamos = PrestamosDeSocio.crear(
                codigo, limite=self.limite, plazo=self.plazo, multa_por_dia=self.multa_por_dia
            )
        resultado = prestamos.prestar(ejemplar, hoy)
        self.repositorio.guardar(prestamos)
        return resultado

@dataclass
class DevolverEjemplar:

    repositorio: RepositorioDePrestamos

    def ejecutar(
        self, *, socio: CodigoDeSocio | str, ejemplar: CodigoDeEjemplar | str, hoy: date
    ) -> Multa:
        codigo = _como_socio(socio)
        prestamos = _cargar(self.repositorio, codigo)
        if prestamos is None:
            raise SocioSinPrestamos(codigo.valor)
        multa = prestamos.devolver(ejemplar, hoy)
        self.repositorio.guardar(prestamos)
        return multa

@dataclass
class ConsultarPrestamosDeSocio:

    repositorio: RepositorioDePrestamos

    def ejecutar(self, *, socio: CodigoDeSocio | str) -> dict[str, object]:
        raise NotImplementedError(
            "TODO(alumno): implementar ConsultarPrestamosDeSocio.ejecutar"
        )
