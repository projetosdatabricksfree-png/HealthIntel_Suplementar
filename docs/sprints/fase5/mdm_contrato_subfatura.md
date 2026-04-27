# MDM Privado de Contrato e Subfatura

**Sprint:** 30 (Fase 5)
**Schema físico:** `bruto_cliente`, `stg_cliente`, `mdm_privado`
**Tag dbt:** `mdm_privado`

## Objetivo

Permitir que cada cliente (tenant) ingira seus dados internos de contrato e
subfatura, reconciliando-os com o MDM público da plataforma sem misturar
domínios e sem expor dados privados em schemas públicos.

## Diferença entre MDM público e MDM privado

| Aspecto | MDM público (`mdm_ans`) | MDM privado (`mdm_privado`) |
|---|---|---|
| Origem | Dados ANS abertos | Dados internos do cliente |
| Tenant | N/A — entidade global | `tenant_id` obrigatório, NOT NULL |
| Acesso | `healthintel_cliente_reader` (leitura) | Sem acesso a `cliente_reader` |
| RLS | Não aplicável | Sim, em `bruto_cliente.*` |
| Validação documental | `dq_*_documento` (Sprint 27/28) | Reusa `dq_*` offline. Sem Receita/Serpro/BrasilAPI |

## Regra de `tenant_id`

- Nasce em `bruto_cliente.contrato` e `bruto_cliente.subfatura`. NOT NULL.
- Não pode ser inferido a partir de fonte_arquivo, hash_arquivo ou source_system.
- Carga sem tenant é rejeitada antes de virar staging.
- Toda chave hash determinística inclui `tenant_id`.

## Regra de RLS

- `bruto_cliente.contrato` e `bruto_cliente.subfatura` têm RLS ENABLE + FORCE.
- Política: `tenant_id = current_setting('app.tenant_id', true)`.
- Aplicação ou processo de carga deve setar `app.tenant_id` antes de leitura/escrita.
- Sem `app.tenant_id` setado, leitura retorna zero linhas.

## Fluxo

```
bruto_cliente.contrato       ──▶ stg_cliente_contrato ──▶ mdm_contrato_master  ──▶ xref_contrato_origem
bruto_cliente.subfatura      ──▶ stg_cliente_subfatura ──▶ mdm_subfatura_master ──▶ xref_subfatura_origem

mdm_contrato_master  ──▶ mdm_contrato_exception
                     ──▶ mdm_operadora_contrato_exception
                     ──▶ mdm_prestador_contrato_exception (reservada)
mdm_subfatura_master ──▶ mdm_subfatura_exception
```

## Regras de contrato

- Hash: `md5('contrato' | tenant_id | numero_contrato_normalizado | registro_ans_canonico | cnpj_operadora_canonico)`.
- Operadora resolvida via `mdm_operadora_master` por `registro_ans_canonico` ou `cnpj_canonico`.
- Sem operadora resolvida → `QUARENTENA` + exceção `CONTRATO_SEM_OPERADORA_MDM`.
- CNPJ divergente do MDM público → `QUARENTENA` + exceção `CONTRATO_CNPJ_OPERADORA_DIVERGENTE_MDM`.
- Score 0–100. `GOLDEN ≥ 85`, `CANDIDATE ≥ 60 < 85`, `QUARENTENA < 60` ou exceção bloqueante.

## Regras de subfatura

- Hash: `md5('subfatura' | tenant_id | numero_contrato_normalizado | codigo_subfatura_normalizado)`.
- Contrato resolvido pelo par `(tenant_id, numero_contrato_normalizado)` no `mdm_contrato_master`.
- Sem contrato → `QUARENTENA` + exceção `SUBFATURA_SEM_CONTRATO`.
- Duplicidade por contrato + código + competência → exceção `SUBFATURA_DUPLICADA_COMPETENCIA` (WARNING).

## Regras de crosswalk

- `is_crosswalk_aprovado = false` por padrão; aprovação manual em sprint futura.
- Crosswalk não pode ligar registros de tenants diferentes (teste contratual).

## Regras de exceção bloqueante

| `exception_type` | `is_blocking` | Origem |
|---|---|---|
| `TENANT_AUSENTE` | true | Linha sem `tenant_id` |
| `CONTRATO_SEM_OPERADORA_MDM` | true | `is_operadora_mdm_resolvida = false` |
| `CONTRATO_CNPJ_OPERADORA_DIVERGENTE_MDM` | true | CNPJ contrato ≠ CNPJ MDM público |
| `CONTRATO_DUPLICADO_TENANT` | true | (tenant_id, numero_contrato_normalizado) duplicado |
| `SUBFATURA_SEM_CONTRATO` | true | `is_contrato_resolvido = false` |
| `SUBFATURA_DUPLICADA_COMPETENCIA` | false | Duplicidade contrato+código+competência |
| `LAYOUT_PRIVADO_NAO_RECONHECIDO` | true | Reservado p/ camada de carga |
| `CROSSWALK_TENANT_DIVERGENTE` | true | Crosswalk cruzando tenants |

## Relação com MDM público

- MDM privado **lê** `mdm_operadora_master` para resolver `operadora_master_id`.
- MDM privado **não** modifica MDM público.
- MDM privado **não** publica dados privados em `mdm_ans`, `nucleo_ans`, `consumo_ans`, `api_ans`.

## Anti-escopo

- Sem API/FastAPI nesta sprint. Endpoints premium ficam para Sprint 32.
- Sem produto premium. `consumo_premium_ans` é Sprint 31.
- Sem alteração de modelos públicos da Sprint 29.
- Sem Serpro, Receita online, BrasilAPI, scraping, schema `enrichment`, provider Python de CNPJ.
- Sem UUID v5, sem extensão `uuid-ossp`, sem sequência incremental.
