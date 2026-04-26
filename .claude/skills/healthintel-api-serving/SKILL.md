---
name: healthintel-api-serving
description: Desenvolvimento da API FastAPI e regras da camada `api_ans` — projeções controladas, paginação, autenticação e contrato de envelope.
---

# HealthIntel — API Serving e `api_ans`

## Quando usar esta skill

- Ao criar/alterar router em `api/app/routers/`.
- Ao criar/alterar service em `api/app/services/` ou schema Pydantic em `api/app/schemas/`.
- Ao definir/alterar modelo dbt em `healthintel_dbt/models/api/` (`api_*`).
- Ao revisar autenticação, autorização, paginação, cache, rate limit ou logging de API.

## Regras obrigatórias

1. FastAPI **consome exclusivamente `api_ans`**. Nunca lê `bruto_ans`, `stg_ans`, `int_ans` ou `nucleo_ans`.
2. `api_ans` contém **projeções controladas**: denormalizadas para o caso de uso, **indexáveis** (`post_hook: criar_indices(...)`), **pagináveis** e **seguras** (sem PII desnecessária, sem campos internos de pipeline).
3. Endpoints devem ser:
   - **paginados** por padrão, com limites máximos por página que **impeçam dump integral**;
   - **filtráveis** por chave de negócio (competência, registro_ans/operadora_id, UF, modalidade etc.);
   - **autenticados** via `X-API-Key` (`validar_chave`);
   - **autorizados** por plano (`verificar_plano`) e, quando aplicável, por camada (`verificar_camada('bronze'|'prata')`);
   - **logados** em `plataforma.log_uso` (endpoint, cliente, timestamp, latência, volume retornado).
4. **Resposta sempre em envelope** (Pydantic v2):
   - `dados: [...]`,
   - `meta: { competencia_referencia, versao_dataset, total, pagina }`.
   - Bronze adiciona `aviso_qualidade`. Prata adiciona `qualidade: { taxa_aprovacao, registros_quarentena }`.
5. Cada endpoint **declara** plano/camada permitidos. Camadas e multiplicadores de rate limit:
   - `/v1/bronze/*` — plano `enterprise_tecnico`, `verificar_camada('bronze')`, **cache desabilitado**, custo 3× no bucket.
   - `/v1/prata/*` — plano `analitico`, `verificar_camada('prata')`, **cache TTL 300s**, custo 2× no bucket.
   - `/v1/*` (Ouro) — `verificar_plano`, **cache TTL 60s** quando aplicável, custo 1×.
6. Toda nova rota tem teste de integração em `api/tests/integration/test_{topic}.py` (status, autenticação, autorização por plano/camada, envelope, paginação, filtros).
7. Mudança de contrato em `api_ans` ou em router público é **mudança de produto** — exige aviso e ciclo de versionamento, não é refactor silencioso.

## Anti-padrões

- Endpoint que retorna “tudo” sem paginação ou sem teto de tamanho de página.
- Service consultando `nucleo_ans.fat_*` ou `stg_ans.*` em vez de `api_ans.api_*`.
- Resposta crua (lista no topo) em vez de envelope `{dados, meta}`.
- Dependência de autenticação ausente ou condicional (“em dev liberar tudo”).
- Bronze cacheado em Redis (Bronze é mutável até o lote fechar — **não cachear**).
- Endpoint Premium liberado para plano básico “temporariamente”.
- Logar conteúdo sensível ou payload integral em `log_uso` — logar o suficiente para auditoria/billing, não para vazar dado.
- Quebrar contrato de envelope para “simplificar” o frontend — frontend se adapta ao contrato, não o contrário.

## Checklist antes de concluir

- [ ] Service lê apenas de `api_ans`?
- [ ] Endpoint exige `X-API-Key` e plano/camada corretos?
- [ ] Existe paginação com limite máximo razoável?
- [ ] Existem filtros obrigatórios/recomendados onde fazem sentido?
- [ ] Resposta usa envelope `{dados, meta}` (com `aviso_qualidade` em Bronze e `qualidade` em Prata)?
- [ ] Cache está coerente com a camada (Bronze sem cache; Prata 300s; Gold conforme regra)?
- [ ] Rate limit multiplica corretamente por camada (3× / 2× / 1×)?
- [ ] Há teste de integração cobrindo auth, autorização, envelope e paginação?
- [ ] O modelo `api_*` correspondente tem `post_hook: criar_indices(...)`?

## Exemplo de prompt de uso

> “Vou criar `GET /v1/prata/sinistralidade-procedimento` com filtros por competência e registro_ans.
> Aplique a skill `healthintel-api-serving` e me oriente:
> (1) que modelo `api_*` em `api_ans` esse endpoint deve consumir,
> (2) dependências de auth/plano/camada (`verificar_camada('prata')`),
> (3) shape do envelope com bloco `qualidade`,
> (4) limites de paginação para impedir dump,
> (5) testes de integração mínimos.”
