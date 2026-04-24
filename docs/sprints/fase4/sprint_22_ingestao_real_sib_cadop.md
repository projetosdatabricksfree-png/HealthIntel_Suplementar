# Sprint 22 — Ingestão Real: SIB e CADOP

**Status:** Pendente
**Objetivo:** implementar ingestão real dos dois datasets mais críticos ausentes (SIB beneficiários e CADOP operadoras); introduzir landing zone física; formalizar controle de lote em `plataforma.lote_ingestao`; garantir idempotência por hash.
**Critério de saída:** DAGs SIB e CADOP parsando arquivos reais da ANS; `plataforma.lote_ingestao` registrando cada carga com hash; carga duplicada rejeitada com status `ignorado_duplicata`; `make smoke-sib` + `make smoke-cadop` zero falhas.

## Histórias

### HIS-22.1 — Landing Zone Física

- [ ] Criar volume `ingestao_landing` em `infra/docker-compose.yml` mapeando para `/tmp/healthintel/landing` no container Airflow.
- [ ] Definir variável de ambiente `INGESTAO_LANDING_PATH=/tmp/healthintel/landing` em `.env` e `ingestao/app/config.py`.
- [x] Criar estrutura de diretórios por dataset: `{LANDING_PATH}/{dataset}/{competencia}/` — gerado automaticamente na descarga.
- [ ] Criar utilitário `ingestao/app/landing.py`:
  - `salvar_arquivo(dataset, competencia, nome_arquivo, conteudo_bytes) -> Path`
  - `calcular_hash_arquivo(path: Path) -> str` (SHA-256)
  - `arquivo_ja_processado(hash: str) -> bool` (consulta `plataforma.lote_ingestao`)

### HIS-22.2 — plataforma.lote_ingestao

- [x] Criar DDL `infra/postgres/init/021_lote_ingestao.sql`:
  ```sql
  CREATE TABLE plataforma.lote_ingestao (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      dataset TEXT NOT NULL,
      competencia TEXT,
      arquivo_origem TEXT NOT NULL,
      hash_arquivo TEXT NOT NULL,
      tamanho_bytes BIGINT,
      total_linhas_raw INTEGER,
      total_aprovadas INTEGER,
      total_quarentena INTEGER,
      status TEXT NOT NULL DEFAULT 'iniciado',  -- iniciado | processando | sucesso | sucesso_com_alertas | ignorado_duplicata | erro
      erro_mensagem TEXT,
      iniciado_em TIMESTAMPTZ DEFAULT now(),
      concluido_em TIMESTAMPTZ,
      dag_run_id TEXT,
      versao_layout TEXT,
      checksum_layout TEXT,
      tentativa INTEGER NOT NULL DEFAULT 1,
      id_lote_original UUID REFERENCES plataforma.lote_ingestao(id),
      origem_execucao TEXT NOT NULL DEFAULT 'airflow'
  );
  CREATE INDEX ON plataforma.lote_ingestao (dataset, competencia);
  CREATE INDEX ON plataforma.lote_ingestao (hash_arquivo);
  CREATE UNIQUE INDEX lote_ingestao_hash_arquivo_sucesso_uq
      ON plataforma.lote_ingestao (hash_arquivo)
      WHERE status IN ('sucesso', 'sucesso_com_alertas');
  ```
- [x] Atualizar `ingestao/app/carregar_postgres.py`: integrar `plataforma.lote_ingestao` — registrar início, atualizar status no final, persistir contagens e hash.
- [x] Verificar idempotência: antes de processar arquivo, consultar `lote_ingestao` por hash — se já existe com status `sucesso` ou `sucesso_com_alertas`, retornar `ignorado_duplicata` sem reprocessar.

### HIS-22.3 — Contratos SIB

