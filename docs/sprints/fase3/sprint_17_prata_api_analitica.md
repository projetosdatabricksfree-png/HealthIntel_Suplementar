# Sprint 17 — Prata API Analítica

**Status:** Não iniciada
**Objetivo:** expor a camada prata (`stg_ans` padronizado + `int_ans` enriquecido) via API REST com garantias de tipagem e qualidade; restrita ao plano `analitico` e superiores; visibilidade da quarentena no envelope de metadados.
**Critério de saída:** endpoints prata respondendo com tipagem garantida e metadados de qualidade; plano `analitico` funcionando; endpoints de quarentena operacionais.

## Histórias

### HIS-17.1 — Modelos dbt Prata API

- [ ] Criar pasta `healthintel_dbt/models/api/prata/`.
- [ ] Camada prata entrada — materializar como tabela em `api_ans` a partir de `stg_ans`:
  - `api_prata_cadop.sql` (de `stg_cadop`)
  - `api_prata_sib_operadora.sql`
  - `api_prata_sib_municipio.sql`
  - `api_prata_igr.sql`
  - `api_prata_nip.sql`
  - `api_prata_idss.sql`
  - `api_prata_diops.sql`
  - `api_prata_fip.sql`
  - `api_prata_vda.sql`
  - `api_prata_glosa.sql`
  - `api_prata_rede_assistencial.sql`
- [ ] Camada prata saída — enriquecida a partir de `int_ans`:
  - `api_prata_operadora_enriquecida.sql` (de `int_operadora_canonica` + `int_crescimento_operadora_12m`)
  - `api_prata_municipio_metrica.sql` (de `int_metrica_municipio`)
  - `api_prata_financeiro_periodo.sql` (de `int_financeiro_operadora_periodo`)
- [ ] Configuração: `materialized: table`, `schema: api_ans`, tag `prata`. Post-hook: índices em `competencia` + chave principal.
- [ ] Incluir colunas derivadas de qualidade: `taxa_aprovacao_lote` (calculada via subquery sobre `*_quarentena`).
- [ ] Documentar em `healthintel_dbt/models/api/prata/_prata_api.yml`.

### HIS-17.2 — Router FastAPI Prata

- [ ] Criar `api/app/routers/prata.py` com endpoints por dataset:
  - `GET /v1/prata/cadop`
  - `GET /v1/prata/sib/operadora`
  - `GET /v1/prata/sib/municipio`
  - `GET /v1/prata/igr`
  - `GET /v1/prata/nip`
  - `GET /v1/prata/idss`
  - `GET /v1/prata/diops`
  - `GET /v1/prata/fip`
  - `GET /v1/prata/vda`
  - `GET /v1/prata/glosa`
  - `GET /v1/prata/rede-assistencial`
  - `GET /v1/prata/operadora/enriquecida`
  - `GET /v1/prata/municipio/metrica`
  - `GET /v1/prata/financeiro/periodo`
- [ ] Endpoint de visibilidade de quarentena:
  - `GET /v1/prata/quarentena/resumo` — agregado por dataset + competência
  - `GET /v1/prata/quarentena/{dataset}` — registros rejeitados por dataset (restrito a `enterprise_tecnico`)
- [ ] Filtros: `competencia` obrigatório, `registro_ans` opcional para datasets de operadora.
- [ ] Registrar router em `api/app/main.py` com prefixo `/v1/prata`.

### HIS-17.3 — Schemas Pydantic Prata

- [ ] Criar `api/app/schemas/prata.py`.
- [ ] Envelope prata com metadados de qualidade:
  ```python
  class PrataQualidadeMeta(BaseModel):
      taxa_aprovacao: float          # proporção aprovada vs. bronze
      registros_quarentena: int
      motivos_rejeicao: list[str]    # top motivos por lote

  class PrataMetaResponse(BaseModel):
      fonte: str
      competencia: str
      versao_dataset: str
      qualidade: PrataQualidadeMeta
      total: int
      pagina: int

  class PrataResponse(BaseModel):
      dados: list[dict]
      meta: PrataMetaResponse
  ```
- [ ] Schemas tipados por dataset (registro_ans str, competencia str YYYYMM, etc.) como alternativa a `list[dict]` para os 3 datasets enriquecidos.

### HIS-17.4 — Plano `analitico` e `tecnico`

- [ ] Criar planos formalizados em `plataforma.plano` via seed ou migration:
  - `analitico`: `camadas_permitidas = ['ouro', 'prata']`, rate limit 5.000 req/h, SLA p95 < 200ms
  - `tecnico` (alias para `plus`): `camadas_permitidas = ['ouro', 'prata']`, rate limit 5.000 req/h
- [ ] Garantir compatibilidade retroativa: planos existentes (`piloto`, `essencial`) não acessam prata.
- [ ] Todos os endpoints `GET /v1/prata/*` usam `Depends(verificar_camada('prata'))`.
- [ ] Endpoint de quarentena raw (`/v1/prata/quarentena/{dataset}`) usa `Depends(verificar_camada('bronze'))`.

### HIS-17.5 — Service Layer Prata

- [ ] Criar `api/app/services/prata.py` com funções async:
  - `buscar_prata(dataset: str, competencia: str, filtros: dict, pagina: int, limite: int) -> dict`
  - `buscar_quarentena_resumo(competencia: str | None) -> list[dict]`
  - `buscar_quarentena_dataset(dataset: str, competencia: str, pagina: int, limite: int) -> dict`
- [ ] Redis cache habilitado para prata com TTL 300s (dado padronizado, mais estável que bronze).

### HIS-17.6 — Documentação do Contrato Prata

- [ ] Criar `docs/arquitetura/contrato_prata_api.md`:
  - Tipagem garantida: todos os campos têm tipo definido e domínio validado
  - Quarentena visível: taxa de aprovação sempre no envelope
  - Registros inválidos segregados: não presentes nos dados, acessíveis via endpoint separado
  - Casos de uso: BI técnico, lakehouse externo, ciência de dados, engenharia de dados
  - Plano necessário: `analitico` (ou superior)

## Entregas esperadas

- [ ] dbt modelos `api/prata/api_prata_*.sql` (11 entrada + 3 enriquecidas = 14 tabelas)
- [ ] `api/app/routers/prata.py` com 14 + 2 endpoints
- [ ] `api/app/schemas/prata.py`
- [ ] `api/app/services/prata.py`
- [ ] Planos `analitico` e `tecnico` em `plataforma.plano`
- [ ] `docs/arquitetura/contrato_prata_api.md`
- [ ] Testes `api/tests/integration/test_prata.py`

## Validação esperada

- [ ] `ruff check api`
- [ ] `pytest api/tests/integration/test_prata.py -v`
- [ ] `dbt compile --select tag:prata`
- [ ] `dbt build --select tag:prata` sem falhas
- [ ] Plano `piloto` retorna HTTP 403 em `/v1/prata/*`
- [ ] Plano `analitico` retorna HTTP 200 com campo `qualidade.taxa_aprovacao` no envelope
- [ ] Endpoint `/v1/prata/quarentena/resumo` retorna HTTP 200 com estrutura de resumo por dataset
