Abaixo está a **Sprint 29 completa já corrigida** para ficar compatível com a Sprint 28 offline. Ela substitui o plano anterior, que ainda trazia pontos a ajustar como fase com “Enriquecimento”, schema `mdm`, UUID v5 e `tenant_id` em MDM público. 

````markdown
# Sprint 29 — MDM Público de Operadora, Estabelecimento e Prestador

**Status:** Concluída — hard gates executados com evidência.  
**Fase:** Fase 5 — Qualidade, Governança e MDM sem dependência externa  
**Tag de saída candidata:** `v3.4.0-mdm-publico` — somente após hard gates verdes  
**Pré-requisito:** Sprint 28 concluída com validação determinística de CNPJ offline e hard gates verdes  
**Objetivo:** criar a camada MDM pública/regulatória de operadoras, estabelecimentos CNES e prestadores, com golden records, crosswalk e exceções, sem substituir `int_operadora_canonica` nem `dim_operadora_atual`.  
**Fim esperado:** entidades master públicas disponíveis como insumo técnico para os produtos premium da Sprint 31 e para o futuro MDM privado da Sprint 30, sem criar APIs, endpoints ou schemas premium nesta sprint.  
**Critério de saída:** modelos `mdm_*_master` materializados no schema `mdm_ans`, tabelas `xref_*_origem`, tabelas `mdm_*_exception`, score MDM documentado e testado, sem dependência externa e sem alteração nos modelos canônicos existentes.

---

## Regra-mãe

- [x] `int_operadora_canonica.sql` permanece intacto.
- [x] `dim_operadora_atual.sql` permanece intacto.
- [x] Toda nova lógica MDM vive em `healthintel_dbt/models/mdm/`.
- [x] Nenhuma API externa é usada: proibido Serpro, Receita online, BrasilAPI, scraping, `requests`, `httpx`, `urlopen`, `http_get` ou equivalente.
- [x] Nenhum schema `enrichment` é criado ou referenciado.
- [x] Nenhum provider Python de CNPJ é criado.
- [x] Nenhuma variável de ambiente externa é criada, como `SERPRO_*`, `BRASIL_API_*` ou `HEALTHINTEL_CNPJ_PROVIDER`.
- [x] A validação documental vem exclusivamente da Sprint 28: `quality_ans.dq_*`, `documento_quality_status`, `cnpj_tamanho_valido`, `cnpj_digito_valido` e `cnpj_is_sequencia_invalida`.
- [x] MDM público é global/regulatório. Não incluir `tenant_id` nesta sprint.
- [x] Surrogate keys MDM são hashes determinísticos em `text`, não UUID v5 dependente de extensão PostgreSQL.
- [x] O comando de execução sempre deve ser invocado via ambiente isolado `../.venv/bin/dbt` (conforme Hard Gates V2 e V3), não usar versão global do `dbt`.
- [x] Nenhuma API, endpoint FastAPI, schema premium ou produto de consumo é criado nesta sprint.
- [x] **IMPORTANTE:** Durante a implementação, a IA agente não deve inventar/deduzir colunas. Ela deve inspecionar proativamente as fontes (ex: `dq_cadop_documento`, `dq_operadora_documento`, `stg_cnes_estabelecimento`, `stg_rede_assistencial` etc). Se faltar algum campo exigido no modelo (como `nome_fantasia_canonico`, `situacao_cnes_canonica`, `tipo_prestador_canonico`, `uf_canonica`), force `null::text as <nome_do_campo>` acompanhado de comentário em vez de causar erro no `dbt compile`.

---

## Configuração dbt esperada

Atualizar `healthintel_dbt/dbt_project.yml` para incluir:

