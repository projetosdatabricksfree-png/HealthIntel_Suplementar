from dataclasses import dataclass, field

from ingestao.app.layout_client import validar_arquivo_layout


@dataclass(slots=True)
class IdentificacaoLayout:
    dataset_codigo: str
    compativel: bool
    layout_id: str | None
    layout_versao_id: str | None
    assinatura_colunas: str
    motivos: list[str] = field(default_factory=list)
    colunas_mapeadas: list[dict] = field(default_factory=list)


async def identificar_layout(
    dataset_codigo: str, colunas_detectadas: list[str], nome_arquivo: str
) -> IdentificacaoLayout:
    resultado = await validar_arquivo_layout(
        dataset_codigo=dataset_codigo,
        colunas_detectadas=colunas_detectadas,
        nome_arquivo=nome_arquivo,
    )
    return IdentificacaoLayout(
        dataset_codigo=dataset_codigo,
        compativel=resultado["compativel"],
        layout_id=resultado.get("layout_id"),
        layout_versao_id=resultado.get("layout_versao_id"),
        assinatura_colunas=resultado["assinatura_detectada"],
        motivos=resultado.get("motivos", []),
        colunas_mapeadas=resultado.get("colunas_mapeadas", []),
    )