- [x] Criar `ingestao/app/contratos_sib.py` com:
  - `SCHEMA_SIB_OPERADORA`: campos obrigatórios, tipos esperados, domínios válidos para SIB por operadora
  - `SCHEMA_SIB_MUNICIPIO`: campos e tipos para SIB por município
  - Função `validar_linha_sib(row: dict, schema: dict) -> tuple[bool, str | None]` — retorna `(válido, motivo_rejeicao)`
- [x] Registrar schemas em MongoDB via `scripts/bootstrap_layout_registry_sib.py`:
  - Layout `sib_operadora_v1`: campos, tipos, versão, competencia_col
  - Layout `sib_municipio_v1`: idem para SIB município
- [x] Adicionar target Makefile: `bootstrap-sib-layouts: python scripts/bootstrap_layout_registry_sib.py`

### HIS-22.4 — DAG Ingestão SIB

- [x] Criar `ingestao/dags/dag_ingest_sib.py`:
  - Schedule: `@monthly` (dados publicados mensalmente pela ANS)
  - Parâmetro: `competencia` (YYYYMM)
  - Tasks:
    1. `download_sib` — baixar arquivo SIB da URL ANS (FTP ou HTTP) para landing zone; calcular hash; verificar duplicata
    2. `validar_layout_sib` — consultar MongoDB para resolver layout; validar cabeçalho e encoding
    3. `carregar_sib_operadora` — validar cada linha via `contratos_sib.py`; aprovados → `bruto_ans.sib_operadora`; rejeitados → `bruto_ans.sib_operadora_quarentena`; registrar `lote_ingestao`
    4. `carregar_sib_municipio` — idem para SIB município
    5. `registrar_versao_sib` — chamar `dag_registrar_versao` para `sib_operadora` e `sib_municipio`
  - Em `dag_mestre_mensal.py`: adicionar SIB como sub-DAG após CADOP.
- [ ] Adicionar target `make dag-test DAG=dag_ingest_sib` — parsing sem falhas.

### HIS-22.5 — Contratos CADOP

- [x] Criar `ingestao/app/contratos_cadop.py`:
  - `SCHEMA_CADOP`: campos do arquivo CADOP (registro_ans, razao_social, cnpj, modalidade, uf_sede, situacao, etc.)
  - Função `validar_linha_cadop(row: dict) -> tuple[bool, str | None]`
- [x] Criar `scripts/bootstrap_layout_registry_cadop.py`:
  - Layout `cadop_v1`: campos obrigatórios, mapeamento coluna → campo
- [x] Adicionar target Makefile: `bootstrap-cadop-layouts: python scripts/bootstrap_layout_registry_cadop.py`

### HIS-22.6 — DAG Ingestão CADOP

- [x] Criar `ingestao/dags/dag_ingest_cadop.py`:
  - Schedule: `@monthly` (CADOP publicada mensalmente)
  - Parâmetro: `competencia`
  - Tasks:
    1. `download_cadop` — baixar da ANS para landing zone
    2. `validar_layout_cadop` — resolver layout em MongoDB
    3. `carregar_cadop` — validar linhas; aprovados → `bruto_ans.cadop`; rejeitados → `bruto_ans.cadop_quarentena`; registrar lote
    4. `registrar_versao_cadop`
  - Integrar em `dag_mestre_mensal.py` como primeiro passo (operadoras ativas devem estar disponíveis antes de beneficiários).

### HIS-22.7 — Seed Demo SIB e CADOP

- [x] Criar `scripts/seed_demo_sib.py`: inserir registros demo em `bruto_ans.sib_operadora` e `bruto_ans.sib_municipio` para competência `202501` com hash e `lote_ingestao` preenchidos.
- [x] Adicionar target: `demo-data-sib: python scripts/seed_demo_sib.py`
- [x] Verificar que `scripts/seed_demo_core.py` já popula `bruto_ans.cadop` — se não, criar `scripts/seed_demo_cadop.py`.
- [x] Adicionar target: `demo-data-cadop: python scripts/seed_demo_cadop.py`

