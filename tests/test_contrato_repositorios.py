from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from ejercicio.dominio.prestamos import PrestamosDeSocio
from ejercicio.dominio.repositorios import RepositorioDePrestamos
from ejercicio.dominio.valores import CodigoDeSocio, MultaPorDia, PlazoDeDias

HOY = date(2026, 10, 4)

def test_el_adaptador_cumple_el_puerto(repositorio):
    assert isinstance(repositorio, RepositorioDePrestamos)

def test_buscar_devuelve_none_si_no_hay_nada(repositorio):
    assert repositorio.buscar(CodigoDeSocio("S-0001")) is None

def test_guardar_y_buscar_el_agregado_sobrevive_la_ida_y_vuelta(repositorio):
    socio = PrestamosDeSocio.crear(
        "S-0001",
        limite=2,
        plazo=PlazoDeDias(9),
        multa_por_dia=MultaPorDia(Decimal("1.25")),
    )
    socio.prestar("E-0001", HOY)
    socio.prestar("E-0002", HOY)
    socio.devolver("E-0001", HOY + timedelta(days=11))
    repositorio.guardar(socio)

    recuperado = repositorio.buscar(CodigoDeSocio("S-0001"))
    assert recuperado == socio
    assert len(recuperado.activos()) == 1
    assert recuperado.limite == 2
    assert recuperado.plazo == PlazoDeDias(9)
    assert recuperado.multa_por_dia == MultaPorDia(Decimal("1.25"))
    assert recuperado.total_multas().soles == Decimal("2.50")
    devuelto = next(p for p in recuperado.prestamos if p.ejemplar.valor == "E-0001")
    assert devuelto.plazo == PlazoDeDias(9)
    assert devuelto.multa.soles == Decimal("2.50")

def test_codigos_registrados_ordenados(repositorio):
    for codigo in ("S-0002", "S-0001", "S-0009"):
        repositorio.guardar(PrestamosDeSocio.crear(codigo))
    assert [c.valor for c in repositorio.socios_registrados()] == ["S-0001", "S-0002", "S-0009"]
