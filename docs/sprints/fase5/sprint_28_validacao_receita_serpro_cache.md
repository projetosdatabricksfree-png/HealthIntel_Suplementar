# Sprint 28 — Validação Oficial Receita/Serpro com Cache e Auditoria

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.3.0-receita`
**Objetivo:** consultar fonte oficial (Receita/Serpro) sem quebrar dbt, sem scraping e sem chamada externa dentro do build.
**Fim esperado:** CNPJ/CPF validados contra fonte externa via processo Python controlado, com cache persistente e auditoria.
**Critério de saída:** cliente Python configurável `SerproCnpjProvider` + `MockCnpjProvider` com testes; tabela `enrichment.documento_receita_cache` populada por job dedicado; modelos dbt `int_*_receita*` e `dim_documento_validado` materializados; nenhum modelo dbt invoca chamada HTTP externa.

## Contexto técnico

A validação oficial de CNPJ deve ser feita por integração controlada (gov.br/Serpro). Para CPF, existe solução digital de consulta cadastral, mas CPF deve ser tratado como dado pessoal e só pode entrar em fluxo privado/tenant — nunca em produto público derivado da ANS.

## Regra-mãe

- [ ] Nenhum modelo dbt pode chamar API externa.
- [ ] Cache vive em schema separado `enrichment` (criar via migration nova, não alterar `plataforma` nem `bruto_ans`).
- [ ] Logs e payloads não podem expor CPF/CNPJ completo em texto claro — apenas mascarado e hash.

## Histórias

### HIS-08.1 — Criar cliente Python CNPJ

- [ ] Criar `shared/python/healthintel_quality/integrations/serpro_cnpj_client.py`.
- [ ] Criar interface `CnpjProvider` (Protocol/ABC).
- [ ] Criar provider `SerproCnpjProvider`.
- [ ] Criar provider `MockCnpjProvider` para testes locais.
- [ ] Criar controle de timeout configurável.
- [ ] Criar retry com backoff exponencial.
- [ ] Criar rate limit (token bucket).
- [ ] Criar tratamento de erro por status HTTP (401, 403, 404, 429, 5xx).
- [ ] Criar logs sem expor CNPJ completo (mascarar últimos 8 dígitos).
- [ ] Criar testes em `testes/unit/test_serpro_cnpj_client.py` usando o `MockCnpjProvider`.

### HIS-08.2 — Criar cache oficial de documentos

- [ ] Criar migration nova para schema `enrichment` em `infra/migrations/`.
- [ ] Criar tabela `enrichment.documento_receita_cache`.
- [ ] Criar campo `documento_hash` (PK).
- [ ] Criar campo `documento_tipo` (CNPJ | CPF).
- [ ] Criar campo `documento_normalizado_mascarado`.
- [ ] Criar campo `fonte_validacao` (SERPRO | RECEITA_PUBLICA | MOCK).
- [ ] Criar campo `situacao_cadastral`.
- [ ] Criar campo `razao_social_receita`.
- [ ] Criar campo `nome_fantasia_receita`.
- [ ] Criar campo `cnae_principal`.
- [ ] Criar campo `natureza_juridica`.
- [ ] Criar campo `dt_consulta` (timestamp).
- [ ] Criar campo `payload_resumido_json` (jsonb).
- [ ] Criar campo `validacao_status` (ATIVO | INATIVO | NAO_ENCONTRADO | ERRO).
- [ ] Criar índices em `documento_hash` e `dt_consulta`.

### HIS-08.3 — Criar job de enriquecimento CNPJ

- [ ] Criar `scripts/enrichment/enriquecer_cnpj_receita.py`.
- [ ] Buscar CNPJs distintos de `stg_cadop`.
- [ ] Buscar CNPJs distintos de `stg_cnes_estabelecimento`.
- [ ] Ignorar CNPJs tecnicamente inválidos (consumindo `dq_*_documento` da Sprint 27).
- [ ] Consultar somente CNPJs sem cache válido (TTL configurável).
- [ ] Atualizar cache.
- [ ] Gerar log de auditoria em `plataforma.log_enriquecimento` (tabela nova).
- [ ] Gerar relatório de falhas em `reports/enrichment/falhas_{timestamp}.csv`.
- [ ] Garantir que NUNCA é executado dentro de `dbt build`.
- [ ] Criar `make enrich-cnpj` no Makefile.
- [ ] Criar DAG opcional `dag_enriquecer_cnpj_receita.py` (cadência semanal).

### HIS-08.4 — Criar modelos dbt de enriquecimento

- [ ] Criar `healthintel_dbt/models/enrichment/int_cnpj_receita_validado.sql`.
- [ ] Criar `healthintel_dbt/models/enrichment/dim_documento_validado.sql`.
- [ ] Criar `healthintel_dbt/models/enrichment/int_cadop_cnpj_receita.sql`.
- [ ] Criar `healthintel_dbt/models/enrichment/int_cnes_cnpj_receita.sql`.
- [ ] Criar coluna `is_cnpj_receita_encontrado`.
- [ ] Criar coluna `is_cnpj_ativo_receita`.
- [ ] Criar coluna `nome_divergente_receita` (compara nome ANS x nome Receita).
- [ ] Criar coluna `fonte_documento_status`.
- [ ] Documentar no `_enrichment.yml` com testes `not_null` em chaves e `accepted_values` em `fonte_documento_status`.

## Entregas esperadas

- [ ] `shared/python/healthintel_quality/integrations/serpro_cnpj_client.py` + testes
- [ ] Migration `enrichment` schema + tabela `documento_receita_cache`
- [ ] `scripts/enrichment/enriquecer_cnpj_receita.py` + Makefile + DAG opcional
- [ ] 4 modelos dbt em `healthintel_dbt/models/enrichment/`
- [ ] `_enrichment.yml` com testes genéricos
- [ ] `plataforma.log_enriquecimento` (tabela nova de auditoria)

## Validação esperada (hard gates)

- [ ] `pytest testes/unit/test_serpro_cnpj_client.py -v` zero falhas.
- [ ] `make enrich-cnpj` (ambiente local) popula cache com `MockCnpjProvider`.
- [ ] `dbt build --select tag:enrichment` zero erros.
- [ ] `dbt test --select tag:enrichment` zero falhas.
- [ ] Inspeção manual: nenhum modelo dbt importa biblioteca de rede ou faz `http_get`.
- [ ] Logs do job não contêm CNPJ em texto claro.

## Resultado Esperado

Sprint 28 entrega validação oficial de CNPJ com isolamento total entre o pipeline dbt (que continua determinístico e offline) e o processo de enriquecimento externo (Python + cache). A coluna `is_cnpj_ativo_receita` passa a ser insumo confiável para os MDMs das Sprints 29 e 30 e para os produtos premium da Sprint 31.
