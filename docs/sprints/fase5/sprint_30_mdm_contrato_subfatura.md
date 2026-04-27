Ajustei a Sprint 30 para ficar **10/10** e totalmente compatível com a Sprint 28/29: sem Serpro, sem Receita online, sem BrasilAPI, sem `enrichment`, sem UUID v5/extensão PostgreSQL, com `tenant_id` desde a entrada física, RLS, hashes determinísticos e hard gates objetivos. A versão original ainda citava fase com “Enriquecimento”, UUID v5 e validação Serpro em regra contratual, então corrigi esses pontos. 

````markdown
# Sprint 30 — MDM Privado de Contrato e Subfatura por Tenant

**Status:** Concluída  
**Fase:** Fase 5 — Qualidade, Governança e MDM sem dependência externa  
**Tag de saída candidata:** `v3.5.0-mdm-privado` — somente após hard gates verdes  
**Pré-requisito:** Sprint 29 concluída com MDM público em `mdm_ans` e hard gates verdes  
**Objetivo:** criar o módulo MDM privado por tenant para contrato e subfatura, permitindo reconciliar dados internos de clientes com entidades públicas já masterizadas, sem alterar modelos públicos e sem publicar dados privados indevidamente.  
**Fim esperado:** contratos e subfaturas privados modelados com `tenant_id`, RLS, crosswalk, exceções e score MDM, prontos para uso por produtos premium futuros.  
**Critério de saída:** modelos `mdm_contrato_master`, `mdm_subfatura_master`, `xref_*_origem` e `mdm_*_exception` materializados no schema privado; `tenant_id` obrigatório; RLS configurado; nenhuma dependência externa; nenhum dado privado vazando para schemas públicos.

---

## Contexto técnico

Contrato e subfatura **não vêm dos dados públicos abertos da ANS**. São dados privados por cliente/tenant.

Esta sprint cria o módulo privado que permite reconciliar dados internos do cliente com o MDM público da plataforma:

- `mdm_ans.mdm_operadora_master`
- `mdm_ans.mdm_estabelecimento_master`
- `mdm_ans.mdm_prestador_master`

O objetivo é permitir casos como:

- divergência de número de contrato;
- subfatura órfã;
- contrato apontando para operadora errada;
- contrato com CNPJ de operadora incompatível com MDM público;
- duplicidade de contrato por tenant;
- duplicidade de subfatura por contrato e competência;
- inconsistência entre contrato, subfatura, operadora e prestador.

Esta sprint **não cria produto premium**, **não cria endpoint** e **não publica dados privados para cliente final**. Ela apenas prepara a camada privada segura que será consumida pela Sprint 31.

---

## Regra-mãe

- [x] Toda tabela física privada bruta vive em schema `bruto_cliente`.
- [x] Toda staging privada vive em schema lógico `stg_cliente`.
- [x] Todo modelo MDM privado vive em schema lógico/físico `mdm_privado`.
- [x] Todo modelo MDM privado vive em `healthintel_dbt/models/mdm_privado/`.
- [x] Toda staging privada vive em `healthintel_dbt/models/staging/cliente/`.
- [x] `tenant_id` é obrigatório e `NOT NULL` desde a entrada física.
- [x] `tenant_id` nasce em `bruto_cliente.*` e não pode ser inferido tardiamente.
- [x] Row-level security deve impedir leitura cruzada entre tenants.
- [x] Nenhuma tabela pública pode receber dados de contrato/subfatura.
- [x] Nenhum modelo público da Sprint 29 pode ser alterado.
- [x] Nenhum modelo de `mdm_ans`, `quality_ans`, `nucleo_ans`, `api_ans`, `consumo_ans` ou `consumo_premium_ans` pode ser alterado nesta sprint.
- [x] Nenhuma API, endpoint FastAPI ou produto premium é criado nesta sprint.
- [x] Nenhuma validação Serpro, Receita online, BrasilAPI, scraping, cache externo ou chamada web é usada.
- [x] Nenhum schema `enrichment` é criado ou referenciado.
- [x] Nenhum provider Python de CNPJ é criado.
- [x] Nenhuma variável de ambiente externa é criada, como `SERPRO_*`, `BRASIL_API_*` ou `HEALTHINTEL_CNPJ_PROVIDER`.
- [x] A validação de CNPJ usa somente MDM público e validação documental offline da Sprint 28.
- [x] Chaves MDM privadas são hashes determinísticos `text` via `md5(concat_ws('|', ...))`, não UUID v5 dependente de extensão PostgreSQL.
- [x] Se não houver dados privados reais no ambiente, os modelos devem compilar e materializar zero linhas com estrutura válida.
- [x] A implementação não deve inventar colunas inexistentes. Deve inspecionar as fontes antes de modelar. Se campo canônico não existir, usar `null::text as <campo>` com comentário técnico.

