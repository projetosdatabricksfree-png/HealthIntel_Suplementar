# Template de Documentação de Coluna

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template oficial para documentar toda coluna da plataforma HealthIntel Suplementar.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome_fisico` | Nome no PostgreSQL | `cnpj_normalizado` |
| `nome_logico` | Nome legível | "CNPJ normalizado" |
| `descricao` | Descrição funcional | "CNPJ com 14 dígitos, validado deterministicamente" |
| `origem` | Fonte do dado | `stg_ans.stg_cadop.nr_cnpj` |
| `tipo_fisico_pg` | Tipo PostgreSQL | `varchar(14)` |
| `tipo_equivalente_sqlserver` | Quando aplicável | `varchar(14)` |
| `dominio_negocio` | Domínio funcional | `Documento / Cadastro` |
| `aceita_nulo` | `sim` ou `nao` | `nao` |
| `regra_preenchimento` | Como é gerado | `normalizar_cnpj(nr_cnpj)` |
| `regra_normalizacao` | Transformação | `somente dígitos, 14 posições, zero-fill` |
| `regra_validacao` | Validação aplicada | `validar_cnpj_completo()` |
| `exemplo_valido` | Valor válido | `11222333000181` |
| `exemplo_invalido` | Valor inválido | `123` |
| `chave` | `pk`, `fk`, `uk`, `nenhuma` | `nenhuma` |
| `indexavel` | `sim` ou `nao` | `sim` |
| `exposta_api` | `sim` ou `nao` | `sim` |
| `sensibilidade_lgpd` | Classificação | `publico` |
| `campo_tecnico` | `sim` ou `nao` | `nao` |
| `campo_auditoria` | `sim` ou `nao` | `nao` |
| `produto_premium` | `sim` ou `nao` | `sim` |
| `data_criacao` | Data de criação | `2026-04-27` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `deprecated` | `ativo` |

## Exemplo Preenchido

| Campo | Valor |
|-------|-------|
| nome_fisico | `cnpj_normalizado` |
| nome_logico | CNPJ normalizado |
| descricao | CNPJ da operadora com 14 dígitos |
| origem | `stg_cadop.nr_cnpj` |
| tipo_fisico_pg | `varchar(14)` |
| aceita_nulo | `nao` |
| regra_normalizacao | dígitos + zero-fill 14 |
| regra_validacao | `validar_cnpj_completo()` |
| exemplo_valido | `11222333000181` |
| exemplo_invalido | `123` |
| chave | `nenhuma` |
| indexavel | `sim` |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |
| campo_tecnico | `nao` |
| produto_premium | `sim` |
| data_criacao | 2026-04-15 |
| owner | Engenharia de Dados |
| status | ativo |

## Checklist de Validação
- [ ] Todos os campos obrigatórios preenchidos
- [ ] Tipo físico corresponde ao DDL
- [ ] CNPJ/CPF/CNES/Registro ANS nunca numérico
- [ ] Campos técnicos não expostos em API