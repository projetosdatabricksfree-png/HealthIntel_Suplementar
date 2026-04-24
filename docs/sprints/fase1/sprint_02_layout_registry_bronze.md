# Sprint 02 — Layout Registry e Bronze

**Status:** Concluida
**Objetivo:** operacionalizar o registry de layout em `MongoDB` e preparar a ingestao deterministica para bronze.
**Criterio de saida:** layouts, versoes, aliases e validacoes estruturais ficam persistidos com rastreabilidade.

## Historias

### HIS-02.1 — Persistir o cadastro de datasets e layouts

- [x] Criar repositorio Mongo real em `mongo_layout_service/app/repositories/layout_repository.py`.
- [x] Criar colecoes `fonte_dataset`, `layout`, `layout_versao`, `layout_alias`, `layout_execucao` e `evento_layout`.
- [x] Criar indices para busca operacional e unicidade de layout.

### HIS-02.2 — Implementar o servico administrativo de layout

- [x] Implementar `mongo_layout_service/app/services/layout_service.py` com CRUD de layout, versao e alias.
- [x] Implementar rotas administrativas em `mongo_layout_service/app/routers/layout.py`.
- [x] Integrar a API publica administrativa com proxy HTTP em `api/app/services/layout_admin.py`.

### HIS-02.3 — Selecionar layout por regra deterministica

- [x] Implementar assinatura estrutural baseada em colunas detectadas.
- [x] Implementar validacao sem heuristica semantica.
- [x] Implementar resolucao de aliases manuais por layout e versao.

### HIS-02.4 — Registrar execucao e incompatibilidade estrutural

- [x] Persistir execucoes de validacao em `layout_execucao`.
- [x] Expor consulta de layouts incompativeis.
- [x] Persistir quarentena operacional em tabelas relacionais de `plataforma`.

### HIS-02.5 — Integrar a ingestao bronze ao registry

- [x] Conectar `ingestao/app/identificar_layout.py` ao servico real de layout.
- [x] Conectar `ingestao/app/aplicar_alias.py` ao layout resolvido por versao.
- [x] Implementar carga efetiva de `CADOP` em `bruto_ans`.
- [x] Implementar carga efetiva de `SIB por operadora` em `bruto_ans`.
- [x] Implementar carga efetiva de `SIB por municipio` em `bruto_ans`.

### HIS-02.6 — Formalizar DDL bronze e DAG de particoes mensais

- [x] Formalizar DDL de `bruto_ans.cadop` com todos os 20 campos do CSV ANS (`registro_ans`, `cnpj`, `razao_social`, `nome_fantasia`, `modalidade`, `logradouro`, `numero`, `complemento`, `bairro`, `cidade`, `uf`, `cep`, `ddd`, `telefone`, `fax`, `endereco_eletronico`, `representante`, `cargo_representante`, `regiao_de_comercializacao`, `data_registro_ans`) e indice `ix_cadop_registro_ans` em `infra/postgres/init/001_schemas.sql`.
- [x] Formalizar DDL de `bruto_ans.sib_beneficiario_operadora` com particao RANGE por `competencia`, PRIMARY KEY `(cd_operadora, competencia, _lote_id)`, BRIN index `ix_sib_operadora_competencia_brin` e indice `ix_sib_operadora_cd`.
- [x] Formalizar DDL de `bruto_ans.sib_beneficiario_municipio` com particao RANGE por `competencia` e PRIMARY KEY `(cd_municipio, cd_operadora, competencia, _lote_id)`.
- [x] Criar `dag_criar_particao_mensal` (cron `'0 0 25 * *'`) responsavel por criar particoes do mes seguinte em `bruto_ans.sib_beneficiario_operadora`, `bruto_ans.sib_beneficiario_municipio` e `plataforma.log_uso` antes do inicio do ciclo mensal.
- [x] Adicionar `dag_dbt_freshness` (`dbt source freshness` com alerta por e-mail) como sub-DAG do `dag_mestre_mensal`.
- [x] Adicionar `dag_registrar_versao` (atualiza `plataforma.versao_dataset` ao final de cada ciclo) como sub-DAG do `dag_mestre_mensal`.

## Validacao e Conclusao

**Data de conclusao:** 2026-04-22

**Status:** ✅ **CONCLUIDA**

### Checklist de Saida

- [x] MongoDB layout registry operacional com CRUD de layout, versao e alias.
- [x] Assinatura estrutural deterministica implementada (sem semantica).
- [x] Validacao de execucoes persistidas em `layout_execucao`.
- [x] Ingestao bronze integrada ao registry.
- [x] Carga de CADOP, SIB operadora e SIB municipio implementadas.
- [x] DDL bronze formalizada: `bruto_ans.cadop`, `sib_beneficiario_operadora`, `sib_beneficiario_municipio`.
- [x] Tabelas particionadas por `competencia` (RANGE).
- [x] DAG de particoes mensais (`dag_criar_particao_mensal`) criada e agendada.
- [x] DAG de freshness (`dag_dbt_freshness`) integrada ao ciclo.
- [x] DAG de versionamento (`dag_registrar_versao`) integrada ao ciclo.
- [x] Ambiente pronto para Sprint 03 (camada canonica inicial).

### Artifacts de Sprint

| Artefato | Localizacao | Status |
|----------|-------------|--------|
| Layout repository | `mongo_layout_service/app/repositories/layout_repository.py` | ✅ Operacional |
| Layout service | `mongo_layout_service/app/services/layout_service.py` | ✅ CRUD completo |
| Layout router | `mongo_layout_service/app/routers/layout.py` | ✅ Administrativo |
| Layout admin proxy | `api/app/services/layout_admin.py` | ✅ Integrado |
| DDL bronze | `infra/postgres/init/001_schemas.sql` | ✅ Formalizado |
| Particoes mensal | `ingestao/dags/dag_criar_particao_mensal.py` | ✅ Agendado |
| Freshness | `ingestao/dags/dag_dbt_freshness.py` | ✅ Integrado |
| Versionamento | `ingestao/dags/dag_registrar_versao.py` | ✅ Integrado |
| dag_mestre_mensal | `ingestao/dags/dag_mestre_mensal.py` | ✅ Atualizado |
