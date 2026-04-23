# Sprint 15 — Governança de Camadas

**Status:** Não iniciada
**Objetivo:** formalizar os contratos técnicos de cada camada medallion; implementar quarentena real na prata; hardening de bronze com hash e versionamento de lote; definir gates de qualidade entre camadas.
**Critério de saída:** matriz formal de camadas documentada; quarentena implementada nos principais datasets; `_sources.yml` completo com freshness SLO; zero registros inválidos silenciosos na prata.

## Histórias

### HIS-15.1 — Hardening da Camada Bronze

- [ ] Adicionar colunas `_hash_arquivo` (SHA-256 do arquivo fonte) e `_hash_linha` (SHA-256 por linha concatenada) nas tabelas `bruto_ans.*` via DDL de migração `infra/postgres/init/013_bronze_hash.sql`.
- [ ] Criar índice único em `(competencia, _hash_arquivo)` por tabela particionada para garantir idempotência de carga.
- [ ] Atualizar `ingestao/app/carregar_postgres.py`: calcular e persistir `_hash_arquivo` antes de inserir; rejeitar lote duplicado por hash.
- [ ] Adicionar campo `hash_arquivo` em `plataforma.job` e persistir no final de cada carga bem-sucedida.
- [ ] Validar: carga duplicada do mesmo arquivo deve ser rejeitada com status `ignorado_duplicata` em `plataforma.job`.

### HIS-15.2 — Quarentena Real na Prata

- [ ] Para cada dataset principal (CADOP, SIB operadora, SIB município, IGR, NIP, IDSS, DIOPS, FIP, VDA, glosa, rede assistencial), criar tabela `bruto_ans.*_quarentena` com colunas: `id_quarentena BIGSERIAL`, `lote_id UUID`, `arquivo_origem TEXT`, `linha_original JSONB`, `motivo_rejeicao TEXT`, `regra_falhou TEXT`, `_carregado_em TIMESTAMPTZ`.
- [ ] DDL consolidado em `infra/postgres/init/014_quarentena.sql`.
- [ ] Atualizar `ingestao/app/carregar_postgres.py`: separar registros com falha estrutural (encoding, campo obrigatório nulo, tipo inválido) para quarentena antes de inserir na tabela principal.
- [ ] Criar view `plataforma.vw_resumo_quarentena` agregando contagem por tabela, lote e competência.
- [ ] Critério de qualidade: taxa de quarentena > 5% por lote deve gerar alerta em `plataforma.job` (status `sucesso_com_alertas`).

### HIS-15.3 — Gates de Qualidade entre Camadas

- [ ] Definir thresholds mínimos de aprovação por camada em `healthintel_dbt/dbt_project.yml` como variável `quality_gates`:
  - `min_taxa_aprovacao_stg: 0.95` — prata entrada: ≥ 95% das linhas bronze devem passar na staging.
  - `min_integridade_referencial_int: 1.0` — prata saída: 100% das chaves devem resolver nas dimensões.
  - `min_linhas_fato: 1` — ouro: toda fact table deve ter ao menos 1 linha por competência ativa.
- [ ] Criar testes singulares `healthintel_dbt/tests/assert_gate_qualidade_stg_*.sql` verificando taxa de aprovação.
- [ ] Testes de gate são **bloqueantes** (`severity: error`) — falha impede materialização do ouro.

### HIS-15.4 — Freshness SLO Completo

- [ ] Auditar `healthintel_dbt/models/staging/_sources.yml`: garantir que todos os 17 datasets de staging têm entrada `freshness` com `warn_after` e `error_after` definidos.
- [ ] Adicionar freshness para datasets da Fase 2: `cnes_estabelecimento`, `tiss_procedimento_trimestral`.
- [ ] Executar `dbt source freshness` e registrar baseline de latência atual por dataset.
- [ ] Criar `docs/arquitetura/freshness_slo.md` com tabela: dataset | publicação ANS | frequência | warn_after | error_after | última carga.

### HIS-15.5 — Documentação Formal de Contratos

- [ ] Criar `docs/arquitetura/contratos_por_camada.md` com matriz completa:

  | Camada | Objetivo | Transformações permitidas | Validações | Saída esperada | Risco principal | Exposição API |
  |--------|----------|--------------------------|------------|----------------|-----------------|---------------|
  | Bronze | Espelho técnico fiel | Apenas auditoria (hash, lote, encoding) | Estruturais | Tabela particionada idempotente | Dado truncado ou corrompido | Bronze API (enterprise_tecnico) |
  | Prata entrada (stg) | Dado utilizável | Cast, normalização, surrogate key, referências | Qualidade de dado | View padronizada | Domínio incorreto silencioso | Prata API (analitico) |
  | Prata saída (int) | Dado enriquecido | Joins, dedup, janelas, flags metodológicas | Consistência analítica | Ephemeral pronto para ouro | Explosão de join, duplicidade pós-dedup | Prata API enriquecida (analitico) |
  | Ouro analítico (nucleo) | Verdade analítica | Modelagem dimensional, scores, rankings | Regras de negócio | Fact/dim com SLA interno | Score fora de range, share > 100% | — (interno) |
  | Ouro serviço (api_ans) | Produto comercial | Desnormalização, índices, paginação | Contrato de schema | Tabela indexada com envelope estável | Latência, drift de schema | Ouro API (todos os planos) |

- [ ] Criar `docs/arquitetura/` se não existir.

## Entregas esperadas

- [ ] DDL `infra/postgres/init/013_bronze_hash.sql`
- [ ] DDL `infra/postgres/init/014_quarentena.sql`
- [ ] `ingestao/app/carregar_postgres.py` atualizado com hash e quarentena
- [ ] `healthintel_dbt/dbt_project.yml` com variável `quality_gates`
- [ ] Testes singulares `assert_gate_qualidade_stg_*.sql`
- [ ] `healthintel_dbt/models/staging/_sources.yml` completo com freshness SLO
- [ ] `docs/arquitetura/contratos_por_camada.md`
- [ ] `docs/arquitetura/freshness_slo.md`
- [ ] View `plataforma.vw_resumo_quarentena`

## Validação esperada

- [ ] `ruff check ingestao`
- [ ] `pytest ingestao/tests/` — zero falhas
- [ ] `dbt compile` sem erros
- [ ] `dbt test --select tag:staging` com gates de qualidade passando
- [ ] `dbt source freshness` sem `error` para datasets ativos
- [ ] Carga duplicada rejeitada com status `ignorado_duplicata` (teste manual ou automatizado)
