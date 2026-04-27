# Dicionário de Colunas — Padrão Obrigatório

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir o padrão obrigatório para documentar toda coluna da plataforma HealthIntel Suplementar. Toda coluna nova deve ter uma entrada neste dicionário.

---

## Template de Documentação de Coluna

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **nome_fisico** | Nome no PostgreSQL | `cnpj_normalizado` |
| **nome_logico** | Nome legível | "CNPJ normalizado" |
| **descricao** | Descrição funcional | "CNPJ da operadora com 14 dígitos, validado deterministicamente" |
| **origem** | Fonte do dado | `stg_ans.stg_cadop — nr_cnpj` |
| **tipo_fisico_pg** | Tipo PostgreSQL | `varchar(14)` |
| **tipo_equivalente_sqlserver** | Quando aplicável | `varchar(14)` |
| **dominio_negocio** | Domínio funcional | `Documento / Cadastro` |
| **aceita_nulo** | `sim` ou `nao` | `nao` |
| **regra_preenchimento** | Como o valor é gerado | `normalizar_cnpj(stg_cadop.nr_cnpj)` |
| **regra_normalizacao** | Transformação aplicada | `somente dígitos, 14 posições, zeros à esquerda` |
| **regra_validacao** | Validação aplicada | `validar_cnpj_completo(cnpj_normalizado) → dígito verificador` |
| **exemplo_valido** | Valor válido | `11222333000181` |
| **exemplo_invalido** | Valor inválido | `123` (tamanho errado), `11222333000182` (dígito inválido) |
| **chave** | `pk`, `fk`, `uk`, `nenhuma` | `nenhuma` |
| **indexavel** | `sim` ou `nao` | `sim` |
| **exposta_api** | `sim` ou `nao` | `sim` |
| **sensibilidade_lgpd** | Classificação LGPD | `publico` |
| **campo_tecnico** | Uso interno da plataforma | `nao` |
| **campo_auditoria** | Registro de auditoria | `nao` |
| **produto_premium** | Aparece em produto premium | `sim` |

---

## Colunas Críticas — Referência Rápida

### `registro_ans`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(6)` |
| aceita_nulo | `nao` |
| regra_normalizacao | `zfill(6)`, somente dígitos |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |
| produto_premium | `sim` |

### `competencia`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `int` |
| aceita_nulo | `nao` |
| regra_validacao | `200001 <= competencia <= competencia_atual + 1`, mês entre 01 e 12 |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |
| produto_premium | `sim` |

### `cnpj`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(14)` |
| aceita_nulo | Depende do contexto |
| regra_normalizacao | Somente dígitos, 14 posições, zeros à esquerda |
| regra_validacao | Dígito verificador determinístico |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |
| produto_premium | `sim` |
| **NUNCA** | `int`, `integer`, `bigint`, `numeric`, `decimal` |

### `cpf`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(11)` |
| aceita_nulo | Fluxo privado com justificativa LGPD |
| regra_normalizacao | Somente dígitos, 11 posições |
| exposta_api | `nao` (apenas em fluxo privado) |
| sensibilidade_lgpd | `pessoal` |
| produto_premium | Apenas em fluxo privado |
| **NUNCA** | `int`, `integer`, `bigint`, `numeric`, `decimal` |

### `cnes`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(7)` |
| aceita_nulo | `nao` |
| regra_normalizacao | `zfill(7)`, somente dígitos |
| regra_validacao | Formato de 7 dígitos |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |
| produto_premium | `sim` |

### `uf`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `char(2)` |
| aceita_nulo | `sim` |
| regra_normalizacao | Maiúscula |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |

### `cd_municipio`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(7)` — código IBGE com 7 dígitos |
| aceita_nulo | `sim` |
| regra_normalizacao | `zfill(7)` |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |

### `cd_procedimento_tuss`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(10)` |
| aceita_nulo | `nao` |
| exposta_api | `sim` |
| sensibilidade_lgpd | `publico` |

### `valor_*` / `vl_*`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `numeric(18,2)` |
| aceita_nulo | Depende do contexto |
| **NUNCA** | `float`, `real`, `double precision` |

### `qt_*`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `bigint` |
| aceita_nulo | `sim` |
| exposta_api | `sim` |

### `taxa_*`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `double precision` |
| aceita_nulo | `sim` |
| exposta_api | `sim` |

### `dt_*` (data pura)
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `date` |
| aceita_nulo | `sim` |

### `_carregado_em`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `timestamp(3)` |
| aceita_nulo | `nao` |
| campo_tecnico | `sim` |
| campo_auditoria | `sim` |
| exposta_api | `nao` |

### `_hash_arquivo`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(64)` |
| aceita_nulo | `nao` |
| campo_tecnico | `sim` |
| exposta_api | `nao` |
| **NUNCA** exposto em API pública ou premium |

### `_lote_ingestao`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(36)` |
| aceita_nulo | `nao` |
| campo_tecnico | `sim` |
| campo_auditoria | `sim` |
| exposta_api | `nao` |

### `tenant_id`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(64)` |
| aceita_nulo | `nao` em schemas privados |
| sensibilidade_lgpd | `restrito` |
| exposta_api | Apenas em rotas privadas coerentes com autorização |

### `mdm_status`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(20)` |
| aceita_nulo | `nao` |
| valores validos | `ATIVO`, `INATIVO`, `PENDENTE`, `EXCLUIDO` |
| exposta_api | `sim` |

### `mdm_confidence_score`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `double precision` |
| aceita_nulo | `sim` |
| faixa | `0.0` a `1.0` |
| exposta_api | `sim` |

### `quality_score_*`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `double precision` |
| aceita_nulo | `sim` |
| faixa | `0.0` a `100.0` |
| exposta_api | `sim` |

### `documento_quality_status`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `varchar(20)` |
| aceita_nulo | `nao` |
| valores validos | `VALIDO`, `INVALIDO`, `NAO_VERIFICADO` |
| exposta_api | `sim` |

### `is_cnpj_estrutural_valido`
| Campo | Valor |
|-------|-------|
| tipo_fisico_pg | `boolean` |
| aceita_nulo | `nao` |
| exposta_api | `sim` |

---

## Regras

1. Toda coluna nova deve ser documentada antes do merge em main.
2. Usar template `templates/template_coluna.md`.
3. CNPJ, CPF, CNES e Registro ANS **nunca** são tipos numéricos.
4. Colunas técnicas (`_carregado_em`, `_hash_arquivo`, `_lote_ingestao`) **nunca** são expostas em API.
5. Coluna publicada não muda tipo silenciosamente. Alteração exige deprecation + nova coluna.