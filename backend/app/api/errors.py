from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.errors import DomainError

STATUS_BY_CODE = {
    "not_found": 404,
    "unauthorized": 401,
    "forbidden": 403,
    "conflict": 409,
    "invalid_submission": 422,
    "rate_limited": 429,
    "hint_limit": 429,
    "domain_error": 400,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        status = STATUS_BY_CODE.get(exc.code, 400)
        return JSONResponse(
            status_code=status,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "loc": [str(part) for part in item.get("loc", [])],
                "msg": str(item.get("msg", "Invalid value.")),
                "type": str(item.get("type", "value_error")),
            }
            for item in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Check the submitted fields.",
                    "details": details,
                }
            },
        )
