# OBSOLETO — Sprint 28 substituída

Este documento foi substituído por:
`docs/sprints/fase5/sprint_28_validacao_cnpj_offline.md`

A Sprint 28 não usa Serpro, Receita online, BrasilAPI, cache externo, provider Python ou schema enrichment. A validação de CNPJ é 100% offline, determinística e sem dependência externa.

---

(Conteúdo original preservado como referência histórica. Nenhuma seção abaixo tem valor normativo.)

# Sprint 28 — Validação Oficial CNPJ Serpro com Cache e Auditoria

**Status:** Roadmap — não iniciada. Nenhum artefato físico desta sprint existe no repositório (verificado: `shared/python/healthintel_quality/integrations/` ausente; `healthintel_dbt/models/enrichment/` ausente; `infra/postgres/init/026_fase5_quality_enrichment_mdm.sql` ausente; tabela `enrichment.documento_receita_cache` inexistente).
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate.
**Tag de saída prevista:** `v3.3.0-serpro-cnpj` (somente após hardgates verdes).
**Pré-requisito:** Sprint 27 com hardgates verdes (`v3.2.0-dq-documental`). A Sprint 28 consome `quality_ans.dq_cadop_documento` e `quality_ans.dq_cnes_documento` para filtrar entrada antes de gastar quota Serpro.
**Baseline congelado:** `v3.0.0` (commit `fe7b839`). **Não alterado por esta sprint.**
**Schemas novos:** `enrichment` (cache externo) e `plataforma` recebe a tabela nova `plataforma.log_enriquecimento` (auditoria de chamadas).
**Objetivo:** consultar fonte oficial de CNPJ (Serpro) sem quebrar o build dbt, sem scraping e sem chamada externa dentro do `dbt build`.
**Fim esperado:** CNPJs públicos de CADOP/CNES validados contra Receita Federal via processo Python controlado, com cache persistente, auditoria, mascaramento de logs e nenhuma chamada HTTP dentro do grafo dbt.
**Critério de saída técnico:** cliente Python configurável `SerproCnpjProvider` + `MockCnpjProvider` com testes; tabela `enrichment.documento_receita_cache` populada por job dedicado; modelos dbt `int_*_receita*` e `dim_documento_validado` materializados em `enrichment`; nenhum modelo dbt invoca chamada HTTP externa (verificado por inspeção e por busca textual de `requests`/`http` em `models/`).
**Critério de saída operacional:** `pytest testes/unit/test_serpro_cnpj_client.py -v` zero falhas; `make enrich-cnpj` (modo Mock) popula cache; `dbt build --select tag:enrichment` zero erros; `dbt test --select tag:enrichment` zero falhas; diff contra `v3.0.0` mostra zero alteração em `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*`; `grep -R "requests\|httpx\|urlopen" healthintel_dbt/models/` retorna vazio.

## Regra-mãe (não negociável)

