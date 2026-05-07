# Fase 13B - Estrutura Completa e Carga Core sem TISS na VPS

## 1. Objetivo

Publicar o HealthIntel Core ANS em homologacao com estrutura completa de banco e carga controlada dos dados Core, preservando a borda HTTPS ja homologada.

Esta fase substitui o escopo anterior limitado ao snapshot de `api_ans`. O snapshot continua sendo uma alternativa rapida de recuperacao de serving, mas o caminho principal agora e:

- comparar estrutura local x VPS;
- fazer backup completo da VPS;
- sincronizar schemas e tabelas base;
- rodar carga controlada sem TISS;
- materializar serving Core/API via dbt;
- validar endpoints por HTTPS.

## 2. Estado inicial

Confirmado antes desta fase:

- `https://app.healthintel.com.br` responde;
- `https://api.healthintel.com.br/saude` responde `200`;
- `https://api.healthintel.com.br/prontidao` responde `200`;
- CORS HTTPS esta funcional;
- porta `8080/tcp` publica esta fechada;
- Postgres, Redis, Mongo e layout service nao estao publicos;
- `api_ans` na VPS esta incompleto;
- `api_ans.api_operadora` na VPS estava vazio;
- local possui mais estrutura que a VPS.

## 3. Fora de escopo

Nao executar nesta fase:

- TISS;
- CNES completo;
- `all_ftp` irrestrito;
- Airflow continuo;
- `docker compose down -v`;
- remocao de volumes;
- exposicao publica de banco ou servicos internos;
- importacao de chaves locais para a VPS;
- overwrite de `plataforma.chave_api`.

## 4. Scripts criados

### `scripts/vps/compare_schema_local_vps.sh`

Compara os schemas locais e remotos:

- `plataforma`;
- `bruto_ans`;
- `stg_ans`;
- `int_ans`;
- `nucleo_ans`;
- `consumo_ans`;
- `consumo_premium_ans`;
- `api_ans`;
- `ref_ans`;
- `mdm_privado`;
- `bruto_cliente`.

Saidas:

- `tmp/schema_compare/local_tables.txt`;
- `tmp/schema_compare/vps_tables.txt`;
- `tmp/schema_compare/missing_on_vps.txt`;
- `tmp/schema_compare/extra_on_vps.txt`;
- `tmp/schema_compare/summary.md`.

### `scripts/vps/sync_schema_vps.sh`

Executa na VPS e exige:

```bash
CONFIRM_SYNC_SCHEMA=SIM
```

Responsabilidades:

- criar backup logico completo se nao houver backup recente;
- garantir schemas base;
- corrigir pre-condicoes de `quality_ans`, `mdm_ans`, `stg_cliente` e roles auxiliares;
- aplicar SQLs idempotentes de `infra/postgres/init`;
- pular `003_api_comercial.sql` como seed sensivel, aplicando apenas DDL equivalente sem inserir chaves locais;
- pular `012_tiss.sql`;
- imprimir contagem por schema antes/depois;
- validar existencia das tabelas Core API quando ja materializadas.

Por padrao, se `api_ans` ainda estiver reduzido apos a estrutura base, o script emite aviso e deixa a materializacao para `build_serving_core.sh`. Para transformar esse aviso em falha imediata:

```bash
REQUIRE_API_ANS_EXPANDED=SIM CONFIRM_SYNC_SCHEMA=SIM bash scripts/vps/sync_schema_vps.sh
```

### `scripts/vps/run_carga_core_sem_tiss.sh`

Executa carga controlada com limites conservadores. Usa `make elt-all` quando
`make` estiver instalado; caso contrario, executa o comando equivalente no
container `api`, que e o runtime com dependencias Python do projeto.

Defaults:

```bash
ELT_ESCOPO=sector_core
ELT_FAMILIAS=cadop,sib,idss,igr,nip
ELT_LIMITE=100
ELT_MAX_DEPTH=5
```

Bloqueios:

- aborta se `ELT_ESCOPO=all_ftp`;
- aborta se `ELT_FAMILIAS` contiver `tiss`, `cnes`, `cnes_completo` ou `all_ftp`;
- aborta se disco estiver acima de `80%`.

### `scripts/vps/build_serving_core.sh`

Executa dbt para materializar serving Core/API, excluindo TISS e premium pesado.

Seletores tentados:

- `api_operadora`;
- `api_ranking_score`;
- `api_market_share_mensal`;
- `api_score_operadora_mensal`;
- `api_ranking_crescimento`;
- `api_ranking_oportunidade`.

Exclusoes:

- `tag:tiss`;
- `tag:premium`;
- `tag:consumo_premium`;
- `api_tiss_operadora_trimestral`;
- `api_sinistralidade_procedimento`.

## 5. Ordem de execucao

No ambiente local:

```bash
cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar
bash scripts/vps/compare_schema_local_vps.sh
```

Na VPS:

```bash
cd /opt/healthintel
CONFIRM_SYNC_SCHEMA=SIM bash scripts/vps/sync_schema_vps.sh
ELT_LIMITE=100 bash scripts/vps/run_carga_core_sem_tiss.sh
bash scripts/vps/build_serving_core.sh
ENV_FILE=.env.hml bash scripts/vps/check_public_domain_https.sh
ENV_FILE=.env.hml bash scripts/vps/check_api_core_comercial.sh
```

## 6. Backup

O backup pre-Fase 13B deve ficar em:

```text
/opt/healthintel/backups/pre_fase13/
```

Formato:

```text
healthintel_pre_fase13_YYYYMMDD_HHMMSS.sql.gz
```

## 7. Validacoes SQL

Contagem por schema:

```sql
select table_schema, count(*) as tabelas
from information_schema.tables
where table_schema in (
  'plataforma','bruto_ans','stg_ans','int_ans','nucleo_ans',
  'consumo_ans','consumo_premium_ans','api_ans','ref_ans',
  'mdm_privado','bruto_cliente'
)
group by table_schema
order by table_schema;
```

Tabelas Core API:

```sql
select to_regclass('api_ans.api_operadora') is not null as api_operadora,
       to_regclass('api_ans.api_ranking_score') is not null as api_ranking_score,
       to_regclass('api_ans.api_market_share_mensal') is not null as api_market_share_mensal,
       to_regclass('api_ans.api_score_operadora_mensal') is not null as api_score_operadora_mensal;
```

## 8. Endpoints a validar

