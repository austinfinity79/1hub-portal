from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


class DuplicateNoticeError(AppException):
    def __init__(self, full_order_id: str) -> None:
        super().__init__(400, f"Notice already processed for order {full_order_id}")


class InvalidStateTransition(AppException):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(422, f"Invalid state transition: {current} -> {target}")


class SignatureVerificationFailed(AppException):
    def __init__(self) -> None:
        super().__init__(401, "Napas signature verification failed")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
