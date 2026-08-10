from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

PROBLEM_TYPE_BASE = "https://agent-travel.local/errors"


class ApiError(Exception):
    def __init__(
        self,
        status: int,
        title: str,
        detail: str,
        type_slug: str,
        errors: list[dict] | None = None,
    ):
        self.status, self.title, self.detail = status, title, detail
        self.type_slug, self.errors = type_slug, errors


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        body = {
            "type": f"{PROBLEM_TYPE_BASE}/{exc.type_slug}",
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
            "instance": str(request.url.path),
        }
        if exc.errors:
            body["errors"] = exc.errors
        return JSONResponse(
            status_code=exc.status, content=body, media_type="application/problem+json"
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {"field": ".".join(str(p) for p in e["loc"]), "detail": e["msg"]} for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            media_type="application/problem+json",
            content={
                "type": f"{PROBLEM_TYPE_BASE}/validation-error",
                "title": "Validation failed",
                "status": 422,
                "detail": "Um ou mais campos são inválidos.",
                "instance": str(request.url.path),
                "errors": errors,
            },
        )
