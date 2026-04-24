# Sprint 24 — consumo_ans: Camada de Entrega para Clientes

**Status:** Concluída
**Objetivo:** criar o schema `consumo_ans` com tabelas Gold desnormalizadas prontas para entrega ao cliente; o cliente conecta com Power BI, Metabase, Python, psql ou qualquer ferramenta de sua escolha — o HealthIntel entrega o dado curado e o contrato de acesso, não a visualização; automatizar refresh via Airflow; criar role de acesso restrito; validar conectividade e smoke E2E.
**Critério de saída:** 8 modelos em `consumo_ans` compilando via dbt; `make consumo-refresh` executando sem erro; `make smoke-consumo` zero falhas; contrato de dados publicado em `docs/arquitetura/consumo_ans_guia.md`.

## Histórias

### HIS-24.1 — Schema consumo_ans e Role de Acesso

- [x] Criar DDL `infra/postgres/init/022_consumo_ans.sql`:
  ```sql
  CREATE SCHEMA IF NOT EXISTS consumo_ans;

  CREATE ROLE healthintel_cliente_reader NOLOGIN;

  GRANT USAGE ON SCHEMA consumo_ans TO healthintel_cliente_reader;
  GRANT SELECT ON ALL TABLES IN SCHEMA consumo_ans TO healthintel_cliente_reader;
  ALTER DEFAULT PRIVILEGES IN SCHEMA consumo_ans GRANT SELECT ON TABLES TO healthintel_cliente_reader;

  -- Exemplo por cliente: usuário LOGIN individual herda a role de grupo.
  -- Credenciais devem ser provisionadas fora do DDL, via secret manager/processo operacional.
  CREATE USER cliente_exemplo LOGIN;
  GRANT healthintel_cliente_reader TO cliente_exemplo;

  -- Garantir isolamento: sem acesso às camadas internas
  REVOKE ALL ON SCHEMA bruto_ans FROM healthintel_cliente_reader;
  REVOKE ALL ON SCHEMA stg_ans FROM healthintel_cliente_reader;
  REVOKE ALL ON SCHEMA int_ans FROM healthintel_cliente_reader;
  REVOKE ALL ON SCHEMA nucleo_ans FROM healthintel_cliente_reader;
  REVOKE ALL ON SCHEMA plataforma FROM healthintel_cliente_reader;
  ```
- [x] Role `healthintel_cliente_reader`: role de grupo `NOLOGIN`, read-only exclusivo em `consumo_ans`; cada cliente deve receber usuário próprio `LOGIN` e `GRANT healthintel_cliente_reader TO <cliente>`.
- [x] Usuários cliente não acessam `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans` ou `plataforma`.
- [x] Adicionar `consumo_ans` em `healthintel_dbt/dbt_project.yml` como schema gerenciado com macro `generate_schema_name` existente.
- [x] Criar pasta `healthintel_dbt/models/consumo/` com `_consumo.yml` base.

### HIS-24.2 — Modelos de Entrega em consumo_ans

Cada modelo materializa como `table` em `consumo_ans`. Tag: `consumo`. Colunas com nomes legíveis — sem prefixos técnicos internos.

- [x] Criar `healthintel_dbt/models/consumo/consumo_operadora_360.sql`:
  - Source: `nucleo_ans.mart_operadora_360`
  - Grão: `(registro_ans, competencia)` — visão mensal consolidada da operadora
  - Colunas analíticas sem colunas técnicas internas; histórico entregue conforme contrato do cliente
  - Post-hook: índice em `(registro_ans, competencia)`

- [x] Criar `healthintel_dbt/models/consumo/consumo_beneficiarios_operadora_mes.sql`:
  - Source: `nucleo_ans.fat_beneficiario_operadora`
  - Grão: `(registro_ans, competencia)`
  - Colunas: `registro_ans`, `razao_social`, `modalidade`, `competencia`, `qt_beneficiarios`, `variacao_mensal_pct`, `variacao_12m_pct`

- [x] Criar `healthintel_dbt/models/consumo/consumo_beneficiarios_municipio_mes.sql`:
  - Source: `nucleo_ans.fat_beneficiario_localidade`
  - Grão: `(registro_ans, cd_municipio, competencia)`
  - Colunas: `registro_ans`, `razao_social`, `cd_municipio`, `nome_municipio`, `uf`, `competencia`, `qt_beneficiarios`

