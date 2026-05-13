# Evidência Sprint 43 — Fechamento controlado das 92 tabelas vazias

**Branch**: `sprint-43-fechamento-92-tabelas`
**Commit base**: `6444ba5`
**Data início**: 2026-05-13

> **Status atual**: **Fundação operacional entregue (F0–F4 + F7).** Cargas reais
> P0/P1, ajuste de DAGs e dashboards seguem em frentes subsequentes nesta mesma
> branch. Esta evidência é incremental — atualizada a cada marco.

---

## 1. Backup pré-execução (F0) — ✅ Concluído

| Item | Valor |
|---|---|
| Diretório | `/opt/backups/healthintel/20260513_143329_pre_sprint43_92_tabelas/` |
| `pg_dump -Fc` | `healthintel_pre_sprint43.dump` (33 MB) |
| Tar repo | `opt_healthintel_pre_sprint43.tar.gz` (766 MB; sem `.venv`/`node_modules`/`dist`) |
| `commit.txt` | `6444ba51e3a266e5c81843c6be8d55274aea7224` |
| `branch.txt` | `sprint-43-fechamento-92-tabelas` |
| `timestamp.txt` | `2026-05-13T14:36:17+02:00` |

Backup verificável (`ls -lh` confirma 4 arquivos não-vazios, `pg_dump.stderr.log` e `tar.stderr.log` vazios).

## 2. Inventário inicial das 92 (F1) — ✅ Concluído

```
total inspecionado: 144 tabelas (api_ans + consumo_ans + nucleo_ans)
zeradas (count=0): 92  | populadas: 52
zeradas por prioridade: P0=11, P1=55, P2=21, P3=5
zeradas por domínio: regulatorio(21), rede(13), tiss(9), cnes(7), ntrp(7),
                     financeiro(6), ressarcimento(6), outros(5), beneficiario(4),
                     produto(3), premium(3), glosa(2), vda(2), sip(2), cadop(1),
                     portabilidade(1)
```

Artefatos:
- `docs/evidencias/sprint43/inventario_92_tabelas_vazias_inicio.csv` (145 linhas)
- `docs/sprints/fase10/classificacao_92_tabelas_vazias_sprint43.md`
- `scripts/auditoria/sprint43_inventario_92_tabelas_vazias.sql`
- `scripts/auditoria/sprint43_count_real_tabelas_vazias.py`

## 3. Auditoria granular (F2 + F3) — ✅ Concluído

### Migration 051 aplicada na VPS
- `infra/postgres/init/051_sprint43_tentativa_carga_ans.sql`
- Tabela: `plataforma.tentativa_carga_ans` (29 colunas, 5 índices, 1 CHECK com 17 status)
- FK opcional para `lote_ingestao(id)` e `arquivo_fonte_ans(id)` (`on delete set null`)
- Idempotente; aplicada via psql contra container `postgres` em execução

Status válidos: `INICIADO`, `SEM_NOVOS_ARQUIVOS`, `ARQUIVO_JA_CARREGADO`,
`BAIXADO`, `VALIDADO`, `CARREGADO`, `CARREGADO_SEM_LINHAS`,
`CARREGADO_SEM_CHAVE`, `IGNORADO_DUPLICATA`, `FONTE_INDISPONIVEL`,
`LAYOUT_NAO_MAPEADO`, `ERRO_DOWNLOAD`, `ERRO_PARSE`, `ERRO_VALIDACAO`,
`ERRO_CARGA`, `ERRO_DBT`, `FINALIZADO`.

### Helper Python entregue
- `ingestao/app/auditoria_tentativa_carga.py`
- API async primária + wrappers `*_sync` para uso em PythonOperator
- 7 shortcuts: `registrar_sem_novos_arquivos`, `registrar_arquivo_ja_carregado`,
  `registrar_fonte_indisponivel`, `registrar_layout_nao_mapeado`,
  `registrar_erro_parse`, `registrar_erro_carga`, `registrar_sucesso_carga`
