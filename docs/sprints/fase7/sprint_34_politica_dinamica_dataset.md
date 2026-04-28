# Sprint 34 — Política Dinâmica de Carga por Dataset

**Status:** Resolvida
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** nenhuma intermediária (tag final da fase: `v4.2.0-dataops` ao fim da Sprint 40)
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov` quando publicada). Fases 1 a 5 não são alteradas por esta sprint.
**Schema novo:** nenhum schema criado. Tabela nova `plataforma.politica_dataset` registrada no schema `plataforma` já existente.
**Objetivo:** classificar todos os datasets ANS atualmente carregados (e os planejados) em uma matriz declarativa de classe + estratégia de carga, materializada em `plataforma.politica_dataset`, sem alterar nenhum modelo dbt, DAG, API ou seed aprovados nas Fases 1 a 5.
**Critério de saída técnico:** `plataforma.politica_dataset` criada via novo bootstrap SQL (`infra/postgres/init/029_fase7_politica_dataset.sql`); 100% dos datasets atualmente em `_sources.yml` classificados em uma das classes (`grande_temporal`, `pequena_full_ate_5gb`, `referencia_versionada`, `snapshot_atual`, `historico_sob_demanda`); documento `docs/arquitetura/politica_carga_dataset.md` publicado; nenhum byte alterado nos modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*`, `dq_*`, `mdm_*`, `consumo_premium_*`, `api_premium_*` do baseline.
**Critério de saída operacional:** `psql` mostra a tabela `plataforma.politica_dataset` populada com pelo menos as entradas de SIB operadora, SIB município, CADOP, IDSS, IGR, NIP, regime especial, prudencial, TUSS procedimento, DE-PARA SIP-TUSS, ROL, prestadores e dimensões IBGE; `dbt parse` zero erros; `pytest ingestao/tests` zero falhas; diff contra baseline `v3.8.0-gov` mostra zero alteração em modelos aprovados.

## Regra-mãe da Fase 7 (não negociável nesta sprint)

- [x] Não alterar contrato de API.
- [x] Não alterar semântica dos modelos dbt existentes.
- [x] Não renomear tabelas existentes sem plano de migração.
- [x] Toda lógica nova entra como artefato novo (bootstrap SQL novo, documento novo, seed dbt novo se aplicável).
- [x] Nenhum dataset grande pode ficar sem política classificada.
- [x] Nenhum dataset versionado carrega histórico antigo por padrão; entradas planejadas ficam com `historico_sob_demanda=false` até haver política operacional aprovada.
- [x] Documentação em português-brasil; checkbox `[ ]` até execução real.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Governança declarativa de carga. |
| Schema físico | `plataforma` (existente). Nova tabela `plataforma.politica_dataset`. |
| Tag dbt | nenhuma (artefato é tabela operacional, não modelo dbt). |
| Materialização | Tabela física PostgreSQL criada via bootstrap SQL. |
| Upstream permitido | Nenhum (tabela de configuração; dados inseridos via SQL versionado). |
| Downstream esperado | Sprints 35 (particionamento), 36 (filtro de janela), 37 (versão vigente), 38 (histórico sob demanda). |
| Owner técnico | Engenharia de dados HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Classificação LGPD | Operacional/interna (não contém dados pessoais). |
| Regra de publicação | Interna apenas. Não exposta em FastAPI, `consumo_ans` ou `consumo_premium_ans`. |
| Regra de rollback | `drop table plataforma.politica_dataset` + remoção de `infra/postgres/init/029_fase7_politica_dataset.sql` + remoção do documento `docs/arquitetura/politica_carga_dataset.md`. Baseline da Fase 5 permanece intacto. |

## Classes de dataset suportadas

