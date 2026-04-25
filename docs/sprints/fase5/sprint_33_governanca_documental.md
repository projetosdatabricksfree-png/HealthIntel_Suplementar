# Sprint 33 — Governança Documental, Catálogos e Padrões Normativos

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.8.0-gov` (sprint pós-Fase 5 técnica)
**Ordem na Fase 5:** executada após as Sprints 26–32 (Baseline → Validação → Receita → MDM → Premium → Endpoints) — a governança formaliza, em documento normativo, o que essas sprints já implementaram tecnicamente.

## Objetivo

Criar a base documental e normativa de governança da plataforma HealthIntel Suplementar para orientar todas as próximas implementações. Esta sprint é **documental e normativa** — não altera tabelas, modelos, índices, constraints, funções, triggers ou qualquer artefato físico já aprovado em hardgate. Toda nova tabela, coluna, índice, chave, relacionamento, constraint, função, trigger ou data product passará a ser obrigatoriamente regida pelos documentos aqui produzidos.

## Regra principal

> **Nada que já tenha passado em hardgate pode ser alterado.**
>
> Tabelas, colunas, schemas, modelos dbt, contratos de API, índices físicos, materializações, particionamentos, marts Gold, modelos `consumo_ans`, role `healthintel_cliente_reader`, DAGs em produção e endpoints publicados permanecem **imutáveis** sob esta sprint. A governança aqui criada **vale a partir das próximas implementações**, sem reescrita retroativa.

## Entregáveis

### Documentos raiz de governança

- [ ] `docs/governanca/README.md` — visão geral da governança documental, sumário, ordem de leitura
- [ ] `docs/governanca/catalogo_tabelas.md` — catálogo oficial de tabelas
- [ ] `docs/governanca/dicionario_colunas.md` — dicionário oficial de colunas
- [ ] `docs/governanca/padroes_tipagem.md` — padrões oficiais de tipagem física e lógica
- [ ] `docs/governanca/padroes_nomenclatura.md` — padrões de nomes para todos os artefatos
- [ ] `docs/governanca/padroes_indices_chaves_constraints.md` — governança de índices, chaves, constraints
- [ ] `docs/governanca/padroes_competencia_datas.md` — regra oficial de competência e datas
- [ ] `docs/governanca/padroes_qualidade_validacao.md` — regras de qualidade documental
- [ ] `docs/governanca/mdm_governanca.md` — governança de MDM, golden record, crosswalk
- [ ] `docs/governanca/hardgate_governanca.md` — hardgate documental obrigatório

### Templates oficiais

- [ ] `docs/governanca/templates/template_tabela.md`
- [ ] `docs/governanca/templates/template_coluna.md`
- [ ] `docs/governanca/templates/template_indice.md`
- [ ] `docs/governanca/templates/template_constraint.md`
- [ ] `docs/governanca/templates/template_funcao.md`
- [ ] `docs/governanca/templates/template_trigger.md`
- [ ] `docs/governanca/templates/template_relacionamento.md`
- [ ] `docs/governanca/templates/template_data_product.md`
- [ ] `docs/governanca/templates/template_mdm.md`
- [ ] `docs/governanca/templates/template_quality_rule.md`
- [ ] `docs/governanca/templates/template_excecao.md`

---

## Histórias

### HIS-13.1 — Catálogo Oficial de Tabelas

Criar o catálogo único e oficial de todas as tabelas da plataforma, com metadados de governança.

- [ ] Criar `docs/governanca/catalogo_tabelas.md` com a estrutura padrão para cada tabela:
  - [ ] o que é a tabela
  - [ ] de onde vem (fonte oficial)
  - [ ] para que serve
  - [ ] camada (`bruto_ans` | `stg_ans` | `int_ans` | `nucleo_ans` | `api_ans` | `consumo_ans` | `consumo_premium` | `mdm` | `plataforma`)
  - [ ] granularidade (uma linha por X)
  - [ ] chave natural
  - [ ] chave surrogate
  - [ ] upstream (lista de tabelas que alimentam)
  - [ ] downstream (lista de tabelas que são alimentadas)
  - [ ] status de publicação (`rascunho` | `homologado` | `publicado` | `deprecated`)
  - [ ] sensibilidade LGPD (`pública` | `interna` | `restrita` | `pessoal` | `sensível`)
  - [ ] owner técnico
  - [ ] owner de negócio
- [ ] Listar no catálogo todas as tabelas existentes hoje (`bruto_ans.*`, `stg_ans.*`, `int_ans.*`, `nucleo_ans.*`, `api_ans.*`, `consumo_ans.*`, `plataforma.*`) **sem alterá-las** — apenas registrar o estado vigente.
- [ ] Documentar que **toda nova tabela** deverá ser registrada neste catálogo antes de ser materializada.
- [ ] Definir que catálogo é a fonte da verdade — divergência entre catálogo e implementação física é exceção formal.

### HIS-13.2 — Dicionário Oficial de Colunas

Criar o dicionário oficial de colunas da plataforma com regras de preenchimento e validação.

- [ ] Criar `docs/governanca/dicionario_colunas.md` com a estrutura padrão por coluna:
  - [ ] o que é a coluna
  - [ ] de onde vem (origem física na fonte ANS / DATASUS / interno)
  - [ ] para que serve
  - [ ] tipo físico (PostgreSQL e equivalente SQL Server, quando aplicável)
  - [ ] tipo lógico (domínio de negócio)
  - [ ] aceita nulo (sim / não / condicional)
  - [ ] regra de preenchimento
  - [ ] regra de normalização (referência à macro dbt ou função SQL)
  - [ ] regra de validação (referência ao teste dbt ou check constraint)
  - [ ] exemplo válido
  - [ ] exemplo inválido
  - [ ] chave (PK | FK | natural | surrogate | nenhuma)
  - [ ] indexável (sim / não / condicional)
  - [ ] exposta na API (sim / não / condicional)
  - [ ] sensibilidade LGPD
- [ ] Cadastrar inicialmente as colunas críticas que aparecem em múltiplas tabelas: `registro_ans`, `competencia`, `cnpj`, `cpf`, `cnes`, `uf`, `cd_municipio`, `cd_procedimento_tuss`, `valor_*`, `qt_*`, `taxa_*`, `dt_*`, `_carregado_em`, `_hash_arquivo`, `_lote_ingestao`.
- [ ] Definir que **toda nova coluna** deve ter entrada neste dicionário antes de subir para hardgate.

### HIS-13.3 — Padrões de Tipagem

Definir o padrão oficial de tipagem física e lógica.

- [ ] Criar `docs/governanca/padroes_tipagem.md` com regras obrigatórias:
  - [ ] CPF sempre `varchar(11)` — nunca numérico
  - [ ] CNPJ sempre `varchar(14)` — nunca numérico
  - [ ] competência sempre `int` no formato `YYYYMM`
  - [ ] valores monetários, saldos, receitas, despesas, mensalidades, sinistros, glosas e pagamentos sempre `decimal(18,2)`
  - [ ] taxas, alíquotas, índices, percentuais técnicos e métricas com escala maior usam `float` (precisão dupla) — proibido para valor monetário
  - [ ] quantidades sempre `bigint`
  - [ ] flags sempre `bit`, aceitando somente `0` ou `1`
  - [ ] datas funcionais sempre `datetime2` (PostgreSQL: `timestamp(3)` em colunas técnicas, `date` em colunas de data pura)
  - [ ] timestamps técnicos sempre `datetime2`
  - [ ] códigos com zero à esquerda sempre `varchar` — nunca numérico
  - [ ] `registro_ans` sempre `varchar(6)`, normalizado pela macro `normalizar_registro_ans()`
  - [ ] `cnes` sempre `varchar(7)`
  - [ ] `uf` sempre `char(2)`, maiúscula, validada contra lista oficial de UFs
- [ ] Mapear cada padrão para o tipo equivalente em PostgreSQL e SQL Server, com observação para `dbt` Postgres.
- [ ] Listar exceções formais já aprovadas (se houver), com justificativa, owner e data.
- [ ] Determinar que tipagem fora do padrão exige aprovação documental antes do hardgate físico.

### HIS-13.4 — Governança de Precisão, Escala e Tipo Numérico

Garantir consistência absoluta no domínio numérico, separando dinheiro de métrica técnica.

- [ ] Criar a seção "Precisão e Escala" em `docs/governanca/padroes_tipagem.md`:
  - [ ] justificar formalmente por que valores financeiros usam `decimal(18,2)` (precisão exata, requisito contábil-regulatório)
  - [ ] proibir uso de `float`, `double precision` ou `real` para valor monetário em qualquer camada
  - [ ] permitir `float` apenas para taxas, alíquotas, índices, percentuais técnicos e métricas com escala maior
  - [ ] proibir tipos diferentes para o mesmo domínio sem justificativa formal (ex.: receita não pode ser `decimal(18,2)` em uma tabela e `numeric(20,4)` em outra)
  - [ ] criar regra de exceção aprovada — modelo de registro com motivo, alternativa avaliada e owner
  - [ ] tornar obrigatória a documentação que justifique precisão e escala de qualquer campo numérico fora dos padrões
  - [ ] criar regra de revisão técnica para alteração de tipo numérico em coluna já publicada (sempre via deprecation + nova coluna, nunca alteração direta)
- [ ] Documentar a relação `decimal(18,2)` ↔ contabilidade ANS/DIOPS/SIB (convergência normativa).

### HIS-13.5 — Regra Oficial de Competência

Padronizar o conceito e a representação de competência em toda a plataforma.

- [ ] Criar `docs/governanca/padroes_competencia_datas.md`:
  - [ ] regra: competência é sempre normalizada para `YYYYMM`
  - [ ] regra: armazenamento sempre `int`
  - [ ] nome preferencial da coluna: `competencia` (não `anomes`, `mes_referencia`, `dt_competencia` em tabelas publicadas)
  - [ ] validação: `mes` entre `01` e `12`
  - [ ] validação: competência dentro de faixa aceitável (mínima `200001`, máxima `competencia_atual + 1`)
  - [ ] diferenciar formalmente: `competencia` ≠ `data de carga` ≠ `data de processamento` ≠ `data de atualização`
  - [ ] documentar aliases de origem encontrados em fontes ANS: `anomes`, `ano_mes`, `mes_referencia`, `periodo`, `dt_competencia`, `data_atendimento` — todos devem ser convertidos para `competencia` na staging quando representarem competência
  - [ ] reservar entrada para macro futura `normalizar_competencia(coluna_origem, formato_origem)` com contrato de entrada/saída especificado
- [ ] Listar regras de validação aplicáveis: `not_null`, `between 200001 and <competencia_max>`, `mes between 1 and 12`.

### HIS-13.6 — Padrão de Nomenclatura

Definir nomenclatura oficial para todos os artefatos físicos e lógicos.

- [ ] Criar `docs/governanca/padroes_nomenclatura.md` com convenções:
  - [ ] tabelas staging: `stg_<dominio>_<entidade>`
  - [ ] tabelas intermediate: `int_<dominio>_<processo>`
  - [ ] fatos: `fat_<dominio>_<grao>`
  - [ ] dimensões: `dim_<entidade>`
  - [ ] marts: `mart_<dominio>_<visao>`
  - [ ] API: `api_<dominio>_<grao>`
  - [ ] consumo: `consumo_<dominio>_<grao>`
  - [ ] consumo premium: `consumo_premium_<dominio>_<entidade>_<status>`
  - [ ] MDM master: `mdm_<entidade>_master`
  - [ ] crosswalk: `xref_<entidade>_origem`
  - [ ] tabelas de exceção: `*_exception` (ex.: `mdm_operadora_exception`)
  - [ ] views: `vw_<dominio>_<entidade>`
  - [ ] funções: `fn_<acao>_<entidade>`
  - [ ] procedures: `prc_<numero>_<acao>_<entidade>`
  - [ ] triggers: `trg_<tabela>_<evento>`
  - [ ] primary keys: `pk_<tabela>`
  - [ ] foreign keys: `fk_<tabela_origem>_<tabela_destino>`
  - [ ] unique constraints: `uk_<tabela>_<colunas>`
  - [ ] check constraints: `ck_<tabela>_<regra>`
  - [ ] default constraints: `df_<tabela>_<coluna>`
  - [ ] índices: `ix_<tabela>_<colunas>`
  - [ ] índices únicos: `ux_<tabela>_<colunas>`
- [ ] Documentar exceções existentes (tabelas legadas já aprovadas que não seguem o padrão), sem renomeá-las.
- [ ] Definir que toda nova nomenclatura segue rigorosamente o padrão.

### HIS-13.7 — Índices, Chaves e Relacionamentos

Criar a governança documental de estruturas de acesso.

- [ ] Criar `docs/governanca/padroes_indices_chaves_constraints.md`, seção "Índices":
  - [ ] documentar para que serve cada índice
  - [ ] documentar qual consulta o índice atende
  - [ ] documentar se atende filtro, join, ordenação ou unicidade
  - [ ] documentar cardinalidade esperada
  - [ ] documentar impacto em escrita
  - [ ] documentar se o índice é obrigatório ou opcional
- [ ] Seção "Chaves":
  - [ ] documentar chaves naturais (definição por entidade)
  - [ ] documentar chaves surrogate (regras de geração e estabilidade)
  - [ ] documentar primary keys (uma por tabela publicada)
  - [ ] documentar foreign keys (sempre nomeadas `fk_*`)
- [ ] Seção "Relacionamentos":
  - [ ] documentar relacionamentos físicos (FK no banco)
  - [ ] documentar relacionamentos lógicos usados pelo dbt (`relationships` em YAML)
  - [ ] documentar relacionamentos entre CADOP, CNES, TISS, TUSS, beneficiários (SIB), financeiro (DIOPS), regulatório (NIP, RN623), MDM e consumo premium

### HIS-13.8 — Constraints, Funções e Triggers

Definir uso correto de constraints, funções e triggers.

- [ ] Em `docs/governanca/padroes_indices_chaves_constraints.md`, seção "Constraints":
  - [ ] documentar quando usar constraints (regra de domínio inviolável e barata)
  - [ ] documentar quando não usar constraints (regra de qualidade analítica que pode mudar)
  - [ ] toda coluna `bit` deve ter constraint `CHECK (col IN (0,1))`
  - [ ] toda coluna `uf` deve ter constraint `CHECK (uf = UPPER(uf) AND uf IN (<lista oficial>))`
  - [ ] toda data funcional ou técnica deve usar `datetime2` salvo exceção formal
- [ ] Seção "Funções":
  - [ ] documentar quando usar funções (encapsular regra reusada por múltiplas tabelas/queries)
  - [ ] documentar quando não usar funções (lógica analítica pesada → modelo dbt)
  - [ ] toda função deve ter entrada, saída, tipo de retorno e determinismo documentados
- [ ] Seção "Triggers":
  - [ ] documentar quando usar triggers (auditoria, regra operacional inevitável)
  - [ ] documentar quando não usar triggers (regra analítica, agregação, transformação)
  - [ ] proibir trigger com regra analítica pesada
  - [ ] toda trigger deve ter motivo e escopo documentados

### HIS-13.9 — Governança de Qualidade

Padronizar regras e scores de qualidade documental.

- [ ] Criar `docs/governanca/padroes_qualidade_validacao.md`:
  - [ ] regras de validação documental: CPF, CNPJ, CNES, registro ANS, competência, contrato, subfatura, MDM
  - [ ] validação Receita/Serpro via cache para CPF/CNPJ — contrato de cache, TTL, fallback
  - [ ] definição dos scores documentais:
    - [ ] `quality_score_documental` (preenchimento e consistência de campos)
    - [ ] `quality_score_mdm` (aderência ao golden record)
    - [ ] `quality_score_publicacao` (aprovação no hardgate)
  - [ ] regras de exceção bloqueante (impede publicação)
  - [ ] regras de exceção não bloqueante (publica com aviso de qualidade)
  - [ ] rastreabilidade obrigatória da validação: data/hora, fonte da validação, regra aplicada, resultado
  - [ ] integração documental com tabela `*_exception` (severidade, regra de bloqueio)

### HIS-13.10 — Governança de MDM

Definir as regras documentais de Master Data Management.

- [ ] Criar `docs/governanca/mdm_governanca.md`:
  - [ ] conceito de **golden record**
  - [ ] conceito de **crosswalk** (`xref_<entidade>_origem`)
  - [ ] **survivorship rule** — qual fonte vence em caso de divergência, por entidade
  - [ ] tratamento de **exceções MDM** (tabela `*_exception`)
  - [ ] MDM de **operadora** (chave: `registro_ans`)
  - [ ] MDM de **prestador**
  - [ ] MDM de **estabelecimento** (chave: `cnes`)
  - [ ] MDM de **contrato**
  - [ ] MDM de **subfatura**
  - [ ] divergências bloqueantes vs. não bloqueantes
  - [ ] regra de sobrevivência por fonte (CADOP > SIB > DIOPS para razão social, por exemplo — definir formalmente)
  - [ ] **score de confiança** por golden record
  - [ ] processo de **aprovação manual de crosswalk**
  - [ ] **trilha de auditoria** obrigatória para correções manuais (quem, quando, por quê)

### HIS-13.11 — Templates Oficiais

Disponibilizar templates de uso obrigatório para qualquer novo artefato.

- [ ] Criar `docs/governanca/templates/template_tabela.md` com seções: identidade, camada, granularidade, chaves, upstream, downstream, sensibilidade LGPD, owners, contrato.
- [ ] Criar `docs/governanca/templates/template_coluna.md` com todos os campos do dicionário (HIS-13.2).
- [ ] Criar `docs/governanca/templates/template_indice.md` com: nome, tabela, colunas, tipo (filtro/join/ordenação/unicidade), justificativa, cardinalidade, impacto em escrita, obrigatoriedade.
- [ ] Criar `docs/governanca/templates/template_constraint.md` com: nome, tabela, tipo (PK/FK/UK/CK/DF), regra de negócio associada, severidade.
- [ ] Criar `docs/governanca/templates/template_funcao.md` com: nome, entrada, saída, tipo de retorno, determinismo, dependências, exemplo.
- [ ] Criar `docs/governanca/templates/template_trigger.md` com: nome, tabela, evento, motivo, escopo (auditoria/operacional), regras proibidas.
- [ ] Criar `docs/governanca/templates/template_relacionamento.md` com: tabela origem, tabela destino, cardinalidade, físico/lógico, regra dbt aplicável.
- [ ] Criar `docs/governanca/templates/template_data_product.md` com: nome, owner, SLA, granularidade, contrato de API, plano comercial associado, score de qualidade.
- [ ] Criar `docs/governanca/templates/template_mdm.md` com: entidade, golden record, fontes, survivorship rule, score de confiança, processo de exceção.
- [ ] Criar `docs/governanca/templates/template_quality_rule.md` com: regra, severidade, bloqueante/não bloqueante, fonte, evidência.
- [ ] Criar `docs/governanca/templates/template_excecao.md` com: artefato, motivo da exceção, alternativa avaliada, owner, validade, revisão prevista.
- [ ] Definir em `docs/governanca/README.md` que toda nova entidade deve usar o template correspondente — PRs sem o template preenchido são bloqueados.

### HIS-13.12 — Hardgate de Governança

Criar o hardgate documental que toda implementação futura deve passar.

- [ ] Criar `docs/governanca/hardgate_governanca.md` listando os checks obrigatórios:
  - [ ] toda tabela nova tem descrição
  - [ ] toda coluna nova tem descrição
  - [ ] CPF é `varchar(11)`
  - [ ] CNPJ é `varchar(14)`
  - [ ] competência é `int` no formato `YYYYMM`
  - [ ] valor financeiro é `decimal(18,2)`
  - [ ] taxas, alíquotas e índices técnicos são `float`
  - [ ] flags são `bit` com domínio obrigatório `0` ou `1`
  - [ ] datas e timestamps técnicos são `datetime2`
  - [ ] UF é `char(2)` em maiúsculo, validada
  - [ ] todo índice tem justificativa documentada
  - [ ] toda chave tem relacionamento documentado
  - [ ] toda constraint tem regra documentada
  - [ ] toda função tem entrada, saída e determinismo documentados
  - [ ] toda trigger tem motivo e escopo documentados
  - [ ] todo modelo premium tem score de qualidade
  - [ ] todo modelo MDM tem regra de sobrevivência
  - [ ] toda tabela `*_exception` tem severidade e regra de bloqueio
  - [ ] todo data product tem owner, SLA, granularidade e contrato de API
- [ ] Definir o fluxo de aplicação do hardgate documental: PR → checagem documental → checagem física (dbt/SQL) → aprovação → merge.
- [ ] Reforçar a invariante: **nenhuma tabela ou lógica aprovada anteriormente é alterada por esta sprint**.

---

## Critério de Aceite

- [ ] Todos os documentos de governança listados em "Entregáveis" foram criados.
- [ ] O catálogo de tabelas (`catalogo_tabelas.md`) tem template oficial e cobre as tabelas existentes.
- [ ] O dicionário de colunas (`dicionario_colunas.md`) tem template oficial e cobre as colunas críticas.
- [ ] Os padrões de tipagem estão definidos em `padroes_tipagem.md`.
- [ ] CPF está documentado como `varchar(11)`.
- [ ] CNPJ está documentado como `varchar(14)`.
- [ ] `competencia` está documentada como `int` no formato `YYYYMM`.
- [ ] Valores financeiros estão documentados como `decimal(18,2)`.
- [ ] Taxas, alíquotas, índices técnicos e percentuais técnicos estão documentados como `float` quando exigirem escala maior.
- [ ] Flags estão documentadas como `bit` aceitando somente `0` ou `1`.
- [ ] Datas e timestamps técnicos estão documentados como `datetime2`.
- [ ] UF está documentada como `char(2)`.
- [ ] Todo índice exige justificativa documentada.
- [ ] Toda chave exige relacionamento documentado.
- [ ] Toda constraint exige regra documentada.
- [ ] Toda função exige entrada, saída e determinismo documentados.
- [ ] Toda trigger exige motivo e escopo documentados.
- [ ] Todo modelo premium exige score de qualidade.
- [ ] Todo modelo MDM exige regra de sobrevivência.
- [ ] Os 11 templates oficiais foram criados em `docs/governanca/templates/`.
- [ ] O hardgate de governança documental foi publicado e é referenciado pelo processo de PR.
- [ ] **Nenhuma tabela ou lógica aprovada anteriormente foi alterada.**

## Resultado Esperado

Ao final da Sprint 26, a plataforma HealthIntel Suplementar passa a contar com um corpo documental normativo completo em `docs/governanca/`, composto por catálogos, dicionários, padrões de tipagem, nomenclatura, índices, chaves, constraints, competência/datas, qualidade, MDM, templates e hardgate. Toda nova tabela, coluna, índice, chave, relacionamento, constraint, função, trigger e data product passa a ser obrigatoriamente regida por estes documentos. A base física aprovada em hardgates anteriores permanece intacta — a governança aplica-se a partir das próximas implementações da Fase 5.
