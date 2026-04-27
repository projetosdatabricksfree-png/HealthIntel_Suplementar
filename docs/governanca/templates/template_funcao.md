# Template de Documentação de Função

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar funções PostgreSQL.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome` | Nome da função | `normalizar_cnpj` |
| `entrada` | Parâmetros e tipos | `cnpj text` |
| `saida` | Tipo de retorno | `varchar(14)` |
| `descricao` | O que faz | "Remove não-dígitos e aplica zero-fill 14" |
| `deterministica` | `sim` ou `nao` | `sim` |
| `efeitos_colaterais` | Efeitos além do retorno | `nenhum` |
| `chamada_externa` | Faz HTTP/API call? | `nao` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `deprecated` | `ativo` |

## Regras
- Proibido fazer chamada externa (HTTP, API) sem ADR.
- Documentar contrato (entrada/saída) sempre.