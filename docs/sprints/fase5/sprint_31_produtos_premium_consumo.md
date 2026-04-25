# Sprint 31 — Produtos Premium Validados para Consumo

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.6.0-premium`
**Objetivo:** criar novos data products comerciais sem substituir os atuais.
**Fim esperado:** API premium vendendo dados curados, validados e com qualidade explícita.
**Critério de saída:** modelos `consumo_premium_*` materializados em `consumo_ans` (ou em `consumo_premium_ans` se separação de schema for definida); todos com `mdm_status`, `quality_score_*` e referência aos master IDs; nenhum modelo `consumo_*` existente alterado.

## Regra-mãe

- [ ] `consumo_operadora_360` permanece intacta.
- [ ] Nenhum dos 8 modelos atuais de `consumo_ans` é alterado.
- [ ] Nenhum modelo TISS/CNES existente é alterado.
- [ ] Modelos premium são consumidos por endpoints premium novos (Sprint 32) e não substituem rotas existentes.

## Histórias

### HIS-11.1 — Criar consumo premium de operadora

- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_operadora_360_validado.sql`.
- [ ] Usar `consumo_operadora_360` como fonte (LEFT JOIN, leitura apenas).
- [ ] Adicionar `operadora_master_id`.
- [ ] Adicionar `cnpj_digito_valido` (vindo de `dq_operadora_documento`).
- [ ] Adicionar `cnpj_receita_status` (vindo de `int_cnpj_receita_validado`).
- [ ] Adicionar `mdm_status`.
- [ ] Adicionar `quality_score_documental` (0–100).
- [ ] Adicionar `quality_score_mdm` (0–100).
- [ ] Não alterar `consumo_operadora_360`.
- [ ] Tag dbt `consumo_premium`.

### HIS-11.2 — Criar consumo premium CNES

- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_cnes_estabelecimento_validado.sql`.
- [ ] Usar `stg_cnes_estabelecimento` e fatos CNES existentes como fonte.
- [ ] Adicionar `estabelecimento_master_id`.
- [ ] Adicionar `prestador_master_id`.
- [ ] Adicionar `cnpj_digito_valido`.
- [ ] Adicionar `cnpj_receita_status`.
- [ ] Adicionar `municipio_valido` (validado contra `ref_municipio_ibge`).
- [ ] Adicionar `cnes_formato_valido`.
- [ ] Adicionar `quality_score_cnes`.
- [ ] Não alterar os fatos CNES já existentes.

### HIS-11.3 — Criar consumo premium TISS/TUSS

Contexto: o Padrão TISS é obrigatório para troca eletrônica de dados na saúde suplementar e mantém o componente TUSS como representação de conceitos. TISS sem dimensão TUSS versionada perde valor comercial.

- [ ] Criar `healthintel_dbt/models/staging/stg_tuss_terminologia.sql`.
- [ ] Criar `healthintel_dbt/models/marts/dimensao/dim_tuss_terminologia.sql`.
- [ ] Criar `healthintel_dbt/models/marts/dimensao/dim_tuss_procedimento.sql`.
- [ ] Criar `healthintel_dbt/models/consumo/xref_tiss_tuss_procedimento.sql`.
- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_tiss_procedimento_tuss_validado.sql`.
- [ ] Usar `stg_tiss_procedimento`, `int_tiss_operadora_trimestre`, `fat_tiss_procedimento_operadora` e `mart_tiss_procedimento` como fontes.
- [ ] Adicionar `versao_tuss`.
- [ ] Adicionar `codigo_tuss`.
- [ ] Adicionar `descricao_tuss`.
- [ ] Adicionar `vigencia_inicio`.
- [ ] Adicionar `vigencia_fim`.
- [ ] Adicionar `is_tuss_vigente` (bit).
- [ ] Adicionar `tiss_tuss_match_status` (MATCHED | UNMATCHED | DEPRECATED | AMBIGUOUS).
- [ ] Não alterar os modelos TISS já existentes.

### HIS-11.4 — Criar consumo premium contrato/subfatura

- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_contrato_validado.sql`.
- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_subfatura_validada.sql`.
- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_contrato_subfatura_operadora.sql`.
- [ ] Criar `healthintel_dbt/models/consumo/consumo_premium_contrato_inconsistencia.sql`.
- [ ] Expor `contrato_master_id`.
- [ ] Expor `subfatura_master_id`.
- [ ] Expor `operadora_master_id`.
- [ ] Expor `mdm_status`.
- [ ] Expor `quality_score_contrato`.
- [ ] Expor `quality_score_subfatura`.
- [ ] Filtrar exceções bloqueantes (não publicar em premium).

## Entregas esperadas

- [ ] 4 modelos `consumo_premium_*` (operadora, CNES, TISS/TUSS, contrato/subfatura)
- [ ] 4 modelos auxiliares contrato/subfatura (`_validado`, `_validada`, `_subfatura_operadora`, `_inconsistencia`)
- [ ] Dimensão TUSS (`stg_tuss_terminologia`, `dim_tuss_terminologia`, `dim_tuss_procedimento`, `xref_tiss_tuss_procedimento`)
- [ ] Tag dbt `consumo_premium`
- [ ] `_consumo_premium.yml` com testes genéricos (`unique`, `not_null`, `accepted_values`)

## Validação esperada (hard gates)

- [ ] `dbt build --select tag:consumo_premium` zero erros.
- [ ] `dbt test --select tag:consumo_premium` zero falhas.
- [ ] `consumo_operadora_360.sql` e os 8 modelos atuais de `consumo_ans` byte-idênticos à tag `v3.0.0`.
- [ ] Modelos TISS existentes inalterados.
- [ ] `quality_score_*` ∈ [0, 100] em 100% das linhas.
- [ ] Nenhuma linha em `consumo_premium_*` com CNPJ tecnicamente inválido (validação cruzada com `dq_*`).
- [ ] Nenhuma linha de contrato/subfatura premium com exceção `is_blocking = 1`.

## Resultado Esperado

Sprint 31 entrega os primeiros data products comerciais validados e enriquecidos da Fase 5. Cada linha publicada tem score de qualidade explícito, master IDs e rastreabilidade até a fonte oficial (Receita/Serpro). Os modelos atuais permanecem intactos — clientes legados continuam consumindo o `consumo_ans` original, clientes premium passam a ter acesso aos `consumo_premium_*`.
