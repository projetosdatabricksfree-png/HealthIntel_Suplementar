from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.app.core.config import get_settings

settings = get_settings()

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


def _criar_response_limite_excedido(request_id: str) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content={
            "detail": {
                "codigo_erro": "PAYLOAD_EXCEDIDO",
                "mensagem": "Payload acima do limite operacional configurado.",
            }
        },
    )
    response.headers["X-Request-ID"] = request_id
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


async def aplicar_hardening_http(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.app_max_request_size_bytes:
                return _criar_response_limite_excedido(request_id)
        except ValueError:
            return _criar_response_limite_excedido(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    for header, value in SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)
    if settings.app_env.lower() != "local":
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response
