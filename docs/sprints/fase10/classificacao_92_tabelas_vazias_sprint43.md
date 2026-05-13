# Classificação das 92 tabelas vazias — Sprint 43

**Data**: 2026-05-13
**Branch**: `sprint-43-fechamento-92-tabelas`
**Commit base**: `6444ba5`
**Auditoria origem**: Sprint 42 (validação read-only)

## Resumo

| | Total |
|---|---:|
| Tabelas em `api_ans`+`consumo_ans`+`nucleo_ans` | 144 |
| Populadas (`count(*) > 0`) | 52 |
| **Zeradas (`count(*) = 0`)** | **92** |

## Distribuição por prioridade

| Prioridade | Tabelas | Critério |
|---|---:|---|
| **P0** | 11 | Fechar nesta sprint obrigatoriamente — bloqueiam MVP comercial |
| **P1** | 55 | Tentar carregar; documentar se fonte indisponível |
| **P2** | 21 | Classificar + preparar carga (marts derivadas, premium) |
| **P3** | 5 | Logado; fora do escopo desta sprint |

## Distribuição por domínio (zeradas)

| Domínio | Tabelas |
|---|---:|
| regulatorio | 21 |
| rede | 13 |
| tiss | 9 |
| cnes | 7 |
| ntrp | 7 |
| financeiro | 6 |
| ressarcimento | 6 |
| outros | 5 |
| beneficiario | 4 |
| produto | 3 |
| premium | 3 |
| glosa | 2 |
| vda | 2 |
| sip | 2 |
| cadop | 1 |
| portabilidade | 1 |

## P0 — Fechar obrigatoriamente (11 tabelas)

### TISS — 4 recortes (9 tabelas)

| schema | tabela | camada | DAG |
|---|---|---|---|
| api_ans | api_prata_tiss_procedimento | api | dag_ingest_tiss |
| api_ans | api_tiss_ambulatorial_operadora_mes | api | dag_ingest_tiss |
| api_ans | api_tiss_hospitalar_operadora_mes | api | dag_ingest_tiss |
| api_ans | api_tiss_operadora_trimestral | api | dag_ingest_tiss |
| api_ans | api_tiss_plano_mes | api | dag_ingest_tiss |
| api_ans | api_premium_tiss_procedimento_tuss_validado | api/premium | dag_ingest_tiss + dbt |
| consumo_ans | consumo_tiss_utilizacao_operadora_mes | consumo | dag_ingest_tiss |
| nucleo_ans | fat_tiss_procedimento_operadora | nucleo | dag_ingest_tiss + dbt |
| nucleo_ans | mart_tiss_procedimento | nucleo | dag_ingest_tiss + dbt |

**Aceite**: cada uma com `count(*) > 0` e colunas críticas não-nulas. Fonte ANS TISS subfamílias documentada com 3 variantes históricas no MongoDB.

### SIP (2 tabelas)

| schema | tabela | camada | DAG |
|---|---|---|---|
| api_ans | api_sip_assistencial_operadora | api | dag_ingest_sip_delta |
| consumo_ans | consumo_sip_assistencial_operadora | consumo | dag_ingest_sip_delta |

**Aceite**: parser SIP corrige 8 de 10 colunas vazias. Bronze não fica `CARREGADO` com >50% colunas críticas nulas. Se fonte ANS realmente não traz `registro_ans`, classificar `FONTE_SEM_CHAVE_OPERADORA` e documentar.

### Bloqueador adicional não-tabela

- **57.074 órfãos `registro_ans` em `stg_produto_caracteristica` vs `stg_cadop`**: decisão binária bug vs histórico legítimo (F7).

## P1 — Tentar carregar (55 tabelas)

CSV completo em `docs/evidencias/sprint43/inventario_92_tabelas_vazias_inicio.csv`.

DAGs alvo (com schedule revisado para cadência natural):

| Domínio | Tabelas | DAG | Schedule |
|---|---:|---|---|
| regulatorio | 21 | `dag_ingest_nip`, `dag_anual_idss`, `dag_ingest_rn623`, `dag_ingest_regulatorios_complementares` | @monthly/@yearly/@quarterly |
| cnes | 7 | `dag_ingest_cnes` | @monthly |
| ntrp | 7 | `dag_ingest_precificacao_ntrp` | @monthly |
| financeiro | 6 | `dag_ingest_diops`, `dag_ingest_fip` | @quarterly |
| ressarcimento | 6 | `dag_ingest_ressarcimento_sus` | @monthly |
| beneficiario | 4 | `dag_ingest_sib`, `dag_ingest_beneficiarios_cobertura` | @monthly |
| rede | 13 | `dag_ingest_rede_assistencial`, `dag_ingest_rede_prestadores` | @monthly |
| glosa | 2 | `dag_ingest_glosa` | @monthly |
| vda | 2 | `dag_ingest_vda` | @monthly |
| portabilidade | 1 | `dag_ingest_portabilidade` | @monthly |

Critério de aceite P1: cada tabela com **tentativa registrada** em `plataforma.tentativa_carga_ans` com status conclusivo (`CARREGADO`, `SEM_NOVOS_ARQUIVOS`, `FONTE_INDISPONIVEL`, `LAYOUT_NAO_MAPEADO`, etc.). Populá-la com `count(*) > 0` é o objetivo, mas não pré-requisito se a fonte real está inacessível **e** isso está justificado.

## P2 — Classificar + preparar (21 tabelas)

Marts derivadas estruturais (`fat_*`, `mart_*`, `dim_*`) que dependem de upstream P0/P1 carregado. Premium (3 tabelas). Acreditação/qualidade/rede operacional secundária.

Critério de aceite P2: tentativa registrada + modelo dbt confere materialização correta. População depende de upstream completo (deferida para Sprint 44 se necessário).

## P3 — Documentado e logado (5 tabelas)

`outros` (5 tabelas) sem classificação automática: a maioria tabelas estruturais legadas ou seeds que requerem mapeamento manual. Documentadas no CSV; tentativa diária criada via DAG existente; população não obrigatória nesta sprint.

## Critério de fechamento da Sprint 43

A sprint **não exige** populá-las 92/92 magicamente. Exige que **cada uma**:
- Tenha tentativa registrada em `plataforma.tentativa_carga_ans` com status conclusivo
- Tenha classificação válida (P0/P1/P2/P3) + motivo
- Tenha DAG diária/cadência natural agendada com auditoria
- Tenha layout cadastrado no MongoDB (ou status `LAYOUT_NAO_MAPEADO` com rascunho criado)
- Tenha validação dbt rodando (modelo materializado quando upstream existe)

P0 é mais duro: **count(*) > 0** real é obrigatório.
