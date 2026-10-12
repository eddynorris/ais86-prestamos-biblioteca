from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal

from ejercicio.dominio.errores import ErrorDeDominio
from ejercicio.dominio.valores import MultaPorDia, PlazoDeDias
from ejercicio.nucleo.casos_uso import (
    ConsultarPrestamosDeSocio,
    DevolverEjemplar,
    PrestarEjemplar,
)
from ejercicio.dominio.repositorios import RepositorioDePrestamos

HOY = date(2026, 10, 4)

def _titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")

def demo(repositorio: RepositorioDePrestamos, hoy: date = HOY) -> None:
    print("Contexto delimitado: PRÉSTAMOS DE BIBLIOTECA (ejercicio)")
    print(f"Adaptador de repositorio: {repositorio!r}")

    prestar = PrestarEjemplar(
        repositorio, plazo=PlazoDeDias(7), multa_por_dia=MultaPorDia(Decimal("1.00"))
    )
    devolver = DevolverEjemplar(repositorio)
    consultar = ConsultarPrestamosDeSocio(repositorio)

    try:
        _titulo("1. Prestar dos ejemplares al socio S-0001")
        prestar.ejecutar(socio="S-0001", ejemplar="E-0001", hoy=hoy)
        prestar.ejecutar(socio="S-0001", ejemplar="E-0002", hoy=hoy)
        print(f"Socios con registro: {repositorio.socios_registrados()}")

        _titulo("2. Devolver E-0001 con 3 días de atraso")
        from datetime import timedelta

        multa = devolver.ejecutar(socio="S-0001", ejemplar="E-0001", hoy=hoy + timedelta(days=10))
        print(f"Multa generada: {multa}")

        _titulo("3. Reporte del socio")
        print(consultar.ejecutar(socio="S-0001"))
    except NotImplementedError as pendiente:
        print(f"\n[EJERCICIO PENDIENTE] {pendiente}")
        print("Completá los TODO y volvé a correr este guion.")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Demo del ejercicio (Semana 6, AIS86).")
    parser.add_argument(
        "--sqlite",
        nargs="?",
        const=":memory:",
        default=None,
        metavar="RUTA",
        help="usa el adaptador SQLite (necesita el ejercicio completo)",
    )
    args = parser.parse_args(argv)

    if args.sqlite is None:
        from ejercicio.adaptadores.repositorio_en_memoria import PrestamosEnMemoria

        repositorio: RepositorioDePrestamos = PrestamosEnMemoria()
    else:
        from ejercicio.adaptadores.repositorio_sqlite import PrestamosEnSQLite

        repositorio = PrestamosEnSQLite(args.sqlite)

    demo(repositorio)
    return 0