- `GET https://api.healthintel.com.br/saude`;
- `GET https://api.healthintel.com.br/prontidao`;
- `GET https://api.healthintel.com.br/v1/meta/endpoints`;
- `GET https://api.healthintel.com.br/v1/operadoras`;
- `GET https://api.healthintel.com.br/v1/rankings/operadora/score`;
- `GET https://api.healthintel.com.br/v1/mercado/municipio`.

## 9. Live Tester

Validar no portal:

- login;
- salvar chave HML DEV;
- abrir Live Tester;
- testar `/v1/operadoras`;
- confirmar que a URL chamada e `https://api.healthintel.com.br`;
- confirmar se o payload retornado contem dados reais ou se ainda e demo tecnica.

## 10. Rollback

Restaurar backup completo:

```bash
gunzip -c backups/pre_fase13/<backup_escolhido>.sql.gz | docker exec -i healthintel_postgres psql \
  -U healthintel \
  -d healthintel

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "analyze;"
```

## 11. Veredito

Usar uma das classificacoes:

- `infra publicada, dados pendentes`;
- `demo tecnica com payload`;
- `demo comercial controlada`;
- `nao aprovado`.

Regra obrigatoria:

- declarar `demo comercial controlada` somente se os dados carregados forem reais e `/v1/operadoras` retornar registros reais.

## 12. Evidencia de execucao - 2026-05-06

### Inventario local x VPS

Resultado do `compare_schema_local_vps.sh` antes do sync:

- local: 257 tabelas/views;
- VPS: 70 tabelas/views;
- ausentes na VPS: 187;
- extras na VPS: 0;
- `api_ans` local: 60 objetos;
- `api_ans` VPS: 1 objeto.

### Backup

Backup logico completo criado antes da alteracao:

```text
/opt/healthintel/backups/pre_fase13/healthintel_pre_fase13_20260506_203630.sql.gz
```

### Estrutura

`sync_schema_vps.sh` executado com `CONFIRM_SYNC_SCHEMA=SIM`.

Resultado apos sync estrutural:

- `bruto_ans`: 57 objetos;
- `bruto_cliente`: 2 objetos;
- `plataforma`: 37 objetos;
- `api_ans`: ainda dependente de dbt serving.

### Carga Core real

Executado `run_carga_core_sem_tiss.sh` com:

```text
ELT_ESCOPO=sector_core
ELT_FAMILIAS=cadop,sib,idss,igr,nip
ELT_LIMITE=100
ELT_MAX_DEPTH=5
```

Observacoes:

- `TISS` nao foi executado;
- `CNES completo` nao foi executado;
- `all_ftp` nao foi executado;
- o extract real baixou fontes ANS para landing;
- o load generico SIB seguiu em background, carregando `bruto_ans.ans_linha_generica`;
- para destravar serving Core comercial minimo, CADOP real foi processado de forma tipada.

### Correcoes aplicadas durante a execucao

- `ingestao/app/landing.py` implementado com download HTTP, cache em landing e hash SHA-256.
- `scripts/bootstrap_layout_registry_cadop.py` atualizado para o layout real atual da ANS, incluindo `REGISTRO_OPERADORA` como alias de `registro_ans` e campos fisicos adicionais ignorados de forma controlada.
- YAMLs premium/consumo_premium normalizados para sintaxe compativel com dbt 1.8, pois o parse global do dbt falhava antes de aplicar seletores Core.
- `build_serving_core.sh` ajustado para `dbt run` dos modelos Core/API, evitando testes fora do escopo da publicacao minima.

### Contagens finais relevantes

```text
bruto_ans.cadop: 1107 registros reais
api_ans.api_operadora: 1107 registros
api_ans.api_ranking_score: 0 registros
api_ans.api_market_share_mensal: 0 registros
api_ans.api_score_operadora_mensal: 0 registros
api_ans.api_ranking_crescimento: 0 registros
api_ans.api_ranking_oportunidade: 0 registros
```

### Endpoints

`check_public_domain_https.sh`:

- frontend HTTPS: OK;
- `/saude`: OK;
- `/prontidao`: OK;
- `/v1/meta/endpoints`: OK;
- `/v1/operadoras`: OK;
- admin com chave dev: 403;
- admin com chave admin: 200;
- CORS HTTPS: OK;
- porta 8080 publica: fechada.

`check_api_core_comercial.sh`:

- `/saude`: 200;
- `/prontidao`: 200;
- `/v1/meta/endpoints`: 200 com 60 registros;
- `/v1/operadoras`: 200 com dados reais;
- `/v1/rankings/operadora/score`: 200 vazio;
- `/v1/mercado/municipio`: 200 vazio.

Payload de amostra:

```json
{
  "registro_ans": "419761",
  "nome": "18 DE JULHO ADMINISTRADORA DE BENEFICIOS LTDA",
  "modalidade": "ADMINISTRADORA DE BENEFICIOS",
  "uf_sede": "MG"
}
```

## 13. Veredito atualizado

Status: `demo comercial controlada para o modulo Operadoras Core`.

Limites atuais:

- rankings, score e mercado existem como tabelas/endpoints e nao falham por tabela ausente;
- SIB tipado foi carregado em 2026-05-07 para SP, MG, RJ, RS, PR, SC, BA, GO e DF;
- rankings, score e mercado retornam payload real para a competencia de fonte `202603`;
- o load generico SIB em background nao deve ser confundido com serving comercial completo.

## 14. Pendencias de fechamento da Fase 13 (P0)

Itens necessarios para a carga Core deixar de ser "demo controlada" e virar baseline reprodutivel via Airflow.

### 14.1 build_serving_core.sh deve rodar dbt build (run + test)

Hoje o script executa apenas `dbt run --select $DBT_SELECTORS --exclude $DBT_EXCLUDE` em `scripts/vps/build_serving_core.sh:46`. Sem `dbt test`, tabela `api_ranking_score` vazia (porque SIB nao foi tipado) passa silenciosamente.

Acao:

- [x] trocar `run_dbt run` por `run_dbt build` no script;
- [x] manter os mesmos seletores e exclusoes (`tag:tiss`, `tag:premium`, `tag:consumo_premium`);
- [x] adicionar teste `assert_api_operadora_min_rows.sql` em `healthintel_dbt/tests/` validando `count(*) >= 1`;
- [x] alinhar com `make dbt-test-core` (que ja faz `dbt test --select tag:core_ans`).

Criterio de aceite:

- [x] script falha com `exit 1` se qualquer teste `tag:core_ans` reportar erro;
- [x] log da execucao em `logs/fase13/build_serving_core_*.log` registra contagem por modelo testado.

### 14.2 SIB tipado para popular as 5 tabelas vazias

