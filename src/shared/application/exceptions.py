class AppException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"


class NotFoundError(AppException):
    status_code: int = 404

    def __init__(self, entity: str, entity_id: str | None = None):
        if entity_id:
            self.detail = f"{entity} with id '{entity_id}' not found"
        else:
            self.detail = f"{entity} not found"


class DuplicateError(AppException):
    status_code: int = 409

    def __init__(self, entity: str, field: str, value: str):
        self.detail = f"{entity} with {field} '{value}' already exists"


class UnauthorizedError(AppException):
    status_code: int = 401

    def __init__(self, detail: str = "Not authenticated"):
        self.detail = detail


class ForbiddenError(AppException):
    status_code: int = 403

    def __init__(self, detail: str = "Forbidden"):
        self.detail = detail


class ValidationError(AppException):
    status_code: int = 400

    def __init__(self, detail: str):
        self.detail = detail


class EventBusUnavailableError(AppException):
    status_code: int = 503

    def __init__(self):
        self.detail = "Event bus unavailable"
