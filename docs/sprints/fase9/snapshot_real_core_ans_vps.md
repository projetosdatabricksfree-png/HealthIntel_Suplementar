# Sprint: Snapshot Real Core ANS na VPS

**Fase:** Fase 9 — MVP comercial Core ANS  
**Status:** [ ] Em andamento  
**Tag de saída prevista:** `v3.5.0-core-ans-real`  
**Produto:** HealthIntel Core ANS  
**Ambiente:** VPS Contabo — `5.189.160.27` (512 GB SSD)  
**Critério de negócio:** hardgate técnico obrigatório antes do primeiro cliente pagante  

---

## 1. Objetivo do Sprint

Este sprint prova que o ambiente de homologação na VPS consegue operar com dados reais da ANS (não demo/seed) dentro dos limites de disco e performance da VPS de 512 GB.

### O que o sprint prova

- executa a carga `FULL2A_SEM_TISS_REAL` com dados reais (SIB 2 anos + famílias pequenas);
- materializa as 8 tabelas de `consumo_ans` via `dbt build --select tag:core_ans`;
- passa nos testes dbt do Core (`dbt test --select tag:core_ans`) com zero falhas;
- passa no smoke test da API Core com dados reais — não seed (`falhas: 0`);
- mantém disco raiz abaixo de 75% durante todo o processo.

### O que este sprint NÃO faz

- não executa carga TISS (`PENDENTE_PARSER_LOAD_REAL`);
- não executa `all_ftp`;
- não altera rotas, schemas ou contratos de API existentes;
- não configura Airflow scheduler (não sobe em HML por design);
- não configura backup externo (repo2/pgBackRest) — requisito de sprint separado.

**Sem aprovação deste sprint, nenhuma demonstração com dados reais e nenhum contrato de piloto devem ser assinados.**

---

## 2. Pré-condições Obrigatórias

Todos os itens abaixo devem estar `[x]` antes de executar qualquer passo da Seção 4. Um item não marcado bloqueia o início.

### 2.1 Ambiente VPS

```
[ ] SSH funcional: ssh root@5.189.160.27
[ ] Projeto sincronizado em /opt/healthintel via rsync (sem .git, sem .env*, sem .venv, sem data/)
[ ] .env.hml existe em /opt/healthintel/.env.hml
[ ] .env.hml tem chmod 600
[ ] .env.hml não contém nenhum placeholder <trocar...>
[ ] ANS_ANOS_CARGA_HOT=2 definido em .env.hml
[ ] .venv python disponível: /opt/healthintel/.venv/bin/python --version
```

Sincronizar projeto:

```bash
rsync -av --exclude='.git' --exclude='.env*' --exclude='node_modules' \
  --exclude='.venv' --exclude='data/' \
  /caminho/local/HealthIntel_Suplementar/ \
  root@5.189.160.27:/opt/healthintel/
```

### 2.2 Serviços Docker em execução

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  ps
```

Serviços obrigatórios `running`: `healthintel_postgres`, `healthintel_redis`, `healthintel_api`, `healthintel_nginx`, `healthintel_mongo`, `healthintel_layout_service`, `healthintel_frontend`.

Serviços que **não** devem estar rodando: Airflow scheduler, Airflow webserver, dbt contínuo.

Se os serviços estiverem parados:

```bash
cd /opt/healthintel
bash scripts/vps/deploy_hml_ip.sh
```

### 2.3 Disco inicial

```bash
df -h /
```

**Requisito:** uso do disco raiz abaixo de **60%** antes de iniciar. Se acima, limpar `data/landing` de execuções anteriores:

```bash
du -sh /opt/healthintel/data/landing*/
rm -rf /opt/healthintel/data/landing_full2a_sem_tiss/
```

### 2.4 API respondendo com dados existentes

```bash
cd /opt/healthintel
source .env.hml

curl -s http://127.0.0.1:8080/saude
curl -s http://127.0.0.1:8080/prontidao
curl -s "http://127.0.0.1:8080/v1/operadoras?pagina=1&por_pagina=5" \
  -H "X-API-Key: ${HML_DEV_API_KEY}"
```

Todos devem retornar HTTP 200. Se a API não responder: `bash scripts/vps/check_hml_ip.sh`.

### 2.5 dbt compilável

```bash
cd /opt/healthintel/healthintel_dbt
DBT_LOG_PATH=/tmp/healthintel_dbt_logs \
DBT_TARGET_PATH=/tmp/healthintel_dbt_target \
../.venv/bin/dbt compile --select tag:core_ans
```

Zero erros de compilação obrigatório antes de continuar.

### 2.6 Lock livre

```bash
ls -la /tmp/healthintel_full2a.lock 2>/dev/null \
  && echo "LOCK EXISTE — verificar processo" \
  || echo "Lock livre — ok"
