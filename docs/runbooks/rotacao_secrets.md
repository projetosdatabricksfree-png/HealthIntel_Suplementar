# Runbook — Rotacao de Secrets

## Scope

Cobre os secrets gerenciados em `.env.hml` na VPS (`/opt/healthintel/.env.hml`).
Nao se aplica a chaves API de clientes — ver `onboarding_chave_comercial.md`.

## Secrets catalogados

| Variavel | Uso | Frequencia de rotacao |
|----------|-----|----------------------|
| `POSTGRES_PASSWORD` | Senha do superuser PostgreSQL | 90 dias ou apos incidente |
| `MONGO_INITDB_ROOT_PASSWORD` | Senha root MongoDB | 90 dias ou apos incidente |
| `API_JWT_ADMIN_SECRET` | JWT para rotas admin (`/admin/billing`, etc.) | 90 dias ou apos incidente |
| `LAYOUT_SERVICE_TOKEN` | Token de auth do mongo_layout_service | 90 dias ou apos incidente |
| `AIRFLOW_FERNET_KEY` | Criptografia de conexoes e variaveis no Airflow | Anual ou apos vazamento |
| `PGBACKREST_REPO2_CIPHER_PASS` | Criptografia do backup S3 | Anual (requer re-encriptacao do backup) |
| `SENTRY_DSN` | DSN do Sentry (nao e senha, mas e configuracao sensivel) | Rotacionar se exposto publicamente |

## Procedimento padrao (PostgreSQL, MongoDB, JWT, Layout Token)

```bash
# 1. Gerar novo valor
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# 2. Editar .env.hml na VPS
nano /opt/healthintel/.env.hml

# 3. Reiniciar os servicos afetados
cd /opt/healthintel
docker compose --env-file .env.hml down
docker compose --env-file .env.hml up -d

# 4. Aguardar healthcheck verde
docker compose ps

# 5. Verificar /prontidao
curl -s https://api.healthintel.com.br/prontidao | jq
```

## Rotacao do AIRFLOW_FERNET_KEY

O Fernet key criptografa conexoes e variaveis no Airflow. Rotacionar exige re-encriptacao:

```bash
# 1. Gerar nova chave
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Adicionar a nova chave como segunda entrada (lista separada por virgula)
#    para que conexoes antigas ainda funcionem durante a transicao
# No .env.hml:
# AIRFLOW_FERNET_KEY=<nova_chave>,<chave_antiga>

# 3. Reiniciar o Airflow
docker compose restart airflow-webserver airflow-scheduler

# 4. Re-encriptar conexoes com a nova chave
docker compose exec airflow-webserver airflow connections export - | \
  docker compose exec -T airflow-webserver airflow connections import -

# 5. Remover a chave antiga do .env.hml (deixar so a nova)
# AIRFLOW_FERNET_KEY=<nova_chave>

# 6. Reiniciar de novo
docker compose restart airflow-webserver airflow-scheduler
```

## Rotacao do PGBACKREST_REPO2_CIPHER_PASS

Rotacionar a senha do backup S3 exige re-backup completo — agendar manutencao:

```bash
# 1. Gerar nova senha (minimo 32 chars)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# 2. Atualizar /etc/healthintel/pgbackrest.env com nova senha

# 3. Re-materializar pgbackrest.conf
envsubst < /opt/healthintel/infra/pgbackrest/pgbackrest.conf.template \
  > /etc/pgbackrest/pgbackrest.conf

# 4. Forcar novo backup full com nova senha
sudo -u postgres pgbackrest --stanza=healthintel --repo=2 backup --type=full

# 5. Confirmar via pgbackrest info
sudo -u postgres pgbackrest --stanza=healthintel --repo=2 info
```

## Politica de armazenamento

- `.env.hml` deve ter `chmod 600 .env.hml` e pertencer ao usuario que roda o docker compose.
- Nunca comitar valores reais em git. O arquivo `.gitignore` deve conter `.env.hml`.
- Nao armazenar secrets em logs, `plataforma.job.mensagem_erro` nem outputs de DAG.

## Criterio de aceite apos rotacao

- `docker compose ps` mostra todos os containers `healthy` ou `running`;
- `/prontidao` retorna `status: ok`;
- `make smoke-core` passa sem erro;
- nenhum secret antigo aparece em `docker compose logs` dos ultimos 10 min.
