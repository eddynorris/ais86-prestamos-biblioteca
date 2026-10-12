from datetime import date, timedelta
from decimal import Decimal

import pytest

from ejercicio.dominio.errores import EjemplarYaPrestado, LimiteDePrestamosAlcanzado
from ejercicio.dominio.valores import CodigoDeSocio, Multa, MultaPorDia, PlazoDeDias
from ejercicio.nucleo.casos_uso import ConsultarPrestamosDeSocio, DevolverEjemplar, PrestarEjemplar

HOY = date(2026, 10, 4)

def test_flujo_de_prestamo_devolucion_consulta_y_repositorio(repositorio):
    nombre_adaptador = type(repositorio).__name__
    prestar = PrestarEjemplar(
        repositorio,
        limite=2,
        plazo=PlazoDeDias(7),
        multa_por_dia=MultaPorDia(Decimal("1.50")),
    )

    primero = prestar.ejecutar(socio="S-0001", ejemplar="E-0001", hoy=HOY)
    assert primero.vence() == HOY + timedelta(days=7)
    print(f"\nFLUJO [{nombre_adaptador}]")
    print(f"PRESTAR E-0001 | {HOY.isoformat()} -> vence {primero.vence().isoformat()}")

    with pytest.raises(EjemplarYaPrestado):
        prestar.ejecutar(socio="S-0001", ejemplar="E-0001", hoy=HOY)
    segundo = prestar.ejecutar(socio="S-0001", ejemplar="E-0002", hoy=HOY)
    assert segundo.esta_activo()
    print("PRESTAR E-0002 | activo")

    with pytest.raises(LimiteDePrestamosAlcanzado):
        prestar.ejecutar(socio="S-0001", ejemplar="E-0003", hoy=HOY)
    print("RECHAZOS | duplicado=E-0001 | límite=E-0003")

    fecha_devolucion = HOY + timedelta(days=10)
    multa = DevolverEjemplar(repositorio).ejecutar(
        socio="S-0001", ejemplar="E-0001", hoy=fecha_devolucion
    )
    assert multa == Multa(Decimal("4.50"))
    print(f"DEVOLVER E-0001 | {fecha_devolucion.isoformat()} | atraso=3d | multa={multa}")

    reporte = ConsultarPrestamosDeSocio(repositorio).ejecutar(socio="S-0001")
    assert reporte == {
        "socio": "S-0001",
        "activos": 1,
        "historial": 2,
        "multas": Decimal("4.50"),
    }
    print(
        f"CONSULTA {reporte['socio']} | activos={reporte['activos']} | "
        f"historial={reporte['historial']} | multa total=S/ {reporte['multas']:.2f}"
    )

    recuperado = repositorio.buscar(CodigoDeSocio("S-0001"))
    assert recuperado is not None
    assert recuperado.limite == 2
    assert recuperado.plazo == PlazoDeDias(7)
    assert recuperado.multa_por_dia == MultaPorDia(Decimal("1.50"))
    assert [p.ejemplar.valor for p in recuperado.activos()] == ["E-0002"]
    assert len(recuperado.prestamos) == 2
    devuelto = next(p for p in recuperado.prestamos if p.ejemplar.valor == "E-0001")
    assert devuelto.fecha_devolucion == fecha_devolucion
    assert devuelto.multa == Multa(Decimal("4.50"))
    print(
        f"RECUPERAR | activo={recuperado.activos()[0].ejemplar.valor} | "
        f"historial={len(recuperado.prestamos)} | límite={recuperado.limite}"
    )
    print(
        f"POLÍTICA | plazo={recuperado.plazo.dias}d | "
        f"tarifa/día=S/{recuperado.multa_por_dia.soles:.2f} | "
        f"multa guardada=S/{devuelto.multa.soles:.2f}"
    )
    print("RESULTADO | flujo correcto")