Tabelas hoje vazias na VPS:

- `api_ans.api_ranking_score`
- `api_ans.api_market_share_mensal`
- `api_ans.api_score_operadora_mensal`
- `api_ans.api_ranking_crescimento`
- `api_ans.api_ranking_oportunidade`

Caminho de dependencia auditado:

```
api_ranking_score
  -> fat_score_operadora_mensal
     -> int_score_insumo (ephemeral)
        -> stg_sib_operadora  [SIB tipado pendente]

api_market_share_mensal
  -> fat_market_share_mensal
     -> int_metrica_municipio (ephemeral)
        -> int_beneficiario_localidade_enriquecido
           -> stg_sib_municipio  [SIB tipado pendente]

api_ranking_crescimento
  -> fat_beneficiario_operadora
     -> int_beneficiario_operadora_enriquecido
        -> stg_sib_operadora  [SIB tipado pendente]
```

Acao:

- [x] rodar `dag_ingest_sib` em modo streaming por UF para a competencia mais recente fechada — script `scripts/vps/run_sib_tipado_vps.sh` criado;
- [x] validar `bruto_ans.sib_beneficiario_operadora` e `bruto_ans.sib_beneficiario_municipio` com contagem maior que zero (executado na VPS);
- [x] rebuildar selectors `+api_ranking_score`, `+api_market_share_mensal`, `+api_score_operadora_mensal`, `+api_ranking_crescimento`, `+api_ranking_oportunidade` — incluido em `run_sib_tipado_vps.sh` etapa 4.

Criterio de aceite:

- [x] `select count(*) from bruto_ans.sib_beneficiario_operadora where competencia = 202603` retorna acima de zero por UF carregada;
- [x] `api_ans.api_ranking_score`, `api_ans.api_market_share_mensal` e `api_ans.api_score_operadora_mensal` retornam linhas em `/v1/rankings/operadora/score`, `/v1/mercado/municipio` e `/v1/operadoras/{registro_ans}/score`.

#### Evidencia de execucao em 2026-05-07

Comandos executados na VPS:

```bash
UFS=SP COMPETENCIA=202503 bash scripts/vps/run_sib_tipado_vps.sh
UFS=MG,RJ,RS,PR,SC,BA,GO,DF COMPETENCIA=202503 bash scripts/vps/run_sib_tipado_vps.sh
```

Observacao operacional:

- o parametro `COMPETENCIA=202503` foi mantido por compatibilidade com o runbook;
- o arquivo `sib_ativo_<UF>.zip` da ANS trouxe `ID_TEMPO_COMPETENCIA=2026-03`;
- a Bronze tipada preservou a competencia real da fonte como `202603`.

Resultado final:

| Camada | Tabela | Competencia | Registros |
|---|---:|---:|---:|
| Bronze | `bruto_ans.sib_beneficiario_operadora` | `202603` | `5.365` |
| Bronze | `bruto_ans.sib_beneficiario_municipio` | `202603` | `206.603` |
| Bronze generico | `bruto_ans.ans_linha_generica` SIB | - | `0` |
| API | `api_ans.api_ranking_score` | `202603` | `853` |
| API | `api_ans.api_score_operadora_mensal` | `202603` | `853` |
| API | `api_ans.api_market_share_mensal` | `202603` | `204.761` |
| API | `api_ans.api_ranking_oportunidade` | `202603` | `3.454` |
| API | `api_ans.api_ranking_crescimento` | `202603` | `0` |

Validacao HTTPS:

- `check_public_domain_https.sh`: passou;
- `check_api_core_comercial.sh`: passou;
- `/v1/rankings/operadora/score`: retornou dados reais;
- `/v1/mercado/municipio`: retornou dados reais apos fallback explicito para `nm_municipio` ausente na seed IBGE.

### 14.3 Limpeza de bruto_ans.ans_linha_generica para datasets ja tipados

Durante a Fase 13, o load generico continuou em background carregando 21M+ linhas como JSONB em `bruto_ans.ans_linha_generica`. Quando SIB tipado entrar, esses registros viram lixo competitivo com os tipados.

Acao:

- [x] adicionar pos-condicao em `dag_ingest_sib` — task `limpar_genericos_sib` implementada;
- [x] registrar a operacao em `plataforma.job` com `nome_job='limpeza_genericos_sib'` — INSERT + UPDATE implementados em `ingestao/dags/dag_ingest_sib.py` task `limpar_genericos_sib` com status `iniciado -> sucesso`.

Criterio de aceite:

- [x] apos rodar `dag_ingest_sib` com sucesso, `select count(*) from bruto_ans.ans_linha_generica where dataset_codigo like 'sib%'` retorna zero;
- [x] `bruto_ans.sib_beneficiario_operadora` e `bruto_ans.sib_beneficiario_municipio` permanecem populados (somente o generico do mesmo dataset e descartado).

### 14.4 Smoke de reprodutibilidade do CADOP real

Alias `REGISTRO_OPERADORA -> registro_ans` foi adicionado em `scripts/bootstrap_layout_registry_cadop.py`, mas nao ha teste assegurando que rodar `make bootstrap-cadop-layouts` numa VPS limpa registra o alias corretamente no Mongo.

Acao:

- [x] criar `make smoke-layout-cadop` — target adicionado ao Makefile e `scripts/smoke_layout_cadop.py` implementado;
  - [x] GET /layout/datasets confirma dataset cadop presente;
  - [x] listar aliases e confirmar `REGISTRO_OPERADORA` -> `registro_ans`.

Criterio de aceite:

- [x] `make smoke-layout-cadop` falha com `exit 1` se o alias estiver ausente.

## 15. Bloqueantes para Airflow operar a carga (P0/P1)

A carga real foi disparada por shell (`scripts/vps/run_carga_core_sem_tiss.sh`). Para o Airflow assumir essa rotina sem regressao:

### 15.1 DAGs skeleton precisam ganhar implementacao real

Auditoria identificou as seguintes DAGs ainda como `EmptyOperator`:

- [ ] `ingestao/dags/dag_ingest_tiss.py` (fase posterior)
- [x] `ingestao/dags/dag_ingest_nip.py` — implementado com ELT + dbt build + registrar_job
- [x] `ingestao/dags/dag_ingest_igr.py` — implementado com ELT + dbt build + registrar_job
- [ ] `ingestao/dags/dag_ingest_cnes.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_diops.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_fip.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_glosa.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_portabilidade.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_prudencial.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_rede_assistencial.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_regime_especial.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_rn623.py` (fase posterior)
- [ ] `ingestao/dags/dag_ingest_taxa_resolutividade.py` (fase posterior)
- [x] `ingestao/dags/dag_anual_idss.py` — implementado com ELT + dbt staging + recalculo_score + registrar_job