- [x] Criar `healthintel_dbt/models/consumo/consumo_financeiro_operadora_trimestre.sql`:
  - Source: `nucleo_ans.fat_financeiro_operadora_trimestral`
  - Grão: `(registro_ans, trimestre)`
  - Colunas: `registro_ans`, `razao_social`, `trimestre`, `receita_total`, `sinistralidade_pct`, `despesas_administrativas`, `resultado_operacional`, `margem_operacional_pct`

- [x] Criar `healthintel_dbt/models/consumo/consumo_regulatorio_operadora_trimestre.sql`:
  - Source: `nucleo_ans.mart_regulatorio_operadora`
  - Grão: `(registro_ans, trimestre)`
  - Colunas: `registro_ans`, `razao_social`, `trimestre`, `nivel_alerta`, `tendencia_regulatoria`, `qtd_processos_ativos`, `multas_total`, `idss_score`, `indice_reclamacao`

- [x] Criar `healthintel_dbt/models/consumo/consumo_rede_assistencial_municipio.sql`:
  - Source: `nucleo_ans.mart_rede_assistencial`
  - Grão: `(registro_ans, cd_municipio, competencia)`
  - Colunas: `registro_ans`, `razao_social`, `cd_municipio`, `nome_municipio`, `uf`, `competencia`, `qt_prestadores`, `densidade_por_10k`, `gap_leitos_cnes`, `classificacao_vazio`

- [x] Criar `healthintel_dbt/models/consumo/consumo_oportunidade_municipio.sql`:
  - Source: `nucleo_ans.mart_mercado_municipio`
  - Grão: `(cd_municipio, competencia)`
  - Colunas: `cd_municipio`, `nome_municipio`, `uf`, `competencia`, `qt_beneficiarios_total`, `penetracao_pct`, `score_oportunidade`, `qt_operadoras_ativas`, `hhi`, `operadora_dominante`

- [x] Criar `healthintel_dbt/models/consumo/consumo_score_operadora_mes.sql`:
  - Source: `nucleo_ans.mart_score_operadora`
  - Grão: `(registro_ans, competencia)`
  - Colunas: `registro_ans`, `razao_social`, `modalidade`, `competencia`, `score_total`, `faixa_score`, `posicao_geral`, `posicao_por_modalidade`, `componente_core`, `componente_regulatorio`, `componente_financeiro`, `componente_rede`, `componente_estrutural`, `variacao_score_mom`

### HIS-24.3 — Documentação YAML dos Modelos de Consumo

- [x] Criar `healthintel_dbt/models/consumo/_consumo.yml` documentando todos os 8 modelos:
  - `config`: `materialized: table`, `schema: consumo_ans`, `tags: [consumo]`
  - `description`: propósito do data product, grão, cadência de atualização
  - `columns`: cada coluna com `description`, unidade (se numérica), valores esperados
  - `tests`: `not_null` em chaves, `dbt_utils.expression_is_true` para invariantes críticos (score 0-100, sinistralidade ≥ 0)
- [x] Adicionar exposures em `healthintel_dbt/models/exposures.yml`:
  ```yaml
  - name: consumo_ans_clientes
    type: application
    owner: {name: Engenharia, email: engenharia@healthintel.com.br}
    depends_on:
      - ref('consumo_operadora_360')
      - ref('consumo_score_operadora_mes')
      - ref('consumo_beneficiarios_operadora_mes')
      - ref('consumo_beneficiarios_municipio_mes')
      - ref('consumo_financeiro_operadora_trimestre')
      - ref('consumo_regulatorio_operadora_trimestre')
      - ref('consumo_rede_assistencial_municipio')
      - ref('consumo_oportunidade_municipio')
  ```

### HIS-24.4 — DAG de Refresh consumo_ans

- [x] Criar `ingestao/dags/dag_dbt_consumo_refresh.py`:
  - Schedule: `@daily`
  - Tasks:
    1. `dbt_run_marts` — `dbt run --select tag:mart`
    2. `dbt_run_consumo` — `dbt run --select tag:consumo`
    3. `dbt_test_consumo` — `dbt test --select tag:consumo`
    4. `registrar_refresh_consumo` — inserir em `plataforma.job` com `dataset='consumo_ans'`, status e timestamp
  - Dependência: roda após `dag_mestre_mensal` completar com sucesso no mesmo período