```

Se o lock existir: `cat /tmp/healthintel_full2a.lock` para identificar o PID. Verificar se o processo ainda está ativo (`ps -p <PID>`) antes de remover manualmente.

---

## 3. Sequência de Execução

A ordem é obrigatória. Não pular passos, não reordenar. Cada passo depende do anterior.

### Passo 1 — Snapshot do sistema ANTES da carga

```bash
cd /opt/healthintel

# Snapshot de disco, memória e Docker
make capacidade-snapshot NIVEL=FULL2A_SEM_TISS MOMENTO=antes

# Snapshot do PostgreSQL (tamanho por schema e top tabelas)
SNAP_TS=$(date +%Y%m%d_%H%M%S)
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  exec -T postgres psql -U healthintel -d healthintel \
  -c "SELECT schemaname, pg_size_pretty(SUM(pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename)))::bigint) AS total FROM pg_tables GROUP BY schemaname ORDER BY SUM(pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename))) DESC;" \
  > "docs/evidencias/capacidade/capacidade_FULL2A_SEM_TISS_postgres_antes_vps_${SNAP_TS}.txt"
```

Registrar o % de uso do disco raiz neste momento como referência.

**Artefatos esperados em `docs/evidencias/capacidade/`:**
- `capacidade_FULL2A_SEM_TISS_antes_YYYYMMDD_HHMMSS.txt`
- `capacidade_FULL2A_SEM_TISS_postgres_antes_vps_YYYYMMDD_HHMMSS.txt`

### Passo 2 — Dry-run de validação

```bash
cd /opt/healthintel
make carga-ans-padrao-vps-dry-run
```

Verificar obrigatoriamente na saída:

- `DRY_RUN: true` — confirma modo seguro
- `Janela temporal: 202501 até 202701` (baseado em `ANS_ANOS_CARGA_HOT=2` e ano 2026)
- `landing_path=./data/landing_full2a_sem_tiss` — landing isolada confirmada
- `tiss_ambulatorial: PENDENTE_PARSER_LOAD_REAL` — TISS excluído confirmado
- `DRY_RUN_OK` no arquivo de status gerado em `docs/evidencias/capacidade/`

**Se qualquer um desses itens falhar: NÃO executar a carga real.** Investigar e corrigir primeiro.

### Passo 3 — Monitoramento de disco em background

Em um terminal separado (tmux recomendado):

```bash
cd /opt/healthintel
make capacidade-monitor NIVEL=FULL2A_SEM_TISS
```

Ou em background sem bloquear o terminal:

```bash
cd /opt/healthintel
nohup bash scripts/capacidade/monitorar_carga.sh FULL2A_SEM_TISS \
  > /tmp/monitor_full2a_sem_tiss.log 2>&1 &
echo "PID monitor: $!"
```

O monitor emite alerta se disco passar de 80% e aviso crítico em 90%.

### Passo 4 — Carga real FULL2A_SEM_TISS_REAL

```bash
cd /opt/healthintel
make carga-ans-padrao-vps
```

Este comando executa `scripts/capacidade/executar_carga_ans_padrao_vps.sh false`, que:
- adquire lock exclusivo em `/tmp/healthintel_full2a.lock`;
- carrega `sib` com janela de 2 anos (`ANS_ANOS_CARGA_HOT=2`);
- carrega `cadop, idss, igr, nip, sip, diops, rpc, caderno_ss, plano` (completo);
- exclui `tiss` com status `PENDENTE_PARSER_LOAD_REAL`;
- emite `CARGA_CONCLUIDA_SEM_TISS_REAL` no status file ao finalizar.

**Critério de conclusão:** arquivo `docs/evidencias/capacidade/FULL2A_SEM_TISS_status_YYYYMMDD_HHMMSS.txt` deve conter a linha `CARGA_CONCLUIDA_SEM_TISS_REAL`.

Duração esperada: 2 a 6 horas. Não interromper sem necessidade.

### Passo 5 — Verificar status da carga

```bash
cd /opt/healthintel
make elt-status
```

Verificar:
- `sib`: `carregado` > 0 (esperar 20+ arquivos para `ANS_ANOS_CARGA_HOT=2`)
- `cadop`, `idss`, `igr`, `nip`: `carregado` > 0
- `tiss`: `PENDENTE_PARSER_LOAD_REAL` ou ausente da listagem de carregados

### Passo 6 — dbt build Core ANS

```bash
cd /opt/healthintel
make dbt-build-core
```

Executa `dbt build --select tag:mart tag:core_ans`. Materializa as 8 tabelas em `consumo_ans`:

```
consumo_operadora_360
consumo_score_operadora_mes
consumo_beneficiarios_operadora_mes
consumo_beneficiarios_municipio_mes
consumo_financeiro_operadora_trimestre
consumo_regulatorio_operadora_trimestre
consumo_oportunidade_municipio
consumo_rede_assistencial_municipio
```

**Critério:** zero modelos com erro. Warnings em modelos fora do escopo `core_ans` são investigados mas não bloqueiam.

### Passo 7 — Testes dbt Core ANS

```bash
cd /opt/healthintel
make dbt-test-core
```

Executa `dbt test --select tag:core_ans`.

**Critério:** zero falhas. Cada falha de teste bloqueia a aprovação do sprint.

### Passo 8 — Smoke test da API Core com dados reais

Descobrir um registro ANS real presente nos dados carregados:

```bash
cd /opt/healthintel
source .env.hml

docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  exec -T postgres psql -U healthintel -d healthintel -c \
  "SELECT registro_ans, nome_razao_social FROM consumo_ans.consumo_operadora_360 LIMIT 5;"
```

Executar o smoke com registro real:

```bash
cd /opt/healthintel

SMOKE_BASE_URL=http://127.0.0.1:8080 \
SMOKE_API_KEY="${HML_DEV_API_KEY}" \
SMOKE_REGISTRO_ANS="<registro_ans_real>" \
.venv/bin/python scripts/smoke_core.py \
  2>&1 | tee "docs/evidencias/capacidade/smoke_core_vps_$(date +%Y%m%d).txt"
```

**Critério:** última linha do output deve ser `falhas: 0`.

### Passo 9 — Snapshot do sistema DEPOIS da carga

```bash
cd /opt/healthintel

make capacidade-snapshot NIVEL=FULL2A_SEM_TISS MOMENTO=depois

SNAP_TS=$(date +%Y%m%d_%H%M%S)
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  exec -T postgres psql -U healthintel -d healthintel \
  -c "SELECT schemaname, pg_size_pretty(SUM(pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename)))::bigint) AS total FROM pg_tables GROUP BY schemaname ORDER BY SUM(pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename))) DESC;" \
  > "docs/evidencias/capacidade/capacidade_FULL2A_SEM_TISS_postgres_depois_vps_${SNAP_TS}.txt"
```

### Passo 10 — Relatório de capacidade

```bash
cd /opt/healthintel
make capacidade-relatorio NIVEL=FULL2A_SEM_TISS
```

Artefato gerado: `docs/evidencias/capacidade/capacidade_FULL2A_SEM_TISS_relatorio_YYYYMMDD_HHMMSS.md`

### Passo 11 — Validação de endpoints com dados reais (da máquina local)

```bash
bash scripts/vps/check_public_ip.sh \
  2>&1 | tee "docs/evidencias/capacidade/check_public_ip_vps_$(date +%Y%m%d).txt"
```

Validações manuais adicionais:

```bash
BASE_URL="http://5.189.160.27:8080"
API_KEY="<HML_DEV_API_KEY>"

# Operadoras — deve retornar dados reais, não seed
curl -s "$BASE_URL/v1/operadoras?pagina=1&por_pagina=5" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

# Metadados — deve refletir competência real carregada
curl -s "$BASE_URL/v1/meta/atualizacao" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

