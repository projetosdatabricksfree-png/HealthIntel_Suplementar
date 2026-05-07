# Fase 10 - Deploy VPS por IP para homologacao

## Objetivo

Preparar e executar deploy controlado do HealthIntel Core ANS em VPS de homologacao usando IP publico, antes da migracao para dominio e HTTPS.

Este ambiente e de homologacao, nao producao final. O objetivo e validar frontend, portal, API, CORS, API key e conectividade com banco em uma VPS Contabo usando:

- Frontend: `http://5.189.160.27`
- API temporaria: `http://5.189.160.27:8080`

## Migracao temporaria para dominio HTTP

Depois que `app.healthintel.com.br` e `api.healthintel.com.br` apontarem para a VPS, a homologacao pode migrar do IP para dominio ainda em HTTP:

- Frontend: `http://app.healthintel.com.br`
- API temporaria: `http://api.healthintel.com.br:8080`

Variaveis necessarias no `.env.hml` da VPS:

```env
FRONTEND_PUBLIC_URL=http://app.healthintel.com.br
API_PUBLIC_URL=http://api.healthintel.com.br:8080
API_ALLOWED_HOSTS=localhost,127.0.0.1,5.189.160.27,app.healthintel.com.br,api.healthintel.com.br,api,healthintel_api
API_CORS_ALLOWED_ORIGINS=http://app.healthintel.com.br,http://api.healthintel.com.br:8080,http://5.189.160.27,http://5.189.160.27:8080,http://localhost:5173,http://127.0.0.1:5173
```

Reaplicar ambiente:

```bash
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  up -d --build api nginx frontend
```

Validar com:

```bash
bash scripts/vps/check_public_domain_http.sh
```

## Arquitetura

Servicos que sobem nesta etapa:

| Servico | Container | Papel | Exposicao |
|---|---|---|---|
| Frontend | `healthintel_frontend` | Site publico e portal do cliente | Publico em `80` |
| Nginx API | `healthintel_nginx` | Proxy da API e layout service | API publica em `8080`; layout apenas loopback |
| API FastAPI | `healthintel_api` | Contratos REST e autenticacao por `X-API-Key` | Interna no compose |
| PostgreSQL | `healthintel_postgres` | Banco operacional/serving | Loopback `127.0.0.1:5432` |
| Redis | `healthintel_redis` | Cache/rate limit | Loopback `127.0.0.1:6379` |
| Mongo | `healthintel_mongo` | Registry/layouts | Loopback `127.0.0.1:27018` |
| Layout service | `healthintel_layout_service` | API interna de layouts | Loopback `127.0.0.1:8081` |

Nao subir inicialmente:

- Airflow webserver
- Airflow scheduler
- dbt continuo
- cargas ANS pesadas
- TISS
- CNES completo

## Portas expostas

Portas publicas temporarias:

| Porta | Uso | Observacao |
|---|---|---|
| `22/tcp` | SSH | Necessaria para administracao |
| `80/tcp` | Frontend | Temporario por IP |
| `8080/tcp` | API | Temporario ate existir dominio/HTTPS |

Portas internas ou loopback:

| Porta | Bind recomendado | Uso |
|---|---|---|
| `5432` | `127.0.0.1:5432` | PostgreSQL |
| `6379` | `127.0.0.1:6379` | Redis |
| `27018` | `127.0.0.1:27018` | Mongo |
| `8081` | `127.0.0.1:8081` | Layout service |

Depois da migracao para dominio/HTTPS, a porta `8080` deve ser fechada publicamente e a API deve responder por `443` via proxy.

## Variaveis de ambiente

Criar na VPS:

```bash
cd /opt/healthintel
cp .env.hml.example .env.hml
nano .env.hml
chmod 600 .env.hml
```

Valores obrigatorios para homologacao por IP:

