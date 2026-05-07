# Fase 13B - Runbook Operacional de Publicacao Core na VPS

**Projeto:** HealthIntel Suplementar  
**Produto:** HealthIntel Core ANS  
**Ambiente alvo:** VPS de homologacao `5.189.160.27`  
**Frontend:** `https://app.healthintel.com.br`  
**API:** `https://api.healthintel.com.br`

---

## 1. Objetivo

Publicar o HealthIntel Core ANS em homologacao com estrutura completa de schemas/tabelas e carga controlada dos dados Core, preservando a borda HTTPS ja homologada.

O escopo anterior, limitado ao snapshot de `api_ans`, fica mantido neste documento apenas como alternativa rapida de recuperacao do serving. O caminho principal da Fase 13B e estrutura completa + carga Core controlada + dbt serving.

O resultado esperado desta fase e:

- schemas do projeto criados na VPS;
- `api_ans` na VPS com mais de uma tabela;
- tabelas Core API existentes na VPS;
- `/v1/operadoras` retornando payload nao vazio por HTTPS;
- `/v1/rankings/operadora/score` e `/v1/mercado/municipio` deixando de falhar por `UndefinedTable`;
- Live Tester do portal chamando `https://api.healthintel.com.br` com resposta de payload.

---

## 2. Escopo e limites

### 2.1 Escopo desta fase

- comparar estrutura local x VPS;
- criar backup completo da VPS;
- sincronizar schemas e tabelas base sem apagar dados;
- preservar `plataforma.chave_api`;
- executar carga controlada Core sem TISS, se autorizada;
- materializar serving Core/API via dbt;
- revalidar endpoints Core por HTTPS;
- registrar o resultado em `docs/infra/fase_13_estrutura_e_carga_core_vps.md`.

### 2.2 Fora do escopo

Nao tocar:

- `plataforma.chave_api`;
- logs de uso por cliente;
- TISS;
- CNES completo;
- Airflow;
- dbt continuo;
- cargas pesadas;
- abertura de novas portas;
- CORS, TLS, Caddy ou edge publica.

### 2.3 Alternativa rapida: snapshot `api_ans`

O snapshot de `api_ans` documentado nas secoes seguintes continua valido como alternativa de recuperacao rapida do serving.

Usar essa alternativa somente quando:

- a estrutura base ja estiver correta;
- o objetivo for destravar payload tecnico rapidamente;
- a origem dos dados estiver classificada no manifesto;
- o time aceitar que seed demo gera apenas `demo tecnica com payload`.

Para publicacao mais consistente, preferir a Fase 13B: estrutura completa + carga Core controlada + dbt serving.

---

## 3. Estado inicial confirmado

### 3.1 Borda publica

- `https://app.healthintel.com.br` responde;
- `https://api.healthintel.com.br/saude` responde `200`;
- `https://api.healthintel.com.br/prontidao` responde `200`;
- CORS HTTPS esta homologado;
- `8080/tcp` continua fechado publicamente;
- PostgreSQL, Redis, Mongo e layout service seguem fechados ao publico.

### 3.2 Camada de serving

Na VPS:

- `api_ans` possui somente `1` tabela;
- `api_ans.api_operadora` possui `0` linhas;
- `/v1/operadoras` responde `200` com `dados: []`;
- `/v1/rankings/operadora/score` falha porque `api_ans.api_ranking_score` nao existe;
- `/v1/mercado/municipio` falha porque `api_ans.api_market_share_mensal` nao existe.

No ambiente local:

- `api_ans` esta materializado com multiplas tabelas;
- `api_ans.api_operadora` possui `2` linhas;
- os registros locais vieram de `scripts/seed_demo_core.py` e correlatos.

### 3.3 Classificacao do dataset local

O snapshot local atual deve ser tratado como:

`DEMO_TECNICA_COM_PAYLOAD`

Motivo:

- existe registro explicitamente nomeado como `OPERADORA EXEMPLO`;
- os `registro_ans` `123456` e `654321` aparecem em scripts `seed_demo_*`;
- nao ha evidencias suficientes para classificar o dataset local atual como serving comercial real da ANS.

Consequencia operacional:

- esta fase pode destravar payload funcional e smoke da API;
- esta fase **nao** autoriza declarar `demo comercial controlada`.

---

## 4. Modos de snapshot

### 4.1 Snapshot completo do schema `api_ans`

Descricao:

- exporta todas as tabelas do schema `api_ans`;
- restaura a coerencia rapida de endpoints que dependem de varias tabelas;
- reduz o risco de esquecer dependencias do serving.

Uso recomendado nesta sprint: **sim**

### 4.2 Snapshot minimo por tabela

Descricao:

- exporta apenas tabelas selecionadas;
- reduz volume e acoplamento;
- exige catalogo preciso das dependencias do serving.

Uso recomendado nesta sprint: **nao**

### 4.3 Default desta fase

Usar como padrao:

- exportar o schema `api_ans` completo do ambiente local;
- importar somente `api_ans` na VPS;
- preservar todos os demais schemas intactos.

