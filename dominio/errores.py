from __future__ import annotations

class ErrorDeDominio(Exception):

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje

class ValorInvalido(ValueError):

    def __init__(self, concepto: str, recibido: object, esperado: str) -> None:
        super().__init__(f"{concepto} inválido: {recibido!r}. Se esperaba {esperado}.")
        self.concepto = concepto
        self.recibido = recibido
        self.esperado = esperado

class LimiteDePrestamosAlcanzado(ErrorDeDominio):

    def __init__(self, codigo_socio: str, limite: int) -> None:
        super().__init__(
            f"El socio {codigo_socio} ya tiene {limite} préstamo(s) activo(s), "
            f"que es el máximo permitido."
        )

class EjemplarYaPrestado(ErrorDeDominio):

    def __init__(self, codigo_ejemplar: str) -> None:
        super().__init__(f"El ejemplar {codigo_ejemplar} ya está prestado.")

class PrestamoNoEncontrado(ErrorDeDominio):

    def __init__(self, codigo_ejemplar: str) -> None:
        super().__init__(f"El socio no tiene un préstamo activo del ejemplar {codigo_ejemplar}.")

class SocioSinPrestamos(ErrorDeDominio):

    def __init__(self, codigo_socio: str) -> None:
        super().__init__(f"No existe registro de préstamos para el socio {codigo_socio}.")