```env
APP_ENV=hml
API_ENV=hml
FRONTEND_PUBLIC_URL=http://5.189.160.27
API_PUBLIC_URL=http://5.189.160.27:8080
POSTGRES_EXTERNAL_PORT=127.0.0.1:5432
MONGO_EXTERNAL_PORT=127.0.0.1:27018
REDIS_EXTERNAL_PORT=127.0.0.1:6379
LAYOUT_EXTERNAL_PORT=127.0.0.1:8081
API_EXTERNAL_PORT=8080
FRONTEND_EXTERNAL_PORT=80
API_ALLOWED_HOSTS=localhost,127.0.0.1,5.189.160.27,api,healthintel_api
API_CORS_ALLOWED_ORIGINS=http://5.189.160.27,http://5.189.160.27:80,http://5.189.160.27:8080,http://localhost:5173,http://127.0.0.1:5173
VITE_API_BASE_URL=http://5.189.160.27:8080
VITE_ENABLE_DEMO_FALLBACK=false
VITE_APP_NAME=HealthIntel Core ANS
```

Nao versionar `.env.hml`. Trocar todos os placeholders antes de executar deploy.

## Setup inicial da VPS

Na VPS, como root ou usuario com sudo:

```bash
sudo mkdir -p /opt
cd /opt
```

Instalar base, Docker, swap e firewall:

```bash
cd /opt/healthintel
sudo bash scripts/vps/setup_base_vps.sh
```

O script libera somente:

```bash
22/tcp
80/tcp
8080/tcp
```

Ele nao desativa SSH, nao bloqueia root automaticamente e nao altera regras de banco/dados.

## Copia do projeto para VPS

Opcao com `rsync` a partir da maquina local:

```bash
rsync -avz --delete \
  --exclude '.git' \
  --exclude '.env' \
  --exclude '.env.local' \
  --exclude '.env.hml' \
  --exclude '.env.prod' \
  --exclude 'frontend/healthintel_frontend_fase9/.env' \
  --exclude 'frontend/healthintel_frontend_fase9/.env.production' \
  --exclude 'node_modules' \
  --exclude 'dist' \
  --exclude '.venv' \
  --exclude '/data/' \
  /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar/ \
  root@5.189.160.27:/opt/healthintel/
```

Depois copiar o exemplo e preencher localmente na VPS:

```bash
ssh root@5.189.160.27
cd /opt/healthintel
cp .env.hml.example .env.hml
nano .env.hml
chmod 600 .env.hml
```

## Deploy

Executar na VPS:

```bash
cd /opt/healthintel
bash scripts/vps/deploy_hml_ip.sh
```

O script:

- valida `.env.hml`;
- bloqueia placeholders `<trocar...>`;
- gera `frontend/healthintel_frontend_fase9/.env.production`;
- executa `docker compose config`;
- sobe somente `postgres mongo redis api mongo_layout_service nginx frontend`;
- nao sobe Airflow nem dbt.

Comando equivalente manual:

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  up -d --build postgres mongo redis api mongo_layout_service nginx frontend
```

## Logs

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  ps

docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  logs -f api nginx frontend
```

Logs especificos:

```bash
docker logs -f healthintel_api
docker logs -f healthintel_nginx
docker logs -f healthintel_frontend
docker logs -f healthintel_postgres
```

## Rollback

Rollback simples da camada exposta:

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  stop frontend nginx api mongo_layout_service
```

Rollback completo dos servicos de homologacao sem apagar volumes:

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  down
```

Nao usar `down -v` em homologacao com dados a preservar.

## Testes locais na VPS

Executar:

```bash
cd /opt/healthintel
bash scripts/vps/check_hml_ip.sh
```

Checks cobertos:

- `http://127.0.0.1:8080/saude`
- `http://127.0.0.1:8080/prontidao`
- `http://127.0.0.1:8080/v1/meta/endpoints` com chave admin
- `http://127.0.0.1:8080/v1/operadoras` com chave dev
- admin billing com chave dev retornando `403`
- admin billing com chave admin retornando `200` ou erro real nao-auth
- CORS com `Origin: http://5.189.160.27`
- frontend em `http://127.0.0.1:80`

