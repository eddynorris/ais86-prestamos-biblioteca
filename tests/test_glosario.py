from __future__ import annotations

import ast
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DOMINIO = RAIZ / "dominio"
GLOSARIO = RAIZ / "glosario.md"

_COLUMNAS = ("Término (el idioma del negocio)", "En el código", "Significado")

def _identificadores_del_dominio() -> set[str]:

    encontrados: set[str] = set()
    for archivo in sorted(DOMINIO.glob("*.py")):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ClassDef):
                encontrados.add(nodo.name)
                for hijo in nodo.body:
                    if isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        encontrados.add(hijo.name)
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                encontrados.add(nodo.name)
    return encontrados

def _filas_del_glosario() -> list[list[str]]:
    lineas = GLOSARIO.read_text(encoding="utf-8").splitlines()
    indice = next(
        (i for i, linea in enumerate(lineas) if linea.startswith("|") and _COLUMNAS[0] in linea),
        None,
    )
    assert indice is not None, f"El glosario debe tener una tabla que empiece por {_COLUMNAS[0]!r}"
    filas = []
    for linea in lineas[indice + 1:]:
        if not linea.startswith("|"):
            break
        celdas = [celda.strip() for celda in linea.strip("|").split("|")]
        if len(celdas) != 3 or set(celdas[0]) <= set("-: "):
            continue
        filas.append(celdas)
    return filas

def test_glosario_tiene_11_terminos_completos():
    filas = _filas_del_glosario()
    assert len(filas) == 11, f"Se requieren 11 términos de negocio; se encontraron {len(filas)}."
    incompletas = [
        termino
        for termino, codigo, significado in filas
        if not codigo.strip() or not significado.strip() or "¿?" in (codigo, significado)
    ]
    assert not incompletas, f"Completa identificador y significado para: {', '.join(incompletas)}"

def test_identificadores_del_glosario_existen_en_dominio():
    identificadores = _identificadores_del_dominio()
    errores = []
    ignorar = {"El", "En", "el", "la", "los"}
    for termino, en_el_codigo, significado in _filas_del_glosario():
        citados = [
            nombre
            for nombre in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", en_el_codigo)
            if nombre not in ignorar
        ]
        if (
            not citados
            or not en_el_codigo.strip()
            or not significado.strip()
            or "¿?" in en_el_codigo
            or "¿?" in significado
        ):
            errores.append(f"{termino}: falta identificador o significado")
            continue
        faltantes = [nombre for nombre in citados if nombre not in identificadores]
        if faltantes:
            errores.append(f"{termino}: no existe(n) en dominio/: {', '.join(faltantes)}")
    assert not errores, "Glosario incompleto o desactualizado:\n" + "\n".join(errores)

def test_el_glosario_usa_terminos_de_negocio():
    terminos = [fila[0].casefold() for fila in _filas_del_glosario()]
    tecnicos = ("repositorio", "adaptador", "caso de uso", "entidad", "value object", "sqlite", "dto", "manager", "helper", "handler")
    encontrados = [termino for termino in terminos if any(palabra in termino for palabra in tecnicos)]
    assert not encontrados, f"Usa términos del negocio, no nombres técnicos: {', '.join(encontrados)}"
