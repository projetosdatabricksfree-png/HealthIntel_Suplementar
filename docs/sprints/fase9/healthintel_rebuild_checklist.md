# HealthIntel Suplementar — Rebuild Controlado

> **Marque `[x]` à medida que cada etapa for concluída.**
> O GitHub deve ser a **fonte única da verdade**. A VPS não pode ter hotfix invisível.

---

## Regras Obrigatórias (não negociáveis)

- [ ] Não apagar a VPS atual sem backup
- [ ] Não apagar banco sem dump
- [ ] Não apagar volumes Docker sem snapshot
- [ ] Não dropar schemas antes de backup
- [ ] Não rodar full-refresh global sem aprovação explícita
- [ ] Não criar dados fake ou mocks permanentes
- [ ] Não commitar `.env`, secrets, tokens, senhas ou API keys
- [ ] Não esconder falhas de pipeline
- [ ] Não corrigir diretamente em produção sem refletir no repositório
- [ ] Não sincronizar domínio/produção antes de validar endpoints
- [ ] Não remover endpoint do frontend/documentação para esconder falha de dados
- [ ] Não tratar `infra/postgres/init/*.sql` como migration reaplicável em banco existente

---

## Fase 1 — Corrigir o Repositório Primeiro

- [ ] Entrar no projeto local:
  ```bash
  cd /home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar
  ```

- [ ] Verificar estado atual:
  ```bash
  git status --short
  git branch --show-current
  git rev-parse HEAD
  ```

- [ ] Corrigir o arquivo `healthintel_dbt/models/marts/fato/fat_beneficiario_operadora.sql` com o bloco abaixo:
  ```sql
  -- depends_on: {{ ref('ref_competencia') }}
  -- depends_on: {{ ref('stg_sib_operadora') }}
  {{
      config(
          unique_key=['operadora_id', 'competencia'],
          incremental_strategy='delete+insert',
          on_schema_change='sync_all_columns'
      )
  }}
  select
      operadora_id,
      registro_ans,
      competencia,
      competencia as competencia_id,
      beneficiario_total as qt_beneficiario_ativo,
      beneficiario_medico as qt_beneficiario_medico,
      beneficiario_odonto as qt_beneficiario_odonto,
      beneficiario_total_12m_anterior,
      beneficiario_media_12m,
      taxa_crescimento_12m,
      volatilidade_24m
  from {{ ref('int_beneficiario_operadora_enriquecido') }}
  {% if is_incremental() %}
  where competencia in (
      select distinct competencia
      from {{ ref('stg_sib_operadora') }}
      order by competencia desc
      limit 3
  )
  {% endif %}
  ```

- [ ] Validar localmente:
  ```bash
  make dbt-parse
  ```

- [ ] Se banco local disponível, validar build:
  ```bash
  cd healthintel_dbt
  ../.venv/bin/dbt build --select fat_beneficiario_operadora consumo_beneficiarios_operadora_mes consumo_operadora_360
  cd ..
  ```

- [ ] Revisar diff antes de commitar:
  ```bash
  git diff
  ```

- [ ] Commitar e fazer push:
  ```bash
  git add healthintel_dbt/models/marts/fato/fat_beneficiario_operadora.sql
  git commit -m "fix: alinhar filtro incremental de beneficiarios à competencia real da SIB"
  git push origin main
  ```

- [ ] Confirmar que o push foi realizado com sucesso

---

## Fase 2 — Backup da VPS Atual

- [ ] Entrar na VPS:
  ```bash
  ssh healthintel-vps
  ```

- [ ] Registrar estado atual:
  ```bash
  hostname && date && df -h && free -h
  docker ps
  docker volume ls
  ```

- [ ] Criar diretório de backup:
  ```bash
  mkdir -p /opt/backups/healthintel/$(date +%Y%m%d_%H%M%S)
  export BACKUP_DIR="/opt/backups/healthintel/$(date +%Y%m%d_%H%M%S)"
  echo "$BACKUP_DIR"
  ```

- [ ] Backup dos arquivos atuais:
  ```bash
  tar -czf "$BACKUP_DIR/opt_healthintel_files.tar.gz" /opt/healthintel 2>/tmp/healthintel_backup_files.err || true
  ```

- [ ] Backup do `.env` separado:
  ```bash
  cp /opt/healthintel/.env "$BACKUP_DIR/env.backup" 2>/dev/null || true
  chmod 600 "$BACKUP_DIR/env.backup" 2>/dev/null || true
  ```

- [ ] Identificar container PostgreSQL:
  ```bash
  docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
  ```

- [ ] Carregar variáveis e fazer dump do banco:
  ```bash
  cd /opt/healthintel
  set -a && source .env && set +a
  docker exec healthintel_postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
    > "$BACKUP_DIR/healthintel_$(date +%Y%m%d_%H%M%S).dump"
  ```