| Classe | Definição | Estratégia de carga padrão |
|--------|-----------|----------------------------|
| `grande_temporal` | Fato volumoso com competência mensal. | `ano_vigente_mais_ano_anterior` (`anos_carga_hot=2`). |
| `pequena_full_ate_5gb` | Tabela cadastral/dimensão pequena. | `full_ate_5gb`. |
| `referencia_versionada` | Tabela de referência publicada com versão (TUSS, ROL). | `ultima_versao_vigente`. |
| `snapshot_atual` | Cadastro/rede vigente sem histórico contratado. | `snapshot_atual`. |
| `historico_sob_demanda` | Janela histórica vendida como add-on. | `historico_sob_demanda` (sem carga padrão). |

## Histórias

### HIS-34.1 — Documento arquitetural da política de carga

- [x] Criar `docs/arquitetura/politica_carga_dataset.md`.
- [x] Descrever as cinco classes (`grande_temporal`, `pequena_full_ate_5gb`, `referencia_versionada`, `snapshot_atual`, `historico_sob_demanda`).
- [x] Descrever as estratégias de carga (`ano_vigente_mais_ano_anterior`, `full_ate_5gb`, `ultima_versao_vigente`, `snapshot_atual`, `historico_sob_demanda`).
- [x] Documentar matriz de datasets atuais e classe atribuída, cobrindo no mínimo: SIB operadora, SIB município, D-TISS, VDA, glosa, portabilidade, CADOP, IDSS, IGR, NIP, regime especial, prudencial, lista de excelência/redução, TUSS procedimento, TUSS material, TUSS medicamento, DE-PARA SIP-TUSS, ROL procedimentos, prestadores/rede, QUALISS, dimensões IBGE/UF/município, seeds/ref.
- [x] Documentar regra de recomendação automática com aprovação manual: quando uma tabela `pequena_full_ate_5gb` ultrapassar 5 GB físicos, o sistema gera recomendação de reclassificação para `grande_temporal` ou `snapshot_atual`, que deve ser aprovada manualmente.
- [x] Documentar exceções e justificativas (ex.: regime especial é cadastral mas tem snapshot histórico crítico).

### HIS-34.2 — Tabela `plataforma.politica_dataset`

- [x] Criar `infra/postgres/init/029_fase7_politica_dataset.sql`.
- [x] DDL exata:

```sql
create table if not exists plataforma.politica_dataset (
    dataset_codigo text primary key,
    descricao text not null,
    classe_dataset text not null
        check (classe_dataset in ('grande_temporal','pequena_full_ate_5gb','referencia_versionada','snapshot_atual','historico_sob_demanda')),
    estrategia_carga text not null
        check (estrategia_carga in ('ano_vigente_mais_ano_anterior','full_ate_5gb','ultima_versao_vigente','snapshot_atual','historico_sob_demanda')),
    schema_destino text not null,
    tabela_destino text not null,
    coluna_competencia text,
    anos_carga_hot integer,
    limite_full_gb numeric(10,2),
    particionar_por_ano boolean not null default false,
    carregar_apenas_ultima_versao boolean not null default false,
    historico_sob_demanda boolean not null default true,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);
```

- [x] Adicionar índice por `classe_dataset`.
- [x] Adicionar trigger para atualizar `atualizado_em` em qualquer `update`.
- [x] Validar `check` constraints com `psql`.

### HIS-34.3 — Carga inicial declarativa

