from __future__ import annotations

import argparse
import http.server
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any

_bloqueo_ejecucion = threading.Lock()
RAIZ_PROYECTO = Path(__file__).resolve().parent
DIR_WEB = RAIZ_PROYECTO / "web"


def extraer_tareas(ruta_readme: Path) -> list[str]:
    if not ruta_readme.exists():
        return []

    contenido = ruta_readme.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    en_seccion = False
    tareas: list[str] = []
    buffer_actual: list[str] = []

    for linea in lineas:
        texto = linea.strip()
        if texto.startswith("## Completar"):
            en_seccion = True
            continue
        elif en_seccion and texto.startswith("## "):
            break

        if en_seccion:
            match = re.match(r"^\s*(\d+\.|\-|\*)\s+(.*)$", linea)
            if match:
                if buffer_actual:
                    tareas.append(" ".join(buffer_actual).strip())
                    buffer_actual = []
                buffer_actual.append(match.group(2).strip())
            elif buffer_actual:
                if not texto or texto.startswith("No modificar"):
                    tareas.append(" ".join(buffer_actual).strip())
                    buffer_actual = []
                else:
                    buffer_actual.append(texto)

    if buffer_actual:
        tareas.append(" ".join(buffer_actual).strip())

    return tareas


def ejecutar_pruebas(directorio_raiz: Path) -> dict[str, Any]:
    if not _bloqueo_ejecucion.acquire(blocking=False):
        return {
            "ok": False,
            "exit_code": -1,
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1,
                "duration": 0.0,
            },
            "tests": [],
            "stdout": "",
            "stderr": "",
            "error": "Ya hay una ejecución de pruebas en curso. Espera a que termine.",
        }

    fd, ruta_reporte = tempfile.mkstemp(prefix="pytest_report_", suffix=".json")
    os.close(fd)

    try:
        entorno = os.environ.copy()
        entorno["PYTEST_REPORT_FILE"] = ruta_reporte
        entorno["PYTHONPATH"] = str(directorio_raiz) + (os.pathsep + entorno.get("PYTHONPATH", "") if entorno.get("PYTHONPATH") else "")

        comando = [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "plugin_pruebas",
            "-vv",
            "-s",
            "--tb=short",
        ]

        inicio = time.time()
        proceso = subprocess.run(
            comando,
            cwd=str(directorio_raiz),
            env=entorno,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        duracion = round(time.time() - inicio, 3)

        salida_reporte: dict[str, Any] = {}
        if os.path.exists(ruta_reporte) and os.path.getsize(ruta_reporte) > 0:
            try:
                with open(ruta_reporte, "r", encoding="utf-8") as f:
                    salida_reporte = json.load(f)
            except Exception:
                salida_reporte = {}

        if "summary" in salida_reporte and "tests" in salida_reporte:
            resumen = salida_reporte["summary"]
            resumen["duration"] = duracion
            return {
                "ok": True,
                "exit_code": proceso.returncode,
                "summary": resumen,
                "tests": salida_reporte.get("tests", []),
                "stdout": proceso.stdout,
                "stderr": proceso.stderr,
                "error": None,
            }

        return {
            "ok": True,
            "exit_code": proceso.returncode,
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1 if proceso.returncode != 0 else 0,
                "duration": duracion,
            },
            "tests": [],
            "stdout": proceso.stdout,
            "stderr": proceso.stderr,
            "error": "No se pudo generar el reporte estructurado de pruebas.",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "exit_code": -1,
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1,
                "duration": 60.0,
            },
            "tests": [],
            "stdout": exc.stdout if isinstance(exc.stdout, str) else "",
            "stderr": exc.stderr if isinstance(exc.stderr, str) else "",
            "error": "La ejecución de pruebas excedió el tiempo límite (60 segundos).",
        }
    except Exception as exc:
        return {
            "ok": False,
            "exit_code": -1,
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1,
                "duration": 0.0,
            },
            "tests": [],
            "stdout": "",
            "stderr": str(exc),
            "error": f"Error al iniciar pytest: {exc}",
        }
    finally:
        _bloqueo_ejecucion.release()
        if os.path.exists(ruta_reporte):
            try:
                os.unlink(ruta_reporte)
            except OSError:
                pass


class ManejadorServidor(http.server.BaseHTTPRequestHandler):
    directorio_raiz = RAIZ_PROYECTO
    directorio_web = DIR_WEB

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        ruta_limpia = self.path.split("?")[0].rstrip("/")
        if ruta_limpia == "":
            ruta_limpia = "/"

        if ruta_limpia == "/api/tasks":
            self.responder_json(200, {
                "ok": True,
                "tasks": extraer_tareas(self.directorio_raiz / "README.md"),
            })
            return

        if ruta_limpia in ("/", "/index.html"):
            self.servir_archivo(self.directorio_web / "index.html", "text/html; charset=utf-8")
            return

        nombre_archivo = ruta_limpia.lstrip("/")
        if nombre_archivo.startswith("web/"):
            nombre_archivo = nombre_archivo[4:]

        archivo_candidato = (self.directorio_web / nombre_archivo).resolve()
        try:
            archivo_candidato.relative_to(self.directorio_web.resolve())
        except ValueError:
            self.send_error(403, "Acceso denegado")
            return

        if archivo_candidato.is_file():
            sufijo = archivo_candidato.suffix.lower()
            tipos = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".json": "application/json; charset=utf-8",
                ".svg": "image/svg+xml",
                ".png": "image/png",
            }
            mime = tipos.get(sufijo, "application/octet-stream")
            self.servir_archivo(archivo_candidato, mime)
            return

        self.send_error(404, "Recurso no encontrado")

    def do_POST(self) -> None:
        ruta_limpia = self.path.split("?")[0].rstrip("/")

        if ruta_limpia == "/api/tests":
            resultado = ejecutar_pruebas(self.directorio_raiz)
            codigo_http = 409 if resultado.get("error") and "en curso" in resultado["error"] else 200
            self.responder_json(codigo_http, resultado)
            return

        self.send_error(404, "Endpoint no encontrado")

    def servir_archivo(self, ruta_archivo: Path, content_type: str) -> None:
        try:
            cuerpo = ruta_archivo.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(cuerpo)
        except OSError:
            self.send_error(500, "Error al leer archivo")

    def responder_json(self, codigo_http: int, datos: dict[str, Any]) -> None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo_http)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(cuerpo)


def crear_servidor(host: str = "127.0.0.1", puerto: int = 8000, directorio_raiz: Path | None = None) -> http.server.HTTPServer:
    raiz = directorio_raiz or RAIZ_PROYECTO

    class _ManejadorConfigurado(ManejadorServidor):
        directorio_raiz = raiz
        directorio_web = raiz / "web"

    return http.server.HTTPServer((host, puerto), _ManejadorConfigurado)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    servidor = crear_servidor(host="127.0.0.1", puerto=args.port)
    print(f"Servidor iniciado en http://127.0.0.1:{args.port}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
