# Sprint 21 — Prata Completa

**Status:** Concluída
**Objetivo:** fechar todas as lacunas da camada Prata — cobertura de testes, CNES e TISS na prata, aviso de qualidade no envelope, smoke E2E e documentação de colunas no YAML dbt.
**Critério de saída:** todos os endpoints Prata registrados em `PRATA_DATASETS` cobertos por testes de integração; `make smoke-prata` zero falhas; `api_prata_cnes_*` e `api_prata_tiss_procedimento` servindo dados; `aviso_qualidade` emitido quando `taxa_aprovacao < 0.95`.

## Histórias

### HIS-21.0 — Auditoria de Dependências Prata

- [x] Confirmar existência dos modelos/sources:
  - `stg_ans.stg_cnes_estabelecimento`
  - `stg_ans.stg_tiss_procedimento`
  - modelos `int_ans` derivados de CNES, se utilizados
  - modelos `int_ans` derivados de TISS, se utilizados
- [x] Caso algum source/modelo não exista, decidir explicitamente:
  - criar nesta sprint;
  - usar seed/demo controlado;
  - ou bloquear o endpoint até a dependência existir.
- [x] Registrar no `_prata_api.yml` a origem real de cada modelo Prata.
- [x] Bloquear implementação de modelo `api_prata_*` que dependa de tabela inexistente sem fallback técnico documentado.

### HIS-21.1 — Testes de Integração para todos os Endpoints Dataset

- [x] Expandir `api/tests/integration/test_prata.py` com um teste por endpoint dataset usando padrão `fake_service` (monkeypatch no `buscar_prata`):
  - `test_prata_cadop_retorna_payload`
  - `test_prata_sib_operadora_retorna_payload`
  - `test_prata_sib_municipio_retorna_payload`
  - `test_prata_igr_retorna_payload`
  - `test_prata_nip_retorna_payload`
  - `test_prata_idss_retorna_payload`
  - `test_prata_diops_retorna_payload`
  - `test_prata_fip_retorna_payload`
  - `test_prata_vda_retorna_payload`
  - `test_prata_glosa_retorna_payload`
  - `test_prata_rede_assistencial_retorna_payload`
  - `test_prata_operadora_enriquecida_retorna_payload`
  - `test_prata_municipio_metrica_retorna_payload`
  - `test_prata_financeiro_periodo_retorna_payload`
- [x] Adicionar teste de bloqueio por plano: `test_prata_cadop_plano_piloto_retorna_403` — plano `piloto` não acessa `/v1/prata/*`.
- [x] Adicionar teste de envelope: `test_prata_qualidade_no_meta` — campo `meta.qualidade.taxa_aprovacao` sempre presente.
- [x] Adicionar teste de quarentena dataset: `test_prata_quarentena_dataset_retorna_payload`.
- [x] Padrão de fake_auth compartilhado: extrair `_fake_prata_auth()` em fixture de módulo para evitar duplicação entre testes.

### HIS-21.2 — CNES na Camada Prata

`api_prata_*` são modelos de serving API dos endpoints `/v1/prata/*`. Eles materializam contratos de leitura em `api_ans`, mas não devem usar `api_ans` como source de outro modelo `api_ans`; para CNES, preferir `stg_ans.stg_cnes_estabelecimento` ou modelo `int_ans` derivado, conforme a necessidade de enriquecimento.

- [x] Criar `healthintel_dbt/models/api/prata/api_prata_cnes_municipio.sql`:
  - Source: `stg_ans.stg_cnes_estabelecimento` ou `int_ans` derivado de CNES
  - Materialização: `table`, schema: `api_ans`, tag: `prata`
  - Colunas adicionais de qualidade: `versao_dataset`, `taxa_aprovacao_lote`
  - Post-hook: índice em `competencia` + `cd_municipio`
- [x] Criar `healthintel_dbt/models/api/prata/api_prata_cnes_rede_gap.sql`:
  - Source: `stg_ans.stg_cnes_estabelecimento` ou `int_ans` derivado de CNES
  - Mesma configuração de materialização e qualidade
- [x] Registrar em `healthintel_dbt/models/api/prata/_prata_api.yml`:
  - Descrição, `config`, grão e colunas principais documentados
- [x] Adicionar ao `PRATA_DATASETS` em `api/app/services/prata.py`:
  ```python
  "cnes_municipio": {"tabela": "api_ans.api_prata_cnes_municipio", "competencia": "competencia", "fonte": "cnes_estabelecimento"},
  "cnes_rede_gap": {"tabela": "api_ans.api_prata_cnes_rede_gap", "competencia": "competencia", "fonte": "cnes_estabelecimento"},
  ```
- [x] Adicionar filtros CNES em `PRATA_FILTROS_PERMITIDOS`: `cnes_municipio → {cd_municipio}`, `cnes_rede_gap → {cd_municipio, registro_ans}`.
- [x] Criar endpoints em `api/app/routers/prata.py`:
  - `GET /v1/prata/cnes/municipio` — `Depends(verificar_camada("prata"))`, filtro `cd_municipio`
  - `GET /v1/prata/cnes/rede-gap` — `Depends(verificar_camada("prata"))`, filtro `cd_municipio` + `registro_ans`

### HIS-21.3 — TISS na Camada Prata

`api_prata_tiss_procedimento` segue a mesma regra de serving API: contrato final em `api_ans` para `/v1/prata/*`, com origem em `stg_ans` ou `int_ans`, nunca em outro modelo `api_ans`.

