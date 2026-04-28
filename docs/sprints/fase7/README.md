# Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup

Este diretório materializa a governança mínima da Fase 7. A Fase 7 é aditiva e operacional: parte do baseline da Fase 5 (`v3.8.0-gov`) e prepara o HealthIntel Suplementar para rodar inicialmente em VPS, com controle forte de volume, particionamento anual no PostgreSQL, política de retenção por classe de dataset, backup profissional com pgBackRest e histórico sob demanda por cliente.

## Regra-mãe da Fase 7

- A Fase 7 não altera contratos de API, semântica de modelos dbt existentes, nomes de tabelas aprovadas nas Fases 1 a 5, nem lógica de macros já validadas.
- Toda mudança entra como artefato novo (tabelas de governança em `plataforma`, funções SQL novas em `plataforma`, DAGs novas, scripts de operação) ou ajuste declarativo de partições e políticas.
- Particionamento mensal histórico das tabelas SIB é substituído por particionamento anual, sem renomear a tabela-mãe e sem alterar a coluna `competencia` (continua `YYYYMM` inteiro).
- Não pode haver ano fixo hardcoded em código. A janela de carga é calculada dinamicamente por função SQL e parâmetro `ANS_ANOS_CARGA_HOT`.
- Política de carga é declarativa em `plataforma.politica_dataset` — código consulta a política antes de baixar/carregar.
- Histórico antigo não é carregado por padrão para todos os clientes; vira add-on premium controlado por entitlement.
- Backup somente dentro da mesma VPS não é disaster recovery. Repositório externo S3-compatible é obrigatório antes de cliente pagante.

## Decisões centrais

1. **Tabelas grandes temporais (Classe A)**: carregar apenas ano vigente + ano anterior (`ANS_ANOS_CARGA_HOT=2`). SIB operadora, SIB município, D-TISS, VDA, glosa, portabilidade.
2. **Tabelas pequenas (Classe B)**: carregar full enquanto a tabela física ficar até 5 GB. CADOP, IDSS, IGR, dimensões, seeds, referências pequenas.
3. **Tabelas de referência versionadas (Classe C)**: carregar somente a última versão vigente. TUSS procedimentos, TUSS materiais, TUSS medicamentos, DE-PARA SIP-TUSS e ROL de procedimentos.
4. **Snapshots atuais**: carregar somente o cadastro vigente. Prestadores cadastrais, QUALISS e CNES ficam como `snapshot_atual`, salvo decisão futura documentada.
5. **Histórico antigo**: vendido sob demanda como add-on premium, com backfill controlado por DAG.

## Particionamento anual obrigatório

```text
sib_beneficiario_operadora_2025  -> FOR VALUES FROM (202501) TO (202601)
sib_beneficiario_operadora_2026  -> FOR VALUES FROM (202601) TO (202701)
sib_beneficiario_operadora_2027  -> FOR VALUES FROM (202701) TO (202801)
```

Proibido criar partições mensais como `sib_beneficiario_operadora_2026_01`. A coluna `competencia` continua `YYYYMM` inteiro (ex.: `202602`).

## Janela dinâmica de carga (28/04/2026)

```text
ano_vigente = 2026
ano_inicial = 2025
ano_final = 2026
ano_preparado = 2027
competencia_minima = 202501
competencia_maxima_exclusiva = 202701
```

Na virada para 2027 a janela passa automaticamente para `[202601, 202801)` sem alteração de código.

## Sequência da Fase 7

| Sprint | Escopo | Status |
|--------|--------|--------|
| Sprint 34 | Política dinâmica de carga por dataset | Resolvida |
| Sprint 35 | Particionamento anual por `competencia YYYYMM` | Resolvida |
| Sprint 36 | Janela dinâmica de carga na ingestão | Resolvida |
| Sprint 37 | Última versão para TUSS, procedimentos e prestadores | Resolvida |
| Sprint 38 | Histórico sob demanda por cliente | Resolvida no MVP técnico |
| Sprint 39 | Backup full, diferencial e WAL archive com pgBackRest | Backlog |
| Sprint 40 | Restore, PITR e release operacional `v4.2.0-dataops` | Backlog |

## Camadas/objetos novos planejados

| Objeto | Schema | Primeira sprint | Observação |
|--------|--------|-----------------|------------|
| `politica_dataset` | `plataforma` | Sprint 34 | Tabela de governança declarativa por dataset. |
| `cliente_dataset_acesso` | `plataforma` | Sprint 38 | Entitlement por cliente. |
| `solicitacao_historico` | `plataforma` | Sprint 38 | Pedidos de backfill premium. |
| `versao_dataset_vigente` | `plataforma` | Sprint 37 | Manifesto de versão vigente de TUSS/ROL/DE-PARA/prestadores/QUALISS. `plataforma.versao_dataset` é log per-carga legado. |
| `retencao_particao_log` | `plataforma` | Sprint 35 | Auditoria de criação/destacamento de partição. |
| `backup_execucao` | `plataforma` | Sprint 39 | Auditoria de execução de backup. |
| `calcular_janela_carga_anual` | `plataforma` | Sprint 35 | Função SQL stable. |
| `criar_particao_anual_competencia` | `plataforma` | Sprint 35 | Função SQL plpgsql. |
| `preparar_particoes_janela_atual` | `plataforma` | Sprint 35 | Função SQL plpgsql. |
| `dag_historico_sob_demanda.py` | `ingestao/dags` | Sprint 38 | DAG de backfill controlado. |

## Política de retenção (resumo)

