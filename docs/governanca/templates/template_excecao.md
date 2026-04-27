# Template de Documentação de Exceção

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar exceções de qualidade (quality_ans.*_exception).

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `tipo` | Categoria da exceção | `CNPJ_DIGITO_INVALIDO` |
| `severidade` | `BLOQUEANTE` ou `WARNING` | `WARNING` |
| `mensagem` | Descrição legível | "CNPJ 11222333000182 dígito verificador inválido" |
| `bloqueio` | Impede produto principal? | `false` (WARNING) |
| `tabela_origem` | Tabela onde foi detectada | `quality_ans.quality_operadora_exception` |
| `data_deteccao` | Quando detectada | `2026-04-15` |
| `owner_correcao` | Responsável pela correção | `Engenharia de Dados` |
| `status` | `aberta`, `corrigida`, `ignorada` | `aberta` |

## Checklist
- [ ] Severidade definida (BLOQUEANTE/WARNING)
- [ ] Owner de correção definido
- [ ] Bloqueio coerente com severidade