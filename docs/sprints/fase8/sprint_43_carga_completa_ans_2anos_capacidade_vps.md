# Sprint 43: Carga ANS 2 anos e Teste de Capacidade VPS

## Objetivo

Executar carga controlada dos dados públicos da ANS seguindo a política de governança da Fase 8, medindo se uma VPS de aproximadamente 542 GB suporta o sistema com dados reais, sem confundir download massivo com carga efetiva no PostgreSQL.

Após a execução parcial de 2026-04-29, a carga operacional corrigida passa a ser chamada de `FULL2A_SEM_TISS_REAL`, porque TISS real foi excluído da carga padrão até existir parser/load validado para `tiss_ambulatorial`.

## Critérios de Aceite

- [x] Scripts de monitoramento de capacidade criados em `scripts/capacidade/`.
- [ ] Snapshot do sistema antes/depois gerado corretamente para `FULL2A_SEM_TISS`.
- [ ] Carga respeitando `ANS_ANOS_CARGA_HOT=2` para tabelas grandes carregáveis.
- [ ] Carga completa para tabelas pequenas carregáveis.
- [ ] Relatório final de consumo de recursos gerado.
- [ ] `make dbt-build`, `make dbt-test` e `make smoke` aprovados após a carga.

## Execução corrigida

A execução padrão deve ser feita por `make carga-ans-padrao-vps`, que encapsula:

- lock operacional com `flock` em `/tmp/healthintel_full2a.lock`;
- landing isolada por padrão em `./data/landing_full2a_sem_tiss`;
- remoção de TISS real da carga padrão;
- bloqueio de comando real com `--limite 50`;
- status final `CARGA_CONCLUIDA_SEM_TISS_REAL` quando a carga sem TISS terminar.

Comandos seguros após a correção:

```bash
bash -n scripts/capacidade/*.sh
make carga-ans-padrao-vps-dry-run
make capacidade-snapshot NIVEL=FULL2A_SEM_TISS MOMENTO=antes
make carga-ans-padrao-vps
make capacidade-snapshot NIVEL=FULL2A_SEM_TISS MOMENTO=depois
make capacidade-relatorio NIVEL=FULL2A_SEM_TISS
make dbt-build
make dbt-test
make smoke
```

## Escopo da FULL2A_SEM_TISS_REAL

### Famílias carregáveis na carga padrão

- Grande temporal: `sib`.
- Pequenas/full até 5 GB: `cadop`, `idss`, `igr`, `nip`, `sip`, `diops`, `rpc`, `caderno_ss`, `plano`.

### Pendentes por parser/load

- `tiss`
  - status: `PENDENTE_PARSER_LOAD_REAL`;
  - dataset real do discovery: `tiss_ambulatorial`;
  - contrato de carga/dbt existente: `tiss_procedimento`, `bruto_ans.tiss_procedimento_trimestral`, `stg_tiss_procedimento`;
  - decisão: fora da FULL2A padrão até implementação e validação de parser/load real.

O alvo opcional `make carga-ans-padrao-vps-incluir-pendentes` existe apenas para operação experimental e exige `CONFIRMAR_PENDENTES=SIM`. Esse alvo não conta como aceite da `FULL2A_SEM_TISS_REAL`.

## Atualização — Execução parcial abortada em 2026-04-29

A execução parcial de 2026-04-29 foi útil como teste de download e capacidade inicial, mas não pode ser considerada carga completa.

### Processos concorrentes encontrados

Foram identificadas três execuções simultâneas de `make carga-ans-padrao-vps`:

- duas execuções antigas com:

```bash
.venv/bin/python scripts/elt_all_ans.py --escopo sector_core --familias sib,tiss --limite 50
```

- uma execução mais recente com:

```bash
.venv/bin/python scripts/elt_all_ans.py --escopo sector_core --familias sib,tiss --limite 999999
```

Todos os processos foram encerrados com `kill -TERM`.

### Evidências preservadas

- Snapshot parcial: `docs/evidencias/capacidade/capacidade_FULL2A_parcial_backlog_tiss_20260429_141316.txt`.
- Status parcial: `docs/evidencias/capacidade/FULL2A_status_parcial_backlog_tiss.txt`.
- `data/landing`: 91G.
- Arquivos em landing: 4239.
- Disco: 58%.
- PostgreSQL database size: 113GB.

### Estado por família após parada

| Família | Status observado |
| :--- | :--- |
| `cadop` | `carregado=2` |
| `idss` | `carregado=3` |
| `igr` | `carregado=2`, `erro_carga=3` |
| `nip` | `carregado=7`, `erro_carga=14` |
| `sib` | `carregado=23`, `baixado=32`, `baixado_sem_parser=1`, `ignorado_duplicata=100` |
| `tiss` | `baixado=4155`, `carregado=0` |

### Diagnóstico

O fluxo `scripts/elt_all_ans.py` executa discovery, extract e load por meio de `ingestao/app/elt/orchestrator.py`. O problema não foi ausência de etapa de load no script, mas divergência de contrato:

- `ingestao/app/elt/classifier.py` classifica TISS ambulatorial como `dataset_codigo = tiss_ambulatorial`;
- `ingestao/app/carregar_postgres.py` possui função e contrato de carga para `tiss_procedimento`;
- o dbt lê `bruto_ans.tiss_procedimento_trimestral` em `stg_tiss_procedimento`.

Sem parser/load real para `tiss_ambulatorial`, a carga de TISS não deve ser prometida como parte da FULL2A padrão.

### Decisão

- A execução foi abortada com segurança.
- A FULL2A total com TISS real segue não concluída.
- A medição operacional permitida nesta sprint é `FULL2A_SEM_TISS_REAL`.
- TISS real só entra novamente após implementação de parser/load verdadeiro e teste com poucos arquivos antes de carga massiva.

## Riscos Identificados

- Reutilizar `data/landing` contaminaria a medição com os 91G do TISS parcial.
- Rodar TISS sem parser/load real consome disco sem medir crescimento real do PostgreSQL.
- Executar cargas concorrentes causa disputa de disco, duplicidade operacional e evidência inconsistente.
- Marcar a sprint como concluída sem `dbt-build`, `dbt-test`, `smoke` e relatório final geraria falso aceite operacional.

## Critérios de Aceite Corrigidos

- [ ] Dry-run exibe janela `202501` até `202701` em 2026 com `ANS_ANOS_CARGA_HOT=2`.
- [ ] Dry-run exibe landing padrão `./data/landing_full2a_sem_tiss`.
- [ ] Lock impede duas execuções simultâneas de `make carga-ans-padrao-vps`.
- [ ] Carga real não executa com `--limite 50`.
- [ ] `tiss` aparece como `PENDENTE_PARSER_LOAD_REAL`, fora da carga padrão.
- [ ] Relatório final diferencia baixado, carregado, pendente de parser, erro e duplicidade.
- [ ] Status final sem TISS real usa `CARGA_CONCLUIDA_SEM_TISS_REAL`.