- [ ] Nenhum modelo dbt pode chamar API externa (proibido `requests`, `httpx`, `urlopen`, macros que executem HTTP, hooks que consultem rede). dbt permanece **determinístico e offline**.
- [ ] Cache vive em schema separado `enrichment` (criar via `infra/postgres/init/026_fase5_quality_enrichment_mdm.sql`). Não alterar `plataforma.*` existente nem `bruto_ans.*`.
- [ ] Logs e payloads não podem expor CNPJ completo em texto claro — apenas máscara (`12.345.***/***-**`) e hash (`sha256(documento_normalizado || salt)`).
- [ ] CPF não é entrada, saída, cache, dimensão ou log desta sprint. Filtrar antes de qualquer chamada Serpro.
- [ ] Nenhum cliente comercial enxerga `enrichment.*`. Schema é interno; sem grants para `healthintel_cliente_reader` nem para `healthintel_premium_reader`.
- [ ] `make enrich-cnpj` é idempotente: rerun sem alterar TTL não deve consumir quota Serpro novamente.
- [ ] Quota e rate limit Serpro são respeitados via token bucket em processo, não por tentativa-e-erro.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Enriquecimento externo controlado (CNPJ via Receita/Serpro). |
| Schemas físicos | `enrichment` (cache, modelos dbt de enriquecimento); `plataforma.log_enriquecimento` (auditoria). |
| Tag dbt | `enrichment` (e tags secundárias por domínio: `documento`, `cnpj`, `cadop`, `cnes`). |
| Materialização | `table` para `dim_documento_validado` e `int_*_receita`; `view` ou `ephemeral` quando puro reaproveitamento. |
| Upstream permitido | `enrichment.documento_receita_cache` (preenchido fora do dbt), `quality_ans.dq_cadop_documento`, `quality_ans.dq_cnes_documento`, `stg_cadop`, `stg_cnes_estabelecimento`, `dim_operadora_atual`. |
| Downstream esperado | Sprint 29 (`mdm_operadora_master`/`mdm_estabelecimento_master` consomem `is_cnpj_ativo_receita`); Sprint 31 (produtos premium derivados); Sprint 32 (endpoints premium opcionalmente expõem flag agregada). |
| Owner técnico | Engenharia de dados HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Classificação LGPD | Pública ANS/DATASUS (CNPJ, razão social, CNAE, situação cadastral) + Interna operacional (hash, mascarado, payload, status, timestamps). **CPF proibido.** |
| Regra de publicação | Interna apenas. Nenhum `enrichment.*` é exposto via FastAPI ou via `consumo_ans`/`consumo_premium_ans`. Exposição futura ocorre apenas como flag derivada em `api_ans.api_premium_*`, sem expor `payload_resumido_json`. |
| Regra de teste | `pytest` no cliente Python (com `MockCnpjProvider`); `dbt test` em `enrichment/_enrichment.yml`; smoke local de `make enrich-cnpj`; verificação de mascaramento de log. |
| Regra de rollback | `drop schema enrichment cascade`, `drop table plataforma.log_enriquecimento`, remoção dos arquivos novos. Baseline `v3.0.0` e Sprint 27 permanecem intactos. |

## Estado Atual vs Estado-Alvo

| Aspecto | Estado Atual (`HEAD`) | Estado-Alvo (`v3.3.0-serpro-cnpj`) |
|---------|------------------------|------------------------------------|
| Validação de CNPJ | Apenas técnica (dígito verificador) via `quality_ans.dq_*_documento` (Sprint 27). | Técnica + oficial (Receita), com `situacao_cadastral`, `razao_social_receita`, `cnae_principal`. |
| Schema `enrichment` | Inexistente. | Criado por `026_fase5_quality_enrichment_mdm.sql`, com `documento_receita_cache` + 4 modelos dbt. |
| Cliente Python externo | Inexistente. | `SerproCnpjProvider` (real) + `MockCnpjProvider` (testes), interface `CnpjProvider`. |
| Auditoria de chamadas externas | Inexistente. | `plataforma.log_enriquecimento` registra hash, status, latência, fonte. |
| Risco de scraping | N/A — sem chamadas externas. | Mitigado: token bucket, retry com backoff, TTL de cache, `MockCnpjProvider` em CI. |
| Comportamento dentro de `dbt build` | Determinístico e offline. | **Permanece determinístico e offline.** O job de enriquecimento roda fora do dbt. |

## Tabela `enrichment.documento_receita_cache` (contrato de coluna)

| Coluna | Tipo | Obrigatório | Classificação LGPD | Regra |
|--------|------|-------------|--------------------|-------|
| `documento_hash` | `text` (PK) | Sim | Interna operacional | `sha256(documento_normalizado || env('HEALTHINTEL_DOCUMENTO_HASH_SALT'))`. |
| `documento_tipo` | `text` | Sim | Interna operacional | `accepted_values = ['CNPJ']` nesta sprint. CPF proibido. |
| `documento_normalizado_mascarado` | `text` | Sim | Pública (mascarada) | Formato `12.345.***/***-**`. **Nunca** o documento completo. |
| `fonte_validacao` | `text` | Sim | Interna operacional | `accepted_values = ['SERPRO','MOCK','MANUAL_IMPORT']`. |
| `situacao_cadastral` | `text` | Não | Pública ANS/DATASUS | Domínio Receita: `ATIVA`, `BAIXADA`, `SUSPENSA`, `INAPTA`, `NULA`. |
| `razao_social_receita` | `text` | Não | Pública ANS/DATASUS | String oficial; comparada com nome ANS via `nome_divergente_receita`. |
| `nome_fantasia_receita` | `text` | Não | Pública ANS/DATASUS | Pode ser `NULL` se Receita não traz. |
| `cnae_principal` | `text` | Não | Pública ANS/DATASUS | Código CNAE 7 dígitos. |
| `natureza_juridica` | `text` | Não | Pública ANS/DATASUS | Código + descrição. |
| `dt_consulta` | `timestamptz` | Sim | Interna operacional | UTC. Insumo para TTL de cache. |
| `payload_resumido_json` | `jsonb` | Sim | Interna operacional | **Apenas campos necessários**; sem CPF de sócio, sem endereço completo, sem telefone. |
| `validacao_status` | `text` | Sim | Interna operacional | `accepted_values = ['ATIVO','INATIVO','NAO_ENCONTRADO','ERRO']`. |
| `_lote_enriquecimento` | `text` | Sim | Interna operacional | Identificador do lote do `make enrich-cnpj`. |

