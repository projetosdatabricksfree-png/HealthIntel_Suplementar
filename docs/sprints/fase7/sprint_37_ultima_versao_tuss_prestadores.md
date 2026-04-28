# Sprint 37 — Última Versão para TUSS, Procedimentos e Prestadores

**Status:** Resolvida no escopo Sprint 37 — mecanismo, tabelas Bronze versionadas, DAGs parametrizadas, smoke dedicado e testes locais concluídos. A carga usa arquivo oficial já disponível em landing/caminho local parametrizado; crawler/download automático ANS permanece fora do escopo desta sprint.
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** nenhuma intermediária (tag final da fase: `v4.2.0-dataops` ao fim da Sprint 40)
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov`) + Sprints 34, 35, 36 da Fase 7. Política em `plataforma.politica_dataset` já distingue `referencia_versionada` de `snapshot_atual`.
**Pré-requisitos:** Sprints 34 e 36 concluídas. `plataforma.politica_dataset` deve listar TUSS, ROL, DE-PARA SIP-TUSS, prestadores cadastrais e QUALISS com `carregar_apenas_ultima_versao=true` ou `estrategia_carga in ('ultima_versao_vigente','snapshot_atual')`.
**Schema novo:** nenhum schema criado. Tabela nova `plataforma.versao_dataset_vigente` no schema `plataforma` existente.

**Decisão técnica (colisão de nomes):** o nome `plataforma.versao_dataset` previsto inicialmente já existia no baseline (`002_bronze_operacional.sql`) como log per-carga genérico (campos `dataset`, `competencia`, `registros`, `status`, sem `vigente`, sem FK). Renomear ou alterar essa tabela violaria a Regra-mãe da Fase 7 ("não renomear tabelas existentes sem plano de migração"). Por isso o manifesto da Sprint 37 entra como artefato novo: `plataforma.versao_dataset_vigente`. A tabela antiga continua intacta com sua função de log per-carga.
**Objetivo:** garantir que datasets de referência versionada (TUSS procedimentos, TUSS materiais/OPME, TUSS medicamentos, DE-PARA SIP-TUSS, ROL) e cadastros de prestadores/rede vigente sejam carregados apenas na última versão publicada pela ANS, sem materializar versões antigas no PostgreSQL da VPS. Histórico antigo passa a ser explicitamente premium/sob demanda.
**Critério de saída técnico:** mecanismo de manifesto vigente entregue em `plataforma.versao_dataset_vigente` (URL fonte, hash do arquivo, data de publicação, data de carga, versão do dataset); helper `ingestao/app/versao_vigente.py` consulta `plataforma.versao_dataset_vigente` e `plataforma.politica_dataset.carregar_apenas_ultima_versao`; helper `ingestao/app/carga_versao_vigente.py` carrega arquivos tabulares reais para `bruto_ans.tuss_procedimento`, `bruto_ans.rol_procedimento`, `bruto_ans.depara_sip_tuss`, `bruto_ans.prestador_cadastral` e `bruto_ans.qualiss`; índice único parcial impede duas versões vigentes; documentação arquitetural registra que `plataforma.versao_dataset` é legado/baseline de log per-carga e não deve ser usado como manifesto vigente.
**Critério de saída operacional:** `pytest ingestao/tests/test_versao_vigente.py` zero falhas; `make smoke-versao-vigente-tuss` comprova troca de versão, remoção da versão anterior em Bronze e invariante de uma vigente; `make smoke-tiss` executa sem o erro pré-existente de tipo em `scripts/seed_demo_rede.py`. Nenhuma alteração em modelos dbt aprovados.

## Regra-mãe da Fase 7 (não negociável nesta sprint)

- [x] Não alterar contrato de API.
- [x] Não alterar semântica de modelos dbt; `stg_tuss_*`, `stg_rede_assistencial`, `int_tuss_*` continuam exatamente como no baseline.
- [x] Não renomear tabelas `bruto_ans.tuss_*` ou `bruto_ans.rol_procedimento`.
- [x] Não materializar versões antigas no PostgreSQL da VPS por padrão nesta sprint; `carga_versao_vigente.py` descarta versões antigas quando a política exige última versão.
- [x] Histórico de versões antigas é vendido como add-on premium pela Sprint 38; nesta sprint apenas registramos disponibilidade, não carregamos.
- [x] Toda decisão de versão do mecanismo consulta `plataforma.versao_dataset_vigente` (manifesto) e `plataforma.politica_dataset.carregar_apenas_ultima_versao`. (`plataforma.versao_dataset` é log per-carga legado do baseline 002 — não é o manifesto vigente.)

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Manifesto de versão + filtro de carga por versão. |
| Schema físico | `plataforma` (tabela nova `versao_dataset_vigente`; `versao_dataset` é tabela de log per-carga legada do baseline 002). |
| Helper novo | `ingestao/app/versao_vigente.py`. |
| DAGs ajustadas | `dag_ingest_tuss.py`, `dag_ingest_rol.py`, `dag_ingest_depara_sip_tuss.py`, `dag_ingest_prestador_cadastral.py`, `dag_ingest_qualiss.py` — DAGs parametrizadas por arquivo/versão/URL oficial. |
| Tag dbt | nenhuma. |
| Owner técnico | Engenharia de dados HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Classificação LGPD | Pública ANS (TUSS/ROL/cadastros). |
| Regra de publicação | Tabelas-fonte continuam internas em `bruto_ans`. Somente a versão vigente registrada em `plataforma.versao_dataset_vigente` permanece na carga padrão das tabelas versionadas da Sprint 37. |
| Regra de rollback | Pausar DAGs da Sprint 37, reverter versão pelo runbook `docs/runbooks/reverter_versao_tuss.md` ou `drop table if exists plataforma.versao_dataset_vigente cascade;` em rollback total. **Não dropar `plataforma.versao_dataset`**, pois ela é legado/baseline de log per-carga. |

## Histórias

### HIS-37.1 — Tabela `plataforma.versao_dataset_vigente`

- [x] Criar `infra/postgres/init/032_fase7_versao_dataset.sql`.
- [x] DDL aplicada (nome final: `versao_dataset_vigente`, ver decisão técnica acima):

```sql
create table if not exists plataforma.versao_dataset_vigente (
    id bigserial primary key,
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    versao text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    publicado_em date,
    carregado_em timestamptz not null default now(),
    arquivo_bytes bigint,
    metadados jsonb,
    vigente boolean not null default true
);
create unique index if not exists ux_versao_dataset_vigente_dataset
    on plataforma.versao_dataset_vigente (dataset_codigo)
    where vigente = true;
