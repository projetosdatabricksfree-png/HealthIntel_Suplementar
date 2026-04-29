# Backup PostgreSQL - Retencao e PITR

## Objetivo

Definir a matriz operacional de retencao dos backups PostgreSQL do HealthIntel Suplementar com pgBackRest, separando claramente retencao por tempo, retencao por quantidade e janela de WAL/PITR.

Este documento complementa:

- `infra/pgbackrest/pgbackrest.conf`, template tecnico da stanza `healthintel`.
- `infra/postgres/conf/postgresql.fase7.conf`, parametros de WAL archive.
- `docs/runbooks/backup_postgres.md`, diagnostico e resposta a incidentes.
- `docs/operacao/disaster_recovery.md`, regra de DR e RPO/RTO.

## Responsabilidade

| Item | Valor |
|------|-------|
| Owner tecnico | DBA/SRE HealthIntel |
| Owner de negocio | Operacao HealthIntel |
| Stanza pgBackRest | `healthintel` |
| Repositorio local | `repo1`, `/var/lib/pgbackrest` |
| Repositorio externo | `repo2`, S3-compatible criptografado |
| RPO alvo | `1h` |
| RTO alvo MVP | ate `8h` |

## Matriz de retencao por tempo - repo1 local

| Tipo | Parametro | Valor | Unidade |
|------|-----------|-------|---------|
| Full | `repo1-retention-full-type=time` / `repo1-retention-full` | 2 | dias |
| Diff | `repo1-retention-diff` | 2 | quantidade de backups retidos |
| WAL | `archive_timeout=3600` + monitoramento | 48h ou limite de disco | horas |

O `repo1` existe para recuperacao operacional rapida na mesma VPS. Ele nao substitui o repositorio externo e nao deve ser tratado como disaster recovery.

## Matriz de retencao por tempo - repo2 externo

| Tipo | Parametro | Valor | Unidade |
|------|-----------|-------|---------|
| Full | `repo2-retention-full-type=time` / `repo2-retention-full` | 35 | dias |
| Diff | `repo2-retention-diff` | 7 | quantidade de backups retidos |
| WAL/PITR | `repo2-retention-full-type=time` cobre WAL | 35 | dias |

O `repo2` e obrigatorio antes de cliente pagante. Deve usar provedor S3-compatible, credenciais fora do git e criptografia `repo2-cipher-type=aes-256-cbc` com `repo2-cipher-pass` armazenado em cofre ou arquivo protegido fora do repositorio.

## Retencao por quantidade - diffs

| Item | Parametro | Valor | Observacao |
|------|-----------|-------|------------|
| Diff local | `repo1-retention-diff` | 2 | quantidade, nao dias |
| Diff externo | `repo2-retention-diff` | 7 | quantidade, nao dias |

`repo*-retention-diff` define quantidade de backups diferenciais retidos. Nao existe `retention-diff-type=time` no pgBackRest. Diffs anteriores ao full mais antigo mantido sao descartados automaticamente pelo ciclo de expiracao.

## Retencao de WAL e PITR

| Item | Repositorio | Periodo | Observacao |
|------|-------------|---------|------------|
| WAL archive local | repo1 | 48h | Limitado por disco; descartado junto com full antigo |
| WAL archive externo | repo2 | 35 dias | Coberto pela retencao temporal do full (`repo2-retention-full-type=time`) |
| PITR externo | repo2 | 35 dias | Permite restore point-in-time dentro da janela de 35 dias se nao houver gap de WAL |

Linhas-guia:

- `repo*-retention-full-type=time` define retencao temporal em dias para backups full.
- `repo*-retention-diff` define quantidade de diffs retidos, nao tempo.
- A retencao de WAL esta vinculada ao full base mais antigo preservado.
- O pgBackRest descarta WALs mais antigos que o full base de retencao.
- O PITR maximo possivel e igual ao periodo do full mais antigo preservado com cobertura continua de WAL.
- Qualquer gap na cadeia de WAL invalida PITR para o intervalo afetado.

