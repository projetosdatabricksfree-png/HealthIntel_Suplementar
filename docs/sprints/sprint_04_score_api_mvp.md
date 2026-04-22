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
