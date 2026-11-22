"""Excepciones de dominio. Los servicios las lanzan y main.py las traduce a HTTP."""


class DomainError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404


class ForbiddenError(DomainError):
    status_code = 403


class ConflictError(DomainError):
    status_code = 409


class BusinessRuleError(DomainError):
    """Violación de una regla de negocio (p. ej. transición de estado no permitida)."""
    status_code = 422


class AuthError(DomainError):
    status_code = 401
