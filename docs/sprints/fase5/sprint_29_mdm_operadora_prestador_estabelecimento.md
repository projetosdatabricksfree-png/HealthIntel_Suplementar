# Sprint 29 — MDM de Operadora, Prestador e Estabelecimento

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.4.0-mdm-publico`
**Objetivo:** criar golden record e crosswalk para operadoras, estabelecimentos CNES e prestadores, sem substituir `int_operadora_canonica` nem `dim_operadora_atual`.
**Fim esperado:** entidades master disponíveis como insumo para os produtos premium da Sprint 31 e para o MDM privado de contrato/subfatura da Sprint 30.
**Critério de saída:** modelos `mdm_*_master` materializados com `mdm_confidence_score`; tabelas `xref_*_origem` para crosswalk; tabelas `*_exception` para divergências; nenhum modelo `int_*` ou `dim_*` existente alterado.

## Regra-mãe

- [ ] `int_operadora_canonica` permanece intacta.
- [ ] `dim_operadora_atual` permanece intacta.
- [ ] Toda nova lógica vive em `healthintel_dbt/models/mdm/`.
- [ ] Surrogate keys MDM são UUID determinístico baseado em chaves naturais validadas.
- [ ] O diretório `mdm` deve estar configurado no `healthintel_dbt/dbt_project.yml` com `+schema: mdm`, `+materialized: table` e `+tags: ["mdm"]`.

## Histórias

### HIS-09.1 — Criar schema lógico MDM

- [ ] Criar pasta `healthintel_dbt/models/mdm/`.
- [ ] Criar `_mdm.yml` documentando todos os modelos da pasta.
- [ ] Criar documentação `docs/fase5/mdm_modelagem.md`.
- [ ] Documentar padrão de surrogate key (`<entidade>_master_id`, UUID v5 determinístico).
- [ ] Documentar padrão de natural key (CNPJ + registro_ans, CNPJ + CNES, etc.).
- [ ] Documentar padrão de crosswalk (`xref_<entidade>_origem`).
- [ ] Documentar padrão de score de confiança (`mdm_confidence_score` 0–100).
- [ ] Documentar padrão de exceção (`mdm_<entidade>_exception`).
- [ ] Definir `mdm_status`: GOLDEN | CANDIDATE | QUARENTENA | DEPRECATED.
- [ ] Criar tag dbt `mdm` para os modelos da pasta.

### HIS-09.2 — Criar MDM de operadora

- [ ] Criar `healthintel_dbt/models/mdm/mdm_operadora_master.sql`.
- [ ] Criar `healthintel_dbt/models/mdm/xref_operadora_origem.sql`.
- [ ] Usar `stg_cadop` como fonte principal.
- [ ] Usar `dim_operadora_atual` como fonte analítica já existente.
- [ ] Usar CNPJ validado (`int_cnpj_receita_validado` da Sprint 28) como reforço de identidade.
- [ ] Criar `operadora_master_id` (UUID v5).
- [ ] Criar `registro_ans_canonico`.
- [ ] Criar `cnpj_canonico`.
- [ ] Criar `razao_social_canonica`.
- [ ] Criar `nome_fantasia_canonico`.
- [ ] Criar `modalidade_canonica`.
- [ ] Criar `mdm_confidence_score` (regras: +30 se CNPJ válido digito, +30 se CNPJ ativo Receita, +20 se nome bate Receita, +20 se registro_ans bate CADOP).
- [ ] Criar `mdm_status`.
- [ ] Criar `healthintel_dbt/models/mdm/mdm_operadora_exception.sql`.
- [ ] Criar regra de divergência por CNPJ + registro_ans + razão social.
- [ ] Documentar no `_mdm.yml` com testes `unique` em `operadora_master_id` e `not_null` nas chaves canônicas.

### HIS-09.3 — Criar MDM de estabelecimento CNES

- [ ] Criar `healthintel_dbt/models/mdm/mdm_estabelecimento_master.sql`.
- [ ] Criar `healthintel_dbt/models/mdm/xref_estabelecimento_origem.sql`.
- [ ] Usar `stg_cnes_estabelecimento` como fonte principal.
- [ ] Usar CNPJ validado como reforço.
- [ ] Criar `estabelecimento_master_id` (UUID v5).
- [ ] Criar `cnes_canonico` (7 dígitos).
- [ ] Criar `cnpj_canonico`.
- [ ] Criar `razao_social_canonica`.
- [ ] Criar `nome_fantasia_canonico`.
- [ ] Criar `municipio_canonico` (validado contra `ref_municipio_ibge`).
- [ ] Criar `situacao_cnes_canonica`.
- [ ] Criar `mdm_confidence_score`.
- [ ] Criar `mdm_status`.
- [ ] Criar `healthintel_dbt/models/mdm/mdm_estabelecimento_exception.sql`.
- [ ] Criar regra de divergência por CNPJ + CNES + razão social.

### HIS-09.4 — Criar MDM de prestador

- [ ] Criar `healthintel_dbt/models/mdm/mdm_prestador_master.sql`.
- [ ] Criar `healthintel_dbt/models/mdm/xref_prestador_origem.sql`.
- [ ] Usar CNES como origem inicial.
- [ ] Permitir futura origem privada do cliente (placeholder de coluna `tenant_id` nullable).
- [ ] Criar `prestador_master_id`.
- [ ] Criar relacionamento entre prestador e estabelecimento (FK lógica `estabelecimento_master_id`).
- [ ] Criar relacionamento entre prestador e operadora quando existir rede (FK lógica `operadora_master_id`).
- [ ] Criar `healthintel_dbt/models/mdm/mdm_prestador_exception.sql`.
- [ ] Criar regra de duplicidade por CNPJ + município + CNES.
- [ ] Criar regra de divergência por CNPJ + razão social.
- [ ] Documentar campos de exceção: `exception_type`, `exception_severity`, `exception_message`, `is_blocking`.

## Entregas esperadas

- [ ] Pasta `healthintel_dbt/models/mdm/` + `_mdm.yml` + `docs/fase5/mdm_modelagem.md`
- [ ] 3 modelos `mdm_*_master` (operadora, estabelecimento, prestador)
- [ ] 3 modelos `xref_*_origem`
- [ ] 3 modelos `*_exception` (`mdm_operadora_exception`, `mdm_estabelecimento_exception`, `mdm_prestador_exception`)
- [ ] Testes genéricos `unique` e `not_null` em todos os master records
- [ ] Tag dbt `mdm` aplicada

## Validação esperada (hard gates)

- [ ] `dbt build --select tag:mdm` zero erros.
- [ ] `dbt test --select tag:mdm` zero falhas.
- [ ] `int_operadora_canonica.sql` e `dim_operadora_atual.sql` byte-idênticos à tag `v3.0.0`.
- [ ] `mdm_confidence_score` ∈ [0, 100] em 100% dos registros (teste singular).
- [ ] `mdm_status` ∈ accepted_values aprovados.
- [ ] Todas as tabelas `*_exception` públicas têm `exception_type`, `exception_severity`, `exception_message` e `is_blocking`.
- [ ] Cobertura: ≥ 95% das operadoras de `dim_operadora_atual` têm registro em `mdm_operadora_master`.

## Resultado Esperado

Sprint 29 estabelece a camada MDM pública (operadora, estabelecimento, prestador) reaproveitando o que já existe e enriquecendo com validação Serpro para CNPJ. Os `*_master_id` se tornam a chave-âncora dos produtos premium das Sprints 30 e 31, mantendo compatibilidade total com o data warehouse existente.
