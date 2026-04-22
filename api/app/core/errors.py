from fastapi import HTTPException
from fastapi.responses import JSONResponse

ERROS_PADRAO = {
    401: "AUTENTICACAO_INVALIDA",
    403: "ACESSO_NEGADO",
    429: "LIMITE_EXCEDIDO",
}


def normalizar_http_exception(exc: HTTPException) -> JSONResponse:
    if exc.status_code not in ERROS_PADRAO:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    detalhe: dict | None = exc.detail if isinstance(exc.detail, dict) else None
    codigo = ERROS_PADRAO[exc.status_code]
    if detalhe:
        codigo = detalhe.get("codigo") or detalhe.get("codigo_erro") or codigo
    mensagem = ""
    if detalhe and detalhe.get("mensagem"):
        mensagem = str(detalhe["mensagem"])
    elif not isinstance(exc.detail, dict):
        mensagem = str(exc.detail)
    extras = {}
    if detalhe:
        extras = {
            chave: valor
            for chave, valor in detalhe.items()
            if chave not in {"codigo", "codigo_erro", "mensagem", "detalhe"}
        }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "codigo": codigo,
            "mensagem": mensagem,
            "detalhe": detalhe.get("detalhe") if detalhe and detalhe.get("detalhe") is not None else extras,
        },
        headers=exc.headers,
    )
