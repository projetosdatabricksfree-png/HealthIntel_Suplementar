# Evidência VPS — Release 0.9 Core ANS Comercial

**Status**: ⏳ **PENDENTE — aguarda deploy real**

Este arquivo será preenchido com evidência da execução real na VPS
`5.189.160.27` quando o operador aprovar o deploy. Estrutura abaixo serve como
**checklist obrigatório**.

---

## 1. Snapshot pré-deploy (a coletar)

```
$ ssh root@5.189.160.27 "cd /opt/healthintel && \
    git status && \
    git rev-parse --short HEAD && \
    git log -1 --oneline && \
    docker compose -f infra/docker-compose.yml ps && \
    df -h | head -10 && \
    free -h"
```

- [ ] hostname:
- [ ] branch atual:
- [ ] commit pré-deploy (SHA):
- [ ] containers UP/healthy:
- [ ] uso de disco:
- [ ] uso de memória:

## 2. Backup pré-deploy (a executar)

```
$ ssh root@5.189.160.27 "cd /opt/healthintel && bash scripts/backup/run.sh"
```

- [ ] caminho backup: `/opt/backups/healthintel/YYYYMMDD_HHMMSS_pre_release_0_9/`
- [ ] tamanho pg_dump:
- [ ] tamanho tar repo:
- [ ] logs sem erro:

## 3. Deploy controlado (a executar)

```
$ ssh root@5.189.160.27 "cd /opt/healthintel && \
    git fetch origin && \
    git checkout v0.9.0-core-ans && \
    make compose-config && \
    docker compose -f infra/docker-compose.yml exec -T postgres \
        psql -U healthintel -d healthintel \
        < infra/postgres/init/060_release_0_9_grants_consumo_ans.sql && \
    docker compose restart api"
```

- [ ] checkout v0.9.0-core-ans: OK
- [ ] migration 060 aplicada (NOTICE 12 tabelas SELECT em 1 schema):
- [ ] containers reiniciados:
- [ ] API responde /saude com 200:

## 4. Smoke pós-deploy (a executar)

```
$ HEALTHINTEL_TARGET_URL=http://5.189.160.27:8080 \
    HEALTHINTEL_API_KEY=<chave-hml> \
    bash scripts/smoke/smoke_api_release_0_9.sh
```

- [ ] PASS:
- [ ] FAIL:
- [ ] log salvo em: `docs/evidencias/release_0_9/smoke_api_release_0_9_vps.log`

## 5. Hard gate contra VPS (a executar)

```
$ ssh root@5.189.160.27 "cd /opt/healthintel && make release-0-9-hardgate"
```

- [ ] hard gate consumo_ans: SUCESSO/FALHA
- [ ] auditor grants empírico: SUCESSO/FALHA (vazamentos: N)
- [ ] auditor endpoints API: SUCESSO/FALHA

## 6. Airflow / DAGs (a verificar)

- [ ] TISS DAGs pausadas (esperado):
- [ ] SIB DAGs pausadas/parciais (esperado):
- [ ] DAGs core (Sprint 43) com schedule ativo:

## 7. Conclusão (a preencher após execução)

| Item | Status |
|---|---|
| VPS no SHA `v0.9.0-core-ans` | ⏳ |
| Todos containers UP/healthy | ⏳ |
| Backup pré-deploy validado | ⏳ |
| Migration 060 aplicada idempotente | ⏳ |
| Smoke API VPS PASS=18 FAIL=0 | ⏳ |
| Hard gate consumo_ans SUCESSO | ⏳ |
| Auditor grants 0 vazamentos | ⏳ |
| Auditor endpoints API SUCESSO | ⏳ |

**Conclusão**: ⏳ A preencher quando deploy real for executado e validado.

---

## Comandos para o operador executar

Sequência fechada — copiar/colar e executar com supervisão:

```bash
# Backup pré-deploy
ssh root@5.189.160.27 "cd /opt/healthintel && bash scripts/backup/run.sh 2>&1 | tee /tmp/backup_pre_release_0_9.log"

# Checkout da tag
ssh root@5.189.160.27 "cd /opt/healthintel && git fetch origin && git checkout v0.9.0-core-ans"

# Aplicar migration 060
ssh root@5.189.160.27 "cd /opt/healthintel && \
    docker compose -f infra/docker-compose.yml exec -T postgres \
        psql -U healthintel -d healthintel \
        < infra/postgres/init/060_release_0_9_grants_consumo_ans.sql 2>&1 | tee /tmp/migration_060.log"

# Restart API
ssh root@5.189.160.27 "cd /opt/healthintel && docker compose -f infra/docker-compose.yml restart api"

# Smoke pós-deploy (rodar do laptop ou da VPS)
HEALTHINTEL_TARGET_URL=http://5.189.160.27:8080 \
    HEALTHINTEL_API_KEY="$HML_DEV_API_KEY" \
    bash scripts/smoke/smoke_api_release_0_9.sh

# Hard gate na VPS
ssh root@5.189.160.27 "cd /opt/healthintel && make release-0-9-hardgate"

# Trazer evidências geradas na VPS para o repo local (se for o caso)
scp root@5.189.160.27:/opt/healthintel/docs/evidencias/release_0_9/*.md \
    docs/evidencias/release_0_9/
```