Índices obrigatórios: `(documento_hash)`, `(dt_consulta DESC)`, `(validacao_status)`, `(_lote_enriquecimento)`.

## Tabela `plataforma.log_enriquecimento` (auditoria)

| Coluna | Tipo | Obrigatório | Regra |
|--------|------|-------------|-------|
| `id` | `bigserial` (PK) | Sim | — |
| `dt_evento` | `timestamptz` | Sim | UTC. |
| `fonte` | `text` | Sim | `SERPRO` ou `MOCK`. |
| `documento_hash` | `text` | Sim | Mesmo hash do cache. |
| `http_status` | `int` | Não | Se chamada falhou antes de status, registrar `NULL`. |
| `latencia_ms` | `int` | Não | Tempo total da chamada. |
| `validacao_status` | `text` | Sim | Domínio do cache. |
| `erro_classe` | `text` | Não | `TIMEOUT`, `RATE_LIMITED`, `AUTH`, `SERVER_5XX`, `PAYLOAD_INVALIDO`. |
| `_lote_enriquecimento` | `text` | Sim | Casamento com `documento_receita_cache`. |

Esta tabela é a **base contábil** de eventual cobrança/relatório de uso da quota Serpro e fonte para alertas operacionais (skill `healthintel-observability-billing-ops`).

## Histórias

### HIS-08.1 — Cliente Python CNPJ

Local previsto: `shared/python/healthintel_quality/integrations/serpro_cnpj_client.py`.

- [ ] Criar arquivo `shared/python/healthintel_quality/integrations/__init__.py`.
- [ ] Criar `shared/python/healthintel_quality/integrations/serpro_cnpj_client.py`.
- [ ] Definir interface `CnpjProvider` (Protocol/ABC) com `consultar(documento: str) -> CnpjReceitaResultado`.
- [ ] Implementar `SerproCnpjProvider` (config via env: `SERPRO_BASE_URL`, `SERPRO_CONSUMER_KEY`, `SERPRO_CONSUMER_SECRET`, `SERPRO_TIMEOUT_SECONDS`).
- [ ] Implementar `MockCnpjProvider` para testes locais e CI (sem rede).
- [ ] Implementar timeout configurável (default 10s).
- [ ] Implementar retry com backoff exponencial (1s, 2s, 4s; máx 3 tentativas).
- [ ] Implementar rate limit (token bucket configurável; default 60 req/min).
- [ ] Tratamento explícito por status HTTP: 401/403 → `AUTH`; 404 → `NAO_ENCONTRADO`; 429 → `RATE_LIMITED` (espera + retry); 5xx → `SERVER_5XX` (retry); timeout → `TIMEOUT`.
- [ ] Logs estruturados (structlog) **sem** CNPJ em texto claro — apenas hash + máscara.
- [ ] Testes em `testes/unit/test_serpro_cnpj_client.py` cobrindo: contrato da interface, retry, rate limit, mascaramento de log, todos os caminhos de erro.

### HIS-08.2 — Bootstrap PostgreSQL `enrichment`

Local previsto: `infra/postgres/init/026_fase5_quality_enrichment_mdm.sql`.

- [ ] Criar `CREATE SCHEMA IF NOT EXISTS enrichment;`.
- [ ] Criar tabela `enrichment.documento_receita_cache` com colunas e índices descritos no contrato acima.
- [ ] Criar `CHECK (documento_tipo = 'CNPJ')` na sprint atual (relaxar em sprint posterior se necessário).
- [ ] Criar tabela `plataforma.log_enriquecimento` com schema acima (sprint pode adicionar índice em `dt_evento`).
- [ ] **Revogar explicitamente** grants em `enrichment` para `healthintel_cliente_reader` e `healthintel_premium_reader`.
- [ ] Validar que script é idempotente (`IF NOT EXISTS` em todos os DDL).