- [ ] Validar que backup existe antes de prosseguir:
  ```bash
  ls -lh "$BACKUP_DIR"
  ```

  > ⛔ **Não prosseguir se não houver dump de banco + backup de arquivos.**

---

## Fase 3 — Criar Stack Limpa (sem destruir a atual)

- [ ] Renomear diretório atual como legacy:
  ```bash
  cd /opt
  mv healthintel healthintel_legacy_$(date +%Y%m%d_%H%M%S)
  ```

- [ ] Clonar repositório limpo:
  ```bash
  git clone https://github.com/projetosdatabricksfree-png/HealthIntel_Suplementar.git healthintel
  cd /opt/healthintel
  ```

- [ ] Confirmar Git válido:
  ```bash
  git status --short
  git branch --show-current
  git rev-parse HEAD
  ```

- [ ] Restaurar `.env` real a partir do backup:
  ```bash
  cp "$BACKUP_DIR/env.backup" /opt/healthintel/.env
  chmod 600 /opt/healthintel/.env
  ```

- [ ] Confirmar que `.env` não será versionado:
  ```bash
  git status --short
  ```

  > ⚠️ Se `.env` aparecer como tracked/untracked perigoso, parar e corrigir `.gitignore`.

---

## Fase 4 — Rebuild da Stack a Partir do Repositório

- [ ] Parar stack legacy:
  ```bash
  cd /opt/healthintel_legacy_*
  docker compose down
  ```

- [ ] Subir stack limpa:
  ```bash
  cd /opt/healthintel
  docker compose up -d --build
  ```

- [ ] Verificar containers e logs:
  ```bash
  docker ps
  docker logs --tail=100 healthintel_postgres || true
  docker logs --tail=100 healthintel_api || true
  docker logs --tail=100 healthintel_airflow_scheduler || true
  ```

- [ ] Validar dependências dbt:
  ```bash
  make dbt-debug
  make dbt-parse
  make audit-schema-parity
  ```

---

## Fase 5 — Decidir: Banco Limpo ou Restore

- [ ] Avaliar os dois caminhos:
  - **Caminho A — Banco limpo + carga real do zero** *(preferencial se há muitas divergências)*
  - **Caminho B — Restore do dump + normalização** *(se a carga é cara de reproduzir)*

- [ ] Decisão registrada: `_______________`

- [ ] Se Caminho A: confirmar que dump antigo está preservado antes de criar volume limpo

- [ ] Se Caminho B: restaurar dump e documentar divergências encontradas

---

## Fase 6 — Bootstrap dbt e Seeds

- [ ] Executar debug e parse:
  ```bash
  make dbt-debug
  make dbt-parse
  ```

- [ ] Executar seeds:
  ```bash
  make dbt-seed
  ```

- [ ] Executar auditoria estrita:
  ```bash
  make audit-schema-parity-strict
  ```

  > ⛔ **Se `audit-schema-parity-strict` falhar, corrigir estrutura antes de carregar dados.**

---

## Fase 7 — Carga do Pacote Mínimo Real de Dados

- [ ] Listar scripts/DAGs disponíveis:
  ```bash
  find ingestao/dags scripts ingestao -maxdepth 5 -type f | sort \
    | grep -Ei "cadop|sib|cnes|idss|igr|nip|diops|financeiro|fip|ans"
  docker exec healthintel_airflow_scheduler airflow dags list
  ```

Fontes a carregar (registrar linhas antes/depois, competência, tempo e erros):

- [ ] CADOP — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___
- [ ] SIB hot — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___
- [ ] CNES agregado — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___
- [ ] IDSS — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___
- [ ] IGR — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___
- [ ] NIP — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___
- [ ] Financeiro validado — comando: `_______________` | linhas antes: ___ | depois: ___ | status: ___

> ⚠️ Não disparar DAG inexistente. Não assumir que uma DAG carrega tudo sem verificar.

---

## Fase 8 — Build dos Marts e Camada API

- [ ] Rodar build dos marts:
  ```bash
  make dbt-build-mart
  ```

- [ ] Rodar auditoria estrita pós-build:
  ```bash
  make audit-schema-parity-strict
  ```

- [ ] Se falhar: identificar model, teste e causa — **não remover teste, não mascarar erro**

- [ ] Se precisar de full-refresh pontual (somente model específico, nunca global):
  ```bash
  cd healthintel_dbt
  DBT_LOG_PATH=/tmp/healthintel_dbt_logs \
  DBT_TARGET_PATH=/tmp/healthintel_dbt_target \
  ../.venv/bin/dbt build --select nome_do_modelo --full-refresh
  cd ..
  ```

---

## Fase 9 — Validação dos Endpoints do Frontend

