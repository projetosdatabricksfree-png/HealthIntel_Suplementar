# Produto Premium TISS/TUSS — Decisão de Fonte e Modo de Operação

**Versão:** 1.0.0 — Sprint 31  
**Data da decisão:** 2026-04-27  
**Responsável técnico:** Engenharia de Dados HealthIntel  

---

## Contexto

A Sprint 31 exige a criação de produtos premium TISS/TUSS em `consumo_premium_ans` e superfícies de API em `api_ans`. Para que esses modelos compilem e sejam testáveis, é necessária uma fonte oficial da Terminologia Unificada da Saúde Suplementar (TUSS) e do Rol de Procedimentos da ANS.

---

## Situação Atual das Fontes TUSS/ROL

### Disponibilidade de fonte oficial

- **Tabela TUSS oficial da ANS:** Não está disponível no momento da Sprint 31 como arquivo público ingerível automaticamente. A ANS publica a TUSS em formato PDF e portal web (https://www.gov.br/ans/pt-br/assuntos/prestadores/tiss), mas não há CSV ou API REST acessível programaticamente.
- **Rol de Procedimentos (RN):** Disponível no portal da ANS em formato PDF/HTML. A resolução normativa vigente (RN 465/2021 e atualizações) lista os procedimentos obrigatórios, mas não há CSV oficial público.

### Decisão arquitetural

**Modo CI Sintético — Não Comercial.** Para permitir que a Sprint 31 compile, teste e valide os contratos técnicos dos modelos TISS/TUSS, e para que os hard gates V1, V2 e V9 sejam executáveis, foi adotada uma base sintética representativa gerada pelo script `scripts/gerar_seeds_tuss_rol.py`.

---

## Características do Modo Sintético

| Atributo | Valor |
|----------|-------|
| **Fonte** | `healthintel_dbt/seeds/ref_tuss.csv` |
| **Fonte** | `healthintel_dbt/seeds/ref_rol_procedimento.csv` |
| **Origem** | Script determinístico `scripts/gerar_seeds_tuss_rol.py` |
| **Número de códigos** | 3.500 códigos TUSS sintéticos |
| **Grupos representados** | Consultas, Exames, Terapias, Cirurgias, Internações, Obstetrícia, Odontologia |
| **Finalidade** | Desenvolvimento, CI e validação de contratos técnicos |
| **Status comercial** | **NÃO COMERCIAL** — não representa dados reais da ANS |
| **Vigência** | 2024-01-01 em diante (sem data fim) |

---

## Modelos TISS/TUSS Criados na Sprint 31

Os modelos abaixo foram criados no escopo da Sprint 31:

| Modelo | Localização | Status |
|--------|------------|--------|
| `stg_tuss_terminologia` | `models/staging/` | Implementado (seed `ref_tuss`) |
| `dim_tuss_terminologia` | `models/marts/dimensao/` | Implementado |
| `dim_tuss_procedimento` | `models/marts/dimensao/` | Implementado |
| `xref_tiss_tuss_procedimento` | `models/consumo_premium/` | Implementado (crosswalk sintético) |
| `consumo_premium_tiss_procedimento_tuss_validado` | `models/consumo_premium/` | Implementado |
| `api_premium_tiss_procedimento_tuss_validado` | `models/api/premium/` | Implementado |
| `api_premium_tuss_procedimento` | `models/api/premium/` | Implementado |

Todos usam `ref_tuss` e `ref_rol_procedimento` como base TUSS, com `tiss_tuss_match_status = 'UNMATCHED'` para indicar explicitamente a ausência de correspondência com TISS real.

---

## Gate V9 — TUSS/ROL Validado

**Status:** PASS (modo sintético documentado como não comercial)

O critério V9 exige que:
- Fontes TUSS/ROL existam fisicamente **OU**
- Modo sintético seja documentado e marcado como não comercial **OU**
- Produto TISS/TUSS seja bloqueado até fonte oficial disponível

Esta documentação satisfaz o segundo critério. Os modelos compilam, materializam e são testáveis.

---

## Roadmap para Fonte Oficial

| Marco | Descrição | Previsão |
|-------|-----------|----------|
| **Sprint 31** | Modo CI sintético, não comercial | Concluído |
| **Sprint futura (TBD)** | Ingestão programática da TUSS via portal ANS | Backlog |
| **Sprint futura (TBD)** | Parser de RN para Rol de Procedimentos | Backlog |
| **Marco comercial** | Substituição de seeds sintéticas por tabelas oficiais versionadas | Antes do primeiro cliente premium em produção |

---

## Aviso Legal

> **ATENÇÃO:** Os dados TUSS/ROL presentes nos modelos `consumo_premium_tiss_procedimento_tuss_validado` e `api_premium_tiss_procedimento_tuss_validado` são **SINTÉTICOS e NÃO COMERCIAIS**. NÃO representam a Terminologia TUSS oficial da ANS nem o Rol de Procedimentos vigente. NÃO devem ser utilizados para precificação, auditoria, reembolso ou qualquer finalidade regulatória ou comercial. A HealthIntel Suplementar substituirá estas bases por fontes oficiais antes da ativação de qualquer cliente premium em produção.