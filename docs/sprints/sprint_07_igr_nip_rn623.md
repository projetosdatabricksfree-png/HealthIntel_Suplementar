# Sprint 07 — IGR, NIP e RN 623

**Status:** Concluida
**Objetivo:** iniciar a fase regulatoria com ingestao e padronizacao das bases regulatórias prioritarias.
**Criterio de saida:** datasets regulatorios principais ficam disponiveis em bronze, staging e API basica.

## Historias

### HIS-07.1 — Ingerir IGR

- [x] Mapear fonte oficial e contrato de coleta do IGR.
- [x] Implementar layout registry para IGR.
- [x] Carregar IGR em `bruto_ans`.

### HIS-07.2 — Ingerir NIP

- [x] Mapear publicacao oficial de NIP.
- [x] Implementar parsing e carga em bronze.
- [x] Criar staging regulatorio para NIP.

### HIS-07.3 — Ingerir listas da RN 623

- [x] Mapear as listas trimestrais de excelencia e reducao.
- [x] Registrar versao de publicacao por trimestre.
- [x] Carregar listas em schema core.

### HIS-07.4 — Preparar historico regulatorio

- [x] Versionar mudancas metodologicas por dataset.
- [x] Garantir compatibilidade de layout entre publicacoes.
- [x] Registrar lineage e origem de cada arquivo regulatorio.

## Entregas implementadas

- [x] DDL regulatoria com `bruto_ans.igr_operadora_trimestral`, `bruto_ans.nip_operadora_trimestral`, `bruto_ans.rn623_lista_operadora_trimestral` e `plataforma.publicacao_regulatoria`.
- [x] Layout registry regulatorio com bootstrap em `scripts/bootstrap_layout_registry_regulatorio.py`.
- [x] Seed demo regulatorio com publicacao versionada em `scripts/seed_demo_regulatorio.py`.
- [x] Camada dbt `stg_igr`, `stg_nip`, `stg_rn623_lista`, `int_regulatorio_operadora_trimestre`, `fat_monitoramento_regulatorio_trimestral`, `api_regulatorio_operadora_trimestral` e `api_rn623_lista_trimestral`.
- [x] Endpoints `GET /v1/operadoras/{registro_ans}/regulatorio` e `GET /v1/regulatorio/rn623`.
- [x] Dags `dag_ingest_igr`, `dag_ingest_nip` e `dag_ingest_rn623`.

## Validacao executada

- [x] `ruff check api ingestao scripts`
- [x] `pytest -q`
- [x] `dbt build`
- [x] `python scripts/bootstrap_layout_registry_regulatorio.py`
- [x] `python scripts/seed_demo_regulatorio.py`
- [x] `python scripts/smoke_piloto.py`