```yaml
models:
  healthintel_dbt:
    mdm:
      +schema: mdm_ans
      +materialized: table
      +tags: ["mdm"]
````

> Observação: o schema físico esperado no banco será `mdm_ans`, mantendo o padrão do projeto: `stg_ans`, `quality_ans`, `nucleo_ans`, `api_ans`, `consumo_ans`.

---

## Padrão técnico MDM

### 1. Surrogate key determinística

Não usar `uuid_generate_v5`, `uuid-ossp` ou extensão adicional.

Usar hash determinístico em `text`:

```sql
md5(concat_ws('|', 'operadora', registro_ans_canonico, coalesce(cnpj_canonico, ''))) as operadora_master_id
```

Padrão:

| Entidade        | Campo ID                    | Regra                                                                    |
| --------------- | --------------------------- | ------------------------------------------------------------------------ |
| Operadora       | `operadora_master_id`       | Hash MD5 de: `operadora`, `registro_ans_canonico`, `cnpj_canonico` |
| Estabelecimento | `estabelecimento_master_id` | Hash MD5 de: `estabelecimento`, `cnes_canonico`, `cnpj_canonico` |
| Prestador       | `prestador_master_id`       | Hash MD5 de: `prestador`, `chave_publica_principal`, `estabelecimento_master_id` |

Todos os IDs devem ser `text`, determinísticos e reproduzíveis.

---

### 2. Status MDM

Campo obrigatório em todos os masters:

```text
mdm_status
```

Valores aceitos:

| Status       | Significado                                                                   |
| ------------ | ----------------------------------------------------------------------------- |
| `GOLDEN`     | Registro canônico com alta confiança                                          |
| `CANDIDATE`  | Registro utilizável, mas com confiança intermediária                          |
| `QUARENTENA` | Registro com inconsistência relevante, não deve ser usado como canônico final |
| `DEPRECATED` | Registro substituído ou mantido apenas para histórico futuro                  |

Regra inicial recomendada:

```text
GOLDEN      -> mdm_confidence_score >= 85
CANDIDATE   -> mdm_confidence_score >= 60 and < 85
QUARENTENA  -> mdm_confidence_score < 60 ou exceção bloqueante
DEPRECATED  -> reservado para evolução futura
```

---

### 3. Score MDM

Campo obrigatório:

```text
mdm_confidence_score
```

Tipo recomendado:

```text
numeric ou integer entre 0 e 100
```

Sempre aplicar limite:

```sql
least(100, greatest(0, score_calculado)) as mdm_confidence_score
```

---

## Histórias

---

## HIS-09.1 — Criar schema lógico MDM

### Entregas

* [x] Criar pasta `healthintel_dbt/models/mdm/`.
* [x] Criar `healthintel_dbt/models/mdm/_mdm.yml`.
* [x] Criar documentação `docs/sprints/fase5/mdm_modelagem.md`.
* [x] Configurar `healthintel_dbt/dbt_project.yml` com schema `mdm_ans`, materialização `table` e tag `mdm`.
* [x] Documentar padrão de surrogate key determinística baseada em `md5`.
* [x] Documentar padrão de natural key por entidade.
* [x] Documentar padrão de crosswalk `xref_<entidade>_origem`.
* [x] Documentar padrão de exceção `mdm_<entidade>_exception`.
* [x] Documentar `mdm_status`.
* [x] Documentar `mdm_confidence_score`.

### Critério de aceite

* [x] `dbt_project.yml` possui bloco `mdm`.
* [x] `_mdm.yml` existe e documenta todos os modelos MDM.
* [x] `mdm_modelagem.md` explica arquitetura, chaves, score, crosswalk e exceções.
* [x] Nenhuma configuração aponta para `enrichment`.
* [x] Nenhuma configuração cria API, endpoint ou schema premium.

---

## HIS-09.2 — Criar MDM de Operadora

### Modelos

* [x] `healthintel_dbt/models/mdm/mdm_operadora_master.sql`
* [x] `healthintel_dbt/models/mdm/xref_operadora_origem.sql`
* [x] `healthintel_dbt/models/mdm/mdm_operadora_exception.sql`

### Fontes permitidas

* [x] `ref('stg_cadop')`
* [x] `ref('dim_operadora_atual')`
* [x] `ref('dq_cadop_documento')`
* [x] `ref('dq_operadora_documento')`
* [x] `ref('audit_operadora_razao_social_divergente_cadop')`

### Campos obrigatórios em `mdm_operadora_master`

* [x] `operadora_master_id`
* [x] `registro_ans_canonico`
* [x] `cnpj_canonico`
* [x] `razao_social_canonica`
* [x] `nome_fantasia_canonico`
* [x] `modalidade_canonica`
* [x] `documento_quality_status`
* [x] `cnpj_tamanho_valido`
* [x] `cnpj_digito_valido`
* [x] `cnpj_is_sequencia_invalida`
* [x] `is_cnpj_estrutural_valido`
* [x] `is_consistente_cadop_dim_operadora`
* [x] `has_divergencia_razao_social`
* [x] `mdm_confidence_score`
* [x] `mdm_status`
* [x] `dt_processamento`

### Regra de `is_cnpj_estrutural_valido`

```sql
case
    when documento_quality_status = 'VALIDO' then true
    else false
