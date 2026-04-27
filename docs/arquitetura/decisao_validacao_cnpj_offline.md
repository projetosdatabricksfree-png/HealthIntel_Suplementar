# ADR-001: Validação de CNPJ Offline e Determinística

**Status:** Aceito  
**Data:** 2026-04-27  
**Decisor:** Engenharia de Dados HealthIntel  
**Sprint:** Sprint 28 — Validação Determinística de CNPJ (Offline)

---

## Contexto

A Sprint 28 originalmente previa validação oficial de CNPJ via Serpro/Receita Federal, com cache externo, auditoria de chamadas e schema `enrichment`. Durante a revisão de arquitetura pré-implementação, identificou-se que essa dependência externa introduzia riscos incompatíveis com os princípios do produto:

- O pipeline dbt deve permanecer determinístico e offline.
- O CI não pode depender de rede, token, segredo ou quota paga para passar.
- O custo recorrente da quota Serpro não tinha contrapartida proporcional no MVP.
- A validação estrutural/matemática já cobre >95% dos erros de CNPJ (formato, dígito verificador, sequências repetidas).

## Decisão

**A Sprint 28 adota validação de CNPJ 100% offline, determinística e sem custo recorrente.**

A validação é composta por três camadas:

1. **Estrutural:** normalização (somente dígitos), tamanho (14 caracteres), rejeição de sequências repetidas (`00000000000000`, `11111111111111`, etc.).
2. **Matemática:** validação dos dois dígitos verificadores via algoritmo oficial de CNPJ.
3. **Referencial interna:** cruzamento entre a dimensão de operadora (`dim_operadora_atual`) e a fonte CADOP/ANS (`stg_cadop`) via `registro_ans`, detectando CNPJs divergentes quando ambos são estruturalmente válidos.

Nenhuma validação online (Serpro, Receita Federal, BrasilAPI ou qualquer API externa) é exigida como hard gate, dependência de CI, provider, job ou schema.

## Alternativas Consideradas

| Alternativa | Decisão | Justificativa |
|-------------|---------|---------------|
| Serpro (API oficial) | Rejeitada | Custo recorrente, dependência de rede, exige credenciais em cofre, quebra determinismo do CI. |
| Receita Federal online | Rejeitada | Mesmo problema do Serpro; e-CNPJ ou certificado digital inviabilizam CI. |
| BrasilAPI (gratuita) | Rejeitada | API gratuita como hard gate introduz dependência externa, instabilidade e risco de rate limit no CI. |
| Scraping | Rejeitada | Risco legal, fragilidade de parse, bloqueio de IP. |
| Validação estrutural + matemática + referencial interna | **Aceita** | 100% offline, 100% determinística, sem custo, sem segredo, sem rede. |

## Consequências

### Positivas
- CI roda sem internet, sem token, sem segredo, sem e-CNPJ.
- Custo operacional zero para validação de CNPJ.
- `dbt build` e `dbt test` permanecem determinísticos.
- Nenhum schema `enrichment` é criado — menos superfície de manutenção.
- Menos risco de vazamento de credenciais.

### Negativas
- Situação cadastral oficial (ATIVA, BAIXADA, SUSPENSA, INAPTA, NULA) não é conhecida no MVP.
- CNPJs válidos estruturalmente mas inexistentes na Receita não são detectados.
- Razão social oficial da Receita não é comparada com a razão social ANS.

## Backlog Futuro

Uma sprint opcional futura pode realizar **ingestão offline dos dados abertos de CNPJ da Receita Federal** (arquivos CSV públicos disponibilizados periodicamente pela RFB), sem dependência de API online, sem token e sem custo. Esta sprint não bloqueia o MVP e não faz parte da Sprint 28.

## Violações Proibidas

- ❌ Criar schema `enrichment`.
- ❌ Criar tabela `documento_receita_cache`.
- ❌ Implementar `SerproCnpjProvider`, `MockCnpjProvider` ou qualquer cliente Python de API externa.
- ❌ Adicionar `make enrich-cnpj` ou DAG de enriquecimento.
- ❌ Usar `requests`, `httpx`, `urlopen` ou qualquer HTTP client em macros/modelos dbt.
- ❌ Exigir `SERPRO_CONSUMER_KEY`, `SERPRO_CONSUMER_SECRET`, `HEALTHINTEL_CNPJ_PROVIDER` ou variáveis de ambiente de API externa.
- ❌ Referenciar `enrichment` em `dbt_project.yml` ou `governanca_minima_fase5.md` como entrega da Sprint 28.