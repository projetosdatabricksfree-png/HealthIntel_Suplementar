# Template de Documentação de Constraint

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template oficial para documentar constraints da plataforma.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome` | Nome (`ck_`, `uk_`) | `ck_quality_dataset_score_0_100` |
| `tabela` | Tabela associada | `api_ans.api_premium_quality_dataset` |
| `tipo` | `check`, `unique`, `not_null` | `check` |
| `regra` | Regra aplicada | `quality_score_documental between 0 and 100` |
| `justificativa` | Por que existe | "Garante scores no intervalo válido" |
| `data_criacao` | Data | `2026-04-27` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `removido` | `ativo` |

## Checklist
- [ ] Nome segue padrão `ck_`/`uk_`
- [ ] Regra barata e inviolável
- [ ] Não bloqueia ingestão bruta sem necessidade