# Sprint 40 — Restore, PITR e Release Operacional `v4.2.0-dataops`

**Status:** Backlog
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** `v4.2.0-dataops` (somente após todos os hardgates verdes em CI ou ambiente reproduzível).
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov`) + Sprints 34, 35, 36, 37, 38, 39 da Fase 7.
**Pré-requisitos:** Sprints 34–39 concluídas. Backup pgBackRest operacional, WAL archive ativo, `plataforma.backup_execucao` populada, repositório externo S3-compatible disponível.
**Schema novo:** nenhum. Tabela `plataforma.backup_execucao` reutilizada para registrar `tipo='restore_test'`.
**Objetivo:** validar e documentar o ciclo completo de **restore** (full, diferencial e PITR), provar que o sistema sobe corretamente após restore, criar o runbook oficial, definir RPO/RTO declarados, instituir o hardgate de backup/restore e publicar a release `v4.2.0-dataops` que fecha a Fase 7.
**Critério de saída técnico:** runbook `docs/runbooks/restore_postgres.md` completo; `make smoke-restore` executa restore full + diff + PITR em ambiente isolado e roda `dbt test` + smoke da API após o restore com zero falhas; documento `docs/operacao/disaster_recovery.md` finalizado com RPO=1h e RTO MVP=8h declarados; hardgate `assert_backup_e_restore_validos.sh` adicionado ao pipeline de CI/CD; release notes `docs/releases/v4.2.0-dataops.md` publicadas; tag git `v4.2.0-dataops` criada **somente após** evidência de restore com sucesso.
**Critério de saída operacional:** `pgbackrest --stanza=healthintel restore --type=time --target='YYYY-MM-DD HH:MM:SS-03'` reconstrói cluster em < RTO declarado; `dbt test` e `pytest api/tests/integration/` aprovados sobre cluster restaurado; pelo menos uma evidência arquivada (`docs/releases/v4.2.0-dataops_evidencia_restore_*.txt`) com saída literal de `pgbackrest info`, `dbt test`, `pytest -q`.

## Regra-mãe da Fase 7 (não negociável nesta sprint)

- [ ] Não alterar contrato de API.
- [ ] Não alterar semântica de modelos dbt.
- [ ] Restore acontece sempre em **cluster isolado** (container/VPS espelho), nunca sobre produção.
- [ ] PITR exige cadeia contínua de WAL desde o full base — qualquer gap quebra o teste; documentar mitigação.
- [ ] Tag `v4.2.0-dataops` **não pode** ser criada antes de `pgbackrest check`, restore real e `dbt test`/`pytest` aprovados.
- [ ] Toda execução de restore é registrada em `plataforma.backup_execucao` com `tipo='restore_test'`.
- [ ] Runbook é a fonte da verdade operacional; passos são executáveis sem ambiguidade.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Operação de restore + PITR + release. |
| Schema físico | `plataforma` (reutiliza `backup_execucao`). |
| Scripts novos | `scripts/backup/pgbackrest_restore.sh`, `scripts/backup/smoke_restore.sh`. |
| Runbook | `docs/runbooks/restore_postgres.md`. |
| Documentação | `docs/operacao/disaster_recovery.md` (final), `docs/releases/v4.2.0-dataops.md`. |
| Hardgate CI | `tests/hardgates/assert_backup_e_restore_validos.sh` invocado pelo pipeline. |
| Owner técnico | DBA/SRE HealthIntel. |
| Owner de negócio | Operação HealthIntel. |
| Classificação LGPD | Operacional crítico. |
| Regra de publicação | Interna. Tag git é a entrega visível. |
| Regra de rollback | Reverter tag `v4.2.0-dataops` se hardgate quebrar; manter Fase 7 nas Sprints 34–39 (todas independentes da release). |

## Histórias

### HIS-40.1 — Runbook de restore

- [ ] Criar `docs/runbooks/restore_postgres.md`.
- [ ] Cobrir três cenários:
  - **Restore full**: cluster destruído, último full, sem WAL adicional.
  - **Restore diferencial**: full + diff mais recente.
  - **PITR**: full + diff + WAL até timestamp específico.
- [ ] Comandos exatos:
  - `pgbackrest --stanza=healthintel restore --target-action=promote`
  - `pgbackrest --stanza=healthintel restore --type=time --target='YYYY-MM-DD HH:MM:SS-03' --target-action=promote`
  - `pgbackrest --stanza=healthintel restore --type=xid --target='<xid>' --target-action=promote`
- [ ] Pré-requisitos: cluster destino vazio, espaço em disco, postgres parado, restauração em diretório `pg1-path` definido.
- [ ] Pós-restore: subir `postgres`, executar `select pg_is_in_recovery()` e `select pg_wal_replay_resume()` se necessário.
- [ ] Validação obrigatória pós-restore: `psql -c "select max(competencia) from bruto_ans.sib_beneficiario_operadora"`, `dbt test`, `pytest api/tests/integration/`.

### HIS-40.2 — Script de restore automatizado

- [ ] Criar `scripts/backup/pgbackrest_restore.sh` que:
  - aceita parâmetros `--type=full|diff|pitr` e `--target=<timestamp>` para PITR;
  - verifica que `PG_RESTORE_DATA_DIR` está vazio (proteção contra restauração em produção);
  - registra início em `plataforma.backup_execucao` (`tipo='restore_test'`, `status='em_execucao'`);
  - executa `pgbackrest restore` apropriado;
  - inicia o cluster destino;
  - executa `psql` validações + `dbt test` + `pytest api/tests/integration/`;
  - registra `status='sucesso'` ou `'falha'` com `log_resumo`/`erro`.
- [ ] Script é idempotente em segunda execução com cluster destino limpo.

### HIS-40.3 — Smoke `make smoke-restore`

- [ ] Criar alvo `make smoke-restore` no `Makefile` que executa `scripts/backup/smoke_restore.sh`.
- [ ] `smoke_restore.sh` orquestra:
  - subir cluster espelho temporário via `docker compose -f infra/docker-compose.restore.yml up -d`;
  - executar `pgbackrest_restore.sh --type=pitr --target='<calculado>'`;
  - rodar `dbt test --project-dir healthintel_dbt --profiles-dir healthintel_dbt --select tag:fato tag:api tag:premium`;
  - rodar `pytest api/tests/integration/ -q`;
  - parar e remover cluster espelho;
  - imprimir resumo final e código de saída.
- [ ] Adicionar `infra/docker-compose.restore.yml` como template do cluster espelho.

### HIS-40.4 — Hardgate CI/CD

- [ ] Criar `tests/hardgates/assert_backup_e_restore_validos.sh` que valida:
  - `pgbackrest --stanza=healthintel check` zero erros.
  - Último full em `plataforma.backup_execucao` tem `status='sucesso'`.
  - Último diff em `plataforma.backup_execucao` tem `status='sucesso'` e `iniciado_em > now() - interval '7 hours'`.
  - Último `tipo='wal'` tem `iniciado_em > now() - interval '1 hour'`.
  - Último `tipo='restore_test'` tem `status='sucesso'` e `iniciado_em > now() - interval '8 days'` (smoke semanal).
- [ ] Integrar ao `make ci-local` como passo final.

### HIS-40.5 — Documentação de DR final

- [ ] Finalizar `docs/operacao/disaster_recovery.md`:
  - declarar **RPO=1h** (perda máxima aceitável de dados em caso de incidente).
  - declarar **RTO MVP=8h** (tempo máximo para retomar operação a partir do incidente).
  - listar cenários cobertos: corrupção lógica, perda de tabela, perda de cluster.
  - listar cenários **não cobertos** pelo MVP: perda total da VPS sem repositório externo (mitigado por repo2 S3-compatible da Sprint 39), região AWS inteira.
  - documentar próximos passos pós-MVP (replicação síncrona, multi-região).
- [ ] Atualizar matriz de retenção em `docs/operacao/backup_retencao_postgres.md` referenciando RPO/RTO.

### HIS-40.6 — Release notes `v4.2.0-dataops`

- [ ] Criar `docs/releases/v4.2.0-dataops.md`.
- [ ] Conteúdo obrigatório:
  - Sumário executivo: o que muda (storage dinâmico, particionamento anual, backup, restore, PITR).
  - Lista das Sprints 34–40 com status `[x]` apenas após hardgates verdes.
  - Migrações requeridas: `029_*` a `034_*`.
  - Variáveis de ambiente novas: `ANS_ANOS_CARGA_HOT`, `PGBACKREST_REPO2_*`.
  - Procedimento de upgrade em VPS existente (passo a passo).
  - Plano de rollback (reverter para baseline `v3.8.0-gov`).
- [ ] Anexar evidências literais (saídas de comando) em arquivos `docs/releases/v4.2.0-dataops_evidencia_*.txt` (gitignore opcional para arquivos > 1 MB).

### HIS-40.7 — Criação da tag git

- [ ] Após todos os hardgates verdes, criar tag anotada `git tag -a v4.2.0-dataops -m "Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup"`.
- [ ] **Hardgate proibitivo**: não criar a tag antes de executar localmente:
  - `make ci-local` (zero falhas);
  - `make smoke-restore` (zero falhas);
  - `tests/hardgates/assert_backup_e_restore_validos.sh` (zero falhas);
  - `pytest testes/regressao/test_endpoints_fase4.py testes/regressao/test_endpoints_fase5.py` (zero falhas).
- [ ] Push da tag exige autorização explícita (não é função do agente).

### HIS-40.8 — Comunicação operacional

- [ ] Atualizar `docs/sprints/fase7/README.md`: marcar Sprint 40 como concluída quando hardgates passarem.
- [ ] Adicionar entrada no `CHANGELOG` (se existir) referenciando `v4.2.0-dataops` e Sprints 34–40.
- [ ] Adicionar comentário em `CLAUDE.md` informando que Fase 7 está concluída e que a Fase 6 comercial pode prosseguir contra base operacional já backed-up.

## Entregas esperadas

- [ ] `docs/runbooks/restore_postgres.md`
- [ ] `scripts/backup/pgbackrest_restore.sh`
- [ ] `scripts/backup/smoke_restore.sh`
- [ ] `infra/docker-compose.restore.yml`
- [ ] Alvo `make smoke-restore` no `Makefile`
- [ ] `tests/hardgates/assert_backup_e_restore_validos.sh`
- [ ] `docs/operacao/disaster_recovery.md` (versão final)
- [ ] `docs/releases/v4.2.0-dataops.md`
- [ ] Atualização de `docs/sprints/fase7/README.md`
- [ ] Tag git `v4.2.0-dataops` (somente após hardgates verdes)

## Validação esperada (hard gates)

- [ ] `make smoke-restore` zero falhas; saída literal arquivada em `docs/releases/v4.2.0-dataops_evidencia_restore_<data>.txt`.
- [ ] Restore full em cluster espelho conclui em < 8h em VPS-equivalente; saída de `pgbackrest restore` arquivada.
- [ ] Restore diff em cluster espelho conclui em < 4h.
- [ ] PITR para timestamp específico conclui sem gaps de WAL.
- [ ] `dbt test --project-dir healthintel_dbt --profiles-dir healthintel_dbt` zero falhas no cluster restaurado.
- [ ] `pytest api/tests/integration/ -q` zero falhas no cluster restaurado.
- [ ] `pytest testes/regressao/test_endpoints_fase4.py testes/regressao/test_endpoints_fase5.py -q` zero falhas (não regressão).
- [ ] `tests/hardgates/assert_backup_e_restore_validos.sh` zero falhas.
- [ ] `select count(*) from plataforma.backup_execucao where tipo='restore_test' and status='sucesso' and iniciado_em > now() - interval '8 days'` >= 1.
- [ ] `make ci-local` zero falhas.
- [ ] Documento `docs/operacao/disaster_recovery.md` declara explicitamente RPO=1h e RTO MVP=8h.
- [ ] Tag `v4.2.0-dataops` criada **somente após** todos os itens acima verdes.
- [ ] `git diff --stat v3.8.0-gov..v4.2.0-dataops -- healthintel_dbt/models healthintel_dbt/macros api/app/services/{operadora,mercado,ranking,regulatorio,financeiro,rede,cnes,tiss,prata,bronze}.py` saída vazia para serviços que não foram alvo de mudança nesta fase.

## Distinção Estado Atual vs Estado-Alvo

| Eixo | Estado atual | Estado-alvo da Sprint 40 |
|------|--------------|--------------------------|
| Restore | Não testado. | Testado em cluster espelho com sucesso (full, diff, PITR). |
| RPO/RTO | Não declarado. | RPO=1h, RTO MVP=8h documentados em `disaster_recovery.md`. |
| Hardgate CI | Sem checagem de backup. | `assert_backup_e_restore_validos.sh` integrado ao `make ci-local`. |
| Runbook | Sem runbook de restore. | Runbook executável com comandos exatos. |
| Tag git | `v3.8.0-gov` (Fase 5). | `v4.2.0-dataops` (Fase 7) criada com evidências. |
| Modelos dbt / API | Baseline `v3.8.0-gov`. | Idem (sem alteração). |
| Comunicação | Fase 7 em backlog. | Fase 7 declarada concluída no `README` e `CLAUDE.md`. |

## Anti-padrões explicitamente rejeitados nesta sprint

- Criar a tag `v4.2.0-dataops` antes de executar restore real.
- Executar restore em cluster de produção como "atalho de teste".
- Pular `dbt test` e `pytest` pós-restore.
- Documentar RPO/RTO sem evidência de teste.
- Reduzir cobertura do hardgate CI por "demora" — restore-test pode ser semanal, não diário, mas não pode ser ausente.
- Push da tag por agente sem autorização explícita do usuário.
- Marcar hardgates `[x]` antes de executar os comandos correspondentes.

## Resultado Esperado

Sprint 40 fecha a Fase 7. O ciclo completo de backup → WAL → restore → PITR é provado, RPO=1h e RTO MVP=8h são declarados com evidência, runbook operacional está pronto e a tag `v4.2.0-dataops` (criada somente após todos os hardgates verdes) marca o release operacional. A partir desse ponto, o produto HealthIntel Suplementar pode rodar em VPS com volume controlado, particionamento anual, histórico premium controlado por entitlement, backup profissional e restore validado — pré-requisito para abrir cliente pagante em produção.
