# Política de Carga por Dataset

## Propósito

Este documento define a governança declarativa de carga de dados no HealthIntel Suplementar. Cada dataset ANS é classificado em uma das cinco classes suportadas, com uma estratégia de carga correspondente. Toda decisão de carga — quantos anos carregar, se particiona por ano, se carrega apenas última versão, se permite histórico sob demanda — é materializada na tabela `plataforma.politica_dataset` e consultada pelo código, nunca hardcoded.

## Classes de Dataset

| Classe | Definição | Estratégia de carga padrão |
|--------|-----------|----------------------------|
| `grande_temporal` | Fato volumoso com competência mensal. Ex.: SIB operadora, VDA, glosa. | `ano_vigente_mais_ano_anterior` (`anos_carga_hot=2`). |
| `pequena_full_ate_5gb` | Tabela cadastral/dimensão pequena. Ex.: CADOP, IDSS, IGR. | `full_ate_5gb` enquanto <= 5 GB físicos. |
| `referencia_versionada` | Tabela de referência publicada com versão (TUSS, ROL). | `ultima_versao_vigente`. Apenas a versão mais recente é materializada. |
| `snapshot_atual` | Cadastro/rede vigente sem histórico contratado. Ex.: prestador cadastral, QUALISS. | `snapshot_atual`. Substitui completamente a cada carga. |
| `historico_sob_demanda` | Janela histórica vendida como add-on premium. | `historico_sob_demanda`. Sem carga padrão; ativada sob entitlement. |

## Estratégias de Carga

| Estratégia | Comportamento |
|------------|---------------|
| `ano_vigente_mais_ano_anterior` | Carrega apenas o ano vigente + ano anterior (configurável via `anos_carga_hot`). |
| `full_ate_5gb` | Carrega completo enquanto `pg_total_relation_size` <= `limite_full_gb`. |
| `ultima_versao_vigente` | Carrega apenas a última versão publicada pela ANS. Versões anteriores são descartadas. |
| `snapshot_atual` | Carrega o snapshot completo atual, substituindo o anterior. |
| `historico_sob_demanda` | Sem carga padrão. Ativado via entitlement por cliente. |

## Reclassificação Automática com Aprovação Manual

Datasets classificados como `pequena_full_ate_5gb` podem carregar full enquanto o tamanho físico da tabela for ≤ 5 GB.

**Regra:**
- Se `pg_total_relation_size(schema_destino.tabela_destino)` ultrapassar `limite_full_gb` (5 GB), o sistema gera uma **recomendação de reclassificação** em `plataforma.reclassificacao_dataset_pendente`.
- A reclassificação **nunca é automática**. Exige aprovação manual (admin/comercial).
- A geração da recomendação é feita por `plataforma.registrar_reclassificacao_dataset_pendente()`, que é idempotente para recomendações abertas (`pendente`, `em_analise`, `aprovada`).
- Entradas planejadas sem tabela física ainda não são marcadas como `historico_sob_demanda=true`; o flag só passa a representar add-on histórico quando o dataset existir e houver política operacional aprovada.
- Sugestão automática de classe:
  - Se for fato temporal com coluna_competencia → sugerir `grande_temporal`.
  - Se for cadastro/dimensão sem competência → sugerir `snapshot_atual`.

## Matriz de Datasets e Lineage Operacional

Esta matriz cruza a política declarativa com os objetos reais do baseline. Entradas marcadas como **planejadas** são dependências explícitas das Sprints 37/38 e não devem ser tratadas como tabela ausente acidental.