```

- [x] Índices auxiliares `ix_versao_dataset_vigente_lookup` e `ix_versao_dataset_vigente_hash` criados.
- [x] View auxiliar `plataforma.vw_versao_vigente` agregando política + manifesto.
- [x] Comentário SQL: para cada `dataset_codigo` só pode existir uma linha com `vigente=true` simultaneamente.

### HIS-37.2 — Helper Python `versao_vigente.py`

- [x] Criar `ingestao/app/versao_vigente.py`.
- [x] Dataclass `VersaoDataset` com `id`, `dataset_codigo`, `versao`, `url_fonte`, `hash_arquivo`, `publicado_em`, `carregado_em`, `arquivo_bytes`, `metadados`, `vigente`.
- [x] Exceções: `PoliticaVersaoDatasetNaoEncontradaError`, `DatasetNaoVersionadoError`, `VersaoDatasetInvalidaError`, `DuasVersoesVigentesError`.
- [x] Função `obter_versao_vigente(dataset_codigo: str) -> VersaoDataset | None` lê `plataforma.versao_dataset_vigente where vigente=true`.
- [x] Função `registrar_nova_versao(...)`:
  - idempotente: mesmo `hash_arquivo` ⇒ `'nada_a_fazer'`;
  - hash diferente: marca anterior como `vigente=false` e insere nova com `vigente=true` em transação atômica.
- [x] Função `politica_exige_apenas_ultima_versao(dataset_codigo: str) -> bool` lê `plataforma.politica_dataset.carregar_apenas_ultima_versao`.
- [x] Função `descartar_versoes_antigas_em_bruto(schema, tabela, dataset_codigo, coluna_versao='versao_dataset')` é no-op quando tabela/coluna não existem; só deleta quando política exige última versão.
- [x] Função `calcular_hash_arquivo(caminho, algoritmo='sha256')` com leitura em chunks; MD5 explicitamente proibido.
- [x] Função `garantir_unica_versao_vigente(dataset_codigo)` valida invariante.

### HIS-37.3 — Ajuste das DAGs de TUSS/ROL/DE-PARA SIP-TUSS

**Status: RESOLVIDO — fluxo real parametrizado por arquivo local/landing.**

Mapeamento implementado:

- `ingestao/app/carga_versao_vigente.py` é o ponto de integração real: calcula SHA-256, registra manifesto vigente, insere em Bronze e remove versões antigas conforme política.
- `scripts/carregar_versao_vigente.py` expõe CLI operacional para arquivo oficial já baixado em landing/caminho local.
- `ingestao/dags/dag_ingest_tuss.py`, `ingestao/dags/dag_ingest_rol.py` e `ingestao/dags/dag_ingest_depara_sip_tuss.py` chamam a CLI com parâmetros `arquivo`, `versao`, `url_fonte` e `publicado_em`.
- `scripts/gerar_seeds_tuss_rol.py` continua apenas como gerador de seeds dbt sintéticos; não é usado como carga Bronze vigente.

Padrão operacional:

```python
from ingestao.app.versao_vigente import (
    calcular_hash_arquivo,
    descartar_versoes_antigas_em_bruto,
    registrar_nova_versao,
)