- [x] Inserir entrada `sib_operadora` com classe `grande_temporal`, estratégia `ano_vigente_mais_ano_anterior`, `anos_carga_hot=2`, `particionar_por_ano=true`.
- [x] Inserir entrada `sib_municipio` com classe `grande_temporal`, estratégia `ano_vigente_mais_ano_anterior`, `anos_carga_hot=2`, `particionar_por_ano=true`.
- [x] Inserir entrada `tiss_producao` com classe `grande_temporal` (quando produção D-TISS for habilitada).
- [x] Inserir entrada `vda` com classe `grande_temporal`.
- [x] Inserir entrada `glosa` com classe `grande_temporal` (revisar volume; permite reclassificar para `pequena_full_ate_5gb` se confirmado <5GB).
- [x] Inserir entrada `portabilidade` com classe `grande_temporal`.
- [x] Inserir entrada `cadop` com classe `pequena_full_ate_5gb`, estratégia `full_ate_5gb`, `limite_full_gb=5`.
- [x] Inserir entrada `idss` com classe `pequena_full_ate_5gb`.
- [x] Inserir entrada `igr` com classe `pequena_full_ate_5gb`.
- [x] Inserir entrada `nip` com classe `pequena_full_ate_5gb`.
- [x] Inserir entrada `regime_especial` com classe `pequena_full_ate_5gb`, justificando snapshot histórico crítico em comentário SQL.
- [x] Inserir entrada `prudencial` com classe `pequena_full_ate_5gb`.
- [x] Inserir entrada `lista_excelencia_reducao` com classe `pequena_full_ate_5gb`.
- [x] Inserir entrada `tuss_procedimento` com classe `referencia_versionada`, estratégia `ultima_versao_vigente`, `carregar_apenas_ultima_versao=true`.
- [x] Inserir entrada `tuss_material_opme` com classe `referencia_versionada`.
- [x] Inserir entrada `tuss_medicamento` com classe `referencia_versionada`.
- [x] Inserir entrada `depara_sip_tuss` com classe `referencia_versionada`.
- [x] Inserir entrada `rol_procedimento` com classe `referencia_versionada`.
- [x] Inserir entrada `prestador_cadastral` com classe `snapshot_atual`, estratégia `snapshot_atual`.
- [x] Inserir entrada `qualiss` com classe `snapshot_atual`.
- [x] Inserir entrada `cnes_estabelecimento` com classe `snapshot_atual` (ou `referencia_versionada` se mantivermos versão por mês ANS — decidir e documentar).
- [x] Inserir entrada `dimensoes_ibge` com classe `pequena_full_ate_5gb` (UF/município/competência via seed).

### HIS-34.5 — Medição automática de tabelas pequenas e reclassificação pendente

Criar view/função para monitorar o tamanho físico real de cada tabela classificada como `pequena_full_ate_5gb` e registrar recomendações de reclassificação quando o limite de 5 GB for excedido.

- [x] Criar view `plataforma.vw_tamanho_dataset` que calcula `pg_total_relation_size` para cada `schema_destino`.`tabela_destino` registrada em `plataforma.politica_dataset`:

```sql
create or replace view plataforma.vw_tamanho_dataset as
select
    pd.dataset_codigo,
    pd.descricao,
    pd.classe_dataset,
    pd.schema_destino,
    pd.tabela_destino,
    pd.limite_full_gb,
    coalesce(
        (
            select pg_total_relation_size(to_regclass(format('%I.%I', pd.schema_destino, pd.tabela_destino)))::numeric / 1e9
        ),
        0
    )::numeric(12,4) as tamanho_gb,
    case
        when pd.classe_dataset = 'pequena_full_ate_5gb'
             and coalesce(
                 (
                     select pg_total_relation_size(to_regclass(format('%I.%I', pd.schema_destino, pd.tabela_destino)))::numeric / 1e9
                 ),
                 0
             ) > pd.limite_full_gb
        then true
        else false
    end as acima_do_limite
from plataforma.politica_dataset pd
where pd.ativo = true;
```

- [x] Criar tabela `plataforma.reclassificacao_dataset_pendente`:

```sql
create table if not exists plataforma.reclassificacao_dataset_pendente (
    id bigserial primary key,
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    tamanho_gb numeric(12,4) not null,
    limite_full_gb numeric(10,2) not null,
    classe_atual text not null,
    classe_sugerida text not null
        check (classe_sugerida in ('grande_temporal','snapshot_atual','referencia_versionada','historico_sob_demanda')),
    motivo text not null,
    detectado_em timestamptz not null default now(),
    status text not null default 'pendente'
        check (status in ('pendente','aprovada','rejeitada','em_analise')),
    aprovado_em timestamptz,
    aprovado_por text,
    constraint ck_reclassificacao_classe_diferente
        check (classe_atual <> classe_sugerida)
);
create index if not exists ix_reclassificacao_pendente_status
    on plataforma.reclassificacao_dataset_pendente (status)
    where status in ('pendente','em_analise');
```

