# Disaster Recovery PostgreSQL

## Regra principal

Backup somente local não é DR.

Regra literal: `backup somente local não é DR`.

Backup somente local não é disaster recovery. Um backup armazenado apenas na mesma VPS protege contra erro logico limitado, mas nao protege contra perda da VPS, perda do volume, bloqueio do provedor, corrupcao ampla do host ou incidente operacional que afete simultaneamente banco e repositorio local.

Antes de cliente pagante, o HealthIntel Suplementar deve ter `repo2` S3-compatible ativo, criptografado e validado pelo pgBackRest.

## Escopo MVP

| Item | Decisao |
|------|---------|
| Banco protegido | PostgreSQL da plataforma HealthIntel Suplementar |
| Ferramenta | pgBackRest |
| Repositorio local | `repo1`, recuperacao rapida na mesma VPS |
| Repositorio externo | `repo2`, S3-compatible com criptografia AES-256 |
| RPO alvo | `1h` |
| RTO alvo MVP | ate `8h` |
| Evidencia obrigatoria | `pgbackrest check`, `pgbackrest info`, auditoria em `plataforma.backup_execucao` |

O RPO de `1h` depende de WAL archive continuo, `archive_timeout=3600` e monitoramento sem atraso. O RTO MVP de ate `8h` e uma meta operacional para restaurar servico em ambiente VPS-equivalente; a prova executavel de restore full, diff e PITR pertence a Sprint 40.

## Cenarios cobertos no MVP

| Cenario | Cobertura | Caminho de recuperacao |
|---------|-----------|------------------------|
| Perda logica de tabela ou dados recentes | Coberto se houver backup e WAL continuo | Restore em cluster isolado e recuperacao via dump seletivo ou PITR |
| Corrupcao parcial do cluster | Coberto se repositorios estiverem integros | Restore full/diff e replay de WAL |
| Perda do cluster PostgreSQL com VPS ainda acessivel | Coberto por repo1 ou repo2 | Restaurar em volume limpo e promover cluster |
| Perda da VPS com repo2 integro | Coberto pelo DR minimo | Provisionar VPS espelho, instalar PostgreSQL/pgBackRest e restaurar a partir do repo2 |

Restore nunca deve ser executado sobre producao. Todo teste ou recuperacao deve usar cluster isolado, volume limpo e validacao explicita antes de troca de trafego.

## Cenarios nao cobertos no MVP

| Cenario | Motivo | Mitigacao esperada |
|---------|--------|--------------------|
| Ausencia de `repo2` externo | Repo1 fica na mesma VPS | Bloquear cliente pagante ate repo2 estar operacional |
| Perda simultanea da VPS e das credenciais do repo2 | Nao ha acesso ao backup externo | Secret manager, break-glass e rotacao documentada |
| Falha regional ampla do provedor S3 escolhido | Repo2 unico nao e multi-regiao | Avaliar replicacao cross-region ou segundo provedor pos-MVP |
| Restore nao testado | Backup sem restore provado nao garante recuperacao | Sprint 40 deve executar restore full, diff e PITR |
| Comprometimento de chave de criptografia | Backup pode ficar inacessivel ou exposto | Cofre, rotacao, auditoria e separacao de acesso |

## Cadeia de decisao em incidente

1. Classificar incidente: erro logico, corrupcao parcial, perda de cluster ou perda de VPS.
2. Congelar escrita se houver risco de ampliar dano logico.
3. Consultar `plataforma.backup_execucao` e `pgbackrest info` para identificar ultimo full, ultimo diff e cobertura WAL.
4. Definir alvo de restore: ultimo estado consistente ou timestamp PITR.
5. Restaurar sempre em cluster isolado.
6. Validar banco restaurado com checks SQL, `dbt test` relevante e smoke da API.
7. Somente depois da validacao, decidir troca de trafego ou extracao seletiva de dados.
8. Registrar incidente, comandos executados, timestamps, RPO observado e RTO observado.

## Validacoes minimas antes de cliente pagante

```bash
sudo -u postgres pgbackrest --stanza=healthintel check
sudo -u postgres pgbackrest --stanza=healthintel info
```

```sql
select tipo, status, iniciado_em, finalizado_em, erro
from plataforma.backup_execucao
where tipo in ('full', 'diff', 'wal', 'check')
order by iniciado_em desc
limit 20;
```

Checklist:

- `repo2` aparece em `pgbackrest info`.
- O ultimo full externo esta dentro da janela de 35 dias.
- O ultimo diff esta dentro da janela operacional de 7h.
- O ultimo WAL arquivado esta dentro de 1h.
- Alertas de `pg_wal` nao estao criticos.
- Credenciais e senha de criptografia estao fora do git.

## Relacao com Sprint 40

A Sprint 39 documenta e configura backup, retencao, WAL archive e DR minimo. A Sprint 40 deve provar restore e PITR com evidencias:

- `docs/runbooks/restore_postgres.md`.
- `scripts/backup/pgbackrest_restore.sh`.
- `make smoke-restore`.
- Registro `plataforma.backup_execucao.tipo='restore_test'`.
- Evidencia de `dbt test` e `pytest api/tests/integration/` sobre cluster restaurado.

Ate a Sprint 40 concluir restore real, o estado correto e: backup documentado e preparado, mas restore/PITR ainda nao provado como hardgate final da Fase 7.

## Custos e escolha do repo2

Consulta realizada em `2026-04-29`. Valores abaixo sao estimativas para triagem inicial e podem mudar por regiao, volume, requests, egress, impostos ou contrato.

| Provedor | Storage aproximado | Observacao operacional | Fonte |
|----------|--------------------|------------------------|-------|
| Cloudflare R2 Standard | `US$0.015/GB-mes` | Bom candidato quando egress previsivel deve ser gratuito | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) |
| Backblaze B2 | `US$6/TB/30 dias` | Egress gratuito ate 3x storage medio; excedente `US$0.01/GB` | [Backblaze B2 Pricing](https://www.backblaze.com/cloud-storage/pricing) |
| Wasabi Pay as You Go | `US$6.99/TB-mes` (`US$0.0068/GB-mes`) | Ha minimo de 1 TB e retencao minima de 90 dias | [Wasabi Pricing FAQ](https://wasabi.com/pricing/faq) |
| AWS S3 Standard | estimativa operacional `US$0.023/GB-mes` em US East/N. Virginia | Avaliar requests, egress, regiao e classe de storage | [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/) |

Selecao inicial recomendada: priorizar provedor S3-compatible com baixo custo de egress e sem minimo operacional que distorca o MVP. A escolha final deve ser registrada junto com a configuracao real de `PGBACKREST_REPO2_*`.
