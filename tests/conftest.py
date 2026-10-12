from __future__ import annotations

import pytest

from ejercicio.adaptadores.repositorio_en_memoria import PrestamosEnMemoria
from ejercicio.adaptadores.repositorio_sqlite import PrestamosEnSQLite

@pytest.fixture(params=["memoria", "sqlite"])
def repositorio(request):
    if request.param == "memoria":
        yield PrestamosEnMemoria()
    else:
        adaptador = PrestamosEnSQLite(":memory:")
        try:
            yield adaptador
        finally:
            adaptador.cerrar()
