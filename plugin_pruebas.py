from __future__ import annotations

import json
import os
from typing import Any

_resultados: dict[str, dict[str, Any]] = {}
_errores_coleccion: list[dict[str, Any]] = []


def pytest_collectreport(report: Any) -> None:
    if report.failed:
        detalle = str(report.longrepr) if report.longrepr else "Fallo durante recolección"
        lineas = [l for l in detalle.splitlines() if l.strip()]
        mensaje = lineas[-1] if lineas else detalle
        _errores_coleccion.append({
            "nodeid": report.nodeid,
            "name": report.nodeid,
            "file": report.nodeid.split("::")[0] if "::" in report.nodeid else report.nodeid,
            "outcome": "error",
            "duration": 0.0,
            "message": mensaje,
            "traceback": detalle,
        })


def pytest_runtest_logreport(report: Any) -> None:
    nodeid = report.nodeid
    partes = nodeid.split("::")
    archivo = partes[0]
    nombre = "::".join(partes[1:]) if len(partes) > 1 else partes[0]

    if nodeid not in _resultados:
        _resultados[nodeid] = {
            "nodeid": nodeid,
            "name": nombre,
            "file": archivo,
            "outcome": "passed",
            "duration": 0.0,
            "message": "",
            "traceback": "",
        }

    item = _resultados[nodeid]
    item["duration"] += getattr(report, "duration", 0.0)

    if report.failed:
        item["outcome"] = "error" if report.when in ("setup", "teardown") else "failed"
        detalle = str(report.longrepr) if report.longrepr else "Error"
        lineas = [l for l in detalle.splitlines() if l.strip()]
        linea_relevante = ""
        for linea in reversed(lineas):
            if any(pref in linea for pref in ("E   ", "Error", "Exception", "NotImplementedError", "AssertionError")):
                linea_relevante = linea.replace("E   ", "").strip()
                break
        item["message"] = linea_relevante or (lineas[-1] if lineas else "Error")
        item["traceback"] = detalle
    elif report.skipped and item["outcome"] == "passed":
        item["outcome"] = "skipped"
        item["message"] = str(getattr(report, "wasxfail", "")) or "Omitido"
    elif report.passed and report.when == "call" and item["outcome"] != "failed":
        item["outcome"] = "passed"


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    ruta = os.environ.get("PYTEST_REPORT_FILE")
    if not ruta:
        return

    lista_pruebas = list(_resultados.values()) + _errores_coleccion
    resumen = {
        "total": len(lista_pruebas),
        "passed": sum(1 for t in lista_pruebas if t["outcome"] == "passed"),
        "failed": sum(1 for t in lista_pruebas if t["outcome"] == "failed"),
        "skipped": sum(1 for t in lista_pruebas if t["outcome"] == "skipped"),
        "errors": sum(1 for t in lista_pruebas if t["outcome"] == "error"),
    }

    datos = {
        "exit_code": int(exitstatus),
        "summary": resumen,
        "tests": lista_pruebas,
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