### HIS-08.3 — Job de enriquecimento CNPJ

Local previsto: `scripts/enrichment/enriquecer_cnpj_receita.py`.

- [ ] Criar diretório `scripts/enrichment/` e `__init__.py`.
- [ ] Criar `scripts/enrichment/enriquecer_cnpj_receita.py`.
- [ ] Buscar CNPJs distintos de `quality_ans.dq_cadop_documento` filtrando `documento_quality_status = 'VALIDO'` (não gastar quota em CNPJ inválido).
- [ ] Buscar CNPJs distintos de `quality_ans.dq_cnes_documento` filtrando `documento_quality_status = 'VALIDO'`.
- [ ] Aplicar TTL configurável (default 30 dias) — só consulta CNPJ sem cache válido.
- [ ] Selecionar provider via env (`HEALTHINTEL_CNPJ_PROVIDER=SERPRO|MOCK`); CI usa `MOCK`.
- [ ] Atualizar `enrichment.documento_receita_cache` (upsert por `documento_hash`).
- [ ] Inserir uma linha em `plataforma.log_enriquecimento` por chamada.
- [ ] Gerar relatório de falhas em `reports/enrichment/falhas_{lote}.csv` (sem CNPJ em texto claro — apenas máscara + hash + erro_classe).
- [ ] **Garantir** que script nunca é importado por modelo dbt (ausência de import em `healthintel_dbt/`).
- [ ] Adicionar alvo `enrich-cnpj` em `Makefile` chamando `python scripts/enrichment/enriquecer_cnpj_receita.py --lote $$(date +%Y%m%d%H%M)`.
- [ ] Criar DAG opcional `ingestao/dags/dag_enriquecer_cnpj_receita.py` (cadência semanal, `schedule_interval='0 3 * * 1'`, sem chamadas dentro de tarefas dbt).

### HIS-08.4 — Modelos dbt de enriquecimento

Local previsto: `healthintel_dbt/models/enrichment/`.

- [ ] Adicionar bloco `enrichment` em `dbt_project.yml` conforme `governanca_minima_fase5.md` (`+schema: enrichment`, `+materialized: table`, `+tags: ["enrichment"]`).
- [ ] Criar `int_cnpj_receita_validado.sql` — junta `enrichment.documento_receita_cache` com `quality_ans.dq_*_documento` para gerar coluna `is_cnpj_ativo_receita` e `fonte_documento_status`.
- [ ] Criar `dim_documento_validado.sql` — dimensão consolidada por `documento_hash` (uma linha por documento ativo conhecido na cache válida).
- [ ] Criar `int_cadop_cnpj_receita.sql` — projeção CADOP × cache, com flags `is_cnpj_receita_encontrado`, `is_cnpj_ativo_receita`, `nome_divergente_receita`.
- [ ] Criar `int_cnes_cnpj_receita.sql` — projeção CNES × cache, com as mesmas flags.
- [ ] Documentar no `_enrichment.yml`:
  - `not_null` em chaves (`documento_hash`, `documento_tipo`, `dt_consulta`, `validacao_status`).
  - `accepted_values` em `fonte_validacao` (`['SERPRO','MOCK','MANUAL_IMPORT']`), `validacao_status` (`['ATIVO','INATIVO','NAO_ENCONTRADO','ERRO']`), `documento_tipo` (`['CNPJ']`).
  - `unique` em `dim_documento_validado.documento_hash`.
  - `relationships` quando aplicável (`int_cadop_cnpj_receita.documento_hash` → `enrichment.documento_receita_cache.documento_hash`).
- [ ] Criar testes singulares `tests/assert_enrichment_sem_cpf.sql` (zero linhas com `documento_tipo = 'CPF'`), `tests/assert_enrichment_sem_documento_em_claro.sql` (validação que `documento_normalizado_mascarado` contém `***`).
- [ ] Tag em todos: `enrichment`. Tags secundárias `documento`, `cnpj`, `cadop`, `cnes` conforme caso.

### HIS-08.5 — Não regressão e isolamento