### HIS-22.8 — Smoke SIB e CADOP

- [x] Criar `scripts/smoke_sib.py`: validar que `bruto_ans.sib_operadora` e `bruto_ans.sib_municipio` contêm registros para `competencia=202501`; validar que `plataforma.lote_ingestao` tem entrada com status `sucesso`; validar que carga duplicada gera `ignorado_duplicata`.
- [x] Criar `scripts/smoke_cadop.py`: idem para CADOP.
- [x] Adicionar targets Makefile:
  ```makefile
  smoke-sib:
      python scripts/smoke_sib.py
  smoke-cadop:
      python scripts/smoke_cadop.py
  ```

### HIS-22.9 — Padronização de colunas técnicas Bronze

- [ ] Garantir que toda tabela Bronze carregada pela ingestão real contenha os campos técnicos obrigatórios: `id_lote`, `arquivo_origem`, `hash_arquivo`, `hash_linha`, `linha_origem`, `competencia`, `versao_layout`, `data_ingestao`, `status_linha`, `motivo_rejeicao`.
- [ ] Documentar contrato das colunas técnicas nos contratos SIB/CADOP e validar presença antes da carga em `bruto_ans`.
- [ ] Aplicar a mesma padronização às tabelas de quarentena para preservar rastreabilidade de rejeições.

### HIS-22.10 — Regressão de Layout ANS Alterado

- [ ] Criar testes de regressão para layout com coluna renomeada por alias conhecido.
- [ ] Criar cenário de coluna obrigatória ausente, com fallback seguro para quarentena.
- [ ] Criar cenário de coluna extra, sem quebra de carga das colunas conhecidas.
- [ ] Criar cenário de ordem de colunas alterada, resolvido por nome/header normalizado.
- [ ] Criar cenário de encoding diferente, com detecção e erro rastreável quando não suportado.
- [ ] Criar cenário de arquivo sem layout aprovado, bloqueando carga Bronze e registrando motivo.
- [ ] Criar cenário de layout antigo reprocessável, reaproveitando histórico/fingerprint aprovado.

## Entregas esperadas

- [x] DDL `infra/postgres/init/021_lote_ingestao.sql`
- [x] `ingestao/app/landing.py`
- [x] `ingestao/app/contratos_sib.py`
- [x] `ingestao/app/contratos_cadop.py`
- [x] `ingestao/dags/dag_ingest_sib.py`
- [x] `ingestao/dags/dag_ingest_cadop.py`
- [x] `scripts/bootstrap_layout_registry_sib.py`
- [x] `scripts/bootstrap_layout_registry_cadop.py`
- [x] `scripts/seed_demo_sib.py`
- [x] `scripts/seed_demo_cadop.py`
- [x] `scripts/smoke_sib.py`
- [x] `scripts/smoke_cadop.py`
- [ ] `infra/docker-compose.yml` com volume `ingestao_landing`
- [x] Makefile com targets `bootstrap-sib-layouts`, `bootstrap-cadop-layouts`, `demo-data-sib`, `demo-data-cadop`, `smoke-sib`, `smoke-cadop`
- [x] `dag_mestre_mensal.py` atualizado com SIB e CADOP

## Validação esperada

- [x] `ruff check ingestao scripts`
- [x] `pytest ingestao/tests/` — zero falhas
- [ ] `make dag-test DAG=dag_ingest_sib` — parsing OK
- [ ] `make dag-test DAG=dag_ingest_cadop` — parsing OK
- [x] `make demo-data-sib` + `make smoke-sib` — zero falhas
- [x] `make demo-data-cadop` + `make smoke-cadop` — zero falhas
- [x] `plataforma.lote_ingestao` contém entradas com `status='sucesso'` para SIB e CADOP
- [ ] Reprocessamento do mesmo arquivo resulta em `status='ignorado_duplicata'`