Selecionar parâmetros reais do banco antes de testar:
```sql
select registro_ans from consumo_ans.consumo_operadora_360 where registro_ans is not null limit 1;
select cd_municipio from consumo_ans.consumo_beneficiarios_municipio_mes where cd_municipio is not null limit 1;
select sg_uf from consumo_ans.consumo_beneficiarios_municipio_mes where sg_uf is not null limit 1;
```

**Status possíveis:** `PRONTO` | `PARCIAL` | `VAZIO` | `BLOQUEADO` | `AUSENTE_BACKEND` | `ERRO` | `NÃO_PUBLICAR`

### Meta
- [ ] `GET /saude` — status: ___
- [ ] `GET /prontidao` — status: ___
- [ ] `GET /v1/meta/dataset` — status: ___
- [ ] `GET /v1/meta/versao` — status: ___
- [ ] `GET /v1/meta/pipeline` — status: ___
- [ ] `GET /v1/meta/endpoints` — status: ___

### Operadoras
- [ ] `GET /v1/operadoras` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/score` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/score-v3` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/score-v3/historico` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/regulatorio` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/score-regulatorio` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/regime-especial` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/portabilidade` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/financeiro` — status: ___
- [ ] `GET /v1/operadoras/{registro_ans}/score-v2` — status: ___

### Regulatório
- [ ] `GET /v1/regulatorio/rn623` — status: ___

### Mercado
- [ ] `GET /v1/mercado/municipio` — status: ___
- [ ] `GET /v1/mercado/vazio-assistencial` — status: ___

### Rankings
- [ ] `GET /v1/rankings/operadora/score` — status: ___
- [ ] `GET /v1/rankings/operadora/crescimento` — status: ___
- [ ] `GET /v1/rankings/municipio/oportunidade` — status: ___
- [ ] `GET /v1/rankings/municipio/oportunidade-v2` — status: ___
- [ ] `GET /v1/rankings/composto` — status: ___

### Rede / CNES
- [ ] `GET /v1/rede/municipio/{cd_municipio}` — status: ___
- [ ] `GET /v1/cnes/municipio/{cd_municipio}` — status: ___
- [ ] `GET /v1/cnes/uf/{sg_uf}` — status: ___

---

## Fase 10 — Cutover Seguro

Só apontar produção/domínio para a stack limpa após **todos** os itens abaixo:

- [ ] Git está limpo (sem hotfix local não versionado)
- [ ] Stack subiu exclusivamente via repositório
- [ ] `dbt parse` passa sem erros
- [ ] `dbt seed` passa sem erros
- [ ] `audit-schema-parity-strict` passa
- [ ] `dbt build mart` passa (ou falhas estão classificadas e aceitas)
- [ ] Endpoints públicos principais respondem com `PRONTO`
- [ ] Não há dados fake ou mocks permanentes
- [ ] Backup existe e foi validado
- [ ] Rollback está possível (stack legacy ainda de pé)

Após cutover:
- [ ] Registrar commit usado: `_______________`
- [ ] Registrar dump usado: `_______________`
- [ ] Registrar data/hora do cutover: `_______________`

---

## Fase 11 — Limpeza Posterior

> Somente após validar produção por pelo menos **um ciclo completo**.

- [ ] Remover diretórios legacy antigos
- [ ] Remover volumes antigos desnecessários
- [ ] Confirmar backup externo preservado
- [ ] Documentar procedimento de rebuild no repositório

---

## Entrega Final — Relatório Obrigatório

- [ ] Commit do GitHub usado como fonte da verdade: `_______________`
- [ ] Fix de `fat_beneficiario_operadora.sql` commitado: `SIM / NÃO`
- [ ] Backup criado — caminho: `_______________` | dump: `SIM / NÃO` | arquivos: `SIM / NÃO`
- [ ] Stack limpa criada em `/opt/healthintel`: `SIM / NÃO`
- [ ] `/opt/healthintel` é repo Git válido: `SIM / NÃO`

### Resultados dos comandos-chave
- [ ] `git status`: ___
- [ ] `docker ps`: ___
- [ ] `make dbt-debug`: ___
- [ ] `make dbt-parse`: ___
- [ ] `make dbt-seed`: ___
- [ ] `make audit-schema-parity-strict`: ___
- [ ] `make dbt-build-mart`: ___

### Fontes carregadas
- [ ] CADOP | [ ] SIB hot | [ ] CNES | [ ] IDSS | [ ] IGR | [ ] NIP | [ ] Financeiro

### Produtos validados
- [ ] Operadora 360 | [ ] Score | [ ] Ranking | [ ] Mercado por município
- [ ] Rede assistencial | [ ] CNES município | [ ] CNES UF | [ ] Financeiro

### Classificação final
| Categoria | Itens |
|---|---|
| ✅ Pronto para cliente | ___ |
| 🟡 Parcial | ___ |
| 🔴 Bloqueado | ___ |
| ⚠️ Riscos restantes | ___ |
| ➡️ Próximo passo seguro | ___ |