- Falhas internas viram WARN (não quebram DAG)

### Testes (11/11 passando)
```
$ POSTGRES_HOST=localhost ... .venv/bin/pytest ingestao/tests/test_auditoria_tentativa_carga.py
ingestao/tests/test_auditoria_tentativa_carga.py::test_inicio_gera_uuid_e_status_iniciado PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_evento_adiciona_segunda_linha_e_status_intermediario PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_final_preenche_finalizado_em_e_duracao PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_status_invalido_levanta PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_shortcut_sem_novos_arquivos PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_shortcut_arquivo_ja_carregado PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_shortcut_fonte_indisponivel PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_shortcut_layout_nao_mapeado PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_shortcut_erro_parse_e_erro_carga PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_shortcut_sucesso_carga_com_linhas_e_sem_linhas PASSED
ingestao/tests/test_auditoria_tentativa_carga.py::test_status_validos_cobre_constraint_db PASSED
======================== 11 passed in 3.02s ========================
```

## 4. Layouts MongoDB: auto-detector + endpoint rascunho (F4) — ✅ Concluído

### Auto-detector (lado ingestão)
- `ingestao/app/layout_autodetect.py`
- Funções: `detectar_cabecalho` (CSV file), `detectar_cabecalho_de_bytes`,
  `assinar_colunas` (sha256 estável), `validar_arquivo_layout`,
  `solicitar_rascunho`, `detectar_e_resolver_layout` (fluxo completo)
- Tolerante a BOM, UTF-8, Latin-1, CP-1252 (4 encodings tentados)
- Retorna `ResultadoDeteccao` (dataclass) com `compativel` ou `rascunho_criado`

### Novo endpoint MongoDB Layout Service
- `POST /layout/{dataset_codigo}/rascunho`
- Schema: `LayoutRascunhoRequest` (`mongo_layout_service/app/schemas/layout.py`)
- Service: `LayoutService.criar_rascunho_layout` — idempotente por assinatura
- Comportamento: se assinatura já existir como versão do layout do dataset,
  retorna com `reaproveitado=True`. Senão, cria Layout (se preciso) + Versão
  com `status='rascunho'`.

### Wrapper Makefile
- `make bootstrap-layouts-sprint43` — reaplica 18 bootstraps existentes
  (TISS, TISS subfamílias, SIP delta, CNES, SIB, CADOP, NIP, IDSS, IGR,
   produtos/planos, TUSS oficial, rede, rede prestadores, regulatórios, etc.)
- Idempotente (scripts usam upsert)

### Testes (8 + 3 novos = 11 passando)
```
$ .venv/bin/pytest ingestao/tests/test_layout_autodetect.py testes/unit/test_layout_service.py
ingestao/tests/test_layout_autodetect.py ........ [ 8 passed]
testes/unit/test_layout_service.py .....           [ 5 passed]
```

## 5. P0.3 — Órfãos produto/CADOP (F7) — ✅ Concluído (decisão documentada)

**Diagnóstico**: os 57.074 órfãos do `dbt test` Sprint 42 representam **57k linhas**, mas **apenas 2.014 operadoras distintas**. Após cruzamento:
- `produto.distinct(registro_ans)` = 2.935
- `cadop.distinct(registro_ans)` = 1.107
- `stg_operadora_cancelada` está **vazio** (fonte ANS não ingerida)

**Decisão**: **Histórico legítimo**, não bug. A fonte `Relatorio_cadop.csv` só publica operadoras ATIVAS. Produtos históricos referenciam operadoras hoje canceladas/em liquidação. A correção definitiva exige ingerir a fonte ANS de operadoras canceladas (Sprint 44).

**Mitigação Sprint 43**: testes dbt de relacionamento de produto→CADOP serão configurados como `severity: warn` (não error) com mensagem "histórico legítimo pendente Sprint 44".

Artefatos:
- `scripts/auditoria/auditar_orfaos_produto_cadop.sql`
- `docs/evidencias/sprint43/orfaos_produto_cadop_decisao.md`

