# Sprint 03 — Camada Canonica Inicial

**Status:** Concluida
**Objetivo:** consolidar a primeira camada dbt canonica para preparar marts e API.
**Criterio de saida:** `staging`, `intermediate`, `snapshot` e dimensoes core ficam consistentes para `CADOP`.

## Historias

### HIS-03.1 — Declarar fontes e documentacao dbt

- [x] Criar `healthintel_dbt/models/staging/_sources.yml`.
- [x] Criar `healthintel_dbt/models/staging/_staging.yml`.
- [x] Criar `healthintel_dbt/models/exposures.yml`.

### HIS-03.2 — Implementar staging core

- [x] Implementar `healthintel_dbt/models/staging/stg_cadop.sql`.
- [x] Implementar `stg_sib_operadora.sql`.
- [x] Implementar `stg_sib_municipio.sql`.

### HIS-03.3 — Implementar camada intermediate e snapshot

- [x] Implementar `healthintel_dbt/models/intermediate/int_operadora_canonica.sql`.
- [x] Implementar `healthintel_dbt/snapshots/snap_operadora.sql`.
- [x] Validar o fluxo completo com `dbt compile` e `dbt test`.

### HIS-03.4 — Materializar dimensoes iniciais

- [x] Implementar `healthintel_dbt/models/marts/dimensao/dim_operadora_atual.sql`.
- [x] Implementar `dim_competencia.sql`.
- [x] Consolidar chave canonica por operadora e competencia.

### HIS-03.5 — Criar macros, seeds e testes de apoio

- [x] Implementar macros em `healthintel_dbt/macros/`.
- [x] Criar seed inicial em `healthintel_dbt/seeds/ufs.csv`.
- [x] Criar teste singular inicial em `healthintel_dbt/tests/test_score_nao_negativo.sql`.
