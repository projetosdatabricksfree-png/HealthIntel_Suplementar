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

### HIS-03.6 — Completar artefatos dbt da camada canonica

- [x] Implementar `healthintel_dbt/models/marts/dimensao/dim_localidade.sql` (table, `nucleo_ans`) com campos `cd_municipio`, `nm_municipio`, `sg_uf`, `nm_regiao` originados de `stg_sib_municipio` e enriquecidos pela seed `ref_municipio_ibge`.
- [x] Implementar `fat_beneficiario_operadora.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, competencia_id]`. Reprocessa ultimas 3 competencias a cada run (ANS frequentemente republica correcoes).
- [x] Implementar `fat_beneficiario_localidade.sql` (incremental merge, `nucleo_ans`). `unique_key: [cd_municipio, operadora_id, competencia_id]`.
- [x] Implementar intermediarios adicionais (todos ephemeral, schema `int_ans`): `int_beneficiario_operadora_enriquecido.sql`, `int_beneficiario_localidade_enriquecido.sql`, `int_idss_normalizado.sql`, `int_crescimento_operadora_12m.sql`, `int_volatilidade_operadora_24m.sql`, `int_metrica_municipio.sql`.
- [x] Criar `healthintel_dbt/seeds/ref_modalidade.csv` com as 8 modalidades ANS padronizadas.
- [x] Renomear `seeds/ufs.csv` para `seeds/ref_uf.csv` para seguir a convencao `ref_*` do PRD.
- [x] Criar `healthintel_dbt/seeds/ref_municipio_ibge.csv` com 5.570 municipios (codigo IBGE 7 digitos, `nm_municipio`, `sg_uf`, `nm_regiao`).
- [x] Criar `healthintel_dbt/seeds/ref_competencia.csv` com calendario jan/2015 a dez/2030.
- [x] Implementar macro `calcular_hhi.sql` (Indice Herfindahl-Hirschman por operadora × mercado × municipio).
- [x] Implementar macro `versao_metodologia_idss.sql` (mapeia `ano_base` para versao metodologica: `v1_faixas|v2_notas|v3_dimensoes|v4_rn505`).
- [x] Implementar macro `criar_indices.sql` (cria indices fisicos pos-materializacao para tabelas `api_ans`).
- [x] Criar `healthintel_dbt/models/staging/_fontes.yml` com declaracao de sources `bruto_ans` e freshness configuravel por tabela.
- [x] Criar arquivos de documentacao yaml faltantes: `models/intermediate/_intermediario.yml`, `marts/dimensao/_dimensao.yml`, `marts/fato/_fato.yml`, `marts/derivado/_derivado.yml`, `models/api/_api.yml` e `models/api/_exposicao.yml`.
- [x] Criar teste dbt `assert_registro_ans_6_digito.sql` (valida que todo `registro_ans` tem exatamente 6 digitos apos normalizacao).
- [x] Criar teste dbt `assert_beneficiario_nao_negativo.sql` (valida que `qt_beneficiario_ativo` >= 0 em `fat_beneficiario_operadora`).
