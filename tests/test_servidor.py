from __future__ import annotations

import json
import os
from pathlib import Path
import threading
import urllib.error
import urllib.request

from ejercicio.servidor import (
    RAIZ_PROYECTO,
    crear_servidor,
    extraer_tareas,
)


def test_extraer_tareas_desde_readme_real():
    tareas = extraer_tareas(RAIZ_PROYECTO / "README.md")
    assert len(tareas) == 4
    assert "dominio/prestamos.py" in tareas[0]
    assert "nucleo/casos_uso.py" in tareas[1]
    assert "adaptadores/repositorio_sqlite.py" in tareas[2]
    assert "glosario.md" in tareas[3]


def test_extraer_tareas_archivo_inexistente(tmp_path: Path):
    assert extraer_tareas(tmp_path / "inexistente.md") == []


def test_extraer_tareas_formato_personalizado(tmp_path: Path):
    archivo = tmp_path / "guia.md"
    archivo.write_text(
        "## Introduccion\nTexto\n\n## Completar\n\n1. Primera tarea\n2. Segunda tarea\n\n## Final\n",
        encoding="utf-8",
    )
    tareas = extraer_tareas(archivo)
    assert tareas == ["Primera tarea", "Segunda tarea"]


def test_servidor_rutas_estaticas_y_api():
    servidor = crear_servidor(host="127.0.0.1", puerto=0, directorio_raiz=RAIZ_PROYECTO)
    puerto = servidor.server_address[1]
    hilo = threading.Thread(target=servidor.serve_forever)
    hilo.daemon = True
    hilo.start()

    base_url = f"http://127.0.0.1:{puerto}"

    try:
        with urllib.request.urlopen(f"{base_url}/") as r:
            assert r.status == 200
            assert "text/html" in r.headers.get("Content-Type", "")
            contenido = r.read().decode("utf-8")
            assert "Préstamos de Biblioteca — AIS86" in contenido

        with urllib.request.urlopen(f"{base_url}/estilos.css") as r:
            assert r.status == 200
            assert "text/css" in r.headers.get("Content-Type", "")

        with urllib.request.urlopen(f"{base_url}/app.js") as r:
            assert r.status == 200
            assert "application/javascript" in r.headers.get("Content-Type", "")

        with urllib.request.urlopen(f"{base_url}/api/tasks") as r:
            assert r.status == 200
            datos = json.loads(r.read().decode("utf-8"))
            assert datos["ok"] is True
            assert len(datos["tasks"]) == 4

        try:
            urllib.request.urlopen(f"{base_url}/no_existe.html")
            assert False
        except urllib.error.HTTPError as err:
            assert err.code == 404

        if not os.environ.get("PYTEST_REPORT_FILE"):
            req = urllib.request.Request(
                f"{base_url}/api/tests",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as r:
                assert r.status == 200
                datos_tests = json.loads(r.read().decode("utf-8"))
                assert datos_tests["ok"] is True
                assert "summary" in datos_tests
                assert "tests" in datos_tests
                assert isinstance(datos_tests["tests"], list)
    finally:
        servidor.shutdown()
        servidor.server_close()