- [ ] Diff contra `v3.0.0` em `healthintel_dbt/models/{staging,intermediate,marts,api,consumo}/` deve ser **vazio**.
- [ ] Diff contra `v3.0.0` em `healthintel_dbt/macros/` deve ser **vazio** (Sprint 28 não cria macros novas; usa apenas a biblioteca Python externa).
- [ ] `grep -R "requests\|httpx\|urlopen\|http_get" healthintel_dbt/models/ healthintel_dbt/macros/` deve retornar vazio.
- [ ] Sprint 27 (`v3.2.0-dq-documental`) permanece intacta — diff em `healthintel_dbt/models/quality/` e `shared/python/healthintel_quality/validators/` deve ser **vazio** após esta sprint.

## Entregas esperadas

| Entrega | Caminho | Tipo |
|---------|---------|------|
| Cliente Python | `shared/python/healthintel_quality/integrations/serpro_cnpj_client.py` | novo |
| Testes | `testes/unit/test_serpro_cnpj_client.py` | novo |
| Bootstrap SQL | `infra/postgres/init/026_fase5_quality_enrichment_mdm.sql` | novo |
| Job de enriquecimento | `scripts/enrichment/enriquecer_cnpj_receita.py` | novo |
| Makefile target | `enrich-cnpj` | adição |
| DAG opcional | `ingestao/dags/dag_enriquecer_cnpj_receita.py` | novo |
| Modelos dbt | `healthintel_dbt/models/enrichment/{int_cnpj_receita_validado,dim_documento_validado,int_cadop_cnpj_receita,int_cnes_cnpj_receita}.sql` | novos |
| YAML | `healthintel_dbt/models/enrichment/_enrichment.yml` | novo |
| Testes singulares | `healthintel_dbt/tests/assert_enrichment_sem_cpf.sql`, `assert_enrichment_sem_documento_em_claro.sql` | novos |
| Auditoria | `plataforma.log_enriquecimento` | tabela nova |

## Validação esperada (hard gates)

Cada item exige evidência objetiva (commit/SHA, output de comando, log de execução) antes de virar `[x]`.

- [ ] `pytest testes/unit/test_serpro_cnpj_client.py -v --cov=healthintel_quality.integrations.serpro_cnpj_client --cov-report=term-missing` zero falhas, cobertura ≥ 90%.
- [ ] `make enrich-cnpj` em ambiente local com `HEALTHINTEL_CNPJ_PROVIDER=MOCK` popula `enrichment.documento_receita_cache` e `plataforma.log_enriquecimento`.
- [ ] `dbt deps && dbt compile` zero erros após adicionar bloco `enrichment` em `dbt_project.yml`.
- [ ] `dbt build --select tag:enrichment` zero erros.
- [ ] `dbt test --select tag:enrichment` zero falhas (incluindo `assert_enrichment_sem_cpf.sql`).
- [ ] Inspeção manual: `grep -R "requests\|httpx\|urlopen" healthintel_dbt/` retorna vazio.
- [ ] Inspeção manual: log de execução do `make enrich-cnpj` não contém CNPJ em texto claro (apenas hash + máscara).
- [ ] `psql -c "select count(*) from enrichment.documento_receita_cache where documento_tipo = 'CPF';"` retorna `0`.
- [ ] `psql -c "select count(*) from enrichment.documento_receita_cache where documento_normalizado_mascarado !~ E'\\*'"` retorna `0`.
- [ ] `psql -c "\\dp enrichment.documento_receita_cache"` mostra zero grants para `healthintel_cliente_reader` e `healthintel_premium_reader`.
- [ ] `git diff --stat v3.0.0 -- healthintel_dbt/models/{staging,intermediate,marts,api,consumo} healthintel_dbt/macros` retorna vazio.
- [ ] Reexecução de `make enrich-cnpj` dentro do TTL não emite chamada Serpro (verificável em `plataforma.log_enriquecimento`).
- [ ] Tag `v3.3.0-serpro-cnpj` aplicada **somente** após todos os itens acima verdes.

## Comandos de validação local