---

## Anti-escopo explícito

| Item | Status |
|------|--------|
| Serpro | Fora do escopo |
| Receita online | Fora do escopo |
| BrasilAPI | Fora do escopo |
| Scraping | Fora do escopo |
| Schema `enrichment` | Fora do escopo |
| Cache externo de CNPJ | Fora do escopo |
| Provider Python de CNPJ | Fora do escopo |
| API/FastAPI | Fora do escopo |
| Endpoint novo | Fora do escopo |
| Produto premium | Fora do escopo |
| Publicação em `consumo_premium_ans` | Fora do escopo |
| Publicação em `api_ans` | Fora do escopo |
| Dados privados em schema público | Proibido |
| Alterar MDM público da Sprint 29 | Proibido |
| Alterar produtos legados | Proibido |

---

## Configuração dbt esperada

Atualizar `healthintel_dbt/dbt_project.yml`:

```yaml
models:
  healthintel_dbt:
    mdm_privado:
      +schema: mdm_privado
      +materialized: table
      +tags: ["mdm_privado"]
    staging:
      cliente:
        +schema: stg_cliente
        +materialized: view
        +tags: ["staging", "cliente", "privado"]
````

> Observação: se o projeto possuir macro customizada de schema, garantir que o schema físico final seja exatamente `stg_cliente` e `mdm_privado`, ou documentar o nome físico real gerado pelo dbt.

---

## Padrão técnico MDM privado

### 1. Surrogate keys determinísticas

Não usar:

* `uuid_generate_v5`;
* extensão `uuid-ossp`;
* extensão nova de banco;
* função não determinística;
* sequência incremental;
* `random()`.

Usar hash determinístico em `text`.

### Contrato

```sql
md5(concat_ws(
    '|',
    'contrato',
    tenant_id,
    numero_contrato_normalizado,
    coalesce(registro_ans_canonico, ''),
    coalesce(cnpj_operadora_canonico, '')
)) as contrato_master_id
```

### Subfatura

```sql
md5(concat_ws(
    '|',
    'subfatura',
    tenant_id,
    numero_contrato_normalizado,
    codigo_subfatura_normalizado
)) as subfatura_master_id
```

### Crosswalk

```sql
md5(concat_ws(
    '|',
    'xref_contrato',
    tenant_id,
    source_system,
    source_key
)) as xref_contrato_id
```

---

### 2. Status MDM privado

Campo obrigatório em masters privados:

```text
mdm_status
```

Valores aceitos:

| Status       | Significado                                             |
| ------------ | ------------------------------------------------------- |
| `GOLDEN`     | Registro privado canônico resolvido                     |
| `CANDIDATE`  | Registro utilizável, mas com confiança intermediária    |
| `QUARENTENA` | Registro com inconsistência relevante ou bloqueante     |
| `DEPRECATED` | Registro substituído ou reservado para histórico futuro |

Regra inicial recomendada:

```text
GOLDEN      -> mdm_confidence_score >= 85 e sem exceção bloqueante
CANDIDATE   -> mdm_confidence_score >= 60 and < 85 e sem exceção bloqueante
QUARENTENA  -> mdm_confidence_score < 60 ou exceção bloqueante
DEPRECATED  -> reservado para evolução futura
```

---

### 3. Score MDM privado

Campo obrigatório:

```text
mdm_confidence_score
```

Sempre aplicar limite:

```sql
least(100, greatest(0, score_calculado)) as mdm_confidence_score
```

---

## HIS-10.0 — Criar bootstrap privado por tenant

### Arquivo

* [x] `infra/postgres/init/028_fase5_mdm_privado_rls.sql`

### Entregas

* [x] Criar schema `bruto_cliente`.
* [x] Criar schema `mdm_privado`.
* [x] Criar grants/revokes explícitos.
* [x] Garantir que `healthintel_cliente_reader` não acessa `bruto_cliente`.
* [x] Garantir que `healthintel_cliente_reader` não acessa `stg_cliente`.
* [x] Garantir que `healthintel_cliente_reader` não acessa `mdm_privado`.
* [x] Criar tabela `bruto_cliente.contrato`.
* [x] Criar tabela `bruto_cliente.subfatura`.
* [x] Criar RLS por `tenant_id`.
* [x] Criar política de isolamento por `current_setting('app.tenant_id', true)`.
* [x] Criar índices mínimos para `tenant_id`, `hash_arquivo`, `competencia` e chaves de contrato/subfatura.
* [x] Documentar que `app.tenant_id` deve ser setado pela camada de aplicação ou pelo processo de carga privada.

### Campos mínimos — `bruto_cliente.contrato`

* [x] `tenant_id text not null`
* [x] `id_carga text not null`
* [x] `source_system text`
* [x] `fonte_arquivo text`
* [x] `hash_arquivo text not null`
* [x] `competencia int`
* [x] `registro_ans text`
* [x] `cnpj_operadora text`
* [x] `numero_contrato text`
* [x] `tipo_contrato text`
* [x] `vigencia_inicio date`
* [x] `vigencia_fim date`
* [x] `status_contrato text`
* [x] `payload_bruto jsonb`
* [x] `dt_carga timestamp(3) default current_timestamp`

### Campos mínimos — `bruto_cliente.subfatura`

* [x] `tenant_id text not null`
* [x] `id_carga text not null`
* [x] `source_system text`
* [x] `fonte_arquivo text`
* [x] `hash_arquivo text not null`
* [x] `competencia int`
* [x] `numero_contrato text`
* [x] `codigo_subfatura text`
* [x] `centro_custo text`
* [x] `unidade_negocio text`
* [x] `vigencia_inicio date`
* [x] `vigencia_fim date`
* [x] `status_subfatura text`
* [x] `payload_bruto jsonb`
* [x] `dt_carga timestamp(3) default current_timestamp`

### Regras de carga privada

* [x] Carga idempotente por `tenant_id`, `source_system`, `competencia` e `hash_arquivo`.
* [x] Reprocessamento do mesmo arquivo não duplica registros master.
* [x] Layout privado deve ter fingerprint.
* [x] Layout não reconhecido gera exceção bloqueante.
* [x] Nenhuma carga pode entrar sem `tenant_id`.

---

## HIS-10.1 — Criar staging privada

### Modelos

* [x] `healthintel_dbt/models/staging/cliente/stg_cliente_contrato.sql`
* [x] `healthintel_dbt/models/staging/cliente/stg_cliente_subfatura.sql`
* [x] `healthintel_dbt/models/staging/cliente/_staging_cliente.yml`

### Regras para `stg_cliente_contrato`

* [x] Ler de `bruto_cliente.contrato`.
* [x] Normalizar `tenant_id`.
* [x] Normalizar `registro_ans` usando macro existente, se disponível.
* [x] Normalizar `cnpj_operadora` usando macro existente de CNPJ.
* [x] Normalizar `numero_contrato`.
* [x] Normalizar `tipo_contrato`.
* [x] Normalizar `status_contrato`.
* [x] Preservar `hash_arquivo`.
* [x] Preservar `id_carga`.
* [x] Preservar `competencia`.
* [x] Não criar registro sem `tenant_id`.
* [x] Não inferir `tenant_id`.

### Regras para `stg_cliente_subfatura`

* [x] Ler de `bruto_cliente.subfatura`.
* [x] Normalizar `tenant_id`.
* [x] Normalizar `numero_contrato`.
* [x] Normalizar `codigo_subfatura`.
* [x] Normalizar `centro_custo`.
* [x] Normalizar `unidade_negocio`.
* [x] Normalizar `status_subfatura`.
* [x] Preservar `hash_arquivo`.
* [x] Preservar `id_carga`.
* [x] Preservar `competencia`.
* [x] Não criar registro sem `tenant_id`.
* [x] Não inferir `tenant_id`.

### Testes YAML mínimos

* [x] `not_null` em `tenant_id`.
* [x] `not_null` em `id_carga`.
* [x] `not_null` em `hash_arquivo`.
* [x] `not_null` em `numero_contrato` para contrato.
* [x] `not_null` em `numero_contrato` para subfatura.
* [x] `not_null` em `codigo_subfatura` para subfatura, se houver dado.
* [x] `accepted_values` para `status_contrato`, quando domínio estiver definido.
* [x] `accepted_values` para `status_subfatura`, quando domínio estiver definido.

---

## HIS-10.2 — Criar contrato master

### Modelos

* [x] `healthintel_dbt/models/mdm_privado/mdm_contrato_master.sql`
* [x] `healthintel_dbt/models/mdm_privado/xref_contrato_origem.sql`
* [x] `healthintel_dbt/models/mdm_privado/mdm_contrato_exception.sql`

### Fonte obrigatória

* [x] `ref('stg_cliente_contrato')`

### Fontes de referência permitidas

* [x] `ref('mdm_operadora_master')`
* [x] `ref('dq_operadora_documento')`, se necessário para validação documental offline
* [x] `ref('dq_cadop_documento')`, se necessário para validação documental offline

### Regras

* [x] Não modelar contrato master sem origem física privada.
* [x] Não criar contrato sem `tenant_id`.
* [x] Não publicar contrato sem número canônico.
* [x] Resolver `operadora_master_id` por `registro_ans_canonico` e/ou `cnpj_operadora_canonico`.
* [x] Se `operadora_master_id` não for resolvido, o contrato entra em `QUARENTENA`.
* [x] Se CNPJ da operadora divergir do MDM público, gerar exceção bloqueante.
* [x] Não consultar Serpro, Receita online ou BrasilAPI.
* [x] Não usar `cnpj_receita_status`.
* [x] Não usar `is_cnpj_ativo_receita`.
* [x] Não usar `int_cnpj_receita_validado`.

### Campos obrigatórios em `mdm_contrato_master`

* [x] `contrato_master_id`
* [x] `tenant_id`
* [x] `operadora_master_id`
* [x] `numero_contrato_canonico`
* [x] `numero_contrato_normalizado`
* [x] `registro_ans_canonico`
* [x] `cnpj_operadora_canonico`
* [x] `tipo_contrato`
* [x] `vigencia_inicio`
* [x] `vigencia_fim`
* [x] `status_contrato`
* [x] `is_operadora_mdm_resolvida`
* [x] `is_cnpj_operadora_estrutural_valido`
* [x] `has_excecao_bloqueante`
* [x] `mdm_confidence_score`
* [x] `mdm_status`
* [x] `dt_processamento`

### Score de contrato

| Regra                                            | Pontos |
| ------------------------------------------------ | ------ |
| `tenant_id` preenchido                           | +20    |
| `numero_contrato_normalizado` preenchido         | +25    |
| `operadora_master_id` resolvido                  | +25    |
| CNPJ da operadora estruturalmente válido/offline | +10    |
| Vigência preenchida                              | +10    |
| Status de contrato preenchido                    | +10    |

Total máximo: 100.

### Regra de `mdm_status`

```text
GOLDEN      -> score >= 85 e sem exceção bloqueante
CANDIDATE   -> score >= 60 and < 85 e sem exceção bloqueante
QUARENTENA  -> score < 60 ou exceção bloqueante
DEPRECATED  -> reservado
```

---

## HIS-10.3 — Criar subfatura master

### Modelos

* [x] `healthintel_dbt/models/mdm_privado/mdm_subfatura_master.sql`
* [x] `healthintel_dbt/models/mdm_privado/xref_subfatura_origem.sql`
* [x] `healthintel_dbt/models/mdm_privado/mdm_subfatura_exception.sql`

### Fonte obrigatória

* [x] `ref('stg_cliente_subfatura')`

### Fonte de referência obrigatória

* [x] `ref('mdm_contrato_master')`

### Regras

* [x] Não modelar subfatura master sem origem física privada.
* [x] Não criar subfatura sem `tenant_id`.
* [x] Resolver `contrato_master_id` via `tenant_id` + `numero_contrato_normalizado`.
* [x] Subfatura sem contrato resolvido entra em `QUARENTENA`.
* [x] Subfatura duplicada por `tenant_id`, `contrato_master_id`, `codigo_subfatura_normalizado` e `competencia` gera exceção.
* [x] Não misturar tenants.
* [x] Não inferir contrato por aproximação textual sem crosswalk aprovado.

### Campos obrigatórios em `mdm_subfatura_master`

* [x] `subfatura_master_id`
* [x] `contrato_master_id`
* [x] `tenant_id`
* [x] `codigo_subfatura_canonico`
* [x] `codigo_subfatura_normalizado`
* [x] `numero_contrato_normalizado`
* [x] `competencia`
* [x] `centro_custo`
* [x] `unidade_negocio`
* [x] `vigencia_inicio`
* [x] `vigencia_fim`
* [x] `status_subfatura`
* [x] `is_contrato_resolvido`
* [x] `has_excecao_bloqueante`
* [x] `mdm_confidence_score`
* [x] `mdm_status`
* [x] `dt_processamento`

### Score de subfatura

| Regra                                            | Pontos |
| ------------------------------------------------ | ------ |
| `tenant_id` preenchido                           | +20    |
| `codigo_subfatura_normalizado` preenchido        | +25    |
| `contrato_master_id` resolvido                   | +30    |
| Centro de custo ou unidade de negócio preenchido | +10    |
| Vigência preenchida                              | +10    |
| Status preenchido                                | +5     |

Total máximo: 100.

---

## HIS-10.4 — Criar crosswalk privado

### Modelos

* [x] `healthintel_dbt/models/mdm_privado/xref_contrato_origem.sql`
* [x] `healthintel_dbt/models/mdm_privado/xref_subfatura_origem.sql`

### Campos obrigatórios — contrato

* [x] `xref_contrato_id`
* [x] `contrato_master_id`
* [x] `tenant_id`
* [x] `source_system`
* [x] `source_model`
* [x] `source_key`
* [x] `numero_contrato_origem`
* [x] `numero_contrato_normalizado`
* [x] `registro_ans_origem`
* [x] `cnpj_operadora_origem`
* [x] `is_primary_source`
* [x] `is_crosswalk_aprovado`
* [x] `dt_processamento`

### Campos obrigatórios — subfatura

* [x] `xref_subfatura_id`
* [x] `subfatura_master_id`
* [x] `contrato_master_id`
* [x] `tenant_id`
* [x] `source_system`
* [x] `source_model`
* [x] `source_key`
* [x] `codigo_subfatura_origem`
* [x] `codigo_subfatura_normalizado`
* [x] `numero_contrato_origem`
* [x] `numero_contrato_normalizado`
* [x] `is_primary_source`
* [x] `is_crosswalk_aprovado`
* [x] `dt_processamento`

### Regras

* [x] Todo crosswalk privado possui `tenant_id`.
* [x] Crosswalk não pode ligar registros de tenants diferentes.
* [x] Crosswalk aprovado manualmente deve ter trilha futura de auditoria.
* [x] Nesta sprint, `is_crosswalk_aprovado` pode iniciar como `false`.

---

## HIS-10.5 — Criar exceções MDM privadas

### Modelos

* [x] `healthintel_dbt/models/mdm_privado/mdm_contrato_exception.sql`
* [x] `healthintel_dbt/models/mdm_privado/mdm_subfatura_exception.sql`
* [x] `healthintel_dbt/models/mdm_privado/mdm_operadora_contrato_exception.sql`
* [x] `healthintel_dbt/models/mdm_privado/mdm_prestador_contrato_exception.sql`

### Campos obrigatórios

* [x] `tenant_id`
* [x] `exception_type`
* [x] `exception_severity`
* [x] `exception_message`
* [x] `is_blocking`
* [x] `resolved_at`
* [x] `resolved_by`
* [x] `resolution_comment`
* [x] `dt_processamento`

### Tipos mínimos

| exception_type                           | severity   | is_blocking | Regra                                                          |
| ---------------------------------------- | ---------- | ----------: | -------------------------------------------------------------- |
| `TENANT_AUSENTE`                         | `BLOCKING` |        true | Registro privado sem tenant                                    |
| `CONTRATO_SEM_OPERADORA_MDM`             | `BLOCKING` |        true | Contrato não resolve operadora master                          |
| `CONTRATO_CNPJ_OPERADORA_DIVERGENTE_MDM` | `BLOCKING` |        true | CNPJ informado no contrato diverge do MDM público de operadora |
| `CONTRATO_DUPLICADO_TENANT`              | `BLOCKING` |        true | Mesmo contrato duplicado no tenant sem crosswalk aprovado      |
| `SUBFATURA_SEM_CONTRATO`                 | `BLOCKING` |        true | Subfatura não resolve contrato master                          |
| `SUBFATURA_DUPLICADA_COMPETENCIA`        | `WARNING`  |       false | Duplicidade por contrato + subfatura + competência             |
| `LAYOUT_PRIVADO_NAO_RECONHECIDO`         | `BLOCKING` |        true | Layout privado sem fingerprint aprovado                        |
| `CROSSWALK_TENANT_DIVERGENTE`            | `BLOCKING` |        true | Crosswalk tenta ligar registros de tenants diferentes          |

---

## HIS-10.6 — Criar testes contratuais

Criar testes singulares em `healthintel_dbt/tests/mdm_privado/`:

* [x] `assert_mdm_privado_tenant_obrigatorio.sql`
* [x] `assert_mdm_contrato_operadora_resolvida.sql`
* [x] `assert_mdm_subfatura_com_contrato.sql`
* [x] `assert_mdm_contrato_sem_dupla_operadora_ativa.sql`
* [x] `assert_mdm_contrato_sem_duplicidade_tenant.sql`
* [x] `assert_mdm_contrato_cnpj_compativel_mdm_operadora.sql`
* [x] `assert_mdm_subfatura_sem_duplicidade_competencia.sql`
* [x] `assert_mdm_privado_score_entre_0_e_100.sql`
* [x] `assert_mdm_privado_status_valido.sql`
* [x] `assert_mdm_privado_crosswalk_mesmo_tenant.sql`

### Severidade

* [x] Regras bloqueantes devem usar `severity='error'`.
* [x] Regras diagnósticas podem usar `severity='warn'`, desde que tagueadas como `mdm_privado_warning`.
* [x] O hard gate não deve usar `--warn-error` para testes explicitamente diagnósticos.

---

## HIS-10.7 — Criar documentação do MDM privado

### Arquivos

* [x] `healthintel_dbt/models/mdm_privado/_mdm_privado.yml`
* [x] `docs/sprints/fase5/mdm_contrato_subfatura.md`

### Conteúdo mínimo

* [x] Objetivo do MDM privado.
* [x] Diferença entre MDM público e MDM privado.
* [x] Regra de `tenant_id`.
* [x] Regra de RLS.
* [x] Fluxo bruto → staging → MDM privado.
* [x] Regras de contrato.
* [x] Regras de subfatura.
* [x] Regras de crosswalk.
* [x] Regras de exceção bloqueante.
* [x] Relação com MDM público.
* [x] Anti-escopo: sem API, sem premium, sem dados públicos alterados.

---

## Entregas esperadas

### Infra

* [x] `infra/postgres/init/028_fase5_mdm_privado_rls.sql`
* [x] Schemas `bruto_cliente` e `mdm_privado`
* [x] Tabelas `bruto_cliente.contrato` e `bruto_cliente.subfatura`
* [x] Grants, revokes e RLS

### Staging privada

* [x] `stg_cliente_contrato.sql`
* [x] `stg_cliente_subfatura.sql`
* [x] `_staging_cliente.yml`

### MDM privado

* [x] `mdm_contrato_master.sql`
* [x] `mdm_subfatura_master.sql`
* [x] `xref_contrato_origem.sql`
* [x] `xref_subfatura_origem.sql`
* [x] `mdm_contrato_exception.sql`
* [x] `mdm_subfatura_exception.sql`
* [x] `mdm_operadora_contrato_exception.sql`
* [x] `mdm_prestador_contrato_exception.sql`
* [x] `_mdm_privado.yml`

### Testes

* [x] 10 testes singulares de regra contratual e segurança lógica

### Documentação

* [x] `docs/sprints/fase5/mdm_contrato_subfatura.md`
* [x] Evidências de execução atualizadas no documento da sprint

---

## Hard Gates

Cada item exige evidência objetiva antes de considerar a sprint concluída.

### V1 — Build privado

```bash
cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt build --select tag:mdm_privado
```

Critério:

```text
ERROR=0
```

---

### V2 — Testes privados

```bash
cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt test --select tag:mdm_privado
```

Critério:

```text
ERROR=0
```

---

### V3 — Tenant obrigatório

Toda linha dos objetos abaixo deve ter `tenant_id IS NOT NULL`:

* `bruto_cliente.contrato`
* `bruto_cliente.subfatura`
* `stg_cliente_contrato`
* `stg_cliente_subfatura`
* `mdm_contrato_master`
* `mdm_subfatura_master`
* `xref_contrato_origem`
* `xref_subfatura_origem`
* `mdm_contrato_exception`
* `mdm_subfatura_exception`

---

### V4 — Segurança de schema e RLS

`healthintel_cliente_reader` não pode ter acesso a:

* `bruto_cliente`
* `stg_cliente`
* `mdm_privado`

RLS deve existir nas tabelas físicas privadas:

* `bruto_cliente.contrato`
* `bruto_cliente.subfatura`

---

### V5 — Ausência de dependência externa

```bash
if grep -rEi "Serpro|Receita online|BrasilAPI|brasilapi|SERPRO_|BRASIL_API|documento_receita_cache|schema.*enrichment|requests|httpx|urlopen|http_get|int_cnpj_receita_validado|cnpj_receita_status|is_cnpj_ativo_receita" \
  healthintel_dbt/models/mdm_privado/ \
  healthintel_dbt/models/staging/cliente/ \
  infra/postgres/init/028_fase5_mdm_privado_rls.sql; then
  echo "FAIL: dependência externa ou legado Receita/Serpro encontrado no MDM privado"
  exit 1
