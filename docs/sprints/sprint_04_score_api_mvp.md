# Sprint 04 — Score e API MVP

**Status:** Concluida
**Objetivo:** publicar o primeiro fato, disponibilizar a camada `api_ans` e expor a API MVP.
**Criterio de saida:** endpoints centrais ficam disponiveis com contrato base e autenticacao inicial.

## Historias

### HIS-04.1 — Construir o score inicial

- [x] Implementar `healthintel_dbt/models/marts/fato/fat_score_operadora_mensal.sql`.
- [x] Validar materializacao do score contra carga real.
- [x] Formalizar pesos configuraveis por seed ou tabela operacional.

### HIS-04.2 — Publicar a camada de servico `api_ans`

- [x] Implementar `healthintel_dbt/models/api/api_operadora.sql`.
- [x] Documentar o modelo em `healthintel_dbt/models/api/_api.yml`.
- [x] Criar indices fisicos de desempenho em ambiente banco real.

### HIS-04.3 — Expor a API publica inicial

- [x] Implementar `api/app/main.py` com bootstrap FastAPI.
- [x] Implementar `api/app/routers/operadora.py`.
- [x] Implementar `api/app/routers/meta.py`.
- [x] Criar schemas de resposta em `api/app/schemas/operadora.py` e `api/app/schemas/meta.py`.

### HIS-04.4 — Aplicar controles transversais de API

- [x] Implementar middleware de autenticacao em `api/app/middleware/autenticacao.py`.
- [x] Implementar middleware de rate limit em `api/app/middleware/rate_limit.py`.
- [x] Implementar cliente Redis em `api/app/core/redis_client.py`.
- [x] Persistir `log_uso` em PostgreSQL por request autenticado.

### HIS-04.5 — Validar contrato inicial dos endpoints

- [x] Criar teste unitario de saude em `api/tests/unit/test_saude.py`.
- [x] Criar teste de integracao inicial em `api/tests/integration/test_operadora.py`.
- [x] Criar teste unitario do admin de layout em `api/tests/unit/test_admin_layout.py`.

### HIS-04.6 — Completar modelos dbt derivados e endpoints de mercado/ranking

- [ ] Implementar `fat_market_share_mensal.sql` (table full refresh, `nucleo_ans`): market share por operadora × municipio × competencia via `int_metrica_municipio` com calculo de HHI via macro `calcular_hhi`.
- [ ] Implementar `fat_oportunidade_municipio_mensal.sql` (table full refresh, `nucleo_ans`): score de oportunidade por municipio × competencia cruzando beneficiarios, crescimento 12m, HHI e cobertura geografica.
- [ ] Implementar modelos `api_ans` ausentes do PRD: `api_score_operadora_mensal.sql`, `api_market_share_mensal.sql`, `api_oportunidade_municipio_mensal.sql`, `api_ranking_crescimento.sql`, `api_ranking_score.sql`, `api_ranking_oportunidade.sql` (todos table + post-hook `criar_indices`).
- [ ] Implementar `api/app/database.py` com asyncpg pool e SQLAlchemy async engine para consultas na `api_ans`.
- [ ] Implementar `api/app/dependencia.py` com injecoes `validar_chave` (hash SHA-256 + cache Redis TTL 60s) e `verificar_plano` (valida `endpoint_permitido` do plano contratado).
- [ ] Criar `api/app/services/` com queries async apontando exclusivamente para `api_ans` (a FastAPI nunca le `nucleo_ans` diretamente).
- [ ] Criar `api/app/routers/mercado.py` com endpoint `GET /v1/mercado/municipio` (filtros: `uf`, `competencia`, `segmento`). Schema Pydantic v2: `MercadoResumoResponse`.
- [ ] Criar `api/app/routers/ranking.py` com endpoints: `GET /v1/rankings/operadora/score`, `GET /v1/rankings/municipio/oportunidade`, `GET /v1/rankings/operadora/crescimento`.
- [ ] Criar `api/app/schemas/mercado.py` com `MercadoResumoResponse` e `UfResponse`.
- [ ] Criar `api/app/schemas/municipio.py` com `MunicipioResponse` e `OportunidadeResponse`.
- [ ] Garantir que todos os endpoints retornam envelope `{dados: [...], meta: {competencia_referencia, versao_dataset, total, pagina}}`.
- [ ] Criar teste dbt `assert_share_soma_100_por_competencia.sql` (soma de market share por competencia = 100%).
- [ ] Criar teste dbt `assert_sem_duplicata_score_mensal.sql` (unicidade de `[operadora_id, competencia_id]` em `fat_score_operadora_mensal`).
