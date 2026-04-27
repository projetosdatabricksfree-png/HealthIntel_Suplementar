# Hard Gates Normativos

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir os checks obrigatórios (hard gates) que todo merge em main deve passar. Estes gates são normativos e permanentes — aplicam-se a todas as fases posteriores à Fase 5.

---

## Hard Gates por Categoria

### Documentação

| # | Gate | Descrição |
|---|------|-----------|
| HG-DOC-01 | Toda tabela nova tem descrição | `description` no dbt ou entrada no catálogo |
| HG-DOC-02 | Toda coluna nova tem descrição | `description` no schema.yml |
| HG-DOC-03 | Documentação não diverge do artefato físico | Review de PR |
| HG-DOC-04 | Templates preenchidos para tabela, coluna, índice, data product | conforme `docs/governanca/templates/` |

### Tipagem

| # | Gate | Descrição |
|---|------|-----------|
| HG-TYPE-01 | CPF `varchar(11)`, nunca numérico | `grep` por tipo proibido |
| HG-TYPE-02 | CNPJ `varchar(14)`, nunca numérico | `grep` por tipo proibido |
| HG-TYPE-03 | CNES `varchar(7)`, preserva zeros | `grep` por tipo proibido |
| HG-TYPE-04 | Registro ANS `varchar(6)`, preserva zeros | `grep` por tipo proibido |
| HG-TYPE-05 | Competência `int` YYYYMM | `grep` por formato errado |
| HG-TYPE-06 | Dinheiro `numeric(18,2)`, nunca float | `grep` por `float`, `real` em coluna monetária |
| HG-TYPE-07 | Taxa técnica `double precision` | Revisão de PR |
| HG-TYPE-08 | Flags `boolean` | `grep` por `int` 0/1 como flag |
| HG-TYPE-09 | Data pura `date` | Revisão de PR |
| HG-TYPE-10 | Timestamp técnico `timestamp(3)` | Revisão de PR |
| HG-TYPE-11 | UF `char(2)` | Revisão de PR |

### Índices, Chaves e Constraints

| # | Gate | Descrição |
|---|------|-----------|
| HG-IDX-01 | Índice com justificativa documentada | Comentário no SQL ou catálogo |
| HG-IDX-02 | Chave com relacionamento documentado | schema.yml ou catálogo |
| HG-IDX-03 | Constraint com regra documentada | schema.yml |
| HG-IDX-04 | Função com contrato (entrada/saída/efeitos) | Documento ou comentário |
| HG-IDX-05 | Trigger com justificativa | ADR ou documento |
| HG-IDX-06 | Nomenclatura de índice segue padrão | `pk_`, `fk_`, `uk_`, `ck_`, `ix_`, `ux_` |

### MDM

| # | Gate | Descrição |
|---|------|-----------|
| HG-MDM-01 | MDM com survivorship rule documentada | `mdm_governanca.md` |
| HG-MDM-02 | Surrogate key no master | `*_master_id` |
| HG-MDM-03 | `mdm_confidence_score` presente | Coluna no master |
| HG-MDM-04 | Dados públicos e privados não se misturam | Review de PR |

### Qualidade

| # | Gate | Descrição |
|---|------|-----------|
| HG-QUAL-01 | Exception com severidade e bloqueio | `BLOQUEANTE` ou `WARNING` |
| HG-QUAL-02 | Validação de CNPJ determinística offline | Sem dependência externa |
| HG-QUAL-03 | Score de qualidade presente em data product premium | `quality_score_*` |

### Data Products

| # | Gate | Descrição |
|---|------|-----------|
| HG-DP-01 | Data product com owner documentado | Catálogo |
| HG-DP-02 | Data product com SLA documentado | Catálogo |
| HG-DP-03 | Data product com contrato de consumo | API ou SQL |
| HG-DP-04 | Produto premium tem score de qualidade | `quality_score_*` |

### API

