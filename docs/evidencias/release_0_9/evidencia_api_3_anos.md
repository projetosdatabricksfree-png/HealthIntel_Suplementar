# Evidencia - API Core ANS cobertura 3 anos

- Data/hora UTC: 2026-05-16T18:49:00Z
- Branch: `sprint-43-fechamento-92-tabelas`
- Commit: `5ffc9d06e40793244cc0f09e240440956ad54e3a`
- Tag/base: `v3.9.0-homologacao-ans-real-76-g5ffc9d0-dirty`
- Mapa oficial: `docs/catalogo_dados/api_core_ans/mapa_endpoint_fonte_3_anos.yml`
- Auditoria detalhada: `docs/evidencias/release_0_9/cobertura_3_anos_api.md`
- Smoke detalhado: `docs/evidencias/release_0_9/smoke_api_3_anos.md`

## Resultado executivo

Endpoints auditados: 26.
Datasets/tabelas auditados: 23 fontes distintas.

| status | endpoints |
|---|---:|
| `ok_3_anos` | 8 |
| `snapshot_vigente` | 1 |
| `parcial` | 11 |
| `vazio` | 6 |

## Endpoints com 3 anos

- `/v1/regulatorio`
- `/v1/igr`
- `/v1/nip`
- `/v1/idss`
- `/v1/financeiro`
- `/v1/regime-especial`
- `/v1/operadoras/{registro_ans}/financeiro`
- `/v1/operadoras/{registro_ans}/regulatorio`

Snapshot vigente:

- `/v1/operadoras`

## Endpoints parciais

- `/v1/produtos-planos`
- `/v1/historico-planos`
- `/v1/prudencial`
- `/v1/glosa`
- `/v1/mercado/municipio`
- `/v1/rankings/operadora/score`
- `/v1/rankings/operadora/crescimento`
- `/v1/rankings/municipio/oportunidade`
- `/v1/rankings/municipio/oportunidade-v2`
- `/v1/rankings/composto`
- `/v1/operadoras/{registro_ans}/score-v3/historico`

Esses endpoints permanecem marcados como `parcial` e não contam como disponíveis para a afirmação comercial de 3 anos.

## Endpoints roadmap

- `/v1/mercado/vazio-assistencial`
- `/v1/cnes/municipio/{cd_municipio}`
- `/v1/cnes/uf/{sg_uf}`
- `/v1/rede/municipio/{cd_municipio}`
- `/v1/regulatorio/rn623`
- `/v1/operadoras/{registro_ans}/portabilidade`

Esses endpoints não devem aparecer como disponíveis enquanto `total=0` ou enquanto não houver fonte/carga real viável.

## Backfill e cargas

- Criada DAG `dag_backfill_api_core_ans_3_anos`.
- A DAG separa cargas mensais/trimestrais/anuais, exclui TISS e SIB histórico completo, registra bloqueios de roadmap e roda auditoria de cobertura ao final.
- Backfill pesado não foi executado nesta evidência local; execução deve ocorrer de forma controlada via Airflow.
- Cargas bloqueadas/roadmap: CNES, rede município, vazio assistencial, RN623 e portabilidade.

## Comandos executados

```bash
python3 scripts/auditoria/auditar_cobertura_3_anos_api.py \
  --json-out docs/evidencias/release_0_9/cobertura_3_anos_api.json \
  --md-out docs/evidencias/release_0_9/cobertura_3_anos_api.md

.venv/bin/uvicorn api.app.main:app --host 127.0.0.1 --port 8000

HEALTHINTEL_API_KEY=*** .venv/bin/python scripts/smoke/smoke_api_3_anos.py \
  --base-url http://127.0.0.1:8000 \
  --json-out docs/evidencias/release_0_9/smoke_api_3_anos.json \
  --md-out docs/evidencias/release_0_9/smoke_api_3_anos.md

.venv/bin/pytest api/tests/unit/test_meta_service.py \
  api/tests/integration/test_comercial.py \
  api/tests/unit/test_operadora_service.py \
  api/tests/unit/test_ranking_v2_service.py \
  api/tests/unit/test_mercado_service.py
```

## Resultados de validação

- Auditoria de cobertura 3 anos: sucesso; endpoints sem cobertura deixaram de ser `disponivel` no mapa oficial.
- Smoke API 3 anos: sucesso; 9 endpoints disponíveis OK e 17 endpoints corretamente tratados como parcial/roadmap.
- Testes focados: 25 passed.
- Notebook Databricks criado em `docs/exemplos/databricks/healthintel_api_validacao_3_anos.py`; execução em workspace Databricks não realizada nesta máquina.

## Conclusão comercial

- API com endpoints resolvidos: sim, com parciais/roadmap explicitamente governados.
- API com 3 anos nos publicados disponíveis: sim, considerando apenas endpoints com `status_publicacao=disponivel`.
- Core ANS 9/10 comercial: não ainda; há endpoints temporais relevantes em `parcial` que exigem backfill real antes de entrar na afirmação comercial ampla.
