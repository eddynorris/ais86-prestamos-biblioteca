from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ejercicio.dominio.errores import (
    EjemplarYaPrestado,
    LimiteDePrestamosAlcanzado,
    PrestamoNoEncontrado,
)
from ejercicio.dominio.prestamos import PrestamosDeSocio
from ejercicio.dominio.valores import (
    CodigoDeEjemplar,
    CodigoDeSocio,
    Multa,
    MultaPorDia,
    PlazoDeDias,
)

HOY = date(2026, 10, 4)

def un_socio(limite: int = 3, plazo: int = 7, multa: str = "1.00") -> PrestamosDeSocio:
    return PrestamosDeSocio.crear(
        "S-0001", limite=limite, plazo=PlazoDeDias(plazo), multa_por_dia=MultaPorDia(Decimal(multa))
    )

def test_un_socio_nuevo_no_tiene_prestamos():
    socio = PrestamosDeSocio.crear("S-0001")
    assert socio.activos() == ()
    assert socio.codigo == CodigoDeSocio("S-0001")

def test_prestar_agrega_un_prestamo_activo():
    socio = un_socio()
    prestamo = socio.prestar("E-0001", HOY)
    assert prestamo.esta_activo()
    assert prestamo.ejemplar == CodigoDeEjemplar("E-0001")
    assert len(socio.activos()) == 1
    assert socio.esta_activo(CodigoDeEjemplar("E-0001"))

def test_el_codigo_de_ejemplar_se_normaliza():
    socio = un_socio()
    socio.prestar("e-0001", HOY)
    assert socio.esta_activo(CodigoDeEjemplar("E-0001"))

def test_I1_no_se_pueden_pasar_del_limite_de_prestamos_activos():
    socio = un_socio(limite=3)
    socio.prestar("E-0001", HOY)
    socio.prestar("E-0002", HOY)
    socio.prestar("E-0003", HOY)
    with pytest.raises(LimiteDePrestamosAlcanzado):
        socio.prestar("E-0004", HOY)

def test_I1_el_limite_es_una_politica_del_agregado():
    socio = un_socio(limite=1)
    socio.prestar("E-0001", HOY)
    with pytest.raises(LimiteDePrestamosAlcanzado):
        socio.prestar("E-0002", HOY)

def test_I1_devolver_libera_un_cupo():
    socio = un_socio(limite=1)
    socio.prestar("E-0001", HOY)
    socio.devolver("E-0001", HOY)
    socio.prestar("E-0002", HOY)
    assert len(socio.activos()) == 1

def test_I2_no_se_presta_dos_veces_el_mismo_ejemplar_activo():
    socio = un_socio()
    socio.prestar("E-0001", HOY)
    with pytest.raises(EjemplarYaPrestado):
        socio.prestar("E-0001", HOY)

def test_I2_un_ejemplar_devuelto_si_se_puede_volver_a_prestar():
    socio = un_socio()
    socio.prestar("E-0001", HOY)
    socio.devolver("E-0001", HOY)
    socio.prestar("E-0001", HOY)
    assert socio.esta_activo(CodigoDeEjemplar("E-0001"))

def test_I3_devolver_a_tiempo_no_genera_multa():
    socio = un_socio(plazo=7, multa="1.00")
    socio.prestar("E-0001", HOY)
    multa = socio.devolver("E-0001", HOY + timedelta(days=7))
    assert multa == Multa(Decimal("0.00"))

def test_I3_devolver_con_atraso_genera_multa_por_dia():
    socio = un_socio(plazo=7, multa="1.50")
    socio.prestar("E-0001", HOY)

    multa = socio.devolver("E-0001", HOY + timedelta(days=10))
    assert multa == Multa(Decimal("4.50"))
    assert socio.total_multas() == Multa(Decimal("4.50"))

def test_I3_el_prestamo_guarda_su_multa():
    socio = un_socio(plazo=7, multa="2.00")
    socio.prestar("E-0001", HOY)
    socio.devolver("E-0001", HOY + timedelta(days=9))
    devuelto = [p for p in socio.prestamos if not p.esta_activo()][0]
    assert devuelto.multa == Multa(Decimal("4.00"))
    assert devuelto.dias_de_atraso(HOY + timedelta(days=9)) == 2

def test_devolver_un_ejemplar_que_no_se_presto_es_error():
    socio = un_socio()
    with pytest.raises(PrestamoNoEncontrado):
        socio.devolver("E-9999", HOY)

def test_dos_socios_iguales_se_comparan_por_codigo_y_contenido():
    a = un_socio()
    b = un_socio()
    a.prestar("E-0001", HOY)
    b.prestar("E-0001", HOY)
    assert a == b