hash_arquivo = calcular_hash_arquivo(caminho_zip)
resultado = await registrar_nova_versao(
    "tuss_procedimento",
    versao=versao_detectada,
    url_fonte=url,
    hash_arquivo=hash_arquivo,
    publicado_em=publicado_em,
    arquivo_bytes=tamanho_bytes,
    metadados={"layout": "...", "linhas": ...},
)
if resultado == "nada_a_fazer":
    return  # idempotente
# baixa + INSERT só linhas da nova versão
await descartar_versoes_antigas_em_bruto("bruto_ans", "tuss_procedimento", "tuss_procedimento")
```

- [x] Criar `dag_ingest_tuss.py`, `dag_ingest_rol.py`, `dag_ingest_depara_sip_tuss.py` com carga real parametrizada.
- [x] Integrar `versao_vigente.py` e `carga_versao_vigente.py` no caminho operacional de carga.
- [x] Criar tabelas Bronze `bruto_ans.tuss_procedimento`, `bruto_ans.rol_procedimento` e `bruto_ans.depara_sip_tuss` com `versao_dataset`.
- [x] Documentar que histórico TUSS antigo é jogo da Sprint 38 (`historico_sob_demanda`), nunca da DAG mensal.

### HIS-37.4 — Snapshot atual para prestadores cadastrais e QUALISS

**Status: RESOLVIDO — fluxo real parametrizado por arquivo local/landing.**

- [x] Em DAG real de prestadores cadastrais (rede vigente), antes de carregar nova publicação:
  - registrar versão em `plataforma.versao_dataset_vigente`;
  - copiar tabela atual para `bruto_ans.prestador_cadastral_snapshot_anterior`;
  - truncar tabela-alvo `bruto_ans.prestador_cadastral`;
  - `INSERT` da nova versão completa;
  - manter snapshot anterior para rollback rápido (retenção operacional futura pela Sprint 39).
- [x] Idem para QUALISS: `bruto_ans.qualiss` + `bruto_ans.qualiss_snapshot_anterior`.
- [x] Criar `dag_ingest_prestador_cadastral.py` e `dag_ingest_qualiss.py` com parâmetros de arquivo/versão/URL oficial.
- [x] **Regra de classificação obrigatória:** todo dataset relacionado a prestador/rede precisa estar classificado explicitamente como `snapshot_atual`, `referencia_versionada` ou `grande_temporal` em `plataforma.politica_dataset`. Classificações ambíguas ou ausentes são proibidas. Validado em Etapa 4 (zero linhas).
- [x] **Separação entre prestador cadastral e fato histórico de rede:**
  - `prestador_cadastral` — snapshot atual do cadastro de prestadores. Entra como `snapshot_atual`.
  - `qualiss` — snapshot atual da QUALISS (qualificação). Entra como `snapshot_atual`.
  - `rede_vigente` (cnes_estabelecimento) — snapshot atual do cadastro CNES. Entra como `snapshot_atual` (ou `referencia_versionada` se mantivermos versão por mês ANS).
  - **Qualquer fonte de movimentação histórica de rede/prestador** (ex.: alterações de vínculo, histórico de credenciamento, movimentação mensal de rede) **deve ser classificada como `grande_temporal`**, nunca como `snapshot_atual`.
- [x] **Documentar em `docs/arquitetura/politica_carga_dataset.md`** a seção "Prestador cadastral vs fato histórico de rede", deixando explícito:
  - O HealthIntel carrega apenas o snapshot atual do cadastro de prestadores na VPS. Histórico de movimentação de rede/prestadores **não entra na carga padrão**.
  - Se houver fonte de fato histórico real (movimentação mensal de rede, alterações contratuais), ela deve respeitar a janela dinâmica da Sprint 36 (carga hot = ano vigente + ano anterior) ou histórico sob demanda da Sprint 38.
  - Versões antigas do cadastro de prestadores (ex.: prestador_cadastral de meses anteriores) **não entram na carga padrão da VPS** — são consideradas histórico premium se contratadas.
- [x] **Hardgate de classificação:** executado em 2026-04-28 — retornou zero linhas:

```sql
-- Hardgate: todo dataset prestador/rede precisa estar classificado explicitamente
SELECT dataset_codigo, classe_dataset
FROM plataforma.politica_dataset
WHERE dataset_codigo IN ('prestador_cadastral', 'qualiss', 'cnes_estabelecimento', 'rede_assistencial', 'rede_vigente')
  AND classe_dataset NOT IN ('snapshot_atual', 'referencia_versionada', 'grande_temporal');
