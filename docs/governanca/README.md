# Governança HealthIntel Suplementar

**Versão:** v3.8.0-gov
**Data:** 2026-04-27
**Status:** Ativo — normativo para todas as fases posteriores à Fase 5

---

## Objetivo

Estabelecer corpo normativo permanente para o desenvolvimento, evolução e operação da plataforma HealthIntel Suplementar como produto DaaS de dados ANS. Este documento é a raiz da governança e rege todas as decisões técnicas, de qualidade, segurança e comercialização.

---

## Escopo

- Modelagem de dados em todas as camadas (bruto → API)
- Padrões de nomenclatura, tipagem, índices, chaves e constraints
- Validação de qualidade determinística offline
- Master Data Management (MDM) público e privado
- Data products e catálogo de consumo
- API design — contratos, paginação, planos, segurança
- Segurança e LGPD — classificação de dados, RLS, retenção
- Hard gates normativos — checks obrigatórios em toda nova entrega

---

## Camadas Oficiais

| Camada | Schema | Propósito | Status |
|--------|--------|-----------|--------|
| **bruto_ans** | `bruto_ans` | Preservação fiel de arquivos originais ANS | Ativo |
| **stg_ans** | `stg_ans` | Padronização e tipagem sem perda de origem | Ativo |
| **int_ans** | `int_ans` | Transformações intermediárias, junções e deduplicação | Ativo |
| **nucleo_ans** | `nucleo_ans` | Fatos e dimensões canônicas do domínio ANS | Ativo |
| **quality_ans** | `quality_ans` | Validação determinística offline, scores e exceções | Ativo |
| **mdm_ans** | `mdm_ans` | Master Data público de operadoras, estabelecimentos e prestadores | Ativo |
| **api_ans** | `api_ans` | Projeção controlada para consumo via API (ouro e prata) | Ativo |
| **consumo_ans** | `consumo_ans` | Views analíticas públicas para SQL direto (clientes avançados) | Ativo |
| **bruto_cliente** | `bruto_cliente` | Dados brutos do tenant (contratos, subfaturas) — privado | Ativo |
| **stg_cliente** | `stg_cliente` | Padronização de dados do tenant — privado | Ativo |
| **mdm_privado** | `mdm_privado` | MDM privado por tenant — contrato/subfatura com RLS | Ativo |
| **consumo_premium_ans** | `consumo_premium_ans` | Views analíticas premium para SQL direto autorizado | Ativo |
| **plataforma** | `plataforma` | Logs de uso, billing, chaves, planos — interno | Ativo |

### Camadas NÃO ativas

- **enrichment**: não é camada ativa. Qualquer retorno de enriquecimento externo (Serpro, Receita, BrasilAPI, etc.) exige ADR futura com hard gate próprio.
- Qualquer nova camada exige ADR, hard gate e atualização deste catálogo.

---

## Princípios de Documentação

1. Toda tabela nova tem documentação obrigatória.
2. Toda coluna nova tem documentação obrigatória.
3. Documentação é fonte de verdade — não pode divergir do artefato físico.
4. Templates padronizados são obrigatórios para tabelas, colunas, índices, constraints, data products e endpoints.
5. Documentação ausente é blocking para merge em main.

---

## Princípios de Qualidade

1. Validação de CNPJ é determinística e offline — sem dependência externa.
2. CPF apenas em fluxo privado/tenant com justificativa LGPD.
3. CNES validado por formato e referência quando disponível.
4. Registro ANS validado por formato e consistência com CADOP/MDM.
5. Competência validada por faixa (200001 a competencia_atual + 1).
6. Exceção bloqueante impede publicação em produto principal.
7. Warning pode reduzir score sem bloquear publicação.

---

## Princípios de MDM

1. Golden record com survivorship rule explícita.
2. Crosswalk versionado e rastreável.
3. MDM público (`mdm_ans`) para entidades ANS de domínio público.
4. MDM privado (`mdm_privado`) para dados de tenant com RLS.
5. Score de confiança (`mdm_confidence_score`) em todo master.
6. Dados públicos e privados nunca se misturam no mesmo registro.

---

## Princípios de API

1. FastAPI lê **apenas** `api_ans`.
2. API premium (`/v1/premium/*`) lê **apenas** `api_ans.api_premium_*`.
3. Nenhum endpoint lê `consumo_premium_ans`, `mdm_ans`, `mdm_privado`, `quality_ans`, `bruto_cliente` ou `stg_cliente` diretamente.
4. Endpoints privados exigem tenant autenticado.
5. Toda rota tem contrato request/response documentado.
6. Toda rota tem plano comercial e limite de consumo.
7. Toda rota com lista tem paginação e limite máximo de linhas.
8. Nenhuma rota permite dump completo por padrão.

---

## Princípios de Segurança / LGPD

1. Dados classificados em: públicos, internos, restritos, pessoais, sensíveis.
2. CPF apenas em fluxo privado com justificativa LGPD explícita.
3. Dados privados nunca em schema público.
4. RLS obrigatório em schemas com `tenant_id`.
5. Logs sem dados sensíveis de payload.
6. Rastreabilidade de acesso (`plataforma.log_uso`).
7. Política de retenção e exclusão definida por camada.
8. Payload bruto nunca exposto em API pública.

---

## Hard Gates Normativos

Todo merge em main deve passar por:

1. Toda tabela nova tem descrição.
2. Toda coluna nova tem descrição.
3. CPF `varchar(11)`, nunca numérico.
4. CNPJ `varchar(14)`, nunca numérico.
5. CNES `varchar(7)`, preserva zeros.
6. Registro ANS `varchar(6)`, preserva zeros.
7. Competência `int` formato YYYYMM.
8. Dinheiro `numeric(18,2)`, nunca float.
9. Taxa técnica `double precision`.
10. Flags `boolean`.
11. Data pura `date`.
12. Timestamp técnico `timestamp(3)`.
13. UF `char(2)`.
14. Índice com justificativa.
15. Chave com relacionamento documentado.
16. Constraint com regra documentada.
17. Função com contrato.
18. Trigger com justificativa.
19. MDM com survivorship rule.
20. Exception com severidade e bloqueio.
21. Data product com owner, SLA e contrato.
22. Endpoint com contrato request/response.
23. Endpoint premium lê apenas `api_ans`.
24. Dado privado tem `tenant_id`.
25. Produto premium tem score de qualidade.

---

## Relação com as Sprints 28–32

| Sprint | Escopo | Governança associada |
|--------|--------|---------------------|
| Sprint 28 | Validação CNPJ offline | `padroes_qualidade_validacao.md` |
| Sprint 29 | MDM público | `mdm_governanca.md` |
| Sprint 30 | MDM privado/contrato/subfatura | `mdm_governanca.md` + `seguranca_lgpd_governanca.md` |
| Sprint 31 | Produtos premium SQL | `data_products_governanca.md` + `catalogo_tabelas.md` |
| Sprint 32 | Endpoints premium API | `api_governanca.md` + `hardgate_governanca.md` |

---

## Anti-Escopo — Dependências Externas Obrigatórias

As seguintes dependências **NÃO** são requisitos ativos da plataforma:

- **Serpro** — não é obrigatório para validação de CNPJ.
- **Receita online** — não é fonte de verdade operacional.
- **BrasilAPI** — não é dependência obrigatória.
- **enrich-cnpj** — não é comando ativo.
- **schema enrichment** — não é camada ativa.
- **cnpj_receita_status / is_cnpj_ativo_receita / int_cnpj_receita_validado** — não são padrões ativos.
- Qualquer integração externa futura exige ADR, hard gate próprio e atualização deste documento.