- [x] Criar `healthintel_dbt/models/api/prata/api_prata_tiss_procedimento.sql`:
  - Source: `stg_ans.stg_tiss_procedimento` ou `int_ans` derivado de TISS
  - Materialização: `table`, schema: `api_ans`, tag: `prata`
  - Campo de temporalidade: `trimestre` (não `competencia`)
  - Post-hook: índice em `trimestre` + `registro_ans`
- [x] Registrar em `_prata_api.yml` com grão e colunas documentados.
- [x] Adicionar ao `PRATA_DATASETS`:
  ```python
  "tiss_procedimento": {"tabela": "api_ans.api_prata_tiss_procedimento", "competencia": "trimestre", "fonte": "tiss_procedimento_trimestral"},
  ```
- [x] Adicionar filtros: `tiss_procedimento → {registro_ans, cd_procedimento_tuss}`.
- [x] Criar endpoint `GET /v1/prata/tiss/procedimento` com filtros `registro_ans` e `cd_procedimento_tuss`.

### HIS-21.4 — aviso_qualidade no Envelope Prata

- [x] Adicionar campo `aviso_qualidade: str | None` ao `PrataMetaResponse` em `api/app/schemas/prata.py`.
- [x] Atualizar `buscar_prata()` em `api/app/services/prata.py`: após calcular `_qualidade_prata()`, preencher `aviso_qualidade` quando `taxa_aprovacao < 0.95`:
  ```python
  aviso_qualidade = (
      f"Qualidade abaixo do limiar: {qualidade.taxa_aprovacao:.1%} aprovado "
      f"({qualidade.registros_quarentena} registros em quarentena)"
      if qualidade.taxa_aprovacao < 0.95 else None
  )
  ```
- [x] Incluir `aviso_qualidade` no payload antes de salvar no cache.
- [x] Adicionar teste `test_prata_aviso_qualidade_presente_quando_taxa_baixa` em `test_prata.py`.

### HIS-21.5 — Correção verificar_camada em Quarentena Dataset

- [x] Avaliar e corrigir `GET /v1/prata/quarentena/{dataset}` em `api/app/routers/prata.py`:
  - Atualmente usa `Depends(verificar_camada("bronze"))` — planos apenas-bronze acessam dados de quarentena de prata.
  - Corrigir para `Depends(verificar_camada("prata"))` — acesso à quarentena exige no mínimo plano prata.
- [x] Atualizar teste `test_prata_quarentena_dataset_retorna_payload` para validar plano prata.

### HIS-21.6 — Documentação YAML e dbt Tests na Prata

- [x] Expandir `healthintel_dbt/models/api/prata/_prata_api.yml`: para cada um dos 17 modelos (14 originais + 3 novos), adicionar:
  - `config`: `materialized`, `schema`, `tags`
  - `columns`: ao menos as colunas-chave (`competencia`, `registro_ans` ou equivalente, `taxa_aprovacao_lote`)
  - `tests` genéricos por coluna: `not_null` para chave primária + competência
- [x] Adicionar teste singular `healthintel_dbt/tests/assert_prata_taxa_aprovacao_valida.sql` — `taxa_aprovacao_lote` deve estar entre 0 e 1 em todos os modelos prata.

### HIS-21.7 — Smoke Prata

- [x] Criar `scripts/smoke_prata.py` exercitando:
  - Autenticação com plano `analitico` (HTTP 200 em todos os 17 endpoints)
  - Bloqueio com plano `piloto` (HTTP 403 em `/v1/prata/cadop`)
  - Presença de `meta.qualidade.taxa_aprovacao` na resposta
  - Presença de `meta.competencia` na resposta
  - Quarentena resumo (HTTP 200 com estrutura `dados[].dataset`)
- [x] Adicionar target no Makefile:
  ```makefile
  smoke-prata:
      python scripts/smoke_prata.py
  ```

## Entregas esperadas

- [x] `api/tests/integration/test_prata.py` — 18+ testes (todos os datasets + bloqueio + qualidade + quarentena)
- [x] `healthintel_dbt/models/api/prata/api_prata_cnes_municipio.sql`
- [x] `healthintel_dbt/models/api/prata/api_prata_cnes_rede_gap.sql`
- [x] `healthintel_dbt/models/api/prata/api_prata_tiss_procedimento.sql`
- [x] `api/app/routers/prata.py` com 3 novos endpoints (cnes/municipio, cnes/rede-gap, tiss/procedimento)
- [x] `api/app/services/prata.py` com 3 novos datasets em `PRATA_DATASETS`
- [x] `api/app/schemas/prata.py` com `aviso_qualidade` no envelope
- [x] `healthintel_dbt/tests/assert_prata_taxa_aprovacao_valida.sql`
- [x] `scripts/smoke_prata.py`
- [x] Makefile com target `smoke-prata`

## Validação esperada

- [x] `ruff check api`
- [x] `pytest api/tests/integration/test_prata.py -v` — zero falhas
- [x] `dbt compile --select tag:prata`
- [x] `dbt build --select tag:prata` — sem falhas
- [x] `dbt test --select tag:prata` — sem falhas
- [x] `make smoke-prata` — zero falhas
- [x] Plano `piloto` retorna HTTP 403 em `/v1/prata/*`
- [x] Resposta `/v1/prata/cadop?competencia=202501` contém `meta.aviso_qualidade` quando qualidade < 95%
- [x] Endpoints CNES e TISS prata retornam HTTP 200 com plano `analitico`
/