-- Resultado: 0 rows.
```

Datasets em política hoje:
- `prestador_cadastral` → `snapshot_atual` (carregar_apenas_ultima_versao=true)
- `qualiss` → `snapshot_atual` (carregar_apenas_ultima_versao=true)
- `cnes_estabelecimento` → `snapshot_atual` (carregar_apenas_ultima_versao=false — versionado por mês ANS)
- `rede_assistencial` e `rede_vigente` → não incorporados como datasets de política nesta sprint; o dataset operacional equivalente já existente é `rede_prestador` (`grande_temporal`).

### HIS-37.5 — Garantia de não duplicidade

**Status: RESOLVIDO no schema raw** — tabelas Bronze versionadas criadas em `infra/postgres/init/032_fase7_versao_dataset.sql`.

- [x] Criar tabelas brutas reais para TUSS/ROL/DE-PARA com coluna `versao_dataset` e índice único por chave de negócio + versão.
- [x] Criar tabelas brutas reais para `prestador_cadastral` e `qualiss` com coluna `versao_dataset` e snapshot anterior.
- [x] `make smoke-versao-vigente-tuss` valida que, após nova versão, `bruto_ans.tuss_procedimento` mantém `count(distinct versao_dataset)=1`.
- [x] Validar com `select dataset_codigo, count(distinct versao) from plataforma.versao_dataset_vigente where vigente=true group by 1 having count(distinct versao) > 1` retornar zero linhas (validado: índice parcial garante unicidade por design).

### HIS-37.6 — Documentação

- [x] Atualizar `docs/arquitetura/politica_carga_dataset.md` com seção "Última versão vigente e snapshot atual".
- [x] Documentar que TUSS/ROL/DE-PARA têm tipicamente uma publicação por mês/trimestre e que histórico antigo é premium.
- [x] Listar URLs canônicas ANS dos manifests (sem links externos suspeitos; apenas referência ao domínio `gov.br/ans`).
- [x] Criar `docs/runbooks/reverter_versao_tuss.md` com procedimento completo de reversão.

### HIS-37.7 — Testes

- [x] Criar `ingestao/tests/test_versao_vigente.py` com 22 testes:
  - mesma versão (mesmo hash) é idempotente;
  - hash diferente vira nova versão e marca anterior como `vigente=false`;
  - tentativa de marcar duas vigentes simultâneas viola `ux_versao_dataset_vigente_dataset` (IntegrityError);
  - `descartar_versoes_antigas_em_bruto` apaga linhas com `versao_dataset` diferente da vigente quando `politica_exige_apenas_ultima_versao` é true; é no-op caso contrário (tabela/coluna inexistente);
  - hash MD5 explicitamente proibido;
  - dataset `grande_temporal` rejeitado para registro de manifesto;
  - hardgate de classificação prestador/rede com zero linhas.
  - carga real TUSS remove versão anterior e mantém uma `versao_dataset`;
  - snapshot de prestador preserva `snapshot_anterior` antes de substituir.
- [x] 22/22 testes passando.

## Entregas esperadas

- [x] `infra/postgres/init/032_fase7_versao_dataset.sql`
- [x] `ingestao/app/versao_vigente.py`
- [x] `ingestao/app/carga_versao_vigente.py`
- [x] `scripts/carregar_versao_vigente.py`
- [x] `scripts/smoke_versao_vigente_tuss.py`
- [x] DAGs TUSS/ROL/DE-PARA/prestadores cadastrais/QUALISS ajustadas conforme HIS-37.3 e HIS-37.4.
- [x] `ingestao/tests/test_versao_vigente.py`
- [x] Atualização de `docs/arquitetura/politica_carga_dataset.md`
- [x] Runbook curto de reversão de versão (`docs/runbooks/reverter_versao_tuss.md`)

## Validação esperada (hard gates)

- [x] `pytest ingestao/tests/test_versao_vigente.py -v` 22/22 zero falhas.
- [x] `make smoke-versao-vigente-tuss` valida `select count(*) from plataforma.versao_dataset_vigente where vigente=true and dataset_codigo='tuss_procedimento' = 1` dentro de transação controlada.
- [x] `make smoke-versao-vigente-tuss` valida `select count(distinct versao_dataset) from bruto_ans.tuss_procedimento = 1` dentro de transação controlada.
- [x] Tentativa SQL de duas vigentes simultâneas falha com violação de unique index — validado em `test_unique_vigente_impede_duas_vigentes` e `test_garantir_unica_versao_vigente_duas_falha`.
- [x] `make dag-parse` zero erros.
- [x] `make smoke-tiss` não falha mais pelo defeito pré-existente de tipo em `scripts/seed_demo_rede.py`; TISS continua fato (`tiss_producao`, grande_temporal) e não substitui o smoke dedicado de TUSS vigente.
- [x] `git diff --stat HEAD -- healthintel_dbt/models healthintel_dbt/macros api/app` saída vazia.
- [x] `pytest api/tests/integration/` zero falhas em coleta.
- [x] Inspeção: `grep -rn 'versao_2023\|versao_2024_03' healthintel_dbt/models` retorna zero.

## Distinção Estado Atual vs Estado-Alvo

| Eixo | Estado atual | Estado-alvo da Sprint 37 |
|------|--------------|--------------------------|
| Manifesto de versão | `plataforma.versao_dataset` legado existia apenas como log per-carga. | `plataforma.versao_dataset_vigente` rastreia URL/hash/data/versão vigente. |
| Carga TUSS | Sem Bronze versionado antes da Sprint 37. | `dag_ingest_tuss.py` + `carga_versao_vigente.py` carregam arquivo oficial parametrizado apenas na versão vigente em `bruto_ans.tuss_procedimento`. |
| Carga ROL | Sem Bronze versionado antes da Sprint 37. | `dag_ingest_rol.py` + `carga_versao_vigente.py` carregam arquivo oficial parametrizado apenas na versão vigente em `bruto_ans.rol_procedimento`. |
| Prestadores cadastrais | Sem fluxo de snapshot vigente antes da Sprint 37. | `dag_ingest_prestador_cadastral.py` usa snapshot atual + `prestador_cadastral_snapshot_anterior` para rollback rápido. |
| Histórico antigo de TUSS/ROL | Não carregado pela Sprint 37. | Não materializado por padrão; vendido como add-on premium pela Sprint 38. |
| Modelos dbt | Baseline `v3.8.0-gov`. | Idem (sem alteração). |

## Anti-padrões explicitamente rejeitados nesta sprint

- Carregar todas as versões TUSS publicadas desde 2014 "para garantir".
- Materializar versões antigas em `bruto_ans` quando a política diz `carregar_apenas_ultima_versao=true`.
- Ignorar `hash_arquivo` e re-carregar a mesma versão diariamente.
- Marcar duas linhas de `plataforma.versao_dataset_vigente` com `vigente=true` simultaneamente para o mesmo dataset.
- Apagar `bruto_ans.prestador_cadastral_snapshot_anterior` antes do prazo de retenção.
- Usar `requests`/`httpx` sem registrar URL e hash em `plataforma.versao_dataset_vigente` (rastreabilidade obrigatória).
- Marcar hardgates `[x]` antes de executar os comandos correspondentes.

## Dívida Técnica Separada

- [x] Formalizada em `docs/operacao/divida_tecnica_smoke_tiss.md`: `make smoke-tiss` falhava por defeito pré-existente em `scripts/seed_demo_rede.py`, antes de validar TISS ou qualquer artefato da Sprint 37.
- [x] Correção aplicada: `competencia` do seed de rede convertida para `int` nos registros Bronze; `make smoke-tiss` reexecutado.

## Resultado Esperado

Sprint 37 entrega o controle operacional de versão vigente: tabela `plataforma.versao_dataset_vigente`, helper `ingestao/app/versao_vigente.py`, helper de carga `ingestao/app/carga_versao_vigente.py`, tabelas Bronze versionadas, DAGs parametrizadas e testes de invariante (22/22). `plataforma.versao_dataset` permanece legado/baseline de log per-carga e não é manifesto vigente. A carga padrão de TUSS, ROL, DE-PARA SIP-TUSS, prestadores cadastrais e QUALISS agora recebe arquivo oficial por parâmetro e materializa somente a última versão vigente. Histórico antigo é produto premium controlado pela Sprint 38. Nenhum modelo dbt do baseline é alterado.

## Evidências de Execução Local — 2026-04-28

- `docker compose -f infra/docker-compose.yml exec -T postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel < infra/postgres/init/032_fase7_versao_dataset.sql`: 0 erros; tabela, índices, view e comentários reaplicados idempotentemente.
- `.venv/bin/pytest ingestao/tests/test_versao_vigente.py -v`: `22 passed in 1.23s`.
- `make smoke-versao-vigente-tuss`: passou; validou `vigente=smoke_2026_02`, `raw_versoes=1`, `manifesto_vigentes=1` em transação com rollback.
- `.venv/bin/pytest ingestao/tests/ -v`: `81 passed in 7.35s`.
- `docker compose -f infra/docker-compose.yml exec -T redis redis-cli FLUSHDB && .venv/bin/pytest api/tests/integration/ -v`: `32 passed in 0.77s` (flush local necessário para zerar rate-limit entre smokes/testes repetidos).
- `cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt parse`: 0 erros.
- `make dag-parse`: 0 erros; saída `Errors: {}`.
- `.venv/bin/ruff check .`: `All checks passed!`.
- `git diff --check`: saída vazia.
- `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros api/app`: saída vazia.
- `find ingestao/dags -maxdepth 1 -type f \( -name 'dag_ingest_tuss.py' -o -name 'dag_ingest_rol.py' -o -name 'dag_ingest_depara_sip_tuss.py' -o -name 'dag_ingest_prestador_cadastral.py' -o -name 'dag_ingest_qualiss.py' \) -print`: retornou as cinco DAGs da Sprint 37.
- `select to_regclass('bruto_ans.tuss_procedimento')`: retornou `bruto_ans.tuss_procedimento` após bootstrap 032.
- `make smoke-tiss`: passou; 3 checks, 0 falhas, HTTP 200 nos endpoints TISS/rede do smoke.
