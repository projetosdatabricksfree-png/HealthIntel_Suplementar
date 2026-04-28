# Sprint 36 — Janela Dinâmica de Carga na Ingestão

**Status:** Ajustada para nível técnico local 10/10; não concluída automaticamente enquanto smokes dependentes de dados reais/dbt local seguirem pendentes
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** nenhuma intermediária (tag final da fase: `v4.2.0-dataops` ao fim da Sprint 40)
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov`) + Sprints 34 e 35 da Fase 7. Funções `plataforma.calcular_janela_carga_anual` e `plataforma.preparar_particoes_janela_atual` já disponíveis.
**Pré-requisitos:** Sprint 34 concluída (política em `plataforma.politica_dataset`); Sprint 35 concluída (funções de partição anual e tabelas SIB anuais).
**Schema novo:** nenhum schema criado. Tabela nova `plataforma.ingestao_janela_decisao` no schema `plataforma` existente.
**Objetivo:** ensinar todas as DAGs e scripts ELT de datasets `grande_temporal` a respeitarem dinamicamente a janela calculada por `plataforma.calcular_janela_carga_anual`, ignorar competências fora da janela com log explícito, e bloquear carga acidental de histórico inteiro. Sem ano fixo hardcoded.
**Critério de saída técnico:** parâmetro global `ANS_ANOS_CARGA_HOT` no `.env`/Airflow `Variable`; helper Python `ingestao/app/janela_carga.py` consultando `plataforma.politica_dataset` + `plataforma.calcular_janela_carga_anual`; módulos reais SIB filtram competências ≥ `competencia_minima` e < `competencia_maxima_exclusiva` antes do download/load; arquivos fora da janela registrados em `plataforma.ingestao_janela_decisao` com `acao='ignorado_fora_janela'`; hardgate Python que falha pipeline se um único arquivo histórico além da janela for carregado sem flag explícita.
**Critério de saída operacional:** `pytest ingestao/tests/test_janela_carga.py` zero falhas com cobertura ≥ 90%; `make dag-parse` zero erros; smoke dedicado `make smoke-janela-carga-sib` valida competência dentro, abaixo e no limite superior exclusivo; `make smoke-sib` e `make smoke-prata` não falham por `python` inexistente; nenhum modelo dbt nem endpoint API alterado.

## Regra-mãe da Fase 7 (não negociável nesta sprint)

- [x] Não alterar contrato de API.
- [x] Não alterar semântica de modelos dbt; staging continua lendo `bruto_ans.sib_*` exatamente como antes.
- [x] Não renomear DAGs aprovadas (apenas adicionar lógica de filtro dentro delas).
- [x] Nenhum ano hardcoded em lógica produtiva de janela, validado por hardgate preciso em `tests/hardgates/assert_sem_ano_hardcoded_janela.sh`.
- [x] Janela é sempre obtida via `plataforma.calcular_janela_carga_anual(ANS_ANOS_CARGA_HOT)`.
- [x] Arquivos fora da janela são ignorados com log estruturado, nunca falham silenciosamente.
- [x] Histórico só pode ser carregado pela DAG da Sprint 38 (`dag_historico_sob_demanda.py`), não pela DAG mensal.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Camada de decisão de janela na ingestão. |
| Schema físico | `plataforma` (tabela nova `ingestao_janela_decisao`). |
| Helper novo | `ingestao/app/janela_carga.py`. |
| Variáveis novas | `ANS_ANOS_CARGA_HOT` (default `2`). |
| Integração ajustada | Módulos reais `ingestao/app/ingestao_real.py`, `ingestao/app/carregar_postgres.py` e `ingestao/app/pipeline_bronze.py`. DAGs placeholders permanecem sem fluxo artificial. |
| Tag dbt | nenhuma. |
| Owner técnico | Engenharia de dados HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Classificação LGPD | Operacional/interna. |
| Regra de publicação | Interna apenas. |
| Regra de rollback | Reverter `ingestao/app/janela_carga.py` e blocos de filtro nas DAGs; `drop table plataforma.ingestao_janela_decisao`. Datasets atuais voltam a aceitar qualquer competência. |

## Histórias

### HIS-36.1 — Parâmetro global e helper Python

- [x] Adicionar `ANS_ANOS_CARGA_HOT=2` no `.env.exemplo` e em `infra/docker-compose.yml`.
- [x] Documentar no `make airflow-setup` que a variável precisa ser propagada como `Variable` Airflow.
- [x] Criar `ingestao/app/janela_carga.py` com função `obter_janela(dataset_codigo: str, anos: int | None = None) -> JanelaCarga`.
- [x] `JanelaCarga` é um `dataclass` com `competencia_minima: int`, `competencia_maxima_exclusiva: int`, `ano_inicial: int`, `ano_final: int`, `ano_preparado: int`.
- [x] A função consulta `plataforma.politica_dataset` para obter `anos_carga_hot` específico do dataset; se ausente, usa `ANS_ANOS_CARGA_HOT`.
- [x] A função consulta `plataforma.calcular_janela_carga_anual(p_anos_carga)` no mesmo connection.
- [x] Função adicional `competencia_dentro_janela(competencia: int, janela: JanelaCarga) -> bool`.
- [x] Função adicional `registrar_decisao(dataset_codigo: str, competencia: int, acao: Literal['carregado','ignorado_fora_janela','rejeitado_historico_sem_flag'], motivo: str | None = None)` grava em `plataforma.ingestao_janela_decisao`.

### HIS-36.2 — Tabela `plataforma.ingestao_janela_decisao`

- [x] Criar `infra/postgres/init/031_fase7_janela_carga.sql`.
- [x] DDL:

```sql
create table if not exists plataforma.ingestao_janela_decisao (
    id bigserial primary key,
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    competencia integer not null,
    acao text not null
        check (acao in ('carregado','ignorado_fora_janela','rejeitado_historico_sem_flag','ignorado_versao_antiga')),
    motivo text,
    janela_minima integer,
    janela_maxima_exclusiva integer,
    decidido_em timestamptz not null default now(),
    decidido_por text not null default current_user
);
```

- [x] Índice por `(dataset_codigo, decidido_em desc)` e por `(acao)`.

### HIS-36.3 — Filtro nas DAGs SIB

- [ ] Em `ingestao/dags/dag_ingest_sib.py`, antes do passo de download, calcular `janela = obter_janela('sib_operadora')`.
- [ ] Para cada arquivo descoberto, derivar `competencia` do nome/conteúdo e chamar `competencia_dentro_janela`.
- [ ] Se fora: chamar `registrar_decisao(... acao='ignorado_fora_janela')` e pular o arquivo.
- [ ] Se dentro: chamar `registrar_decisao(... acao='carregado')` após carga concluída.
- [ ] Antes do load, garantir que partição anual do `competencia` existe via `select plataforma.preparar_particoes_janela_atual('bruto_ans','sib_beneficiario_operadora', :anos)`.
- [ ] Replicar mesmo padrão para `sib_municipio`, `vda`, `glosa`, `portabilidade`, `tiss_producao` (quando habilitado).
- [x] Integração equivalente aplicada nos módulos reais usados pelo fluxo SIB neste clone: `ingestao/app/ingestao_real.py`, `ingestao/app/carregar_postgres.py` e `ingestao/app/pipeline_bronze.py`.
- [x] DAGs placeholders não foram preenchidas artificialmente; o filtro deve ser conectado nelas quando houver implementação real.

### HIS-36.4 — Hardgate Python contra carga histórica acidental

- [x] Criar função `assegurar_dentro_da_janela_ou_falhar(competencia: int, janela: JanelaCarga, *, permitir_historico: bool = False)` que `raise HistoricoForaDaJanelaError` quando `permitir_historico=False` e a competência está fora.
- [x] Aplicar essa função no operador de load (não só no descobridor de arquivos) para defesa em profundidade.
- [x] DAG mensal padrão chama com `permitir_historico=False`.
- [ ] DAG histórica (Sprint 38) é o único caller permitido a passar `permitir_historico=True`, e mesmo assim sob token de entitlement por cliente.

### HIS-36.5 — Logs de decisão e métricas

- [x] Logs estruturados (`structlog`) com campos `dataset_codigo`, `competencia`, `acao`, `motivo`, `janela_minima`, `janela_maxima_exclusiva`.
- [x] View `plataforma.vw_ingestao_janela_resumo` agregando contagem por `dataset_codigo` x `acao` no último período.
- [x] Documentar consulta padrão para o time de dados monitorar quantos arquivos foram ignorados na última janela.

### HIS-36.6 — Testes

- [x] Criar `ingestao/tests/test_janela_carga.py` com casos:
  - competência dentro da janela retorna `True`;
  - competência abaixo da janela retorna `False` e gera registro `ignorado_fora_janela`;
  - competência igual a `competencia_maxima_exclusiva` é rejeitada (limite exclusivo);
  - chamada com `dataset_codigo` ausente em `politica_dataset` falha com erro claro;
  - virada de ano: usar `freezegun`/`monkeypatch` para simular `2027-01-02` e verificar que `competencia=202602` ainda é aceita mas `202512` é rejeitada.
- [x] Cobertura mínima 90% (`ingestao/app/janela_carga.py`: 99%).
- [x] Adicionar pytest fixture com banco de teste (Docker compose ou conftest pré-existente).

## Entregas esperadas

- [x] `ingestao/app/janela_carga.py`
- [x] `infra/postgres/init/031_fase7_janela_carga.sql`
- [ ] Bloco de filtro adicionado às DAGs `dag_ingest_sib.py`, `dag_ingest_sib_municipio.py` (se aplicável), `dag_ingest_vda.py`, `dag_ingest_glosa.py`, `dag_ingest_portabilidade.py`, `dag_ingest_tiss.py`.
- [x] Integração aplicada aos módulos reais de ingestão/load SIB (`ingestao_real`, `carregar_postgres`, `pipeline_bronze`).
- [x] `ingestao/tests/test_janela_carga.py`
- [x] `scripts/smoke_janela_carga_sib.py`
- [x] `tests/hardgates/assert_sem_ano_hardcoded_janela.sh`
- [x] `plataforma.ingestao_janela_decisao` populada após smoke/testes.
- [x] `plataforma.vw_ingestao_janela_resumo` criada.
- [x] `.env.exemplo` atualizado com `ANS_ANOS_CARGA_HOT=2`.
- [x] Documento `docs/arquitetura/politica_carga_dataset.md` atualizado com seção “janela dinâmica de carga”.

## Validação esperada (hard gates)

- [x] `pytest ingestao/tests/test_janela_carga.py -v --cov=ingestao.app.janela_carga --cov-report=term-missing` zero falhas, cobertura ≥ 90%.
- [x] `make dag-parse` zero erros.
- [x] `make smoke-janela-carga-sib` valida `202602` permitido, `202412` bloqueado e `202701` bloqueado.
- [ ] `make smoke-sib UFS=AC COMPETENCIA=202602` carrega normalmente; registro `acao='carregado'` em `plataforma.ingestao_janela_decisao`.
- [ ] `make smoke-sib UFS=AC COMPETENCIA=202412` (fora da janela hot em 2026) falha imediatamente com `HistoricoForaDaJanelaError` e gera registro `acao='rejeitado_historico_sem_flag'`.
- [x] `select count(*) from plataforma.ingestao_janela_decisao where acao='ignorado_fora_janela'` >= 0 (smoke real pode ou não gerar; teste sintético cobre).
- [x] `make hardgate-sem-ano-hardcoded-janelacarga` passa sem ocorrências.
- [x] `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros api/app` saída vazia (modelos dbt e API não alterados).
- [x] `pytest api/tests/integration/` zero falhas (endpoints continuam funcionando).
- [ ] Smoke `make smoke-prata` zero falhas.

## Distinção Estado Atual vs Estado-Alvo

| Eixo | Estado atual | Estado-alvo da Sprint 36 |
|------|--------------|--------------------------|
| Janela de carga | Módulos reais SIB protegidos; DAGs placeholders ainda sem fluxo próprio. | Calculada dinamicamente, aplicada antes de download/load nos fluxos reais. |
| Variável global | `ANS_ANOS_CARGA_HOT=2` configurada em exemplo, compose, settings e Airflow setup. | Configurável por ambiente/Variable. |
| Logs de decisão | `plataforma.ingestao_janela_decisao` populada por testes/smoke. | Auditoria operacional contínua por carga real. |
| Hardgate histórico | `HistoricoForaDaJanelaError` implementado e testado. | Único bypass futuro via Sprint 38 com entitlement. |
| Comportamento na virada de ano | Automático via função SQL da Sprint 35. | Mantido por `plataforma.calcular_janela_carga_anual`. |
| Modelos dbt / API | Baseline `v3.8.0-gov`. | Idem. |

## Anti-padrões explicitamente rejeitados nesta sprint

- Hardcodar `if competencia >= 202501` ou `current_year - 1` em Python.
- Permitir que a DAG mensal padrão aceite `permitir_historico=True`.
- Falhar silenciosamente para arquivos fora da janela (sem log nem registro em `ingestao_janela_decisao`).
- Apagar registros de `ingestao_janela_decisao` para “limpar histórico” — o registro é auditoria.
- Deixar `ANS_ANOS_CARGA_HOT` sem default no helper (deve cair em `2` se variável ausente).
- Marcar hardgates `[x]` antes de executar os comandos correspondentes.

## Resultado Esperado

Sprint 36 entrega a janela dinâmica de carga na ingestão. Os módulos reais de ingestão/load respeitam automaticamente `ano_vigente + ano_anterior`, sem ano fixo, sem necessidade de editar código em janeiro de 2027. DAGs que hoje são placeholders não foram preenchidas artificialmente. Arquivos fora da janela são ignorados com auditoria, não falham silenciosamente. Tentativas de carga histórica acidental são bloqueadas pelo hardgate Python. A DAG da Sprint 38 ainda não existe; quando ela existir, será o único caminho legítimo para carregar histórico antigo.

## Evidências de execução local — 2026-04-28

### Pré-check obrigatório

- Política `grande_temporal` validada no PostgreSQL local: `sib_operadora`, `sib_municipio`, `vda`, `glosa`, `portabilidade`, `rede_prestador` e `tiss_producao` ativos com `anos_carga_hot=2` e `particionar_por_ano=true`.
- Função Sprint 35 validada: `select * from plataforma.calcular_janela_carga_anual(2, DATE '2026-04-28')` retornou `competencia_minima=202501` e `competencia_maxima_exclusiva=202701`.
- Partições SIB validadas: ambas as tabelas-mãe têm `_2025`, `_2026`, `_2027` e `_default`.
- Hardgate anti-partição mensal SIB executado com zero ocorrências: `grep -rn "_2026_01\|_2026_02\|_2025_01\|FOR VALUES FROM (202601) TO (202602)" ingestao/dags infra/postgres`.
- Arquivos reais mapeados: `ingestao/app/ingestao_real.py`, `ingestao/app/carregar_postgres.py`, `ingestao/app/pipeline_bronze.py`, `scripts/elt_*.py`, `ingestao/app/elt/*`, DAGs placeholders `dag_ingest_vda.py`, `dag_ingest_glosa.py`, `dag_ingest_portabilidade.py`, `dag_ingest_tiss.py`; `dag_ingest_sib.py` e `scripts/run_ingestao_real_sib.py` estão vazios neste clone.

### Implementação registrada

- Bootstrap aplicado com sucesso: `docker compose -f infra/docker-compose.yml exec -T postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel < infra/postgres/init/031_fase7_janela_carga.sql`.
- Tabela criada: `\dt plataforma.ingestao_janela_decisao` retornou `plataforma.ingestao_janela_decisao`.
- View criada: `select * from plataforma.vw_ingestao_janela_resumo limit 5` executou sem erro.
- Helper criado em `ingestao/app/janela_carga.py` usando SQLAlchemy async já existente, sem introduzir camada paralela de conexão.
- Helper passou a emitir logs estruturados via `structlog` com `dataset_codigo`, `competencia`, `acao`, `motivo`, `janela_minima` e `janela_maxima_exclusiva`.
- Defesa em profundidade aplicada no load Bronze central: `ingestao/app/carregar_postgres.py` valida janela antes de inserir e registra `carregado` após carga concluída.
- Fluxo real SIB aplicado em `ingestao/app/ingestao_real.py` antes do download e antes da carga; `permitir_historico=False`.
- Streaming SIB registra decisão `carregado` em `ingestao/app/pipeline_bronze.py` após conclusão.
- Variável adicionada em `.env.exemplo`, `infra/docker-compose.yml`, `ingestao/app/config.py` e propagação Airflow documentada no target `airflow-setup` do `Makefile`.
- `Makefile` padronizado com `PYTHON ?= .venv/bin/python`; targets `smoke-sib` e `smoke-prata` não dependem mais de `python` no host.
- `scripts/smoke_janela_carga_sib.py` criado para validar a janela SIB sem depender de dados reais.
- `tests/hardgates/assert_sem_ano_hardcoded_janela.sh` criado para bloquear hardcode produtivo de ano apenas nos módulos reais de janela.
- `pytest-cov` adicionado às dependências de desenvolvimento em `pyproject.toml`.

### Limitações do clone local

- `dag_ingest_sib.py` e `scripts/run_ingestao_real_sib.py` existem, mas têm 0 linhas; a integração real foi feita nos módulos de ingestão usados pelos scripts/pipelines (`ingestao_real`, `carregar_postgres`, `pipeline_bronze`).
- DAGs `vda`, `glosa`, `portabilidade` e `tiss` são placeholders com `EmptyOperator`; não há discovery/load real nelas para filtrar competência sem inventar DAG artificial.
- `smoke-sib` do `Makefile` não aceita `UFS` nem `COMPETENCIA`; o smoke específico `smoke-janela-carga-sib` cobre bloqueio de `202412` e limite superior exclusivo `202701` via helper real.
- `make smoke-sib` não falha mais por `python` inexistente, mas continua pendente por ausência de dados SIB locais (`operadora=0`, `municipio=0`, `lotes=0`).
- `make smoke-prata` não falha mais por `python` inexistente, mas continua pendente porque o banco local não tem a relação `api_ans.api_prata_cadop`.
- O comando amplo de hardcode produtivo encontra datas pré-existentes em scripts de seed/smoke e `start_date` de DAGs; a Sprint 36 usa hardgate preciso restrito aos módulos produtivos alterados da janela.
- A sprint não está marcada como concluída automaticamente; hardgates operacionais dependentes de dados reais/dbt local seguem pendentes.

### Hardgates executados

- `docker compose -f infra/docker-compose.yml exec -T postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel < infra/postgres/init/031_fase7_janela_carga.sql`: 0 erros.
- `docker compose -f infra/docker-compose.yml exec -T postgres psql -U healthintel -d healthintel -c "\\dt plataforma.ingestao_janela_decisao"`: tabela existe.
- `docker compose -f infra/docker-compose.yml exec -T postgres psql -U healthintel -d healthintel -c "select * from plataforma.vw_ingestao_janela_resumo limit 5"`: 0 erros.
- `.venv/bin/pytest ingestao/tests/test_janela_carga.py -v`: `30 passed in 1.22s`.
- `.venv/bin/pytest ingestao/tests/test_janela_carga.py -v --cov=ingestao.app.janela_carga --cov-report=term-missing`: `30 passed`, cobertura `99%`.
- `make dag-parse`: 0 erros; saída `Errors: {}`.
- `grep -rn "permitir_historico=True" ingestao/dags ingestao/app scripts | grep -v "dag_historico_sob_demanda"`: zero ocorrências.
- `make smoke-janela-carga-sib`: passou; `202602` permitida, `202412` bloqueada e `202701` bloqueada.
- `make hardgate-sem-ano-hardcoded-janelacarga`: passou; saída `Hardgate OK: sem ano hardcoded em logica produtiva de janela.`
- `.venv/bin/pytest api/tests/integration/ -v`: `32 passed in 1.54s`.
- `.venv/bin/pytest ingestao/tests/ -v`: `59 passed in 9.23s`.
- `.venv/bin/ruff check .`: `All checks passed!`.
- `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros api/app`: saída vazia.
- `git diff --check`: saída vazia.
- `select acao, count(*) from plataforma.ingestao_janela_decisao group by acao`: `ignorado_fora_janela=30`, `rejeitado_historico_sem_flag=12` após testes e smoke específico.
- `make smoke-sib`: executou com `.venv/bin/python`; falhou por ausência de dados SIB locais (`operadora=0`, `municipio=0`, `lotes=0`), não por Python inexistente.
- `make smoke-prata`: executou com `.venv/bin/python`; falhou por ausência da relação local `api_ans.api_prata_cadop`, não por Python inexistente.