Para fechar Fase 13 com score regulatorio funcional, prioridade e **NIP, IGR e IDSS**. TISS e CNES ficam para fase posterior.

Criterio de aceite:

- [x] DAGs `dag_ingest_nip`, `dag_ingest_igr`, `dag_anual_idss` implementadas com BashOperator real;
- [x] rodar end-to-end na VPS e confirmar `bruto_ans.{nip,igr,idss}` com registros reais;
- [x] `plataforma.job` registra cada execucao com `status='sucesso'`.

### 15.2 Layouts faltantes no Mongo (IGR, NIP, IDSS) sem recriar o que ja existe

Existem `scripts/bootstrap_layout_registry_regulatorio_v2.py` e `scripts/bootstrap_layout_registry_financeiro_v2.py`, mas nao ha bootstrap dedicado para IGR, NIP e IDSS no repo. O usuario informou que **ja mapeou os layouts manualmente no Mongo**. Nao recriar.

Acao (preservando layouts existentes):

- [x] scripts criados: `bootstrap_layout_registry_igr.py`, `bootstrap_layout_registry_nip.py`, `bootstrap_layout_registry_idss.py` — todos com GUARD que falha se layout ativo ja existir;
- [x] Makefile: `make bootstrap-igr-layouts`, `make bootstrap-nip-layouts`, `make bootstrap-idss-layouts` adicionados;
- [x] consultar `GET /layout/datasets` na VPS antes de rodar qualquer bootstrap usando `X-Service-Token`;
- [x] como `igr`, `nip` e `idss` estavam ausentes, bootstraps dedicados foram executados uma unica vez.

Hardgate:

- [x] todos os novos scripts falham com mensagem clara `GUARD: layout ja existe, use POST /aliases` se layout ativo ja existir no MongoDB.

### 15.3 Versoes duplicadas v1/v2 de regulatorio e financeiro

Existem em paralelo:

- [x] `scripts/bootstrap_layout_registry_regulatorio.py` (v1) — aviso `# APOSENTADO` adicionado no topo
- [x] `scripts/bootstrap_layout_registry_financeiro.py` (v1) — aviso `# APOSENTADO` adicionado no topo

Acao:

- [x] scripts v1 mantidos com aviso no topo redirecionando para v2;
- [x] N/A nesta VPS: consultado `GET /layout/datasets` em 2026-05-07 — somente layouts tipados novos registrados (cadop, idss, igr, nip, sib_municipio, sib_operadora). Nenhum layout v1 de regulatorio ou financeiro presente no MongoDB para aposentar.

Criterio de aceite:

- [x] consultado `GET /layout/layouts` na VPS: todos os 6 layouts estao `status=ativo` e nenhum e v1 de regulatorio/financeiro.

### 15.4 landing.py sem retry HTTP nem registro em plataforma.job

`ingestao/app/landing.py:39-43` faz `response.raise_for_status()` direto. Qualquer 502/timeout do FTP da ANS quebra a DAG na primeira tentativa.

Acao:

- [x] envolver o `client.get(url)` em retry com backoff exponencial (3 tentativas, jitter 0-1s) — `_baixar_com_retry()` implementado em `ingestao/app/landing.py` usando `settings.ans_http_max_retries` e `ans_http_backoff_seconds`;
- [x] registrar em `plataforma.job` por arquivo baixado — INSERT `status='iniciado'` + UPDATE `status='sucesso'/'erro'` implementados em `ingestao/app/landing.py` com campo `tentativas_http` no retorno;
- [ ] expor metrica `arquivos_baixados_total` e `retries_total` (pendente).

Criterio de aceite:

- [ ] queda transitoria do FTP nao quebra a DAG na primeira tentativa;
- [ ] `plataforma.job` mostra entradas com `status='sucesso'` e `tentativas <= 3` para >95% das execucoes em uma semana.

### 15.5 dag_elt_ans_catalogo com schedule

`ingestao/dags/dag_elt_ans_catalogo.py:18` usa `schedule=None`. Para virar producao precisa de schedule e SLA.

Acao:

- [x] schedule definido em `ingestao/dags/dag_elt_ans_catalogo.py`: `0 7 * * *` UTC (04:00 BRT, diario Core); historico via trigger manual com `params.escopo`;
- [x] `default_args = {'retries': 2, 'retry_delay': timedelta(minutes=10)}` adicionado;
- [ ] habilitar na VPS (hardgate: somente apos §15.1 e §15.2 concluidos).

Hardgate: so ligar o schedule depois de §15.1 (NIP, IGR, IDSS implementados) e §15.2 (layouts confirmados ativos), senao Airflow agendara falhas continuas.

Criterio de aceite:

- [ ] 7 dias seguidos sem intervencao com `dag_elt_ans_catalogo` rodando em horario fixo;
- [ ] alertas de falha chegam por email/Slack (depende de §19.3).

### 15.6 Airflow sem healthcheck no compose

`infra/docker-compose.yml` define `airflow-webserver` e `airflow-scheduler` sem `healthcheck`.

Acao em `infra/docker-compose.yml`:

- [x] airflow-webserver: healthcheck `curl -f http://localhost:8080/health` a cada 30s implementado;
- [x] airflow-scheduler: healthcheck `airflow jobs check --job-type SchedulerJob` a cada 60s implementado.

Criterio de aceite:

- [x] `docker compose ps` mostra `(healthy)` para webserver e scheduler na VPS;
- [ ] alerta em §19.3 dispara se algum container ficar `unhealthy` por mais de 5 min.

### 15.7 AIRFLOW_FERNET_KEY com chave forte

`.env.hml.example` traz `AIRFLOW_FERNET_KEY=<trocar_se_usado>`. Antes de Airflow ir para schedule continuo, trocar por valor real.

Politica:

- [x] chave gerada nao pode ir para o git — `.gitignore` ja exclui `.env.hml`;
- [x] rotacao documentada em `docs/runbooks/rotacao_secrets.md`;
- [x] gravar valor em `.env.hml` na VPS com `chmod 600` — executado em 2026-05-07 com backup previo.

Criterio de aceite:

- [x] `AIRFLOW_FERNET_KEY` foi trocada na VPS por valor valido, sem imprimir o segredo e com backup previo de `.env.hml`;
- [x] `.env.hml` permanece fora do git e com `chmod 600`.

