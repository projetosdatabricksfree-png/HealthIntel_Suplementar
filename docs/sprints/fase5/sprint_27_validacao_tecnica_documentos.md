# Sprint 27 — Validação Técnica de CPF, CNPJ, CNES e Registro ANS

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.2.0-dq-documental`
**Objetivo:** adicionar validação técnica de documentos sem alterar staging existente.
**Fim esperado:** novas tabelas de qualidade documental consumindo as tabelas aprovadas, com biblioteca Python e macros dbt próprias.
**Critério de saída:** biblioteca Python `healthintel_quality.validators.documentos` com 100% de cobertura unitária; macros dbt novas em `healthintel_dbt/macros/`; tabelas `dq_*` materializadas; `dbt test` zero falhas nos novos `assert_*`.

## Regra-mãe

- [ ] Não alterar `stg_cadop`, `stg_cnes_estabelecimento`, `stg_*` existentes nem a macro `normalizar_registro_ans.sql`.
- [ ] Toda lógica nova entra em arquivos novos.
- [ ] Antes de criar `healthintel_dbt/models/quality/`, configurar `quality` no `healthintel_dbt/dbt_project.yml` com `+schema: quality_ans`, `+materialized: table` e `+tags: ["quality"]`, conforme governança mínima da Sprint 26.
- [ ] Qualquer validação de CPF criada nesta sprint é técnica e reutilizável, mas CPF não pode entrar em produto público derivado da ANS.

## Histórias

### HIS-07.1 — Criar biblioteca Python de documentos

- [ ] Criar `shared/python/healthintel_quality/validators/documentos.py`.
- [ ] Criar função `normalizar_cpf`.
- [ ] Criar função `normalizar_cnpj`.
- [ ] Criar função `validar_cpf_digito`.
- [ ] Criar função `validar_cnpj_digito`.
- [ ] Criar função `classificar_documento` (CPF | CNPJ | INVALIDO).
- [ ] Criar função `gerar_hash_documento` (SHA-256 com salt configurável).
- [ ] Criar bloqueio para sequências inválidas (`00000000000`, `11111111111`, …, `00000000000000`).
- [ ] Criar testes unitários em `testes/unit/test_documentos.py`.
- [ ] Não chamar nenhuma API externa nessa biblioteca.

### HIS-07.2 — Criar macros dbt novas, sem alterar as existentes

- [ ] Criar `healthintel_dbt/macros/normalizar_cnpj.sql`.
- [ ] Criar `healthintel_dbt/macros/normalizar_cpf.sql`.
- [ ] Criar `healthintel_dbt/macros/validar_cnpj_digito.sql`.
- [ ] Criar `healthintel_dbt/macros/validar_cpf_digito.sql`.
- [ ] Criar `healthintel_dbt/macros/normalizar_cnes.sql`.
- [ ] Criar `healthintel_dbt/macros/validar_cnes_formato.sql`.
- [ ] Criar `healthintel_dbt/macros/validar_registro_ans_formato.sql`.
- [ ] Manter `healthintel_dbt/macros/normalizar_registro_ans.sql` intacta.

### HIS-07.3 — Criar tabelas novas de qualidade documental

- [ ] Criar `healthintel_dbt/models/quality/dq_cadop_documento.sql`.
- [ ] Criar `healthintel_dbt/models/quality/dq_cnes_documento.sql`.
- [ ] Criar `healthintel_dbt/models/quality/dq_operadora_documento.sql`.
- [ ] Criar `healthintel_dbt/models/quality/dq_prestador_documento.sql`.
- [ ] Criar coluna `cnpj_normalizado`.
- [ ] Criar coluna `cnpj_tamanho_valido`.
- [ ] Criar coluna `cnpj_digito_valido`.
- [ ] Criar coluna `cnpj_is_sequencia_invalida`.
- [ ] Criar coluna `documento_quality_status` (VALIDO | INVALIDO_FORMATO | INVALIDO_DIGITO | SEQUENCIA_INVALIDA | NULO).
- [ ] Criar coluna `motivo_invalidade_documento`.
- [ ] Criar arquivo de documentação `_quality.yml` com testes `not_null` em chaves e `accepted_values` em `documento_quality_status`.

### HIS-07.4 — Criar testes de qualidade técnica

- [ ] Criar `healthintel_dbt/tests/assert_cnpj_14_digitos_quando_preenchido.sql`.
- [ ] Criar `healthintel_dbt/tests/assert_cnpj_digito_valido_cadop.sql`.
- [ ] Criar `healthintel_dbt/tests/assert_cnpj_digito_valido_cnes.sql`.
- [ ] Criar `healthintel_dbt/tests/assert_cnes_7_digitos.sql`.
- [ ] Criar `healthintel_dbt/tests/assert_registro_ans_6_digitos_em_mdm.sql`.
- [ ] Criar `healthintel_dbt/tests/assert_sem_documento_invalido_em_consumo_premium.sql`.

## Entregas esperadas

- [ ] `shared/python/healthintel_quality/validators/documentos.py` + testes unitários
- [ ] 7 macros novas em `healthintel_dbt/macros/`
- [ ] 4 modelos `dq_*` em `healthintel_dbt/models/quality/`
- [ ] `_quality.yml` com testes genéricos
- [ ] 6 testes singulares `assert_*` na pasta `tests/`
- [ ] `healthintel_dbt/dbt_project.yml` atualizado para o diretório `quality`

## Validação esperada (hard gates)

- [ ] `pytest testes/unit/test_documentos.py -v` — zero falhas, cobertura ≥ 95%.
- [ ] `dbt compile` zero erros.
- [ ] `dbt build --select tag:quality` sucesso.
- [ ] `dbt test --select tag:quality` zero falhas.
- [ ] `stg_cadop`, `stg_cnes_estabelecimento` e `normalizar_registro_ans.sql` permanecem byte-idênticos à tag `v3.0.0`.

## Resultado Esperado

Sprint 27 entrega a primeira camada de qualidade técnica documental da Fase 5. CPF, CNPJ, CNES e registro_ans passam a ter validação digital verdadeira em tabelas `dq_*` paralelas, sem que nenhum modelo aprovado seja tocado. As macros e a biblioteca Python ficam disponíveis como insumo das Sprints 28–31.
