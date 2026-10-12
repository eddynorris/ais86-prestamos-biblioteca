from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal

from ejercicio.dominio.entidades import Prestamo
from ejercicio.dominio.prestamos import PrestamosDeSocio
from ejercicio.dominio.valores import (
    CodigoDeEjemplar,
    CodigoDeSocio,
    FechaDePrestamo,
    Multa,
    MultaPorDia,
    PlazoDeDias,
)

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS socio (
    codigo      TEXT PRIMARY KEY,
    limite      INTEGER NOT NULL,
    plazo       INTEGER NOT NULL,
    multa_dia   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prestamo (
    codigo_socio     TEXT NOT NULL,
    codigo_ejemplar  TEXT NOT NULL,
    fecha_prestamo   TEXT NOT NULL,
    plazo            INTEGER NOT NULL,
    fecha_devolucion TEXT,
    multa            TEXT NOT NULL,
    PRIMARY KEY (codigo_socio, codigo_ejemplar, fecha_prestamo),
    FOREIGN KEY (codigo_socio) REFERENCES socio (codigo) ON DELETE CASCADE
);
"""

class PrestamosEnSQLite:

    def __init__(self, ruta: str = ":memory:") -> None:
        self._conexion = sqlite3.connect(ruta)
        self._conexion.execute("PRAGMA foreign_keys = ON")
        self._conexion.executescript(_ESQUEMA)
        self._conexion.commit()

    def buscar(self, codigo: CodigoDeSocio) -> PrestamosDeSocio | None:
        raise NotImplementedError("TODO(alumno): implementar PrestamosEnSQLite.buscar")

    def guardar(self, prestamos: PrestamosDeSocio) -> None:
        raise NotImplementedError("TODO(alumno): implementar PrestamosEnSQLite.guardar")

    def socios_registrados(self) -> tuple[CodigoDeSocio, ...]:
        raise NotImplementedError(
            "TODO(alumno): implementar PrestamosEnSQLite.socios_registrados"
        )

    def cerrar(self) -> None:
        self._conexion.close()

    def __repr__(self) -> str:
        return "PrestamosEnSQLite()"