---

## 5. Pre-condicoes obrigatorias

Todos os itens abaixo devem estar verdadeiros antes de iniciar a importacao.

```text
[ ] Containers locais ativos
[ ] Containers da VPS ativos
[ ] HTTPS/CORS preservados
[ ] .env.hml existente apenas na VPS
[ ] Banco nao exposto publicamente
[ ] Snapshot local classificado como demo tecnica
[ ] Diretório local tmp/snapshot_api_ans/ disponivel
[ ] Diretório remoto /opt/healthintel/snapshots/ disponivel
[ ] Diretório remoto /opt/healthintel/backups/api_ans/ disponivel
```

Para o fluxo principal da Fase 13B, tambem validar:

```text
[ ] SSH para a VPS autenticado
[ ] scripts/vps/compare_schema_local_vps.sh disponivel localmente
[ ] scripts/vps/sync_schema_vps.sh disponivel na VPS
[ ] scripts/vps/run_carga_core_sem_tiss.sh disponivel na VPS
[ ] scripts/vps/build_serving_core.sh disponivel na VPS
[ ] scripts/vps/check_public_domain_https.sh disponivel na VPS
[ ] scripts/vps/check_api_core_comercial.sh disponivel na VPS
```

Comandos de referencia:

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar
docker compose -f infra/docker-compose.yml ps

ssh root@5.189.160.27
cd /opt/healthintel
docker compose --env-file .env.hml -f infra/docker-compose.yml -f infra/docker-compose.hml.yml ps

curl -i https://api.healthintel.com.br/saude
curl -i https://api.healthintel.com.br/prontidao
```

---

## 5.1 Fluxo principal Fase 13B

Executar localmente:

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar
bash scripts/vps/compare_schema_local_vps.sh
```

Executar na VPS:

```bash
cd /opt/healthintel
CONFIRM_SYNC_SCHEMA=SIM bash scripts/vps/sync_schema_vps.sh
ELT_LIMITE=100 bash scripts/vps/run_carga_core_sem_tiss.sh
bash scripts/vps/build_serving_core.sh
ENV_FILE=.env.hml bash scripts/vps/check_public_domain_https.sh
ENV_FILE=.env.hml bash scripts/vps/check_api_core_comercial.sh
```

Logs operacionais:

```text
logs/fase13/
```

Inventario local x VPS:

```text
tmp/schema_compare/
```

---

## 6. Diagnostico local antes do snapshot

Executar localmente:

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
select
  relname as tabela,
  n_live_tup::bigint as linhas_estimadas,
  pg_size_pretty(pg_total_relation_size(relid)) as tamanho
from pg_stat_user_tables
where schemaname = 'api_ans'
order by relname;
"

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
select count(*) as total_api_operadora
from api_ans.api_operadora;
"

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
select *
from api_ans.api_operadora
limit 5;
"
```

Classificar `api_operadora` como:

- `REAL`
- `EXEMPLO`
- `SINTETICO`
- `INDEFINIDO`

Default atual desta sprint:

- `EXEMPLO/SINTETICO`

---

## 7. Export local do snapshot

### 7.1 Gerar snapshot

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar

mkdir -p tmp/snapshot_api_ans

docker exec -t healthintel_postgres pg_dump \
  -U healthintel \
  -d healthintel \
  -n api_ans \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  > tmp/snapshot_api_ans/api_ans_snapshot.sql

gzip -f tmp/snapshot_api_ans/api_ans_snapshot.sql

ls -lh tmp/snapshot_api_ans/api_ans_snapshot.sql.gz
```

### 7.2 Manifesto do snapshot

Gerar:

`tmp/snapshot_api_ans/manifesto_api_ans_snapshot.md`

Conteudo obrigatorio:

- data/hora;
- origem local;
- banco;
- schema exportado;
- lista de tabelas;
- contagens por tabela;
- tamanho do arquivo;
- classificacao dos dados;
- veredito: `demo tecnica` ou `comercial`.

---

## 8. Transferencia para a VPS

Criar diretório remoto se necessario:

```bash
ssh root@5.189.160.27 "mkdir -p /opt/healthintel/snapshots"
```

Transferir artefatos:

```bash
scp tmp/snapshot_api_ans/api_ans_snapshot.sql.gz \
  root@5.189.160.27:/opt/healthintel/snapshots/

scp tmp/snapshot_api_ans/manifesto_api_ans_snapshot.md \
  root@5.189.160.27:/opt/healthintel/snapshots/
```

---

## 9. Backup do `api_ans` atual da VPS

Na VPS:

```bash
ssh root@5.189.160.27
cd /opt/healthintel

mkdir -p backups/api_ans

docker exec -t healthintel_postgres pg_dump \
  -U healthintel \
  -d healthintel \
  -n api_ans \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  > backups/api_ans/api_ans_before_import_$(date +%Y%m%d_%H%M%S).sql
```

Registrar o nome exato do backup no relatorio final.

---

## 10. Import reversivel na VPS

Na VPS:

