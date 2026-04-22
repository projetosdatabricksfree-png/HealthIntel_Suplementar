# Testes de carga

Este diretório concentra o cenário Locust da Sprint 06.

## Cenários

- `mixed`: mistura requests com potencial de cache hit e cache miss.
- `hot`: força repetição de busca para medir comportamento com cache aquecido.
- `cold`: randomiza a busca para reduzir reaproveitamento de cache.

## Execução local

```bash
HOST=http://localhost:8080 \
API_KEY=hi_local_dev_2026_api_key \
CACHE_MODE=mixed \
USERS=10 \
SPAWN_RATE=2 \
DURATION=30s \
bash scripts/run_load_test.sh
```

Os CSVs ficam em `testes/load/resultados/`.
