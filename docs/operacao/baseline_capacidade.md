# Baseline de capacidade — Sprint 06

## Ambiente da medição

- Data: `2026-04-22`
- Ambiente: local Docker Compose
- Stack ativa: PostgreSQL 16, MongoDB 7, Redis 7, FastAPI, Nginx
- Dataset demo carregado com `scripts/seed_demo_core.py`
- Build dbt publicado antes da medição

## Resultado local de referência

| Cenário | Usuários | Duração | p95 agregado | Falhas | Observação |
| --- | --- | --- | --- | --- | --- |
| `hot_admin` | `8` | `15s` | `140 ms` | `0%` | cache aquecido com chave administrativa para isolar latência |
| `cold_admin` | `8` | `15s` | `200 ms` | `0%` | busca randomizada sem reaproveitamento de cache |
| `mixed_admin` | `8` | `15s` | `230 ms` | `0%` | mistura de hot e cold em envelope de piloto |
| `cold_starter` | `8` | `15s` | `280 ms` | `58,59%` | cenário saturou `60 rpm` e gerou `429`, confirmando o guard-rail do plano |

## Critério operacional adotado

- `hot`: validar p95 dentro da meta de `200 ms`;
- `cold`: validar estabilidade sem erro e sem crescimento anormal de latência;
- `mixed`: baseline para piloto com design partners.
- arquivos de evidência ficam em `testes/load/resultados/`.

## Capacidade por plano

| Plano | Rate limit | Envelope recomendado no piloto |
| --- | --- | --- |
| Starter | `60 rpm` | 1 integração com cache obrigatório; cenários cold agressivos geram `429` |
| Growth | `180 rpm` | até 3 integrações com cache e paginação |
| Pro | `600 rpm` | integrações múltiplas com refresh operacional |
| Enterprise | customizado | ajuste após teste dedicado e baseline específica |

## Comando padrão

```bash
HOST=http://localhost:8080 CACHE_MODE=mixed USERS=10 SPAWN_RATE=2 DURATION=30s \
bash scripts/run_load_test.sh
```