| Dataset | Classe | Estratégia | Objeto físico | Status | DAG/leitura | Downstream dbt |
|---------|--------|------------|---------------|--------|-------------|----------------|
| sib_operadora | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.sib_beneficiario_operadora | existente | dag_ingest_sib / dag_mestre_mensal | stg_sib_operadora, api_bronze_sib_operadora |
| sib_municipio | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.sib_beneficiario_municipio | existente | dag_ingest_sib / dag_mestre_mensal | stg_sib_municipio, api_bronze_sib_municipio |
| tiss_producao | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.tiss_procedimento_trimestral | existente | dag_ingest_tiss | stg_tiss_procedimento, mart_tiss_procedimento |
| vda | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.vda_operadora_mensal | existente | dag_ingest_vda | stg_vda, fat_vda_operadora_mensal |
| glosa | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.glosa_operadora_mensal | existente | dag_ingest_glosa | stg_glosa, fat_glosa_operadora_mensal |
| portabilidade | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.portabilidade_operadora_mensal | existente | dag_ingest_portabilidade | stg_portabilidade, api_portabilidade_operadora_mensal |
| rede_prestador | grande_temporal | ano_vigente_mais_ano_anterior | bruto_ans.rede_prestador_municipio | existente | dag_ingest_rede_assistencial | stg_rede_assistencial, mart_rede_assistencial |
| cadop | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.cadop | existente | dag_ingest_cadop | stg_cadop, dim_operadora_atual |
| idss | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.idss | existente | dag_anual_idss | stg_idss, fat_idss_operadora |
| igr | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.igr_operadora_trimestral | existente | dag_ingest_igr | stg_igr, int_regulatorio_v2_operadora_trimestre |
| nip | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.nip_operadora_trimestral | existente | dag_ingest_nip | stg_nip, fat_reclamacao_operadora |
| regime_especial | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.regime_especial_operadora_trimestral | existente | dag_ingest_regime_especial | stg_regime_especial, fat_regime_especial_historico |
| prudencial | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.prudencial_operadora_trimestral | existente | dag_ingest_prudencial | stg_prudencial, int_regulatorio_v2_operadora_trimestre |
| lista_excelencia_reducao | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.rn623_lista_operadora_trimestral | existente | dag_ingest_rn623 | stg_rn623_lista, api_rn623_lista_trimestral |
| taxa_resolutividade | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.taxa_resolutividade_operadora_trimestral | existente | dag_ingest_taxa_resolutividade | stg_taxa_resolutividade, int_regulatorio_v2_operadora_trimestre |
| diops | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.diops_operadora_trimestral | existente | dag_ingest_diops | stg_diops, fat_financeiro_operadora_trimestral |
| fip | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.fip_operadora_trimestral | existente | dag_ingest_fip | stg_fip, fat_sinistralidade_procedimento |
| ans_arquivo_generico | pequena_full_ate_5gb | full_ate_5gb | bruto_ans.ans_arquivo_generico | existente | ELT genérico | stg_ans_arquivo_generico |
| dimensoes_ibge | pequena_full_ate_5gb | full_ate_5gb | ref_ans.ref_municipio_ibge | existente | dbt seed | dim_localidade |
| tuss_procedimento | referencia_versionada | ultima_versao_vigente | ref_ans.ref_tuss | planejada para bruto_ans.tuss_procedimento | dbt seed / Sprint 37 | stg_tuss_terminologia, dim_tuss_procedimento |
| tuss_material_opme | referencia_versionada | ultima_versao_vigente | bruto_ans.tuss_material_opme | planejada | Sprint 37 | a definir na Sprint 37 |
| tuss_medicamento | referencia_versionada | ultima_versao_vigente | bruto_ans.tuss_medicamento | planejada | Sprint 37 | a definir na Sprint 37 |
| depara_sip_tuss | referencia_versionada | ultima_versao_vigente | bruto_ans.depara_sip_tuss | planejada | Sprint 37 | xref_tiss_tuss_procedimento |
| rol_procedimento | referencia_versionada | ultima_versao_vigente | ref_ans.ref_rol_procedimento | planejada para bruto_ans.rol_procedimento | dbt seed / Sprint 37 | dim_tuss_procedimento |
| prestador_cadastral | snapshot_atual | snapshot_atual | bruto_ans.prestador_cadastral | planejada | Sprint 37 | mdm_prestador_master |
| qualiss | snapshot_atual | snapshot_atual | bruto_ans.qualiss | planejada | Sprint 37 | a definir na Sprint 37 |
| cnes_estabelecimento | snapshot_atual | snapshot_atual | bruto_ans.cnes_estabelecimento | existente | dag_ingest_cnes | stg_cnes_estabelecimento, fat_cnes_estabelecimento_municipio |
| ans_linha_generica | historico_sob_demanda | historico_sob_demanda | bruto_ans.ans_linha_generica | existente | ELT genérico | stg_ans_linha_generica |

## Prestador Cadastral vs Fato Histórico de Rede

- `prestador_cadastral` — snapshot atual do cadastro de prestadores. Classe `snapshot_atual`.
- `qualiss` — snapshot atual da QUALISS (qualificação). Classe `snapshot_atual`.
- `cnes_estabelecimento` — snapshot atual do cadastro CNES. Classe `snapshot_atual`.
- **Qualquer fonte de movimentação histórica de rede/prestador** (alterações de vínculo, histórico de credenciamento, movimentação mensal de rede) **deve ser classificada como `grande_temporal`**, nunca como `snapshot_atual`.

O HealthIntel carrega apenas o snapshot atual do cadastro de prestadores na VPS. Histórico de movimentação de rede/prestadores **não entra na carga padrão**. Versões antigas do cadastro de prestadores são consideradas histórico premium se contratadas.

## Janela Dinâmica de Carga

A janela de carga para datasets `grande_temporal` é aplicada na ingestão pela Sprint 36. A política vem sempre de `plataforma.politica_dataset` e a janela operacional vem sempre de `plataforma.calcular_janela_carga_anual`, sem ano fixo em código produtivo.

