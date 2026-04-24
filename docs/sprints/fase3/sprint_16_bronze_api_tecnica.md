# Sprint 16 — Bronze API Técnica

**Status:** Concluída
**Objetivo:** expor a camada `bruto_ans` via API REST com envelope de metadados técnicos obrigatórios, restrita ao plano `enterprise_tecnico`; sem transformação semântica; dado as-is com rastreabilidade de lote.
**Critério de saída:** endpoints bronze respondendo com envelope correto; plano `enterprise_tecnico` bloqueando acesso por planos inferiores; contrato documentado sem ambiguidade.

## Histórias

### HIS-16.1 — Modelos dbt Bronze API

- [x] Criar pasta `healthintel_dbt/models/api/bronze/`.
- [x] Para cada dataset principal, criar view thin em `api_ans` sobre `bruto_ans`:
  - `api_bronze_cadop.sql` — select de `bruto_ans.cadop` + metadados auditoria
  - `api_bronze_sib_operadora.sql`
  - `api_bronze_sib_municipio.sql`
  - `api_bronze_igr.sql`
  - `api_bronze_nip.sql`
  - `api_bronze_idss.sql`
  - `api_bronze_diops.sql`
  - `api_bronze_fip.sql`
  - `api_bronze_vda.sql`
  - `api_bronze_glosa.sql`
  - `api_bronze_rede_assistencial.sql`
- [x] Configuração: `materialized: view`, `schema: api_ans`, tag `bronze`.
- [x] Garantir que todas as colunas de auditoria estão expostas: `_lote_id`, `_arquivo_origem`, `_carregado_em`, `_hash_arquivo`, `_layout_id`, `_layout_versao_id`.
- [x] Documentar em `healthintel_dbt/models/api/bronze/_bronze_api.yml`.

### HIS-16.2 — Router FastAPI Bronze

- [x] Criar `api/app/routers/bronze.py` com endpoints paginados por dataset:
  - `GET /v1/bronze/cadop`
  - `GET /v1/bronze/sib/operadora`
  - `GET /v1/bronze/sib/municipio`
  - `GET /v1/bronze/igr`
  - `GET /v1/bronze/nip`
  - `GET /v1/bronze/idss`
  - `GET /v1/bronze/diops`
  - `GET /v1/bronze/fip`
  - `GET /v1/bronze/vda`
  - `GET /v1/bronze/glosa`
  - `GET /v1/bronze/rede-assistencial`
- [x] Filtros obrigatórios: `competencia` (YYYYMM). Filtro opcional: `lote_id`.
- [x] Registrar router em `api/app/main.py` com prefixo `/v1/bronze`.

### HIS-16.3 — Schemas Pydantic Bronze

- [x] Criar `api/app/schemas/bronze.py`.
- [x] Envelope de resposta bronze:
  ```python
  class BronzeMetaResponse(BaseModel):
      fonte: str
      competencia: str
      lote_id: str
      arquivo_origem: str
      carregado_em: datetime
      versao_dataset: str
      aviso_qualidade: str = "Dado bruto sem garantia semântica. Use camada Prata para análise."

  class BronzeResponse(BaseModel):
      dados: list[dict]
      meta: BronzeMetaResponse
  ```
- [x] Campos `dados` tipados como `list[dict]` — sem schema rígido por dataset (dado as-is).

### HIS-16.4 — Controle de Acesso por Camada

- [x] Atualizar `api/app/dependencia.py`: adicionar dependência `verificar_camada(camada: str)` que valida se o plano do cliente tem permissão para acessar a camada solicitada.
- [x] Adicionar coluna `camadas_permitidas TEXT[]` em `plataforma.plano` com valores possíveis: `['bronze', 'prata', 'ouro']`.
- [x] Migration DDL em `infra/postgres/init/015_plano_camadas.sql`.
- [x] Planos atuais migrados:
  - `piloto`, `essencial`: `['ouro']`
  - `plus`: `['ouro', 'prata']`
  - `enterprise`: `['ouro', 'prata', 'bronze']`
  - `enterprise_tecnico`: `['ouro', 'prata', 'bronze']` (raw access incluso)
- [x] Todos os endpoints `GET /v1/bronze/*` usam `Depends(verificar_camada('bronze'))`.

### HIS-16.5 — Service Layer Bronze

- [x] Criar `api/app/services/bronze.py` com funções async por dataset:
  - `buscar_bronze(dataset: str, competencia: str, lote_id: str | None, pagina: int, limite: int) -> dict`
- [x] Query contra view `api_ans.api_bronze_*` correspondente com paginação `LIMIT/OFFSET`.
- [x] Redis cache desabilitado para Bronze API (dado técnico, sem benefício de cache semântico).

### HIS-16.6 — Documentação do Contrato Bronze

- [x] Atualizar `docs/catalogo_endpoints.md` com todos os endpoints `/v1/bronze/*`.
- [x] Criar `docs/arquitetura/contrato_bronze_api.md`:
  - Definição: dado as-is sem transformação semântica
  - Metadados obrigatórios no envelope
  - Ausência de SLA semântico (explícito)
  - Casos de uso: auditoria, debug, reprocessamento, clientes de lakehouse
  - Plano necessário: `enterprise_tecnico`

## Entregas esperadas

- [x] dbt modelos `api/bronze/api_bronze_*.sql` (11 views)
- [x] `api/app/routers/bronze.py` com 11 endpoints
- [x] `api/app/schemas/bronze.py`
- [x] `api/app/services/bronze.py`
- [x] `api/app/dependencia.py` atualizado com `verificar_camada`
- [x] DDL `infra/postgres/init/015_plano_camadas.sql`
- [x] `docs/arquitetura/contrato_bronze_api.md`
- [x] Testes `api/tests/integration/test_bronze.py`

## Validação esperada

- [x] `ruff check api`
- [x] `pytest api/tests/integration/test_bronze.py -v`
- [x] `dbt compile --select tag:bronze`
- [x] Endpoint com plano `piloto` retorna HTTP 403 em `/v1/bronze/*`
- [x] Endpoint com plano `enterprise_tecnico` retorna HTTP 200 com envelope correto
- [x] Campo `aviso_qualidade` presente em todas as respostas bronze