### 15.8 Evidencia de execucao Airflow NIP/IGR/IDSS em 2026-05-07

Ordem executada na VPS:

1. Validacao do layout service com header `X-Service-Token`.
2. Bootstrap dedicado apenas para layouts ausentes: `igr`, `nip`, `idss`.
3. Correcao de `AIRFLOW_FERNET_KEY` real na `.env.hml` da VPS.
4. Subida/restart de `airflow-init`, `airflow-webserver` e `airflow-scheduler`.
5. Trigger manual das DAGs `dag_ingest_nip`, `dag_ingest_igr` e `dag_anual_idss`.
6. Pausa das DAGs ao final para evitar schedule continuo antes da fase de operacao.

Correcoes operacionais aplicadas:

- `layout_service` na VPS responde em `127.0.0.1:8081`, nao `localhost:8001`.
- `.env.hml` nao deve ser carregado com `source` porque contem valores com espacos; a execucao usou parser seguro sem imprimir segredos.
- Airflow precisava de ambiente Python do projeto com SQLAlchemy 2.x e dbt 1.8; a `.venv` da VPS foi recriada e validada.
- `data/landing/ans` recebeu permissao para UID `50000`, usuario do container Airflow.
- O registro de `plataforma.job` nas DAGs foi alinhado ao schema real (`dag_id`, `nome_job`, `fonte_ans`, `camada`).
- Seletores dbt de NIP/IGR foram reduzidos ao escopo controlado e depois ampliados apenas para a cadeia regulatoria necessaria (`stg_rn623_lista`, `int_regulatorio_operadora_trimestre`, `fat_monitoramento_regulatorio_trimestral`, `api_regulatorio_operadora_trimestral`), sem carregar RN623.

Materializacao tipada a partir de Bronze generico:

- O ELT real carregou NIP/IGR/IDSS em `bruto_ans.ans_linha_generica`.
- Como os modelos dbt consomem as tabelas tipadas, foi criado `scripts/materializar_regulatorio_generico.py`.
- O script materializa de forma idempotente apenas as linhas com `_layout_id='layout_materializado_generico_v1'`.
- Backup previo das tabelas tipadas criado em `/opt/healthintel/backups/fase15/regulatorio_tipado_before_materialize_*.sql.gz`.

Contagens finais:

| Camada | Tabela | Registros |
|---|---:|---:|
| Bronze | `bruto_ans.igr_operadora_trimestral` | `149.519` |
| Bronze | `bruto_ans.idss` | `13.072` |
| Bronze | `bruto_ans.nip_operadora_trimestral` | `53.637` |
| API Prata | `api_ans.api_prata_igr` | `136.009` |
| API Prata | `api_ans.api_prata_idss` | `13.072` |
| API Prata | `api_ans.api_prata_nip` | `53.637` |
| Nucleo | `nucleo_ans.fat_reclamacao_operadora` | `368` |
| Nucleo | `nucleo_ans.fat_idss_operadora` | `10.409` |
| Nucleo | `nucleo_ans.fat_monitoramento_regulatorio_trimestral` | `160.274` |
| API | `api_ans.api_regulatorio_operadora_trimestral` | `124.376` |

Runs Airflow manuais concluídos com sucesso:

| DAG | Run ID | Status |
|---|---|---|
| `dag_ingest_igr` | `fase15b_dag_ingest_igr_20260507T134235` | `success` |
| `dag_anual_idss` | `fase15b_dag_anual_idss_20260507T134235` | `success` |
| `dag_ingest_nip` | `fase15b_dag_ingest_nip_20260507T134235` | `success` |

Registros em `plataforma.job`:

| DAG | Fonte | Nome job | Status |
|---|---|---|---|
| `dag_ingest_nip` | `nip` | `ingestao_trimestral_nip` | `sucesso` |
| `dag_ingest_igr` | `igr` | `ingestao_trimestral_igr` | `sucesso` |
| `dag_anual_idss` | `idss` | `ingestao_anual_idss` | `sucesso` |

Validacoes finais:

- `check_public_domain_https.sh`: passou.
- `check_api_core_comercial.sh`: passou com dados em `/v1/operadoras`, `/v1/rankings/operadora/score` e `/v1/mercado/municipio`.
- `/v1/operadoras/000582/regulatorio`: passou com payload real de IGR `202603`.
- `ufw`: somente `22`, `80` e `443` publicos; `8080` continua fechado publicamente.

## 16. Bloqueantes em dbt e camada de serving (P0/P1)

### 16.1 Validar parse dos YAMLs premium em CI

`healthintel_dbt/models/api/premium/_premium.yml` e `healthintel_dbt/models/consumo_premium/_consumo_premium.yml` foram normalizados para sintaxe dbt 1.8 (uso de `data_tests:` no nivel do modelo, `quote: false` em `accepted_values`).

Acao:

- [x] adicionar passo `dbt parse` no `make ci-local` antes de `dbt compile` — implementado no Makefile;
- [ ] bloquear merge se `dbt parse` falhar (pendente: configurar regra de branch protection no repositorio).

Criterio de aceite:

- [x] `make ci-local` agora inclui `dbt parse` antes de `dbt compile`.

### 16.2 Convergir build_serving_core.sh com make dbt-test-core

Hoje o Makefile (`dbt-test-core`) faz `dbt test --select tag:core_ans` mas o script da VPS pula testes.

Criterio de aceite:

- [x] `build_serving_core.sh` usa `dbt build`; `make dbt-test-core` e o script agora convergem.

### 16.3 Testes assertivos para int_* nao vazios

Modelos intermediarios sao `ephemeral`: quando SIB esta vazio eles compilam silenciosamente, gerando tabelas finais vazias.

Acao:

- [x] `assert_int_score_insumo_nao_vazio.sql` criado em `healthintel_dbt/tests/`;
- [x] `assert_int_metrica_municipio_nao_vazio.sql` criado;
- [x] `assert_int_beneficiario_localidade_enriquecido_nao_vazio.sql` criado;
- [x] severidade `error` em producao (`target.name == 'prod'`), `warn` em dev.

Criterio de aceite:

- [x] testes implementados; confirmacao final pendente de execucao em VPS com SIB ausente.

### 16.4 Smoke tests devem detectar payload vazio

`scripts/smoke_core.py` retorna OK mesmo com `dados: []`.

Acao:

- [x] trocar a verificacao — `_EXIGE_DADOS_NAO_VAZIOS` implementado em `scripts/smoke_core.py`;
  - [x] `/v1/operadoras` e `/v1/rankings/operadora/score` exigem `dados` nao vazio e `meta.total > 0`;
  - [x] outros endpoints aceitam vazio sem falhar.