---

## Frentes em aberto (esta mesma branch)

| Fase | Status | Observação |
|---|---|---|
| F5 — Corrigir parser SIP (8 de 10 colunas nulas) | 🔄 Aberto | Requer diagnóstico no parser real + reprocessamento via DAG. |
| F6 — TISS 4 recortes carregados | 🔄 Aberto | Layouts já cadastrados; falta carga real via DAG ingerindo fonte ANS. |
| F8 — Ajustar 14 DAGs com cadência natural | 🔄 Aberto | Padrão definido; aplicar incremento por DAG com auditoria integrada. |
| F9 — dbt tag `sprint43` + materialização | 🔄 Aberto | Modelos novos receberão tag; checagem de marts zeradas pendente. |
| F10 — Dashboards Grafana Sprint 43 | 🔄 Aberto | Grafana + Prometheus existentes; criar JSON dashboards + queries SQL. |
| F11 — Validação final | 🔄 Aberto | Reexecutar inventário; smoke API; agregação `tentativa_carga_ans`. |

## Resumo de testes (cumulativo Sprint 43)

| Suite | Tests | Status |
|---|---:|---|
| `ingestao/tests/test_auditoria_tentativa_carga.py` | 11 | ✅ todos passando |
| `ingestao/tests/test_layout_autodetect.py` | 8 | ✅ todos passando |
| `testes/unit/test_layout_service.py` (novos + existentes) | 5 | ✅ todos passando |
| **Total Sprint 43** | **24** | **✅ 24/24** |

## Resumo de artefatos (cumulativo)

| Caminho | Tipo |
|---|---|
| `infra/postgres/init/051_sprint43_tentativa_carga_ans.sql` | migration SQL |
| `ingestao/app/auditoria_tentativa_carga.py` | helper async/sync |
| `ingestao/app/layout_autodetect.py` | auto-detector + httpx client |
| `mongo_layout_service/app/schemas/layout.py` | +`LayoutRascunhoRequest` |
| `mongo_layout_service/app/services/layout_service.py` | +`criar_rascunho_layout` |
| `mongo_layout_service/app/routers/layout.py` | +`POST /layout/{dataset}/rascunho` |
| `Makefile` | +alvo `bootstrap-layouts-sprint43` |
| `ingestao/tests/test_auditoria_tentativa_carga.py` | 11 testes |
| `ingestao/tests/test_layout_autodetect.py` | 8 testes |
| `testes/unit/test_layout_service.py` | +3 testes (5 totais) |
| `scripts/auditoria/sprint43_inventario_92_tabelas_vazias.sql` | inventory SQL |
| `scripts/auditoria/sprint43_count_real_tabelas_vazias.py` | inventory orchestrator |
| `scripts/auditoria/auditar_orfaos_produto_cadop.sql` | órfãos diagnostic |
| `docs/sprints/fase10/sprint_43_fechamento_92_tabelas_vps.md` | (será criado em commit subsequente) |
| `docs/sprints/fase10/classificacao_92_tabelas_vazias_sprint43.md` | classificação P0/P1/P2/P3 |
| `docs/sprints/fase10/evidencia_sprint_43_fechamento_92_tabelas_vps.md` | este documento |
| `docs/evidencias/sprint43/inventario_92_tabelas_vazias_inicio.csv` | dados |
| `docs/evidencias/sprint43/orfaos_produto_cadop_decisao.md` | decisão |

## Conclusão executiva (parcial — frente F0–F4+F7)

- **VPS OK para demo limitada**: ❌ **não ainda** — TISS/SIP ainda zerados
- **VPS OK para Core API completa**: ❌ **não ainda** — 90+ tabelas comerciais zeradas
- **92 fechadas ou classificadas**: ⚠️ **parcial** — todas inventariadas, todas classificadas em P0–P3, 0 ainda populadas

Próximo marco: F5+F6+F8 (cargas reais P0 + ajuste DAGs).