- [x] Regra operacional:
  - Um dataset `pequena_full_ate_5gb` pode continuar carregando full enquanto `pg_total_relation_size(schema_destino.tabela_destino) <= 5 GB`.
  - Se ultrapassar 5 GB, gerar **alerta** e registrar **recomendação de reclassificação** em `plataforma.reclassificacao_dataset_pendente`, sem reclassificar automaticamente.
  - A reclassificação exige aprovação manual (admin/comercial). Não automatizar `UPDATE politica_dataset SET classe_dataset = 'grande_temporal'`.
- [x] Sugestão de classe:
  - Se for fato temporal com competência → sugerir `grande_temporal`.
  - Se for cadastro/dimensão sem competência → sugerir `snapshot_atual`.
  - Registrar o `motivo` com o tamanho atual e a justificativa.
- [x] Criar função auxiliar `plataforma.calcular_tamanho_tabela_dataset(p_dataset_codigo text) returns numeric` que retorna `pg_total_relation_size` em GB.

**Hardgates da HIS-34.5:**

- [x] `psql -d healthintel -c "select dataset_codigo, tamanho_gb, acima_do_limite from plataforma.vw_tamanho_dataset where classe_dataset = 'pequena_full_ate_5gb'"` executa sem erro.
- [x] `psql -d healthintel -c "\dt plataforma.reclassificacao_dataset_pendente"` mostra a tabela criada.
- [x] Nenhuma tabela classificada como `pequena_full_ate_5gb` pode estar acima de 5 GB sem ter um registro correspondente em `plataforma.reclassificacao_dataset_pendente` com `status in ('pendente','em_analise','aprovada')`. Hardgate validado por:

```sql
select count(*)
from plataforma.vw_tamanho_dataset vw
where vw.classe_dataset = 'pequena_full_ate_5gb'
  and vw.acima_do_limite = true
  and not exists (
      select 1
      from plataforma.reclassificacao_dataset_pendente r
      where r.dataset_codigo = vw.dataset_codigo
        and r.status in ('pendente','em_analise','aprovada')
  );
-- Deve retornar 0
```

### HIS-34.6 — Documentação cruzada

- [x] Atualizar `docs/sprints/fase7/README.md` referenciando o documento arquitetural.
- [x] Adicionar seção em `docs/arquitetura/politica_carga_dataset.md` listando o cruzamento dataset x classe x DAG x modelo dbt downstream (somente leitura — sem alterar DAGs/modelos nesta sprint).
- [x] Garantir que toda entrada da tabela aponte para `schema_destino`/`tabela_destino` realmente existente no baseline ou explicitamente marcada como "planejada".

## Entregas esperadas

- [x] `docs/arquitetura/politica_carga_dataset.md`
- [x] `infra/postgres/init/029_fase7_politica_dataset.sql`
- [x] Atualização de `docs/sprints/fase7/README.md` referenciando este documento.
- [x] Tabela `plataforma.politica_dataset` populada conforme HIS-34.3.

## Validação esperada (hard gates)

Cada item abaixo precisa de evidência objetiva (saída de comando) antes de ser marcado `[x]`. A skill `healthintel-sprint-release-hardgates` proíbe marcar antes da execução real.

- [x] `psql -d healthintel -c "\dt plataforma.politica_dataset"` mostra a tabela criada.
- [x] `psql -d healthintel -c "select count(*), classe_dataset from plataforma.politica_dataset group by classe_dataset"` mostra ao menos uma entrada em cada classe efetivamente usada (`grande_temporal`, `pequena_full_ate_5gb`, `referencia_versionada`, `snapshot_atual`).
- [x] `psql -d healthintel -c "select dataset_codigo from plataforma.politica_dataset where ativo = true order by dataset_codigo"` lista no mínimo os 20 datasets requeridos pela HIS-34.3.
- [x] `psql -d healthintel -c "insert into plataforma.politica_dataset (dataset_codigo, descricao, classe_dataset, estrategia_carga, schema_destino, tabela_destino) values ('teste','teste','classe_inexistente','full_ate_5gb','x','y')"` falha com erro de check constraint.
- [x] `dbt parse --project-dir healthintel_dbt --profiles-dir healthintel_dbt` zero erros.
- [x] `pytest ingestao/tests` zero falhas.
- [x] `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros api/app ingestao/dags` saída vazia. Observação: a tag local `v3.8.0-gov` não existe neste clone, então o hardgate foi validado contra o worktree atual nos paths protegidos.
- [x] Documento `docs/arquitetura/politica_carga_dataset.md` revisado e referenciado pelo `docs/sprints/fase7/README.md`.