**Parâmetro operacional:**

- `ANS_ANOS_CARGA_HOT=2` é o default global.
- `politica_dataset.anos_carga_hot` tem precedência quando preenchido por dataset.
- Datasets não temporais não usam essa regra.

**Regra de janela:**

- Em 2026-04-28 com `anos_carga_hot=2`:
  - `ano_vigente = 2026`
  - `ano_inicial = 2025`
  - `ano_final = 2026`
  - `ano_preparado = 2027`
  - `competencia_minima = 202501`
  - `competencia_maxima_exclusiva = 202701`

- Na virada para 2027 a janela passa automaticamente para `[202601, 202801)` sem alteração de código.
- O limite inferior é inclusivo e o limite superior é exclusivo.
- Em 2026, `202501` até `202612` é aceito; `202412` e `202701` são fora da janela padrão.

**Comportamento de ingestão:**

- Arquivos fora da janela são ignorados com auditoria em `plataforma.ingestao_janela_decisao` usando `acao='ignorado_fora_janela'`.
- O load valida a janela novamente antes de inserir dados em Bronze; fora da janela sem fluxo histórico gera `HistoricoForaDaJanelaError` e `acao='rejeitado_historico_sem_flag'`.
- Carga concluída dentro da janela registra `acao='carregado'`.
- Antes do insert em dataset com `particionar_por_ano=true`, a ingestão chama `plataforma.preparar_particoes_janela_atual`.
- A aplicação ocorre nos módulos reais de ingestão e load (`ingestao/app/ingestao_real.py`, `ingestao/app/carregar_postgres.py` e `ingestao/app/pipeline_bronze.py`). Quando uma DAG do clone é apenas placeholder, a regra não é duplicada artificialmente na DAG; ela deve ser ligada ao fluxo real quando a DAG deixar de ser placeholder.
- Histórico fora da janela padrão é responsabilidade da Sprint 38, sob entitlement; DAGs padrão não devem usar `permitir_historico=True`.

**Monitoramento:**

```sql
select *
from plataforma.vw_ingestao_janela_resumo
order by dataset_codigo, acao;
```

## Última Versão Vigente e Snapshot Atual

A Sprint 37 introduz manifesto auditável de **versão vigente** para datasets de classe `referencia_versionada` e `snapshot_atual`. A carga padrão da VPS materializa apenas a última versão publicada pela ANS — versões antigas não entram na carga padrão.

### Princípios

- **TUSS, ROL e DE-PARA SIP-TUSS** são `referencia_versionada`. Tipicamente possuem uma publicação por mês ou trimestre. A carga padrão mantém apenas a última versão; histórico antigo é vendido como add-on premium pela Sprint 38.
- **prestador_cadastral, qualiss** são `snapshot_atual`. Cada carga substitui completamente a anterior. Versões antigas do cadastro de prestadores **não entram na carga padrão**; se contratadas, viram histórico premium.
- **cnes_estabelecimento** é `snapshot_atual` mas com `carregar_apenas_ultima_versao=false`, pois mantemos versionamento por mês ANS.
- Fato histórico real de movimentação de rede/prestadores (alterações de vínculo, credenciamento mensal) **deve ser classificado como `grande_temporal`**, respeitando a janela dinâmica da Sprint 36 ou o histórico sob demanda da Sprint 38.

### Manifesto: `plataforma.versao_dataset_vigente`

| Coluna | Função |
|--------|--------|
| `dataset_codigo` | FK para `plataforma.politica_dataset`. |
| `versao` | Identificador da versão (ex.: `2026.01`, número de release ANS, vigência). |
| `url_fonte` | URL ou caminho de origem do arquivo. |
| `hash_arquivo` | SHA-256 do arquivo carregado. Usado para idempotência. |
| `publicado_em` | Data de publicação oficial pela ANS, quando informada. |
| `carregado_em` | Timestamp da carga local. |
| `arquivo_bytes` | Tamanho em bytes. |
| `metadados` | JSON livre (layout, observações). |
| `vigente` | `true` apenas para a versão em uso. Unique index parcial impede duas vigentes. |

> **Nota de nomenclatura**: a tabela `plataforma.versao_dataset` (sem sufixo) já existe no baseline 002 como log per-carga genérico. Para evitar colisão e respeitar a Regra-mãe da Fase 7, o manifesto da Sprint 37 vive em `plataforma.versao_dataset_vigente`.

### Helper Python

`ingestao/app/versao_vigente.py` expõe:

- `obter_versao_vigente(dataset_codigo)` → `VersaoDataset | None`.
- `registrar_nova_versao(dataset_codigo, versao, url_fonte, hash_arquivo, ...)` → `'nova_versao'` ou `'nada_a_fazer'` (idempotente por `hash_arquivo`).
- `politica_exige_apenas_ultima_versao(dataset_codigo)` → `bool`.
- `descartar_versoes_antigas_em_bruto(schema, tabela, dataset_codigo)` — no-op se tabela/coluna não existir; deleta apenas quando política exige última versão.
- `calcular_hash_arquivo(caminho)` — SHA-256 em chunks. MD5 explicitamente proibido.
- `garantir_unica_versao_vigente(dataset_codigo)` — defesa em profundidade contra duas vigentes.

`ingestao/app/carga_versao_vigente.py` operacionaliza a carga Bronze:

- recebe arquivo local/landing (`csv`, `txt` ou `zip` com CSV/TXT), `dataset_codigo`, `versao`, `url_fonte` e `publicado_em`;
- carrega `bruto_ans.tuss_procedimento`, `bruto_ans.rol_procedimento`, `bruto_ans.depara_sip_tuss`, `bruto_ans.prestador_cadastral` e `bruto_ans.qualiss`;
- registra o manifesto em `plataforma.versao_dataset_vigente`;
- descarta versões antigas quando `plataforma.politica_dataset.carregar_apenas_ultima_versao=true`;
- para snapshots (`prestador_cadastral`, `qualiss`), copia a tabela atual para `*_snapshot_anterior` antes da substituição.

As DAGs da Sprint 37 são parametrizadas por arquivo oficial já disponível em landing/caminho local. Download/crawler automático de publicações ANS não é responsabilidade desta sprint; a rastreabilidade é preservada pelo `url_fonte` registrado no manifesto.

### Fontes canônicas ANS

Os manifests oficiais são publicados em `https://www.gov.br/ans/`. Não usar mirrors, agregadores externos ou APIs de terceiros (Serpro, BrasilAPI, Receita online, enrich-cnpj — todos proibidos pela Regra-mãe da Fase 5/7). Toda URL utilizada precisa ser registrada em `plataforma.versao_dataset_vigente.url_fonte` para rastreabilidade.

### Reverter versão em emergência

Procedimento operacional documentado em `docs/runbooks/reverter_versao_tuss.md`.

## Objetos de Suporte

| Objeto | Schema | Finalidade |
|--------|--------|------------|
| `politica_dataset` | `plataforma` | Tabela de governança declarativa por dataset. |
| `vw_tamanho_dataset` | `plataforma` | View que monitora tamanho físico real de cada dataset. |
| `reclassificacao_dataset_pendente` | `plataforma` | Recomendações de reclassificação quando ultrapassa 5 GB. |
| `calcular_tamanho_tabela_dataset` | `plataforma` | Função auxiliar que retorna tamanho em GB. |
| `registrar_reclassificacao_dataset_pendente` | `plataforma` | Função idempotente que registra pendências para tabelas pequenas acima de 5 GB. |
| `versao_dataset_vigente` | `plataforma` | **(Sprint 37)** Manifesto da versão vigente para `referencia_versionada` e `snapshot_atual`. |
| `vw_versao_vigente` | `plataforma` | **(Sprint 37)** View agregando política + manifesto + tempo desde a última carga. |
| `tuss_procedimento` | `bruto_ans` | **(Sprint 37)** Bronze da TUSS de procedimentos, mantendo apenas a versão vigente por padrão. |
| `rol_procedimento` | `bruto_ans` | **(Sprint 37)** Bronze do ROL, mantendo apenas a versão vigente por padrão. |
| `depara_sip_tuss` | `bruto_ans` | **(Sprint 37)** Bronze do DE-PARA SIP/TUSS, mantendo apenas a versão vigente por padrão. |
| `prestador_cadastral` | `bruto_ans` | **(Sprint 37)** Snapshot atual de prestadores cadastrais. |
| `qualiss` | `bruto_ans` | **(Sprint 37)** Snapshot atual QUALISS. |

## Exceções e Justificativas

| Dataset | Justificativa |
|---------|---------------|
| regime_especial | É cadastral mas tem snapshot histórico crítico para análise regulatória. Mantido como `pequena_full_ate_5gb`. |
| cnes_estabelecimento | Mantido como `snapshot_atual` com `carregar_apenas_ultima_versao=false` pois preservamos versão por mês ANS. |
| `plataforma.versao_dataset` (baseline 002) vs `plataforma.versao_dataset_vigente` (Sprint 37) | Tabelas distintas com finalidades distintas: a primeira é log per-carga genérico (baseline imutável); a segunda é manifesto de versão vigente. Não confundir. |

---

*Documento controlado pela Fase 7 — Sprint 34, ampliado pela Sprint 37. Revisões exigem aprovação do time de dados.*