else
  echo "PASS: MDM privado sem dependência externa"
fi
```

---

### V6 — Modelos públicos intactos

Antes de implementar, registrar commit-base:

```bash
git rev-parse HEAD
```

Depois validar que modelos públicos não foram alterados:

```bash
git diff --exit-code <COMMIT_BASE_SPRINT_30> -- \
  healthintel_dbt/models/mdm/ \
  healthintel_dbt/models/quality/ \
  healthintel_dbt/models/marts/ \
  healthintel_dbt/models/consumo/ \
  healthintel_dbt/models/api/
```

Critério:

```text
exit code 0
```

---

### V7 — Score privado entre 0 e 100

Teste singular ou YAML deve garantir:

```text
mdm_confidence_score >= 0
mdm_confidence_score <= 100
```

Aplicável a:

* `mdm_contrato_master`
* `mdm_subfatura_master`

---

### V8 — Status MDM privado válido

Valores aceitos:

```text
GOLDEN
CANDIDATE
QUARENTENA
DEPRECATED
```

Aplicável a:

* `mdm_contrato_master`
* `mdm_subfatura_master`

---

### V9 — Exceptions com estrutura obrigatória

Todas as tabelas `mdm_*_exception` privadas devem possuir:

* [x] `tenant_id`
* [x] `exception_type`
* [x] `exception_severity`
* [x] `exception_message`
* [x] `is_blocking`
* [x] `dt_processamento`

---

### V10 — Zero vazamento para schemas públicos

Nenhum arquivo de schema público pode referenciar:

* `bruto_cliente`
* `stg_cliente`
* `mdm_privado`

Exceto documentação autorizada e modelos `consumo_premium`/`api_premium` futuros da Sprint 31/32.

Nesta sprint, o esperado é zero referência fora de:

* `healthintel_dbt/models/staging/cliente/`
* `healthintel_dbt/models/mdm_privado/`
* `infra/postgres/init/028_fase5_mdm_privado_rls.sql`
* `docs/sprints/fase5/`

---

## Evidências de Execução

| Gate | Comando                              | Resultado                                                                 | Data       |
| ---- | ------------------------------------ | ------------------------------------------------------------------------- | ---------- |
| V1   | `dbt build --select tag:cliente tag:mdm_privado` | PASS=55 ERROR=0 (8 tables + 2 views + 45 tests, 0 linhas)     | 2026-04-27 |
| V2   | `dbt test --select tag:mdm_privado`  | PASS=36 ERROR=0                                                           | 2026-04-27 |
| V3   | tenant obrigatório                   | 0 linhas com `tenant_id IS NULL` em 10 objetos                            | 2026-04-27 |
| V4   | grants/RLS                           | RLS+FORCE em `bruto_cliente.contrato`/`subfatura`; 0 grants para `cliente_reader` | 2026-04-27 |
| V5   | grep anti-dependência externa        | PASS — sem Serpro/Receita/BrasilAPI/HTTP                                  | 2026-04-27 |
| V6   | diff modelos públicos                | exit code 0 — `mdm/`, `quality/`, `marts/`, `api/`, `consumo/` intactos   | 2026-04-27 |
| V7   | score privado entre 0 e 100          | 0 linhas fora do intervalo                                                | 2026-04-27 |
| V8   | `mdm_status` privado válido          | 0 linhas fora de {GOLDEN, CANDIDATE, QUARENTENA, DEPRECATED}              | 2026-04-27 |
| V9   | exceptions com campos obrigatórios   | 4 tabelas `*_exception` com 6 colunas obrigatórias presentes              | 2026-04-27 |
| V10  | zero vazamento para schemas públicos | PASS — nenhum schema público referencia `bruto_cliente`/`stg_cliente`/`mdm_privado` | 2026-04-27 |

---

## Resultado Esperado

A Sprint 30 cria a camada MDM privada por tenant para contrato e subfatura.

A plataforma passa a conseguir reconciliar dados públicos regulatórios com dados internos de clientes sem misturar domínios, sem expor dados privados em schemas públicos e sem depender de Serpro, Receita online, BrasilAPI ou qualquer validação externa.

O resultado é uma base privada segura para produtos premium futuros, preservando integralmente o MDM público, os modelos legados e os hard gates já aprovados.