## Testes externos

Da maquina local:

```bash
bash scripts/vps/check_public_ip.sh
```

Ou manualmente:

```bash
curl -i http://5.189.160.27
curl -i http://5.189.160.27:8080/saude
curl -i http://5.189.160.27:8080/prontidao
curl -i "http://5.189.160.27:8080/v1/operadoras?pagina=1&por_pagina=10" \
  -H "X-API-Key: hi_local_dev_2026_api_key"
curl -i -X OPTIONS "http://5.189.160.27:8080/v1/meta/endpoints" \
  -H "Origin: http://5.189.160.27" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-API-Key"
```

## Teste externo pelo notebook

```python
import requests
import pandas as pd

BASE_URL = "http://5.189.160.27:8080"
API_KEY = "hi_local_dev_2026_api_key"

headers = {"X-API-Key": API_KEY}

checks = [
    ("/saude", False),
    ("/prontidao", False),
    ("/v1/meta/endpoints", True),
    ("/v1/operadoras", True),
]

for endpoint, auth in checks:
    resp = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=headers if auth else {},
        params={"pagina": 1, "por_pagina": 20} if endpoint.startswith("/v1") else {},
        timeout=30,
    )
    print(endpoint, resp.status_code)
    print(resp.text[:1000])
    resp.raise_for_status()

resp = requests.get(
    f"{BASE_URL}/v1/operadoras",
    headers=headers,
    params={"pagina": 1, "por_pagina": 20},
    timeout=30,
)

dados = resp.json()
df = pd.json_normalize(dados.get("dados", dados))
display(df)
```

## Checklist de aprovacao

- [ ] `.env.hml` existe na VPS e nao contem placeholders.
- [ ] `.env.hml` esta com `chmod 600`.
- [ ] Firewall libera somente `22`, `80` e `8080` publicamente.
- [ ] PostgreSQL nao esta exposto publicamente.
- [ ] Redis nao esta exposto publicamente.
- [ ] Mongo nao esta exposto publicamente.
- [ ] Layout service nao esta exposto publicamente.
- [ ] Frontend abre em `http://5.189.160.27`.
- [ ] API responde em `http://5.189.160.27:8080/saude`.
- [ ] API responde em `http://5.189.160.27:8080/prontidao`.
- [ ] API protegida aceita `X-API-Key`.
- [ ] Chave dev bloqueia admin com `403`.
- [ ] Chave admin acessa admin billing ou retorna erro real nao-auth.
- [ ] CORS aceita `http://5.189.160.27`.
- [ ] Frontend buildado usa `VITE_API_BASE_URL=http://5.189.160.27:8080`.
- [ ] Airflow, dbt continuo e cargas pesadas nao foram iniciados.
- [ ] Ambiente classificado como homologacao, nao producao.

## Pendencias para producao

- Configurar dominio e HTTPS.
- Fechar porta `8080` publica.
- Usar `https://api.healthintel.com.br` no frontend.
- Rever secrets e rotacao de API keys.
- Definir backups externos e rotina de restore testada.
- Definir observabilidade minima de API e banco.

## Evolucao para HTTPS com Caddy

Depois da homologacao HTTP por dominio, a borda correta e:

- `https://app.healthintel.com.br`
- `https://api.healthintel.com.br`

Nessa etapa:

- `FRONTEND_EXTERNAL_PORT` migra para `127.0.0.1:3000`
- `API_EXTERNAL_PORT` migra para `127.0.0.1:8080`
- `Caddy` passa a publicar `80/443`
- `8080/tcp` deixa de ficar aberta publicamente depois da validacao TLS

O procedimento completo fica documentado em [fase_11b_https_caddy_dominio_vps.md](/home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar/docs/infra/fase_11b_https_caddy_dominio_vps.md).