- [x] Adicionar target Makefile:
  ```makefile
  consumo-refresh:
      dbt run --select tag:mart tag:consumo
      dbt test --select tag:consumo
  ```
- [x] Adicionar target `make dag-test DAG=dag_dbt_consumo_refresh`.

### HIS-24.5 — Smoke consumo_ans

- [x] Criar `scripts/smoke_consumo.py`:
  - Conectar ao PostgreSQL com role `healthintel_cliente_reader`
  - Verificar que `consumo_ans` contém os 8 modelos
  - Definir mapa explícito de filtro temporal por modelo: modelos mensais usam `competencia`; modelos trimestrais usam `trimestre`
  - Para cada modelo: executar `SELECT count(*) FROM consumo_ans.{modelo} WHERE {coluna_temporal} = {valor_referencia}` e validar `count > 0`
  - Verificar isolamento: `healthintel_cliente_reader` recebe `PERMISSION DENIED` em `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans` e `plataforma`
  - Validar `consumo_score_operadora_mes.score_total BETWEEN 0 AND 100` em amostra
- [x] Adicionar target Makefile:
  ```makefile
  smoke-consumo:
      python scripts/smoke_consumo.py
  ```

### HIS-24.6 — Contrato de Dados para Clientes

- [x] Criar `docs/arquitetura/consumo_ans_guia.md` com:
  - Propósito do schema `consumo_ans`: camada de entrega final; o HealthIntel entrega dados curados, o cliente usa a ferramenta de sua escolha
  - Separação de responsabilidades: `api_ans` para REST FastAPI; `consumo_ans` para acesso direto PostgreSQL pelo cliente
  - Conexão PostgreSQL: host, porta, database, schema `consumo_ans`, role `healthintel_cliente_reader`
  - Exemplos de acesso: Power BI (fonte PostgreSQL → tabelas), Metabase (conexão + sync), Python (psycopg2 / SQLAlchemy), psql CLI
  - Catálogo resumido dos 8 data products: nome, grão, colunas principais
  - Histórico disponível: conforme contrato do cliente; janela de últimos 24 meses pode ser opção de MVP ou plano comercial, mas não regra definitiva do schema `consumo_ans`
  - Cadência de refresh: diário via `dag_dbt_consumo_refresh`; SLA: atualizado até 06h00 após `dag_mestre_mensal` noturno
  - Política de acesso: read-only em `consumo_ans`; sem acesso a dados operacionais ou de outros clientes

## Entregas esperadas

- [x] DDL `infra/postgres/init/022_consumo_ans.sql`
- [x] Role `healthintel_cliente_reader` com isolamento garantido
- [x] `models/consumo/consumo_operadora_360.sql`
- [x] `models/consumo/consumo_beneficiarios_operadora_mes.sql`
- [x] `models/consumo/consumo_beneficiarios_municipio_mes.sql`
- [x] `models/consumo/consumo_financeiro_operadora_trimestre.sql`
- [x] `models/consumo/consumo_regulatorio_operadora_trimestre.sql`
- [x] `models/consumo/consumo_rede_assistencial_municipio.sql`
- [x] `models/consumo/consumo_oportunidade_municipio.sql`
- [x] `models/consumo/consumo_score_operadora_mes.sql`
- [x] `models/consumo/_consumo.yml` com column-level docs, config e testes
- [x] `healthintel_dbt/models/exposures.yml` com exposure `consumo_ans_clientes`
- [x] `ingestao/dags/dag_dbt_consumo_refresh.py`
- [x] `scripts/smoke_consumo.py`
- [x] `docs/arquitetura/consumo_ans_guia.md`
- [x] Makefile com targets `consumo-refresh` e `smoke-consumo`

## Validação esperada

- [x] `dbt compile --select tag:consumo`
- [x] `dbt build --select tag:consumo` — sem falhas
- [x] `dbt test --select tag:consumo` — zero falhas
- [x] `make consumo-refresh` — sem erros
- [x] `make smoke-consumo` — zero falhas
- [x] `make dag-test DAG=dag_dbt_consumo_refresh` — parsing OK
- [x] Role `healthintel_cliente_reader` acessa `consumo_ans` mas recebe `PERMISSION DENIED` em `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans` e `plataforma`
- [x] `consumo_ans.consumo_operadora_360` contém registros para `competencia=202501`
