from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse

from mongo_layout_service.app.core.config import get_settings

settings = get_settings()

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


def _payload_excedido(request_id: str) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content={
            "detail": {
                "codigo_erro": "PAYLOAD_EXCEDIDO",
                "mensagem": "Payload acima do limite operacional do layout registry.",
            }
        },
    )
    response.headers["X-Request-ID"] = request_id
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


async def aplicar_hardening_http(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.app_max_request_size_bytes:
                return _payload_excedido(request_id)
        except ValueError:
            return _payload_excedido(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    for header, value in SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)
    return response
