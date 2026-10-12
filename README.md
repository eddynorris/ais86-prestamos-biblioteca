# Préstamos de Biblioteca — Semana 6

## Ejecutar

Requiere Python 3.10 o posterior.

**Windows PowerShell** — desde la raíz del repositorio clonado:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe servidor.py
```

Abrir la interfaz web local en el navegador: `http://127.0.0.1:8000`

Para ejecutar la misma suite y el guion desde el terminal:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -s
.\.venv\Scripts\python.exe -m ejercicio.main
```

**Linux, macOS o WSL** — desde la raíz del repositorio clonado:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python servidor.py
```

Abrir la interfaz web local en el navegador: `http://127.0.0.1:8000`

Para ejecutar la misma suite y el guion desde el terminal:

```bash
.venv/bin/python -m pytest -q -s
.venv/bin/python -m ejercicio.main
```

`pytest -q -s` ejecuta las pruebas y muestra en el terminal el flujo de préstamo, rechazo, devolución, consulta y persistencia para los dos adaptadores. Antes de completar los TODO, algunas pruebas fallarán; la entrega debe terminar con todas aprobadas y el comando de ejecución sin mensajes de pendiente.

## Completar

1. En `dominio/prestamos.py`, implementar `prestar()` y `devolver()`. `prestar()` rechaza un ejemplar activo repetido con `EjemplarYaPrestado` y un préstamo que exceda el límite con `LimiteDePrestamosAlcanzado`; debe permitir volver a prestar un ejemplar ya devuelto. `devolver()` rechaza un ejemplar sin préstamo activo con `PrestamoNoEncontrado` y registra multa cero si se devuelve a tiempo o tarifa diaria por cada día de atraso.
2. En `nucleo/casos_uso.py`, implementar `ConsultarPrestamosDeSocio.ejecutar()`. Debe devolver `{"socio": str, "activos": int, "historial": int, "multas": Decimal}`; `historial` incluye préstamos activos y devueltos. Un socio sin registro produce `SocioSinPrestamos`.
3. En `adaptadores/repositorio_sqlite.py`, implementar `buscar()`, `guardar()` y `socios_registrados()`. `buscar()` devuelve el agregado o `None`; `guardar()` conserva la configuración y el historial completo; `socios_registrados()` devuelve los códigos ordenados. El test de SQLite comprueba también el cierre y reapertura del archivo.
4. En `glosario.md`, completar las 11 filas vinculando cada término del negocio con un identificador real de `dominio/` y su significado.

No modificar `tests/`. La entrega está completa cuando el comando de pruebas de arriba termina sin fallos y el comando de ejecución completa el flujo sin mostrar `[EJERCICIO PENDIENTE]`.