| Item | Retenção |
|------|----------|
| Full local na VPS | 2 dias |
| Diff local na VPS | 2 backups retidos (quantidade, não dias) |
| WAL local | 48h ou limite de disco |
| Full externo (S3-compat) | 35 dias |
| Diff externo | 7 backups retidos (quantidade, não dias) |
| WAL externo / PITR | 35 dias |
| Full mensal | 12 meses |
| Full anual | 3 anos |
| Evidência de restore | 90 dias |

RPO alvo: 1h. RTO alvo MVP: até 8h.

## Documentos planejados pela Fase 7

- `docs/arquitetura/politica_carga_dataset.md` — política declarativa da Sprint 34, matriz dataset x classe x objeto físico x DAG/modelo downstream.
- `docs/arquitetura/particionamento_anual_postgres.md`
- `docs/arquitetura/historico_sob_demanda_cliente.md`
- `docs/operacao/backup_retencao_postgres.md`
- `docs/operacao/disaster_recovery.md`
- `docs/runbooks/backup_postgres.md`
- `docs/runbooks/restore_postgres.md`
- `docs/releases/v4.2.0-dataops.md`

## Ajustes de revisão técnica incorporados

A Fase 7 passou por revisão técnica que resultou nos ajustes abaixo, já refletidos nos documentos de sprint correspondentes:

### 1. Retenção pgBackRest corrigida (Sprint 39)
- `repo1-retention-full-type=time` e `repo2-retention-full-type=time` explicitamente configurados para retenção temporal (dias).
- `repo*-retention-diff` documentado como **quantidade de backups diferenciais retidos**, não dias. Não há `retention-diff-type=time` no pgBackRest.
- Matriz de retenção reorganizada em três categorias: retenção por tempo, retenção por quantidade, retenção de WAL/PITR.
- Linhas-guia documentadas sobre a relação entre retenção de full e descarte automático de diffs/WAL.
- Manutenção de: full diário, diff a cada 6h, WAL archive contínuo, `archive_timeout=3600`, repositório local temporário, repositório externo S3-compatible com criptografia obrigatória.

### 2. Validação de partition pruning via EXPLAIN (Sprint 35)
- Substituído `EXPLAIN (analyze, partitions)` por `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)`.
- Critério documentado: o plano deve ler apenas a partição anual correta (ex.: `_2026`). Leitura em `_2025`, `_2027` ou `_default` faz o hardgate falhar.
- Exemplo obrigatório adicionado: `EXPLAIN (ANALYZE, VERBOSE, BUFFERS) SELECT count(*) FROM bruto_ans.sib_beneficiario_operadora WHERE competencia BETWEEN 202601 AND 202612`.

### 3. Pré-migração segura de partições SIB (Sprint 35, HIS-35.9)
- Nova história HIS-35.9 adicionada com checklist obrigatório antes de qualquer DDL destrutiva.
- Requisitos: backup pgBackRest (ou dump emergencial temporário), dry-run em cluster restaurado, medição de volume, estimativa de lock, validação de downtime, contagem antes/depois por competência, hash por amostragem, plano de rollback.
- Proibição de dropar partições mensais antigas antes de validação e backup.
- Migração por tabela espelho se a tabela-mãe atual não permitir conversão segura.
- Hardgates dedicados: contagem total e por competência, zero linhas em default, dbt build/test, smoke API SIB, hash por amostragem.

### 4. Medição automática de tabelas pequenas até 5 GB (Sprint 34, HIS-34.5)
- View `plataforma.vw_tamanho_dataset` criada para monitorar `pg_total_relation_size` de cada dataset em `plataforma.politica_dataset`.
- Tabela `plataforma.reclassificacao_dataset_pendente` para registrar recomendações de reclassificação.
- Regra: dataset `pequena_full_ate_5gb` carrega full enquanto `<= 5 GB`. Se ultrapassar, gera alerta e registro pendente — sem reclassificação automática.
- Função auxiliar `plataforma.calcular_tamanho_tabela_dataset(p_dataset_codigo)`.
- Hardgate: nenhuma tabela `pequena_full_ate_5gb` acima de 5 GB sem registro de reclassificação pendente.

### 5. Separação prestador cadastral versus fato histórico (Sprint 37)
- Reforçada a regra: prestador_cadastral, QUALISS e rede vigente entram como `snapshot_atual`.
- Qualquer fonte de movimentação histórica de rede/prestador deve ser classificada como `grande_temporal`.
- Decisão documentada em `docs/arquitetura/politica_carga_dataset.md`.
- Hardgate: todo dataset prestador/rede precisa estar classificado explicitamente como `snapshot_atual`, `referencia_versionada` ou `grande_temporal`. Classificações ambíguas proibidas.
- Histórico de prestadores/rede não entra na carga padrão da VPS se for apenas versão antiga do cadastro.

### 6. Sprint 38 dividida entre MVP técnico e pós-MVP comercial
- **MVP técnico obrigatório**: `cliente_dataset_acesso`, `solicitacao_historico`, DAG de backfill, entitlement básico, bloqueio de acesso sem entitlement, paginação obrigatória, testes do fluxo básico. A aprovação de solicitações no MVP pode ser feita via SQL/runbook operacional — o endpoint admin completo é pós-MVP.
- **Pós-MVP/comercial**: endpoint admin completo, billing-close com rubrica histórica, rate limit avançado 5× bucket, telas/admin refinado, exportação controlada.
- Fase 7 pode ser considerada operacional com o MVP técnico; comercialização plena exige os itens pós-MVP.

## Princípio de Execução

A Fase 7 não altera contrato de API, não altera semântica dos modelos dbt existentes e não renomeia tabelas existentes sem plano de migração explícito. Documentação objetiva, executável e alinhada ao runtime VPS inicial. Português-Brasil em toda entrega.