# Ranking de score com dados reais
curl -s "$BASE_URL/v1/rankings/operadora/score?pagina=1&por_pagina=10" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool
```

**Critério:** respostas com razão social real, competência real, valores reais — nenhum "Operadora Demo" ou similar.

### Passo 12 — Verificação final de disco

```bash
cd /opt/healthintel
make monitor-disco
```

**Critério:** uso do disco raiz abaixo de 75%.  
Se entre 75–89%: registrar alerta e planejar limpeza da landing como próxima ação.  
Se 90% ou mais: executar limpeza da landing imediatamente conforme Seção 5 (Rollback).

---

## 4. Evidências Obrigatórias

Todos os 10 artefatos devem existir em `docs/evidencias/capacidade/` antes de marcar o sprint como concluído.

| Evidência | Arquivo | Passo |
|-----------|---------|-------|
| Snapshot sistema antes | `capacidade_FULL2A_SEM_TISS_antes_YYYYMMDD_HHMMSS.txt` | 1 |
| Snapshot PostgreSQL antes | `capacidade_FULL2A_SEM_TISS_postgres_antes_vps_YYYYMMDD_HHMMSS.txt` | 1 |
| Status dry-run | `FULL2A_SEM_TISS_status_*_dry.txt` com `DRY_RUN_OK` | 2 |
| Log monitor disco | `capacidade_FULL2A_SEM_TISS_monitor_*.log` | 3 |
| Status carga real | `FULL2A_SEM_TISS_status_YYYYMMDD_HHMMSS.txt` com `CARGA_CONCLUIDA_SEM_TISS_REAL` | 4 |
| Snapshot sistema depois | `capacidade_FULL2A_SEM_TISS_depois_YYYYMMDD_HHMMSS.txt` | 9 |
| Snapshot PostgreSQL depois | `capacidade_FULL2A_SEM_TISS_postgres_depois_vps_YYYYMMDD_HHMMSS.txt` | 9 |
| Relatório de capacidade | `capacidade_FULL2A_SEM_TISS_relatorio_YYYYMMDD_HHMMSS.md` | 10 |
| Output smoke core | `smoke_core_vps_YYYYMMDD.txt` com `falhas: 0` | 8 |
| Output check public IP | `check_public_ip_vps_YYYYMMDD.txt` | 11 |

---

## 5. Rollback

### 5.1 Abortar carga em andamento (disco crítico)

```bash
# Identificar PID do processo de carga
cat /tmp/healthintel_full2a.lock

# Terminar com SIGTERM (graceful — libera o flock no EXIT)
kill -TERM <PID>

# Confirmar que parou
ps aux | grep elt_all_ans
```

### 5.2 Limpar landing se disco crítico

Somente após confirmar que os arquivos já estão em status `carregado` no PostgreSQL:

```bash
cd /opt/healthintel
make elt-status  # confirmar carregado antes de limpar

du -sh data/landing_full2a_sem_tiss/
rm -rf data/landing_full2a_sem_tiss/
df -h /
```

**Não limpar landing com arquivos em status `baixado` sem carga.**

### 5.3 Reverter tabelas consumo_ans para estado seed/demo

```bash
cd /opt/healthintel

make demo-data
make dbt-seed

cd healthintel_dbt
DBT_LOG_PATH=/tmp/healthintel_dbt_logs \
DBT_TARGET_PATH=/tmp/healthintel_dbt_target \
../.venv/bin/dbt build --select tag:core_ans --full-refresh
```

### 5.4 Reiniciar serviços API/Nginx

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  restart api nginx

bash scripts/vps/check_hml_ip.sh
```

### 5.5 Rollback completo de containers (sem apagar volumes)

```bash
cd /opt/healthintel
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.hml.yml \
  down

bash scripts/vps/deploy_hml_ip.sh
```

Não usar `down -v` com dados que devem ser preservados.

---

## 6. Limites e Regras Operacionais

| Regra | Valor | Consequência |
|-------|-------|--------------|
| Disco raiz — alerta | 75% | Monitorar mais frequentemente; planejar limpeza de landing |
| Disco raiz — parada | 90% | Abortar carga imediatamente com SIGTERM |
| PostgreSQL máximo | 220 GB | Não iniciar carga se já estiver acima |
| Landing máximo | 80 GB | Limpar runs anteriores antes de iniciar |
| TISS | Excluído | `PENDENTE_PARSER_LOAD_REAL` — nunca incluir na FULL2A padrão |
| `all_ftp` | Proibido | Não executar neste ambiente |
| `--limite 50` | Bloqueado | O script aborta com exit code 3 se detectar |
| SIB — janela | 24 meses (`ANS_ANOS_CARGA_HOT=2`) | Não ampliar para histórico completo nesta fase |
| Limpeza landing | Somente pós-`carregado` | Não limpar com arquivos ainda em `baixado` |

---

## 7. Critérios de Aceite

Marcar `[x]` somente após evidência coletada. Nunca antecipar.

### 7.1 Infraestrutura e ambiente

```
[ ] VPS 5.189.160.27 com todos os 7 serviços Docker running durante a execução
[ ] .env.hml sem placeholders, chmod 600
[ ] Firewall libera somente 22/tcp, 80/tcp e 8080/tcp publicamente
[ ] PostgreSQL não exposto publicamente (bind 127.0.0.1:5432 confirmado)
[ ] Redis não exposto publicamente (bind 127.0.0.1:6379 confirmado)
```