## Agenda operacional

| Execucao | Frequencia | Origem |
|----------|------------|--------|
| Full | diario, `03:00` | `pgbackrest-full.timer` |
| Diff | `00:00`, `06:00`, `12:00`, `18:00` | `pgbackrest-diff.timer` |
| WAL archive | continuo, fechado no maximo a cada `3600s` | `archive_command` do PostgreSQL |
| Monitoramento | a cada 5 minutos | `pgbackrest-monitor.timer` |

O `archive-push` e executado pelo PostgreSQL por meio de `archive_command`. Timers de backup nao devem chamar `archive-push` diretamente.

## Validacao obrigatoria

Antes de declarar backup operacional:

```bash
sudo -u postgres pgbackrest --stanza=healthintel check
sudo -u postgres pgbackrest --stanza=healthintel info
sudo -u postgres pgbackrest --stanza=healthintel info --output=json
```

Consultas minimas de auditoria:

```sql
select max(iniciado_em)
from plataforma.backup_execucao
where tipo = 'wal'
  and status = 'sucesso';

select count(*)
from plataforma.backup_execucao
where tipo = 'full'
  and status = 'sucesso'
  and iniciado_em > now() - interval '26 hours';

select count(*)
from plataforma.backup_execucao
where tipo = 'diff'
  and status = 'sucesso'
  and iniciado_em > now() - interval '24 hours';
```

Criterios minimos:

- `pgbackrest check` com exit code `0`.
- Ao menos 1 full bem-sucedido nas ultimas 26h.
- Ao menos 4 diffs bem-sucedidos nas ultimas 24h depois de 24h de operacao.
- WAL arquivado ha menos de 1h.
- `pgbackrest info` exibindo `repo2` com backup full valido antes de cliente pagante.

## Custos aproximados de storage externo

Consulta realizada em `2026-04-29`. Valores sao estimativas operacionais para comparacao inicial e nao substituem simulacao no calculator do provedor, contrato comercial, impostos, requests, egress, classes de storage ou variacao regional.

| Provedor | Storage aproximado | Egress / observacao | Fonte |
|----------|--------------------|---------------------|-------|
| Cloudflare R2 Standard | `US$0.015/GB-mes` | Egress direto gratuito | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) |
| Backblaze B2 | `US$6/TB/30 dias` | Egress gratuito ate 3x storage medio; excedente `US$0.01/GB` | [Backblaze B2 Pricing](https://www.backblaze.com/cloud-storage/pricing) |
| Wasabi Pay as You Go | `US$6.99/TB-mes` (`US$0.0068/GB-mes`) | Minimo de 1 TB e retencao minima de 90 dias | [Wasabi Pricing FAQ](https://wasabi.com/pricing/faq) |
| AWS S3 Standard | estimativa operacional `US$0.023/GB-mes` em US East/N. Virginia | Requests, egress e regiao alteram custo final | [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/) |

## Regras de seguranca

- Chaves S3 e `repo2-cipher-pass` nunca entram no git.
- O arquivo materializado `/etc/pgbackrest/pgbackrest.conf` deve ter permissao restrita e owner `postgres:postgres`.
- O repositorio externo deve ter criptografia pgBackRest habilitada, mesmo que o provedor ofereca criptografia server-side.
- Backups nunca sao expostos por endpoint publico, dashboard ou artefato baixavel por cliente.

## Riscos e controles

| Risco | Controle |
|------|----------|
| Retencao local insuficiente por falta de disco | Monitorar `pg_wal` e repositorio local; repo1 e temporario |
| Gap de WAL | `pgbackrest check`, monitoramento de `pg_stat_archiver` e alerta de WAL atrasado |
| Custo externo crescer com volume | Revisao mensal do uso do bucket e simulacao por provedor |
| Credencial perdida | Secret manager com processo de recuperacao documentado |
| Restore nao testado | Sprint 40 deve validar restore full, diff e PITR em cluster isolado |