```bash
cd /opt/healthintel

cp snapshots/api_ans_snapshot.sql.gz /tmp/api_ans_snapshot.sql.gz
gunzip -f /tmp/api_ans_snapshot.sql.gz

cat /tmp/api_ans_snapshot.sql | docker exec -i healthintel_postgres psql \
  -U healthintel \
  -d healthintel
```

### 10.1 Analyze pos-import

```bash
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "analyze api_ans.api_operadora;"
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "analyze;"
```

---

## 11. Validacao da importacao

Na VPS:

```bash
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
select
  relname as tabela,
  n_live_tup::bigint as linhas_estimadas,
  pg_size_pretty(pg_total_relation_size(relid)) as tamanho
from pg_stat_user_tables
where schemaname = 'api_ans'
order by relname;
"

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
select count(*) as total_api_operadora
from api_ans.api_operadora;
"

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
select *
from api_ans.api_operadora
limit 5;
"
```

Critério minimo:

- `api_ans` com mais de `1` tabela;
- `api_ans.api_operadora` com `count > 0`.

---

## 12. Revalidacao dos endpoints Core

### 12.1 Script padrao

Na VPS:

```bash
cd /opt/healthintel
ENV_FILE=.env.hml bash scripts/vps/check_api_core_comercial.sh
```

### 12.2 Testes HTTPS manuais

Usando a chave HML DEV da VPS, sem imprimi-la em logs:

```bash
curl -i "https://api.healthintel.com.br/v1/operadoras?pagina=1&por_pagina=10" \
  -H "X-API-Key: $HML_DEV_API_KEY"

curl -i "https://api.healthintel.com.br/v1/rankings/operadora/score?pagina=1&por_pagina=10" \
  -H "X-API-Key: $HML_DEV_API_KEY"

curl -i "https://api.healthintel.com.br/v1/mercado/municipio?pagina=1&por_pagina=10" \
  -H "X-API-Key: $HML_DEV_API_KEY"
```

Classificar cada endpoint como:

- `OK_COM_DADOS`
- `OK_VAZIO`
- `ERRO_TABELA`
- `ERRO_BACKEND`
- `ERRO_AUTH`

Critério desta fase:

- `/v1/operadoras` deve retornar `dados` nao vazios;
- `rankings` e `mercado` devem ao menos deixar de falhar por tabela ausente.

---

## 13. Validacao funcional no portal

Abrir:

`https://app.healthintel.com.br`

Executar:

1. login no portal;
2. salvar chave HML DEV;
3. abrir Live Tester;
4. testar `/v1/operadoras`;
5. confirmar que a chamada vai para `https://api.healthintel.com.br`;
6. confirmar que a resposta possui payload.

Se o endpoint responder com payload, mas o dado continuar de seed demo, o status segue sendo:

`demo tecnica com payload`

---

## 14. Rollback

Usar o backup gerado em `/opt/healthintel/backups/api_ans/`.

Comando de rollback:

```bash
cat backups/api_ans/<backup_escolhido>.sql | docker exec -i healthintel_postgres psql \
  -U healthintel \
  -d healthintel

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "analyze;"
```

O rollback deve ser documentado com:

- nome do backup usado;
- motivo da reversao;
- horario da reversao;
- resultado apos revalidacao.

---

## 15. Artefatos obrigatorios

Esta fase deve produzir:

- `tmp/snapshot_api_ans/api_ans_snapshot.sql.gz`
- `tmp/snapshot_api_ans/manifesto_api_ans_snapshot.md`
- `/opt/healthintel/backups/api_ans/api_ans_before_import_<timestamp>.sql`
- `docs/infra/fase_13_snapshot_api_ans_vps.md`

---

## 16. Criterios de aceite

```text
[ ] Snapshot api_ans exportado localmente
[ ] Manifesto criado
[ ] Snapshot copiado para VPS
[ ] Backup api_ans da VPS criado
[ ] Snapshot importado
[ ] VPS api_ans tem mais de 1 tabela
[ ] VPS api_ans.api_operadora count > 0
[ ] /v1/operadoras por HTTPS retorna dados
[ ] Live Tester retorna dados
[ ] /v1/rankings/operadora/score deixa de falhar por tabela ausente
[ ] /v1/mercado/municipio deixa de falhar por tabela ausente
[ ] Nenhum segredo commitado
[ ] Nenhum banco exposto publicamente
[ ] Rollback documentado
[ ] Evidencia final criada
```

---

## 17. Veredito final

Regra de saida desta fase:

- se os dados importados vierem de seed demo:
  - `pronto para demo tecnica com payload`
- se os dados importados vierem de serving real da ANS:
  - `pronto para demo comercial controlada`

Default atual do projeto:

- **esperado apos esta fase: `demo tecnica com payload`**

---

## 18. Referencia de evidencia complementar

Depois da execucao, consolidar:

`docs/infra/fase_13_snapshot_api_ans_vps.md`

Esse documento deve registrar o antes/depois da VPS, o nome do backup, o manifesto usado, o resultado dos endpoints e o veredito final.