## Evidência de Fechamento — 2026-04-28

| Validação | Resultado |
|-----------|-----------|
| Reaplicação de `infra/postgres/init/029_fase7_politica_dataset.sql` | `INSERT 0 28`, sem erro. |
| `\dt plataforma.politica_dataset` | tabela criada. |
| `\dt plataforma.reclassificacao_dataset_pendente` | tabela criada. |
| Classes ativas | `grande_temporal=7`, `pequena_full_ate_5gb=12`, `referencia_versionada=5`, `snapshot_atual=3`, `historico_sob_demanda=1`. |
| Datasets ativos | 28 políticas ativas. |
| Cobertura de `healthintel_dbt/models/staging/_sources.yml` | `fontes_sem_politica` vazio; 20 fontes cobertas. |
| Check constraint de classe inválida | insert rejeitado por `politica_dataset_classe_dataset_check`. |
| `plataforma.vw_tamanho_dataset` | executa sem erro para 12 datasets pequenos. |
| `plataforma.registrar_reclassificacao_dataset_pendente()` | `0` recomendações criadas; nenhuma pendência ausente. |
| Planejadas sem tabela física e `historico_sob_demanda=true` | `0`. |
| `dbt parse` | zero erros. |
| `pytest ingestao/tests -v` | `17 passed`. |
| `ruff check .` | `All checks passed!`. |
| Diff de paths protegidos | `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros api/app ingestao/dags` vazio. |

## Distinção Ponto de Partida vs Estado Entregue

| Eixo | Ponto de partida | Estado entregue da Sprint 34 |
|------|--------------|--------------------------|
| Política de carga | Implícita no código de cada DAG/modelo. | Declarativa em `plataforma.politica_dataset`. |
| Documento arquitetural | Não existe. | `docs/arquitetura/politica_carga_dataset.md` publicado. |
| Cobertura | 0 datasets classificados formalmente. | 100% dos datasets do `_sources.yml` classificados. |
| Bootstrap SQL | `028_fase5_mdm_privado_rls.sql` é o último arquivo. | `029_fase7_politica_dataset.sql` adicionado. |
| Modelos dbt | Baseline `v3.8.0-gov`. | Idem (não tocado). |
| API | Baseline `v3.8.0-gov`. | Idem (não tocado). |

## Anti-padrões explicitamente rejeitados nesta sprint

- Hardcodar lista de datasets no Python; toda decisão de carga deve ser consultável via `plataforma.politica_dataset`.
- Alterar DAGs ou modelos dbt nesta sprint; o consumo da política só ocorre nas Sprints 35–38.
- Apagar/renomear bootstrap SQL anterior; todos os scripts `infra/postgres/init/0XX_*.sql` são imutáveis quando entregues.
- Marcar entradas como `historico_sob_demanda=true` em datasets que ainda nem foram carregados; o flag só representa que o histórico vai virar add-on premium, não que ele já está disponível.
- Marcar hardgates `[x]` antes de executar os comandos correspondentes (proibido pela skill `healthintel-sprint-release-hardgates`).

## Resultado Esperado

Sprint 34 entrega o ponto-zero da Fase 7: governança declarativa de carga em `plataforma.politica_dataset`. Toda decisão posterior (criar partições, filtrar janela, decidir versão única, abrir histórico premium) passa a consultar essa tabela em vez de hardcodar listas. Nenhum modelo/DAG do baseline `v3.8.0-gov` é alterado nesta sprint; ela é puramente aditiva e desbloqueia as Sprints 35 a 38.
