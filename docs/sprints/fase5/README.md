# Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate

A Fase 5 deixa claro que:

- O projeto já passou por hardgate (`v3.0.0`).
- O que existe está pronto e **não deve ser refeito**.
- A camada `consumo_ans` já existe.
- A camada `api_ans` já existe.
- A staging e Gold/fatos já possuem vários modelos importantes.
- O que falta é **enriquecer, validar e criar produtos premium**.
- A Fase 5 cria uma **camada superior de confiança** sem quebrar o baseline.

## Status da Fase 5

**Status:** Backlog
**Versão de partida:** `v3.0.0` (Fase 4 concluída)
**Versão final prevista:** `v3.7.0` (após Sprint 32) + `v3.8.0-gov` (após Sprint 33)

## Regra-mãe da Fase 5

- Não alterar a lógica aprovada das Fases 1 a 4.
- Não renomear tabelas existentes.
- Não substituir `stg_*`, `int_*`, `fat_*`, `api_*` ou `consumo_*` já aprovadas.
- Criar apenas tabelas novas, com sufixos: `_validado`, `_qualificado`, `_mdm`, `_golden`, `_exception`, `_premium`.
- Usar os modelos existentes como fonte.
- Publicar novos produtos de consumo apenas depois de passarem em testes próprios.
- Manter os endpoints atuais funcionando sem mudança de contrato.
- Criar endpoints novos para dados validados/enriquecidos.

## Sprints

| Sprint | Título | Status | Tag prevista |
|--------|--------|--------|--------------|
| [Sprint 26](sprint_26_baseline_congelamento_mapa_expansao.md) | Baseline, Congelamento e Mapa de Expansão | Backlog | `v3.1.0-baseline` |
| [Sprint 27](sprint_27_validacao_tecnica_documentos.md) | Validação Técnica de CPF, CNPJ, CNES e Registro ANS | Backlog | `v3.2.0-dq-documental` |
| [Sprint 28](sprint_28_validacao_receita_serpro_cache.md) | Validação Oficial Receita/Serpro com Cache e Auditoria | Backlog | `v3.3.0-receita` |
| [Sprint 29](sprint_29_mdm_operadora_prestador_estabelecimento.md) | MDM de Operadora, Prestador e Estabelecimento | Backlog | `v3.4.0-mdm-publico` |
| [Sprint 30](sprint_30_mdm_contrato_subfatura.md) | MDM de Contrato e Subfatura (módulo privado por tenant) | Backlog | `v3.5.0-mdm-privado` |
| [Sprint 31](sprint_31_produtos_premium_consumo.md) | Produtos Premium Validados para Consumo | Backlog | `v3.6.0-premium` |
| [Sprint 32](sprint_32_endpoints_smoke_hardgate_fase5.md) | Endpoints Novos, Smoke Tests e Hardgate Fase 5 | Backlog | `v3.7.0` |
| [Sprint 33](sprint_33_governanca_documental.md) | Governança Documental, Catálogos e Padrões Normativos | Backlog | `v3.8.0-gov` |

## Arquitetura Alvo (Fase 5)

```
Fase 1–4 (congelado em v3.0.0)
   ↓
bruto_ans → stg_ans → int_ans → nucleo_ans → api_ans → consumo_ans
                                                            ↓ (intacto)
                                                            ↓
                                                  Cliente legado (Gold/consumo)
   ↓
Fase 5 (aditiva, sem reescrita):
   ↓
dq_*                  ← validação técnica documental (Sprint 27)
enrichment.*          ← cache Receita/Serpro (Sprint 28)
mdm.*                 ← golden record público (Sprint 29)
mdm_privado.*         ← golden record por tenant (Sprint 30)
consumo_premium_*     ← produtos comerciais validados (Sprint 31)
   ↓
api/v1/premium/*      ← rotas premium (Sprint 32)
   ↓
docs/governanca/*     ← normativo formal (Sprint 33)
```

## Critério de Saída da Fase 5

Hardgates a serem executados ao fim da Sprint 32 (release `v3.7.0`):

- [ ] `ruff check api ingestao scripts shared testes`
- [ ] `dbt build --select tag:quality tag:enrichment tag:mdm tag:mdm_privado tag:consumo_premium`
- [ ] `dbt test` zero falhas
- [ ] `make smoke-premium`
- [ ] `make dbt-build-premium`
- [ ] `pytest api/tests/integration/test_premium.py -v`
- [ ] `pytest testes/regressao/test_endpoints_fase5.py -v`
- [ ] `pytest testes/regressao/test_endpoints_fase4.py -v` (regressão Fase 4 ainda zero falhas)
- [ ] Verificação documental: zero alterações em modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*` da `v3.0.0`
- [ ] Tag git `v3.7.0`

## Documentos de apoio

- `docs/fase5/baseline_hardgate_fase4.md` (Sprint 26)
- `docs/fase5/matriz_lacunas_produto.md` (Sprint 26)
- `docs/fase5/padrao_nomes_fase5.md` (Sprint 26)
- `docs/fase5/mdm_modelagem.md` (Sprint 29)
- `docs/fase5/mdm_contrato_subfatura.md` (Sprint 30)
- `docs/produto/catalogo_premium.md` (Sprint 32)
- `docs/produto/quality_scores.md` (Sprint 32)
- `docs/produto/mdm_contrato_subfatura.md` (Sprint 32)
- `docs/produto/validacao_cnpj_receita.md` (Sprint 32)
- `docs/produto/tiss_tuss_premium.md` (Sprint 32)
- `docs/governanca/*` (Sprint 33)