end as is_cnpj_estrutural_valido
```

### Score de operadora

Pontuação recomendada:

| Regra                                                                 | Pontos |
| --------------------------------------------------------------------- | ------ |
| `registro_ans_canonico` existe e está normalizado                     | +25    |
| `registro_ans` é consistente entre CADOP e `dim_operadora_atual`      | +10    |
| `documento_quality_status = 'VALIDO'`                                 | +25    |
| CNPJ tem 14 dígitos e não é sequência inválida                        | +15    |
| Razão social canônica preenchida                                      | +10    |
| Modalidade canônica preenchida                                        | +10    |
| Não há divergência em `audit_operadora_razao_social_divergente_cadop` | +5     |

Total máximo: 100.

### Regras de exceção de operadora

Criar `mdm_operadora_exception.sql` com:

* [x] `operadora_master_id`
* [x] `registro_ans`
* [x] `cnpj`
* [x] `exception_type`
* [x] `exception_severity`
* [x] `exception_message`
* [x] `is_blocking`
* [x] `dt_processamento`

Tipos mínimos:

| exception_type              | severity | is_blocking | Regra                                                        |
| --------------------------- | -------- | ----------- | ------------------------------------------------------------ |
| `CNPJ_DIVERGENTE_CADOP_DIM` | `HIGH`   | `true`      | Mesmo `registro_ans`, CNPJ divergente entre CADOP e dimensão |
| `RAZAO_SOCIAL_DIVERGENTE`   | `MEDIUM` | `false`     | CNPJ igual, razão social diferente                           |
| `CNPJ_INVALIDO_ESTRUTURAL`  | `MEDIUM` | `false`     | Documento inválido estruturalmente                           |
| `REGISTRO_ANS_AUSENTE`      | `HIGH`   | `true`      | Operadora sem chave regulatória confiável                    |

### Crosswalk de operadora

Criar `xref_operadora_origem.sql` com:

* [x] `operadora_master_id`
* [x] `source_system`
* [x] `source_model`
* [x] `source_key`
* [x] `registro_ans_origem`
* [x] `cnpj_origem`
* [x] `is_primary_source`
* [x] `dt_processamento`

Fontes esperadas:

```text
CADOP
DIM_OPERADORA_ATUAL
DQ_CADOP_DOCUMENTO
DQ_OPERADORA_DOCUMENTO
```

### Testes mínimos

* [x] `unique` em `operadora_master_id`
* [x] `not_null` em `operadora_master_id`
* [x] `not_null` em `registro_ans_canonico`
* [x] `accepted_values` em `mdm_status`
* [x] `mdm_confidence_score` entre 0 e 100
* [x] Cobertura: pelo menos 95% de `dim_operadora_atual` deve ter registro em `mdm_operadora_master`

---

## HIS-09.3 — Criar MDM de Estabelecimento CNES

### Modelos

* [x] `healthintel_dbt/models/mdm/mdm_estabelecimento_master.sql`
* [x] `healthintel_dbt/models/mdm/xref_estabelecimento_origem.sql`
* [x] `healthintel_dbt/models/mdm/mdm_estabelecimento_exception.sql`

### Fontes permitidas

* [x] `ref('stg_cnes_estabelecimento')`
* [x] `ref('dq_cnes_documento')`
* [x] `ref('ref_municipio_ibge')`
* [x] Outros modelos públicos já existentes, somente se necessários e sem dependência externa

### Campos obrigatórios em `mdm_estabelecimento_master`

* [x] `estabelecimento_master_id`
* [x] `cnes_canonico`
* [x] `cnpj_canonico`
* [x] `razao_social_canonica`
* [x] `nome_fantasia_canonico`
* [x] `cd_municipio_canonico`
* [x] `uf_canonica`
* [x] `situacao_cnes_canonica`
* [x] `documento_quality_status`
* [x] `cnpj_tamanho_valido`
* [x] `cnpj_digito_valido`
* [x] `cnpj_is_sequencia_invalida`
* [x] `is_cnpj_estrutural_valido`
* [x] `is_municipio_validado_ibge`
* [x] `mdm_confidence_score`
* [x] `mdm_status`
* [x] `dt_processamento`

### Score de estabelecimento

| Regra                                          | Pontos |
| ---------------------------------------------- | ------ |
| `cnes_canonico` existe e tem 7 dígitos         | +35    |
| `documento_quality_status = 'VALIDO'`          | +20    |
| CNPJ tem 14 dígitos e não é sequência inválida | +15    |
| Município validado contra referência IBGE      | +15    |
| Razão social ou nome fantasia preenchido       | +10    |
| Situação CNES preenchida                       | +5     |

Total máximo: 100.

### Regras de exceção de estabelecimento

Criar `mdm_estabelecimento_exception.sql` com:

* [x] `estabelecimento_master_id`
* [x] `cnes`
* [x] `cnpj`
* [x] `exception_type`
* [x] `exception_severity`
* [x] `exception_message`
* [x] `is_blocking`
* [x] `dt_processamento`

Tipos mínimos:

| exception_type             | severity | is_blocking | Regra                                       |
| -------------------------- | -------- | ----------- | ------------------------------------------- |
| `CNES_INVALIDO`            | `HIGH`   | `true`      | CNES ausente ou diferente de 7 dígitos      |
| `CNPJ_INVALIDO_ESTRUTURAL` | `MEDIUM` | `false`     | CNPJ inválido pela validação offline        |
| `MUNICIPIO_NAO_VALIDADO`   | `MEDIUM` | `false`     | Município não encontrado na referência IBGE |
| `RAZAO_SOCIAL_AUSENTE`     | `LOW`    | `false`     | Sem razão social/nome fantasia              |

### Crosswalk de estabelecimento

Criar `xref_estabelecimento_origem.sql` com:

* [x] `estabelecimento_master_id`
* [x] `source_system`
* [x] `source_model`
* [x] `source_key`
* [x] `cnes_origem`
* [x] `cnpj_origem`
* [x] `is_primary_source`
* [x] `dt_processamento`

Fontes esperadas:

```text
CNES
DQ_CNES_DOCUMENTO
```

### Testes mínimos

* [x] `unique` em `estabelecimento_master_id`
* [x] `not_null` em `estabelecimento_master_id`
* [x] `not_null` em `cnes_canonico`
* [x] `accepted_values` em `mdm_status`
* [x] `mdm_confidence_score` entre 0 e 100
* [x] `cnes_canonico` com 7 dígitos

---

## HIS-09.4 — Criar MDM de Prestador Público

### Modelos

* [x] `healthintel_dbt/models/mdm/mdm_prestador_master.sql`
* [x] `healthintel_dbt/models/mdm/xref_prestador_origem.sql`
* [x] `healthintel_dbt/models/mdm/mdm_prestador_exception.sql`

### Fontes permitidas

* [x] `ref('dq_prestador_documento')`, se disponível
* [x] `ref('stg_rede_assistencial')`, se aplicável
* [x] `ref('stg_cnes_estabelecimento')`, como origem pública inicial
* [x] `ref('mdm_estabelecimento_master')`
* [x] `ref('mdm_operadora_master')`, apenas quando houver relacionamento público confiável

### Regra importante

* [x] Não criar `tenant_id`.
* [x] Não criar estrutura multi-tenant.
* [x] Não misturar dados privados de cliente.
* [x] MDM privado de contrato/subfatura fica para Sprint 30.

### Campos obrigatórios em `mdm_prestador_master`

* [x] `prestador_master_id`
* [x] `estabelecimento_master_id`
* [x] `operadora_master_id`, nullable quando não houver relacionamento público confiável
* [x] `cnes_canonico`
* [x] `cnpj_canonico`
* [x] `nome_prestador_canonico`
* [x] `tipo_prestador_canonico`
* [x] `cd_municipio_canonico`
* [x] `uf_canonica`
* [x] `documento_quality_status`
* [x] `is_cnpj_estrutural_valido`
* [x] `mdm_confidence_score`
* [x] `mdm_status`
* [x] `dt_processamento`

### Score de prestador público

| Regra                                                 | Pontos |
| ----------------------------------------------------- | ------ |
| Chave pública principal existe                        | +30    |
| Relacionamento com `estabelecimento_master_id` existe | +25    |
| CNPJ classificado e estruturalmente válido            | +15    |
| Município/UF preenchidos                              | +15    |
| Nome ou descrição do prestador preenchido             | +10    |
| Relacionamento com operadora existe quando aplicável  | +5     |

Total máximo: 100.

### Regras de exceção de prestador

Criar `mdm_prestador_exception.sql` com:

* [x] `prestador_master_id`
* [x] `cnes`
* [x] `cnpj`
* [x] `exception_type`
* [x] `exception_severity`
* [x] `exception_message`
* [x] `is_blocking`
* [x] `dt_processamento`

Tipos mínimos:

| exception_type                  | severity | is_blocking | Regra                                              |
| ------------------------------- | -------- | ----------- | -------------------------------------------------- |
| `PRESTADOR_SEM_ESTABELECIMENTO` | `HIGH`   | `true`      | Prestador não relaciona com estabelecimento master |
| `CNPJ_INVALIDO_ESTRUTURAL`      | `MEDIUM` | `false`     | CNPJ inválido pela validação offline               |
| `DUPLICIDADE_CHAVE_PUBLICA`     | `HIGH`   | `true`      | Duplicidade por CNPJ + município + CNES            |
| `NOME_PRESTADOR_AUSENTE`        | `LOW`    | `false`     | Nome/descrição ausente                             |

### Crosswalk de prestador

Criar `xref_prestador_origem.sql` com:

* [x] `prestador_master_id`
* [x] `source_system`
* [x] `source_model`
* [x] `source_key`
* [x] `cnes_origem`
* [x] `cnpj_origem`
* [x] `registro_ans_origem`, nullable
* [x] `is_primary_source`
* [x] `dt_processamento`

### Testes mínimos

* [x] `unique` em `prestador_master_id`
* [x] `not_null` em `prestador_master_id`
* [x] `not_null` em `estabelecimento_master_id`
* [x] `accepted_values` em `mdm_status`
* [x] `mdm_confidence_score` entre 0 e 100

---

## Entregas esperadas

### Estrutura

* [x] `healthintel_dbt/models/mdm/`
* [x] `healthintel_dbt/models/mdm/_mdm.yml`
* [x] `docs/sprints/fase5/mdm_modelagem.md`

### Masters

* [x] `mdm_operadora_master.sql`
* [x] `mdm_estabelecimento_master.sql`
* [x] `mdm_prestador_master.sql`

### Crosswalk

* [x] `xref_operadora_origem.sql`
* [x] `xref_estabelecimento_origem.sql`
* [x] `xref_prestador_origem.sql`

### Exceções

* [x] `mdm_operadora_exception.sql`
* [x] `mdm_estabelecimento_exception.sql`
* [x] `mdm_prestador_exception.sql`

### Testes singulares recomendados

* [x] `assert_mdm_confidence_score_entre_0_e_100.sql`
* [x] `assert_mdm_operadora_cobertura_minima.sql`
* [x] `assert_mdm_status_valido.sql`, ou via YAML `accepted_values`

---

## Anti-escopo explícito

| Item                      | Status                      |
| ------------------------- | --------------------------- |
| Serpro                    | Fora do escopo              |
| Receita online            | Fora do escopo              |
| BrasilAPI                 | Fora do escopo              |
| Scraping                  | Fora do escopo              |
| Schema `enrichment`       | Fora do escopo              |
| Cache externo de CNPJ     | Fora do escopo              |
| Provider Python de CNPJ   | Fora do escopo              |
| `tenant_id`               | Fora do escopo da Sprint 29 |
| Dados privados de cliente | Fora do escopo              |
| API/FastAPI               | Fora do escopo              |
| Endpoint novo             | Fora do escopo              |
| Schema premium            | Fora do escopo              |
| Produto de consumo        | Fora do escopo              |

---

## Validação esperada — Hard Gates

Cada item exige evidência objetiva antes de considerar a sprint concluída.

### V1 — Compilação dbt

```bash
make dbt-compile
```

Critério:

```text
exit code 0
zero compilation error
```

---

### V2 — Build MDM

```bash
cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt build --select tag:mdm
```

Critério:

```text
ERROR=0
```

---

### V3 — Testes MDM

```bash
cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt test --select tag:mdm
```

Critério:

```text
ERROR=0
```

---

### V4 — Ausência de dependência externa no MDM

```bash
if grep -rEi "Serpro|Receita online|BrasilAPI|brasilapi|SERPRO_|BRASIL_API|documento_receita_cache|schema.*enrichment|requests|httpx|urlopen|http_get" healthintel_dbt/models/mdm/; then
  echo "FAIL: dependência externa encontrada no MDM"
  exit 1