### 7.2 Carga de dados

```
[ ] Dry-run exibiu janela temporal correta (202501 a 202701 com ANS_ANOS_CARGA_HOT=2)
[ ] Dry-run confirmou landing ./data/landing_full2a_sem_tiss
[ ] Dry-run confirmou TISS como PENDENTE_PARSER_LOAD_REAL
[ ] Carga real finalizou com status CARGA_CONCLUIDA_SEM_TISS_REAL
[ ] sib carregou com janela de 2 anos (arquivos carregado > 0)
[ ] cadop carregou (carregado > 0)
[ ] idss carregou (carregado > 0)
[ ] igr carregou (carregado > 0)
[ ] nip carregou (carregado > 0)
[ ] tiss NÃO foi carregado (status PENDENTE_PARSER_LOAD_REAL)
[ ] Nenhuma execução concorrente ocorreu (lock respeitado)
```

### 7.3 dbt Core ANS

```
[ ] dbt compile --select tag:core_ans sem erros
[ ] make dbt-build-core concluiu sem erros em nenhum modelo core_ans
[ ] Todas as 8 tabelas consumo_ans materializadas
[ ] make dbt-test-core concluiu com zero falhas de teste
[ ] consumo_ans.consumo_operadora_360: linhas > 0
[ ] consumo_ans.consumo_score_operadora_mes: linhas > 0
[ ] consumo_ans.consumo_beneficiarios_operadora_mes: linhas > 0
[ ] consumo_ans.consumo_beneficiarios_municipio_mes: linhas > 0
[ ] consumo_ans.consumo_financeiro_operadora_trimestre: linhas > 0
[ ] consumo_ans.consumo_regulatorio_operadora_trimestre: linhas > 0
```

### 7.4 API Core com dados reais

```
[ ] make smoke-core com SMOKE_REGISTRO_ANS real retornou falhas: 0
[ ] /saude retornou HTTP 200
[ ] /prontidao retornou HTTP 200
[ ] /v1/operadoras retornou dados reais (nenhum "Operadora Demo")
[ ] /v1/meta/atualizacao reflete competência real dos dados carregados
[ ] Chave dev bloqueia /admin com HTTP 403
[ ] CORS aceita http://5.189.160.27
[ ] Frontend abre em http://5.189.160.27 (HTTP 200)
```

### 7.5 Capacidade e disco

```
[ ] Snapshot sistema antes coletado em docs/evidencias/capacidade/
[ ] Snapshot PostgreSQL antes coletado em docs/evidencias/capacidade/
[ ] Log monitor disco coletado em docs/evidencias/capacidade/
[ ] Snapshot sistema depois coletado em docs/evidencias/capacidade/
[ ] Snapshot PostgreSQL depois coletado em docs/evidencias/capacidade/
[ ] Relatório de capacidade gerado em docs/evidencias/capacidade/
[ ] Disco raiz abaixo de 75% ao final da execução
[ ] PostgreSQL total abaixo de 220 GB (confirmado no snapshot depois)
[ ] Landing total abaixo de 80 GB (ou landing limpa pós-validação)
```

### 7.6 Proteção comercial

```
[ ] Nenhuma rota de extração integral da base exposta
[ ] API key obrigatória em todos os endpoints protegidos (401 sem chave)
[ ] Rate limit ativo (API_RATE_LIMIT_FAIL_OPEN=false confirmado em .env.hml)
[ ] Paginação obrigatória em /v1/operadoras (parâmetros pagina e por_pagina)
[ ] Ambiente classificado como homologação, não produção
```

---

## 8. Definição de Pronto

O sprint está aprovado para primeira venda quando:

1. Todos os **37 critérios de aceite** da Seção 7 estiverem `[x]`.
2. Todos os **10 artefatos** da Seção 4 existirem em `docs/evidencias/capacidade/`.
3. O relatório de capacidade registrar `CARGA_CONCLUIDA_SEM_TISS_REAL`.
4. O smoke core registrar `falhas: 0`.
5. O disco raiz estiver abaixo de **75%** ao encerrar.
6. A tag `v3.5.0-core-ans-real` foi criada no repositório após todos os critérios acima.

**Pós-aprovação:** o ambiente está apto para demonstrações com dados reais. O backup externo (pgBackRest/R2) deve estar configurado antes de assinar o **primeiro contrato pagante** — este é requisito do Sprint 6 (Operação VPS).
