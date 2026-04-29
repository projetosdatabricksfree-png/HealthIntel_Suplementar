# Runbook — Subida de ambiente

## Objetivo

Subir o stack local ou o ambiente de homologação em VPS com validação mínima de dependências.

## Passos

### Ambiente local

1. Copiar `.env.exemplo` para `.env` ou `.env.local`.
2. Ajustar `*_EXTERNAL_PORT` se já existir serviço local ocupando `5432`, `6379`, `27018`, `8080`, `8081` ou `8088`.
3. Garantir segredos não-padrão fora de `local`:
   - `API_JWT_ADMIN_SECRET`
   - `LAYOUT_SERVICE_TOKEN`
   - `AIRFLOW_FERNET_KEY`
4. Subir a stack:

```bash
make up
```

5. Confirmar containers:

```bash
docker compose -f infra/docker-compose.yml ps
```

6. Popular dados demo:

```bash
python scripts/bootstrap_layout_registry_regulatorio.py
python scripts/seed_demo_core.py
python scripts/seed_demo_regulatorio.py
docker compose -f infra/docker-compose.yml run --rm --entrypoint sh dbt -lc "dbt deps && dbt build"
```

7. Rodar smoke:

```bash
python scripts/smoke_piloto.py
```

### Homologação em VPS

1. Copiar `.env.hml.exemplo` para `.env.hml`.
2. Preencher todos os segredos com valores reais:
   - `POSTGRES_PASSWORD`
   - `MONGO_INITDB_ROOT_PASSWORD`
   - `API_JWT_ADMIN_SECRET`
   - `LAYOUT_SERVICE_TOKEN`
   - `AIRFLOW_FERNET_KEY`
   - `AIRFLOW_ADMIN_PASSWORD`
3. Manter `API_RATE_LIMIT_FAIL_OPEN=false`.
4. Nunca usar as chaves locais `hi_local_dev_2026_api_key` ou
   `hi_local_admin_2026_api_key` em hml/prod. A API bloqueia essas chaves fora
   de ambientes locais, mesmo se elas existirem no banco para smoke de dev.
5. Renderizar o compose de homologação:

```bash
make compose-config-hml
```

6. Confirmar que `/tmp/healthintel-compose-hml.rendered.yml` não contém senhas default como `healthintel`, `admin/admin`, `trocar_em_producao` ou `healthintel_layout_service_local_token_2026`.
7. Subir a stack hml:

```bash
make up-hml
```

8. Materializar dados mínimos e camada de serviço:

```bash
make demo-data
make dbt-seed
make dbt-build
make dbt-test
make smoke
```

9. Validar backup/DR na VPS:

```bash
make smoke-pgbackrest
```

## Critério de sucesso

- `/saude` retorna `200`;
- `/prontidao` retorna `200`;
- `/v1/operadoras` responde com `X-API-Key`;
- `/v1/operadoras/{registro_ans}/regulatorio` responde com `X-API-Key`;
- `dbt build` conclui sem erro;
- smoke não registra falhas.
- Em hml, `make compose-config-hml` renderiza sem segredos default.
- Em hml, `make smoke-pgbackrest` passa com repo2 configurado.