| # | Gate | Descrição |
|---|------|-----------|
| HG-API-01 | Endpoint com contrato request/response | Schema Pydantic |
| HG-API-02 | Endpoint premium lê apenas `api_ans` | `grep` por schema proibido |
| HG-API-03 | Toda rota com lista tem paginação | `pagina`, `limite` |
| HG-API-04 | Limite máximo de 100 linhas por request | Parâmetro `le=100` |
| HG-API-05 | Nenhuma rota permite dump completo por padrão | Sem `limite=0` ou `limite` ilimitado |

### Segurança / LGPD

| # | Gate | Descrição |
|---|------|-----------|
| HG-SEC-01 | Dado privado tem `tenant_id` | Coluna obrigatória |
| HG-SEC-02 | Dado privado nunca em schema público | `mdm_privado`, `consumo_premium_ans` |
| HG-SEC-03 | CPF apenas em fluxo privado | Review de PR |
| HG-SEC-04 | RLS ativo em schemas com `tenant_id` | `infra/postgres/init/` |
| HG-SEC-05 | Logs sem dados sensíveis | Review de `log_uso` |
| HG-SEC-06 | Payload bruto nunca exposto em API | Review de schema Pydantic |

---

## Scripts de Verificação

### V8 — Premium não lê schema proibido
```bash
if grep -rEi "consumo_premium_ans|mdm_ans|mdm_privado|quality_ans|bruto_cliente|stg_cliente|enrichment" api/app/routers/ api/app/services/; then
  echo "FAIL: serviço FastAPI lendo schema proibido diretamente"
  exit 1
else
  echo "PASS: FastAPI premium lê somente api_ans"
fi
```

### V9 — Sem dependência externa
```bash
if grep -rEi "Serpro|Receita online|BrasilAPI|brasilapi|SERPRO_|BRASIL_API|documento_receita_cache|enrich-cnpj|schema.*enrichment|int_cnpj_receita_validado|cnpj_receita_status|is_cnpj_ativo_receita" api/ scripts/ healthintel_dbt/models/api/premium/; then
  echo "FAIL: dependência externa proibida encontrada"
  exit 1
else
  echo "PASS: sem dependência externa proibida"
fi
```

### V7 — CPF/CNPJ como texto (governança)
```bash
# Procura permissões explícitas de tipo numérico
if grep -rEi "CNPJ.*deve ser.*(int|integer|bigint|numeric|decimal)|CPF.*deve ser.*(int|integer|bigint|numeric|decimal)" docs/governanca/; then
  echo "FAIL: governanca permite CPF/CNPJ numerico"
  exit 1
else
  echo "PASS: CPF/CNPJ governados como texto"
fi
```

### V6 — Sem pendência crítica
```bash
if grep -rEi "TODO|TBD|preencher depois|a definir sem decisao" docs/governanca/; then
  echo "FAIL: documentação de governança possui pendências críticas"
  exit 1
else
  echo "PASS: documentação sem pendências críticas explícitas"
fi
```

---

## Fluxo de Aprovação

1. PR aberto com alterações.
2. CI/CD executa hard gates automaticamente.
3. Review humano verifica gates não automatizáveis.
4. Merge apenas se todos os gates passarem.
5. Exceção a hard gate exige ADR + aprovação do owner técnico.

---

## Template de Hard Gate (para novos gates)

```markdown
| # | Gate | Descrição | Automação |
|---|------|-----------|-----------|
| HG-NOVO-01 | Descrição do gate | O que verifica | Script ou manual |
```

---

## Relação com Sprints

| Sprint | Hard Gates Aplicáveis |
|--------|----------------------|
| Sprint 28 | HG-QUAL-02 (validação CNPJ offline) |
| Sprint 29 | HG-MDM-01 a HG-MDM-04 (MDM público) |
| Sprint 30 | HG-SEC-01 a HG-SEC-04 (MDM privado, RLS) |
| Sprint 31 | HG-DP-01 a HG-DP-04 (data products premium) |
| Sprint 32 | HG-API-01 a HG-API-05 (endpoints premium) |
| Sprint 33 | HG-DOC-01 a HG-DOC-04 (documentação) |