else
  echo "PASS: MDM sem dependência externa"
fi
```

---

### V5 — Modelos canônicos intactos

Antes de implementar, registrar commit-base da Sprint 29:

```bash
git rev-parse HEAD
```

Depois da implementação, validar:

```bash
git diff --exit-code <COMMIT_BASE_SPRINT_29> -- \
  healthintel_dbt/models/intermediate/int_operadora_canonica.sql \
  healthintel_dbt/models/marts/dimensao/dim_operadora_atual.sql
```

Critério:

```text
exit code 0
nenhuma alteração nesses dois arquivos
```

> Não comparar obrigatoriamente contra `v3.0.0`, porque os modelos podem ter recebido alterações legítimas em sprints posteriores. A comparação correta é contra o commit-base da Sprint 29.

---

### V6 — Score MDM dentro de 0 a 100

Teste singular ou YAML deve garantir:

```text
mdm_confidence_score >= 0
mdm_confidence_score <= 100
```

Aplicável a:

* `mdm_operadora_master`
* `mdm_estabelecimento_master`
* `mdm_prestador_master`

---

### V7 — Status MDM válido

Todos os masters devem aceitar apenas:

```text
GOLDEN
CANDIDATE
QUARENTENA
DEPRECATED
```

---

### V8 — Estrutura obrigatória nas exceptions

Todas as tabelas públicas `mdm_*_exception` devem possuir:

* [x] `exception_type`
* [x] `exception_severity`
* [x] `exception_message`
* [x] `is_blocking`

---

### V9 — Cobertura mínima de operadoras

```text
>= 95% das operadoras de dim_operadora_atual devem existir em mdm_operadora_master
```

Teste recomendado:

```text
assert_mdm_operadora_cobertura_minima.sql
```

---

## Evidências de Execução

| Gate | Comando                                                 | Resultado | Data |
| ---- | ------------------------------------------------------- | --------- | ---- |
| V1   | `dbt compile`                                           | PASS      | 2026-04-27 |
| V2   | `dbt build --select tag:mdm`                            | PASS      | 2026-04-27 |
| V3   | `dbt test --select tag:mdm`                             | PASS      | 2026-04-27 |
| V4   | grep anti-dependência externa em `models/mdm/`          | PASS      | 2026-04-27 |
| V5   | Nenhuma deleção/modificação no modelo canônico          | PASS      | 2026-04-27 |
| V6   | score MDM entre 0 e 100                                 | PASS      | 2026-04-27 |
| V7   | `mdm_status` com valores aceitos                        | PASS      | 2026-04-27 |
| V8   | exceptions com campos obrigatórios                      | PASS      | 2026-04-27 |
| V9   | cobertura mínima de operadoras >= 95%                   | PASS      | 2026-04-27 |

---

## Resultado Esperado

A Sprint 29 estabelece a camada MDM pública e regulatória do HealthIntel, cobrindo operadoras, estabelecimentos CNES e prestadores públicos.

A sprint reaproveita a validação determinística e offline da Sprint 28, sem qualquer dependência de Serpro, Receita online, BrasilAPI, scraping, cache externo ou schema `enrichment`.

Os modelos `mdm_*_master` passam a fornecer chaves canônicas estáveis para uso em produtos premium futuros e no MDM privado da Sprint 30, sem alterar o data warehouse existente e sem expor novas APIs ou produtos de consumo nesta sprint.

Ao final da Sprint 29, o projeto terá:

* golden records públicos;
* crosswalk por origem;
* tabelas de exceção auditáveis;
* score de confiança MDM;
* status MDM padronizado;
* base pública pronta para ser reutilizada pelas próximas sprints.
