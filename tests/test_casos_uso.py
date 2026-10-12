from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ejercicio.dominio.errores import SocioSinPrestamos
from ejercicio.dominio.valores import Multa, MultaPorDia, PlazoDeDias
from ejercicio.nucleo.casos_uso import (
    ConsultarPrestamosDeSocio,
    DevolverEjemplar,
    PrestarEjemplar,
)

from ejercicio.adaptadores.repositorio_en_memoria import PrestamosEnMemoria

HOY = date(2026, 10, 4)

@pytest.fixture
def repo() -> PrestamosEnMemoria:
    return PrestamosEnMemoria()

def test_prestar_crea_el_registro_del_socio(repo):
    PrestarEjemplar(repo).ejecutar(socio="s-0001", ejemplar="e-0001", hoy=HOY)
    assert repo.buscar("S-0001") is not None
    assert repo.socios_registrados()[0].valor == "S-0001"

def test_devolver_devuelve_la_multa_y_guarda(repo):
    PrestarEjemplar(repo, plazo=PlazoDeDias(7), multa_por_dia=MultaPorDia(Decimal("1.00"))).ejecutar(
        socio="S-0001", ejemplar="E-0001", hoy=HOY
    )
    multa = DevolverEjemplar(repo).ejecutar(
        socio="S-0001", ejemplar="E-0001", hoy=HOY + timedelta(days=10)
    )
    assert multa == Multa(Decimal("3.00"))
    assert repo.buscar("S-0001").activos() == ()

def test_devolver_sin_registro_es_error(repo):
    with pytest.raises(SocioSinPrestamos):
        DevolverEjemplar(repo).ejecutar(socio="S-9999", ejemplar="E-0001", hoy=HOY)

def test_consultar_devuelve_el_reporte_del_socio(repo):

    prestar = PrestarEjemplar(repo, plazo=PlazoDeDias(7), multa_por_dia=MultaPorDia(Decimal("1.00")))
    prestar.ejecutar(socio="S-0001", ejemplar="E-0001", hoy=HOY)
    prestar.ejecutar(socio="S-0001", ejemplar="E-0002", hoy=HOY)
    DevolverEjemplar(repo).ejecutar(socio="S-0001", ejemplar="E-0001", hoy=HOY + timedelta(days=10))

    reporte = ConsultarPrestamosDeSocio(repo).ejecutar(socio="S-0001")
    assert reporte["socio"] == "S-0001"
    assert reporte["activos"] == 1
    assert reporte["historial"] == 2
    assert reporte["multas"] == Decimal("3.00")

def test_consultar_un_socio_sin_registro_es_error(repo):
    with pytest.raises(SocioSinPrestamos):
        ConsultarPrestamosDeSocio(repo).ejecutar(socio="S-9999")