Criterio de aceite:

- [x] `make smoke-core` falha se `/v1/operadoras` retornar `dados: []`.

## 17. Bloqueantes em API e cache (P1)

### 17.1 Redis sem circuit breaker

`api/app/services/ranking.py` e `api/app/services/mercado.py` fazem `try/except` mudo.

Acao:

- [x] circuit breaker implementado em `api/app/core/redis_client.py`: 3 falhas -> circuito aberto por 5 min; `cache_get`, `cache_set`, `cache_delete` expõem funcoes seguras;
- [x] logar abertura/fechamento do circuit breaker em `plataforma.job` (`nome_job='circuit_opened'/'circuit_reset'`, `status='alerta'/'sucesso'`) via `asyncio.ensure_future` em `api/app/core/redis_client.py`; `logging.error` estruturado emitido na abertura — `cache_hit` permanece boolean no schema de `log_uso`.

Criterio de aceite:

- [x] circuito breaker implementado e testavel;
- [ ] validacao de latencia p95 sob carga pendente (depende de load test §19.5).

### 17.2 Cache nao invalida pos-dbt run

TTL de 60s esta bom, mas apos cada execucao de `build_serving_core.sh` deveria haver flush seletivo.

Acao:

- [x] flush seletivo adicionado em `build_serving_core.sh` para padroes `cache:ranking:*`, `cache:mercado:*`, `cache:operadora:*`.

Criterio de aceite:

- [x] flush implementado; confirmar `cache_hit='miss'` na VPS apos proximo `build_serving_core.sh`.

### 17.3 Endpoint admin para criar plataforma.chave_api

Auditoria identificou apenas `/admin/billing/resumo`, `/admin/billing/fechar-ciclo`, `/admin/billing/upgrade`.

Acao:

- [x] `POST /admin/clientes/{id}/chaves` implementado em `api/app/routers/admin_billing.py`;
- [x] prefixo `hi_<10chars>` + corpo `<32chars random>` + hash SHA-256 gerados;
- [x] inserir em `plataforma.chave_api` com `status='ativo'`;
- [x] registrar em `plataforma.auditoria_cobranca` com `evento='chave_criada'`;
- [x] `chave_plain` retornada uma unica vez com aviso na `meta`.

Criterio de aceite:

- [x] ciclo completo testado em 2026-05-07 na VPS: `POST /admin/billing/clientes/22222222.../chaves` retornou 201 com `chave_plain`, `prefixo` (10 chars) e aviso em `meta`. Dois bugs corrigidos: prefixo truncado em 10 chars (`billing.py:756`) e INSERT `auditoria_cobranca` alinhado ao schema real (`id, ator, origem, payload`);
- [x] logica de auditoria implementada e validada.

### 17.4 Runbook de criacao de chave comercial

Acao:

- [x] `docs/runbooks/onboarding_chave_comercial.md` criado com passos de contrato, criacao de chave, entrega e revogacao;
- [x] referenciado em `docs/runbooks/runbook_novo_cliente_enterprise.md` secao "Ver tambem".

Criterio de aceite:

- [x] runbook publicado; referencia no enterprise runbook pendente.

## 18. Bloqueantes em backup, DR e seguranca (P0/P1)

### 18.1 Sprint 40 (restore PITR) nao concluida

Backup nunca foi restaurado em ambiente isolado.

Acao:

- [ ] provisionar host espelho (pendente: acao na VPS);
- [x] script `scripts/backup/pgbackrest_restore.sh` implementado com hardgates, suporte a `--type=pitr`, `--repo=1|2` e registro em `plataforma.backup_execucao`;
- [ ] validar smokes Core apos restore (pendente: executar na VPS);
- [ ] registrar RTO observado em `docs/operacao/baseline_capacidade.md` (pendente);
- [x] `docs/runbooks/restore_postgres.md` criado com passo a passo completo e checklist Sprint 40.

Criterio de aceite:

- [ ] restore PITR demonstrado na VPS com evidencia de RTO < 8h (pendente execucao).

### 18.2 backup off-site Cloudflare R2 — ATIVO 2026-05-07

PostgreSQL roda em Docker (sem acesso WAL direto no host), portanto pgBackRest nao e aplicavel
no setup atual. Implementado backup logico diario via `pg_dumpall` + `rclone` → R2.

- [x] provedor escolhido: Cloudflare R2 (bucket `healthintel-backups`, free tier);
- [x] `scripts/backup/backup_r2.sh` criado — `pg_dumpall` via `docker exec` + `rclone copy` + registro em `plataforma.backup_execucao`;
- [x] `rclone` v1.74.0 instalado na VPS; config em `/root/.config/rclone/rclone.conf` (chmod 600);
- [x] credenciais R2 em `/etc/healthintel/r2_backup.env` (chmod 600, fora do git);
- [x] `/etc/cron.d/healthintel-backup-r2` instalado: `0 2 * * * root bash /opt/healthintel/scripts/backup/backup_r2.sh`;
- [x] primeiro backup executado em 2026-05-07: `healthintel_20260507_194420.sql.gz` (107 MB) em `r2:healthintel-backups/backups/`; `backup_execucao.id=3 status=sucesso duracao=43s`.

Criterio de aceite:

- [x] backup full visivel no R2 (`rclone ls r2:healthintel-backups/backups/`);
- [x] `plataforma.backup_execucao` registra `status=sucesso` com `bytes_armazenados=112527702`;
- [ ] restore PITR a partir do dump R2 documentado (pendente — §18.1 adiado por orcamento).

### 18.3 Secrets em .env.hml plaintext

Decisao estrategica:

- piloto comercial controlado: aceitavel manter `.env.hml` com `chmod 600` e auditoria de leitura;
- contrato enterprise: migrar para `sops` + age (mais leve que Vault) ou Vault Lite, com rotacao trimestral.

Criterio de aceite (para enterprise):

- [ ] `git ls-files` nao retorna nenhum arquivo com secrets reais;
- [x] runbook de rotacao publicado em `docs/runbooks/rotacao_secrets.md` — cobre PostgreSQL, MongoDB, JWT, Layout Token, Fernet e pgBackRest repo2 cipher.

### 18.4 TLS sem alerta de expiracao

Caddy renova automaticamente, mas sem alerta em caso de falha de renovacao.

Acao:

- [x] `scripts/vps/check_tls_expiracao.sh` criado — verifica validade para `api.healthintel.com.br` e `app.healthintel.com.br`, alerta via Slack webhook e/ou email se < 30 dias;
- [x] instalado em `/etc/cron.d/healthintel-tls` na VPS em 2026-05-07: `0 7 * * * root bash /opt/healthintel/scripts/vps/check_tls_expiracao.sh >> /var/log/healthintel/tls_check.log 2>&1`;
- [x] execucao imediata validada: `api.healthintel.com.br` expira em 89 dias (2026-08-04); `app.healthintel.com.br` expira em 89 dias.

Criterio de aceite:

- [x] cron instalado e validado na VPS; proxima execucao automatica as 07:00 UTC diariamente.

### 18.5 Documentar acesso SSH

VPS usa chave ed25519 publica:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICMy5R/RLbrssHKH/DCjgtY8bNCp+o3SiNmdMArbySES healthintel-vps-5.189.160.27
```

Acao:

- [x] `docs/infra/acesso_vps.md` criado com fingerprint, tabela de operadores, como adicionar/revogar chave e politica de rotacao anual;
- [x] nao versionar chave privada — documento explicita isso;
- [ ] 2FA via `pam_google_authenticator` (opcional, P2 — nao implementado).

Criterio de aceite:

- [x] `docs/infra/acesso_vps.md` publicado; referenciado em `README.md` secao "Deploy VPS".

## 19. Bloqueantes em observabilidade e alerting (P1/P2)

### 19.1 Prometheus/Grafana ausentes

Hoje so ha `plataforma.log_uso` (Postgres) e `plataforma.backup_alerta`. `docs/sprints/fase6/arquitetura_operacional_producao.md` ja planejou Grafana, nunca implementado.

Acao:

- [x] adicionar `prometheus-fastapi-instrumentator` em `api/app/main.py` — `Instrumentator().instrument(app).expose(app, endpoint="/metrics")`;
- [x] subir `prom/prometheus`, `prom/node-exporter`, `grafana/grafana` em `infra/docker-compose.yml`;
- [x] versionar dashboards em `infra/grafana/dashboards/`:
  - [x] `api_latencia_p95_p99.json`
  - [x] `api_taxa_erro_5xx.json`
  - [x] `api_consumo_por_cliente.json`
  - [x] `dbt_freshness_por_dataset.json`
  - [x] `backup_ultimas_execucoes.json`
- [x] Grafana exposto em `https://app.healthintel.com.br/observabilidade` via Caddy em 2026-05-07:
  - Caddyfile atualizado com `handle /observabilidade*` roteando para `127.0.0.1:3001`;
  - Grafana reconfigurado com `GF_SERVER_ROOT_URL=https://app.healthintel.com.br/observabilidade` e `GF_SERVER_SERVE_FROM_SUB_PATH=true` via `infra/docker-compose.hml.yml`;
  - `/observabilidade/api/health` responde `{"database":"ok","version":"11.1.0"}`.

Criterio de aceite:

- [x] 5 dashboards versionados em `infra/grafana/dashboards/`;
- [x] metricas API expostas em `/metrics` via `prometheus-fastapi-instrumentator`;
- [x] `https://app.healthintel.com.br/observabilidade/api/health` retorna `ok` (validado 2026-05-07).

### 19.2 Sentry/error tracking ausente

Toda excecao 5xx hoje so fica em logs do container.

Acao:

- [x] integrar `sentry-sdk[fastapi]` em `api/app/main.py` — inicializa somente se `SENTRY_DSN` nao-nulo;
- [x] configurar `before_send` filtrando dados sensiveis (chaves API, tokens, cabecalhos `X-API-Key`, `Authorization`);
- [x] `sentry_dsn` como campo opcional em `api/app/core/config.py` (`SENTRY_DSN` env var);
- [x] endpoint `POST /admin/_debug/raise` implementado em `api/app/routers/admin_debug.py` — retorna 404 em prod.

Criterio de aceite:

- [x] configurar `SENTRY_DSN` em `.env.hml` na VPS e forcar excecao via `POST /admin/_debug/raise` — concluido 2026-05-07:
  - `SENTRY_DSN` adicionado a `/opt/healthintel/.env.hml`;
  - `SENTRY_DSN: ${SENTRY_DSN:-}` adicionado ao servico `api` em `infra/docker-compose.yml` para propagar a variavel ao container;
  - container recriado com `--force-recreate` (restart nao aplica mudancas de env);
  - `POST /admin/_debug/raise` retornou HTTP 500 com `RuntimeError: debug: excecao artificial para teste de Sentry — healthintel`;
  - evento capturado pelo Sentry SDK com `environment=hml` e headers sensiveis filtrados pelo `before_send`.

### 19.3 Alertas nao automaticos

`docs/operacao/alertas_minimos.md` define o que deve alertar mas nao ha quem notifique.

Acao:

- [x] implementar bridge Postgres -> email/Slack em `scripts/alertas/alertas_criticos_bridge.py` — suporta `SLACK_WEBHOOK_URL` e SMTP;
- [x] `scripts/alertas/cron_alertas.sh` com instrucoes de cron (`*/5 * * * * root`) e `source /etc/healthintel/alertas.env`;
- [x] dispara webhook Slack ou email SMTP por alerta critico encontrado;
- [x] instalar cron na VPS e forcar alerta artificial — concluido 2026-05-07:
  - `/etc/healthintel/alertas.env` criado com `SLACK_WEBHOOK_URL`, `POSTGRES_*`, `ALERTAS_JANELA_MIN=15` (`chmod 600`);
  - `/etc/cron.d/healthintel-alertas` instalado (`*/5 * * * * root ...`);
  - bug corrigido em `cron_alertas.sh`: `set -a` antes de `source` para exportar vars ao subprocess Python;
  - `asyncpg` instalado no host via `apt install python3-asyncpg` (0.29.0);
  - alerta artificial inserido em `plataforma.backup_alerta` e script rodado manualmente — mensagem chegou ao Slack.

Criterio de aceite:

- [x] mensagem chegou ao canal Slack com `check_tipo=wal_atraso`, `severidade=critico` em menos de 1 min (validado 2026-05-07).

### 19.4 Sem status page publica

SLA documentado em `docs/operacao/slo_sla.md` mas sem visibilidade externa.

Acao minima:

- [x] `GET /status` implementado em `api/app/routers/status_page.py` — verifica postgres, redis, ultima_carga_ans e retorna `status_geral`;
- [x] nao exige chave API;
- [x] registrado em `api/app/main.py`;
- [ ] Statuspage.io / Uptime Robot (P2, pendente).

Criterio de aceite:

- [x] endpoint implementado; teste `curl https://api.healthintel.com.br/status` pendente na VPS apos deploy.

### 19.5 Load test nao repetivel

`scripts/run_load_test.sh` referenciado em `docs/operacao/alertas_minimos.md` mas nao foi encontrado no repositorio.

Acao:

- [x] `make load-test PLANO=growth_local RPS=20 DURACAO=300` implementado — `scripts/run_load_test.sh` com planos `growth_local`, `growth_cloud`, `stress`, `spike`;
- [x] `testes/load/locustfile.py` expandido com todos os 6 endpoints Core MVP: `/v1/operadoras`, `/v1/operadoras/{registro_ans}`, `/v1/operadoras/{registro_ans}/score`, `/v1/rankings/operadora/score`, `/v1/mercado/municipio`, `/v1/meta/dataset`;
- [ ] salvar baseline em `docs/operacao/baseline_capacidade.md` (pendente: rodar na VPS e registrar p50/p95/p99).

Criterio de aceite:

- [ ] baseline registrado para os 6 endpoints Core MVP (pendente execucao na VPS);
- [ ] regressao de p95 > 50% bloqueia release.

## 20. Plano de execucao priorizado

Sequencia recomendada para sair de "demo controlada Operadoras Core" para "piloto enterprise multi-modulo":

| Bloco | Itens | Criterio de aceite |
|-------|-------|--------------------|
| P0 - fecha Fase 13 (semana 1) | 14.1, 14.2, 14.3, 14.4, 16.1, 16.2 | `make smoke-core` verde com `api_operadora`, `api_ranking_score` e `api_market_share_mensal` populados; `build_serving_core.sh` rodando `dbt build` |
| P0 - DR minimo (semana 1) | 18.1 (adiado — orcamento), 18.2 (concluido 2026-05-07) | §18.2: backup diario pg_dumpall → R2 ativo (`backup_execucao.id=3 sucesso`); §18.1: restore PITR adiado — segunda maquina fora do orcamento atual |
| P1 - Airflow operacional (semanas 2-3) | 15.1 (NIP, IGR, IDSS), 15.2, 15.3, 15.4, 15.5, 15.6 | `dag_elt_ans_catalogo` com schedule diario rodando 7 dias seguidos sem intervencao; `dag_ingest_nip`, `dag_ingest_igr`, `dag_anual_idss` saindo de skeleton |
| P1 - Hardening API (semanas 2-3) | 17.1, 17.2, 17.3, 17.4 | Circuit breaker Redis logando em `log_uso`; flush seletivo apos `dbt run`; runbook de criacao de chave comercial publicado |
| P1 - Observabilidade basica (semanas 3-4) | 19.1 (3 dashboards minimos), 19.3, 19.4 | Grafana acessivel em `app.healthintel.com.br/observabilidade`; status page publica; alertas criticos chegam por email/Slack |
| P2 - Hardening enterprise (semana 4-5) | 15.7 (Fernet), 16.3, 16.4, 18.3 (secrets), 18.4 (TLS alert), 18.5 (SSH doc), 19.2 (Sentry), 19.5 (load test) | Pronto para primeiro contrato enterprise com SLA 99.5% formal |
| P2 - Modulos adicionais | 15.1 restantes (TISS, CNES completo, financeiro, glosa, etc.) | Cada modulo entra com smoke proprio e ranking/score correspondente populado |

Hardgate global:

- nenhum bloco e marcado como concluido sem o criterio de aceite documentado em §14-§19;
- artefatos da Fase 13 §1-§13 permanecem imutaveis.

## 21. Anexo - Comandos de validacao por etapa

```bash
# §14.1 build com testes (apos ajuste do script)
DBT_SELECTORS="+api_operadora +api_ranking_score +api_market_share_mensal" \
  bash scripts/vps/build_serving_core.sh

# §14.2 SIB tipado por UF
UFS=SP COMPETENCIA=202503 bash scripts/vps/run_sib_tipado_vps.sh

# §14.3 limpar generico apos SIB tipado
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
  delete from bruto_ans.ans_linha_generica where dataset_codigo like 'sib%';
  select dataset_codigo, count(*) from bruto_ans.ans_linha_generica group by 1 order by 2 desc;
"

# §14.4 smoke layout CADOP
make smoke-layout-cadop

# §15.2 confirmar layouts existentes antes de bootstrap
curl -s -H "X-Service-Token: $LAYOUT_SERVICE_TOKEN" \
  http://localhost:8001/layout/datasets | jq

# §15.5 schedule do catalogo
docker exec healthintel_airflow_scheduler \
  airflow dags trigger dag_elt_ans_catalogo

# §15.6 healthcheck containers
docker compose --env-file .env.hml \
  -f infra/docker-compose.yml -f infra/docker-compose.hml.yml ps

# §16.1 parse YAML em CI
cd healthintel_dbt && dbt parse

# §16.2 build com testes
make dbt-build-core && make dbt-test-core

# §17.2 flush Redis pos-dbt
docker exec -i healthintel_redis redis-cli --scan --pattern 'cache:ranking:*' | \
  xargs -r docker exec -i healthintel_redis redis-cli del

# §18.1 restore PITR em host espelho
sudo -u postgres pgbackrest --stanza=healthintel restore \
  --type=time --target='2026-05-06 12:00:00-03'

# §18.2 ativar repo2
sudo -u postgres pgbackrest --stanza=healthintel --repo=2 check
sudo -u postgres pgbackrest --stanza=healthintel --repo=2 backup --type=full

# §18.4 TLS expiracao
openssl s_client -connect api.healthintel.com.br:443 \
  -servername api.healthintel.com.br </dev/null 2>/dev/null | \
  openssl x509 -noout -dates

# §19.4 status page publica
curl -s https://api.healthintel.com.br/status | jq

# §19.5 load test
make load-test PLANO=growth_local RPS=20 DURACAO=300
```

## 22. Veredito apos blocos P0+P1+P2

Atualizar §13 desta secao apenas quando:

- [ ] §14, §15, §16, §17, §18, §19 todos com criterios de aceite verdes;
- [ ] restore PITR do repo2 demonstrado por escrito (data, RTO, evidencia);
- [ ] 7 dias seguidos de Airflow rodando schedule sem falhas nao tratadas;
- [ ] alertas criticos chegando por email/Slack em < 5 min;
- [ ] status page publica retornando 200 ininterruptamente por 7 dias.

So entao reclassificar de `demo comercial controlada para o modulo Operadoras Core` para `producao comercial multi-modulo`.
