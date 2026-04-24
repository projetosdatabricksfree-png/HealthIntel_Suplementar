# Contrato Bronze API

A Bronze API expõe o espelho técnico da camada `bruto_ans`. O contrato é estrutural, não semântico: o objetivo é rastreabilidade, auditoria e reprocessamento.

## Garantias

- Cada resposta contém `dados` e `meta`.
- `meta` sempre traz `fonte`, `competencia`, `lote_id`, `arquivo_origem`, `carregado_em`, `versao_dataset` e `aviso_qualidade`.
- O dataset servido é o resultado direto da view `api_ans.api_bronze_*`, sem transformação de negócio.
- O acesso é restrito ao plano `enterprise_tecnico`.

## O que a Bronze API não promete

- Não há garantia semântica de conteúdo.
- Não há enriquecimento analítico.
- Não há fallback silencioso para colunas ausentes.
- Não há cache como estratégia principal de estabilidade.

## Casos de uso

- Auditoria técnica.
- Reprocessamento.
- Comparação entre lote original e lote carregado.
- Integração com lakehouse ou pipelines externos.

