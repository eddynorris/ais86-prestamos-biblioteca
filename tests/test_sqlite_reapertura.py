from datetime import date, timedelta
from decimal import Decimal

from ejercicio.adaptadores.repositorio_sqlite import PrestamosEnSQLite
from ejercicio.dominio.valores import CodigoDeSocio, Multa, MultaPorDia, PlazoDeDias
from ejercicio.nucleo.casos_uso import DevolverEjemplar, PrestarEjemplar

HOY = date(2026, 10, 4)

def test_sqlite_conserva_el_estado_al_cerrar_y_reabrir(tmp_path):
    ruta = tmp_path / "biblioteca.sqlite3"
    repositorio = PrestamosEnSQLite(str(ruta))
    try:
        prestar = PrestarEjemplar(
            repositorio,
            limite=2,
            plazo=PlazoDeDias(9),
            multa_por_dia=MultaPorDia(Decimal("1.25")),
        )
        prestamo = prestar.ejecutar(socio="S-0009", ejemplar="E-0099", hoy=HOY)
        fecha_devolucion = prestamo.vence() + timedelta(days=2)
        multa = DevolverEjemplar(repositorio).ejecutar(
            socio="S-0009", ejemplar="E-0099", hoy=fecha_devolucion
        )
        assert multa == Multa(Decimal("2.50"))
    finally:
        repositorio.cerrar()

    repositorio_reabierto = PrestamosEnSQLite(str(ruta))
    try:
        socio = repositorio_reabierto.buscar(CodigoDeSocio("S-0009"))
        assert socio is not None
        assert socio.limite == 2
        assert socio.plazo == PlazoDeDias(9)
        assert socio.multa_por_dia == MultaPorDia(Decimal("1.25"))
        assert len(socio.prestamos) == 1
        assert socio.activos() == ()
        assert socio.total_multas() == Multa(Decimal("2.50"))
        assert socio.prestamos[0].fecha_devolucion == fecha_devolucion
        assert socio.prestamos[0].plazo == PlazoDeDias(9)
        print(
            f"\nSQLITE REABIERTO | socio={socio.codigo.valor} | "
            f"historial={len(socio.prestamos)} | activos={len(socio.activos())}"
        )
        print(
            f"POLÍTICA | plazo={socio.plazo.dias}d | "
            f"tarifa/día=S/{socio.multa_por_dia.soles:.2f} | "
            f"multa=S/{socio.total_multas().soles:.2f} | estado=conservado"
        )
    finally:
        repositorio_reabierto.cerrar()
