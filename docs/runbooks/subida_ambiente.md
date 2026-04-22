# Runbook — Subida de ambiente

## Objetivo

Subir o stack local ou staging repetível da Sprint 06 com validação mínima de dependências.

## Passos

1. Copiar `.env.exemplo` para `.env` ou `.env.local`.
2. Ajustar `*_EXTERNAL_PORT` se já existir serviço local ocupando `5432`, `6379`, `27017`, `8080`, `8081` ou `8088`.
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

## Critério de sucesso

- `/saude` retorna `200`;
- `/prontidao` retorna `200`;
- `/v1/operadoras` responde com `X-API-Key`;
- `/v1/operadoras/{registro_ans}/regulatorio` responde com `X-API-Key`;
- `dbt build` conclui sem erro;
- smoke não registra falhas.