```bash
# 1. Lint Python
make lint

# 2. Testes unitários do cliente
PYTHONPATH=shared/python pytest testes/unit/test_serpro_cnpj_client.py -v \
  --cov=healthintel_quality.integrations.serpro_cnpj_client \
  --cov-report=term-missing

# 3. Bootstrap do schema (idempotente)
psql -h localhost -U postgres -d healthintel \
  -f infra/postgres/init/026_fase5_quality_enrichment_mdm.sql

# 4. Job de enriquecimento em modo Mock (CI-safe)
HEALTHINTEL_CNPJ_PROVIDER=MOCK make enrich-cnpj

# 5. dbt enrichment
cd healthintel_dbt && dbt deps && dbt compile
cd healthintel_dbt && dbt build --select tag:enrichment
cd healthintel_dbt && dbt test --select tag:enrichment

# 6. Não regressão contra baseline
git diff --stat v3.0.0 -- \
  healthintel_dbt/models/staging \
  healthintel_dbt/models/intermediate \
  healthintel_dbt/models/marts \
  healthintel_dbt/models/api \
  healthintel_dbt/models/consumo \
  healthintel_dbt/macros

# 7. Garantia de offline em dbt
grep -R "requests\|httpx\|urlopen\|http_get" healthintel_dbt/

# 8. Verificação de proteção comercial
psql -c "select count(*) from enrichment.documento_receita_cache where documento_tipo = 'CPF';"
psql -c "\\dp enrichment.documento_receita_cache"
psql -c "\\dp plataforma.log_enriquecimento"
```

## Anti-padrões rejeitados (com justificativa por skill)

| Anti-padrão | Skill violada | Por que está proibido |
|-------------|---------------|------------------------|
| Chamar Serpro dentro de macro/post-hook dbt. | `dbt-medallion-modeling`, `data-quality-contracts` | Quebra determinismo do build, gasta quota em CI, expõe segredos no profile dbt. |
| Logar CNPJ em texto claro em `plataforma.log_enriquecimento` ou em stdout. | `commercial-protection-security`, `observability-billing-ops` | Vazamento desnecessário; auditoria deve operar com hash + máscara. |
| Cachear CPF no `documento_receita_cache`. | `daas-governance`, `data-quality-contracts` | CPF está fora do produto público derivado da ANS; entra somente em fluxo privado tenant em sprint posterior. |
| `GRANT SELECT ON enrichment.* TO healthintel_cliente_reader`. | `commercial-protection-security` | Cliente nunca acessa schema interno; cache de enriquecimento não é produto. |
| Endpoint FastAPI lendo `enrichment.documento_receita_cache` direto. | `api-serving`, `dbt-medallion-modeling` | API consome só `api_ans`. Exposição futura é via `api_premium_*` com flag derivada, sem expor `payload_resumido_json`. |
| Reprocessar todos os CNPJs todo run, ignorando TTL. | `observability-billing-ops` | Quota Serpro é cara; `make enrich-cnpj` é idempotente por design. |
| Reabrir `v3.0.0` para "limpar bruto_ans" enquanto adiciona `enrichment`. | `sprint-release-hardgates` | Fase 5 é aditiva; baseline congelado. |
| Tratar `NAO_ENCONTRADO` como `ERRO` (ou inverso). | `data-quality-contracts` | Os quatro estados (`ATIVO`/`INATIVO`/`NAO_ENCONTRADO`/`ERRO`) são distintos e contam diferente em downstream MDM. |
| Carregar CNPJ inválido no Serpro "para confirmar que é inválido". | `observability-billing-ops`, `data-quality-contracts` | Filtragem prévia por `quality_ans.dq_*_documento` é obrigatória. |

## Pendências e riscos

- Quota e custo Serpro precisam ser dimensionados antes de execução em produção (estimativa: ~1.500 CNPJs distintos em CADOP × ~7.000 CNES = ordem de 10⁴ chamadas iniciais; depois apenas delta sobre TTL).
- Credenciais Serpro (`SERPRO_CONSUMER_KEY`/`SECRET`) precisam de cofre — não checar no `.env` versionado.
- Política de TTL deve ser revisitada em Sprint 31 com base em volume real de divergência ANS × Receita.
- Em caso de Serpro indisponível por janela longa, `MOCK`/`MANUAL_IMPORT` permitem operação degradada documentada em `plataforma.log_enriquecimento` (sem reincidência silenciosa de cache antigo).
- Não criar nenhuma rota FastAPI nesta sprint — exposição (se houver) é decisão da Sprint 31/32.

## Resultado Esperado

Sprint 28 entrega validação oficial de CNPJ com isolamento total entre o pipeline dbt (que continua determinístico e offline) e o processo de enriquecimento externo (Python + cache + auditoria). A coluna `is_cnpj_ativo_receita` passa a ser insumo confiável para os MDMs das Sprints 29 e 30 e para os produtos premium da Sprint 31. Nenhum cliente comercial vê `enrichment.*`, nenhum log expõe CNPJ em texto claro, e nenhum modelo dbt faz chamada externa.