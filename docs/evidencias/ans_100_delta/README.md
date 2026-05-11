# Evidências — Sprint 41: Delta ANS 100%

Data de fechamento: 2026-05-11

## Índice

| Arquivo | Conteúdo |
|---------|----------|
| [dbt_build.md](dbt_build.md) | Output do `dbt build --select tag:delta_ans_100` |
| [dbt_test.md](dbt_test.md) | Output do `dbt test --select tag:delta_ans_100` |
| [smoke_sql.md](smoke_sql.md) | Resultado dos smokes SQL das 12 tabelas API |
| [grants.md](grants.md) | Verificação de grants nas schemas |

## Resumo de fechamento

- **162 modelos** buildados com sucesso (PASS=162, ERROR=0)
- **14 novos testes Python** criados e passando (`test_delta_ans_parsers.py`)
- **215 testes totais** passando (101 ingestao + 114 api)
- **ruff check**: zero erros
- **Grants**: `healthintel_cliente_reader` em 19 tabelas `consumo_ans`; `healthintel_premium_reader` em 11 tabelas `consumo_premium_ans`

## Novos artefatos criados nesta sessão

| Artefato | Tipo |
|----------|------|
| `models/staging/stg_quadro_auxiliar_corresponsabilidade.sql` | staging view |
| `models/api/api_plano_servico_opcional.sql` | api table |
| `models/api/api_quadro_auxiliar_corresponsabilidade.sql` | api table |
| `models/consumo/consumo_historico_plano.sql` | consumo table |
| `models/consumo/consumo_plano_servico_opcional.sql` | consumo table |
| `ingestao/tests/test_delta_ans_parsers.py` | 14 testes Python |
| `_stg_produtos_planos.yml` (corrigido + expandido) | documentação + testes dbt |
| `_consumo.yml` (expandido) | documentação + testes dbt |
