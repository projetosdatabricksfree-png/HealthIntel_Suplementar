# Template de Documentação de Data Product

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar data products da plataforma.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome` | Nome do data product | `operadora_360_validado` |
| `dataset` | Tabela física | `api_ans.api_premium_operadora_360_validado` |
| `versao` | Versão do data product | `v1` |
| `plano` | Plano comercial | `premium` |
| `acesso` | `api` ou `sql` | `api` |
| `rota_api` | Se acesso API | `/v1/premium/operadoras` |
| `owner_tecnico` | Responsável | `Engenharia de Dados` |
| `owner_negocio` | Área de negócio | `Produto` |
| `sla_atualizacao` | Frequência | `Mensal (D+5)` |
| `granularidade` | Grão | `Uma linha por operadora por competência` |
| `score_qualidade` | Score publicado | `quality_score_publicacao` |
| `master_ids` | Surrogate keys expostas | `operadora_master_id` |
| `linhagem` | Documento de linhagem | `lineage_fase4.md` |
| `data_criacao` | Data | `2026-04-27` |
| `status` | `ativo`, `deprecated` | `ativo` |

## Checklist
- [ ] Owner definido
- [ ] SLA documentado
- [ ] Score de qualidade presente (premium)
- [ ] Linhagem documentada