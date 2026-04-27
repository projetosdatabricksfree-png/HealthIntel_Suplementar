# Segurança e LGPD — Governança

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir a classificação de dados, regras de acesso, RLS, retenção e conformidade LGPD na plataforma HealthIntel Suplementar.

---

## Classificação de Dados

| Classificação | Descrição | Exemplo | Schema |
|--------------|-----------|---------|--------|
| **Público** | Dados ANS de domínio público | CNPJ, razão social, competência, score | `api_ans`, `consumo_ans` |
| **Interno** | Dados operacionais da plataforma | Logs de ingestão, métricas de pipeline | `plataforma` |
| **Restrito** | Dados privados do tenant | Contratos, subfaturas, números de contrato | `mdm_privado`, `consumo_premium_ans` |
| **Pessoal** | Dados de pessoa física | CPF | Apenas em `bruto_cliente` / `stg_cliente` |
| **Sensível** | Dados de saúde | CID, procedimentos médicos individuais | Não armazenado atualmente |

---

## Regras por Classificação

### Público

1. Acesso liberado conforme plano (ouro/prata/premium).
2. Sem RLS.
3. Exposto em API pública.
4. Sem restrição de retenção além da regra de negócio (60 competências).

### Interno

1. Acesso restrito à engenharia e operação.
2. Nunca exposto em API pública.
3. Retenção conforme necessidade operacional.

### Restrito

1. Acesso apenas pelo tenant dono dos dados.
2. RLS obrigatório (`tenant_id`).
3. Nunca em schema público.
4. API privada exige tenant autenticado.
5. Retenção conforme contrato com tenant.

### Pessoal

1. CPF apenas em fluxo privado.
2. Justificativa LGPD documentada.
3. Consentimento ou base legal registrada antes da ingestão.
4. Mascaramento/hash quando exposto em logs ou interfaces internas.
5. Não exposto em API pública.

### Sensível

1. Atualmente não armazenado.
2. Qualquer armazenamento futuro exige:
   - ADR específica de LGPD;
   - Encriptação em repouso;
   - Trilha de auditoria completa;
   - Aprovação de DPO.

---

## Regras de Acesso

### Row-Level Security (RLS)

1. Schemas com `tenant_id` devem ter RLS ativo.
2. Schemas com RLS: `bruto_cliente`, `stg_cliente`, `mdm_privado`, `consumo_premium_ans`.
3. Schemas sem RLS: `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans`, `quality_ans`, `mdm_ans`, `api_ans`, `consumo_ans`, `plataforma`.
4. RLS implementado via `infra/postgres/init/028_fase5_mdm_privado_rls.sql`.

### Grants

1. Roles separados por camada (ex: `role_api_ans_reader`).
2. API usa role que lê apenas `api_ans`.
3. Tenant Premium com SQL direto usa role que lê `consumo_ans` + `consumo_premium_ans` filtrado por `tenant_id`.
4. Grants documentados em `healthintel_dbt/macros/grants.sql`.

---

## Logs e Auditoria

### Log de Uso (`plataforma.log_uso`)

| Campo | Descrição | Dado sensível? |
|-------|-----------|----------------|
| `chave_id` | Identificador da chave | Não |
| `cliente_id` | Identificador do cliente | Não |
| `plano_id` | Plano contratado | Não |
| `camada` | Camada acessada | Não |
| `endpoint` | Rota acessada | Não |
| `metodo` | HTTP method | Não |
| `codigo_status` | Status HTTP | Não |
| `latencia_ms` | Tempo de resposta | Não |
| `timestamp_req` | Data/hora da requisição | Não |
| `hash_ip` | Hash SHA-256 do IP | Não (irreversível) |

**Nunca logar:** payload de request/response, API key completa, dados pessoais.

---

## Política de Retenção

| Camada | Retenção Padrão |
|--------|----------------|
| `bruto_ans` | Indefinido (histórico completo) |
| `stg_ans` a `consumo_ans` | 60 competências (5 anos) |
| `mdm_ans` | Indefinido (histórico de masters) |
| `api_ans` | 60 competências |
| `bruto_cliente` / `stg_cliente` | Conforme contrato com tenant |
| `mdm_privado` / `consumo_premium_ans` | Conforme contrato com tenant |
| `plataforma.log_uso` | 12 meses |

---

## Política de Exclusão

1. Dados públicos ANS: sem exclusão (domínio público).
2. Dados de tenant: exclusão mediante solicitação formal, prazo de 30 dias.
3. Exclusão deve ser rastreável (log de exclusão).
4. Backups podem conter dados por até 90 dias após exclusão.

---

## Payload Bruto

1. Payload bruto (`jsonb`) armazenado apenas em `bruto_ans` e `bruto_cliente`.
2. Nunca exposto em API pública.
3. Nunca exposto em API premium.
4. Acesso restrito à engenharia.

---

## Produtos Premium Privados

1. Contratos e subfaturas são dados restritos do tenant.
2. API premium privada (`/v1/premium/contratos`, `/v1/premium/subfaturas`) exige tenant autenticado.
3. Nenhuma resposta retorna dados de outro tenant.
4. `tenant_id` é filtro obrigatório no service e no PostgreSQL (RLS).
5. Score de qualidade publicado sem expor valores contratuais sensíveis.