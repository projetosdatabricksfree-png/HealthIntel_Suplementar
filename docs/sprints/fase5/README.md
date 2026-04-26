# Fase 5 — Enriquecimento, Qualidade e MDM

Este diretório materializa a governança mínima da Fase 5. A Fase 5 é aditiva: parte do baseline `v3.0.0`, preserva as entregas das Fases 1 a 4 e cria novas camadas para qualidade documental, enriquecimento externo controlado, MDM público, MDM privado por tenant, produtos premium e API premium.

## Regra de Imutabilidade do Baseline

- A tag git `v3.0.0` é o ponto de congelamento da Fase 4.
- Modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*` e `consumo_*` existentes no baseline `v3.0.0` não podem ser reescritos, renomeados ou ter sua semântica alterada pela Fase 5.
- Toda melhoria da Fase 5 deve entrar como artefato novo, com nome distinto e camada explícita.
- A compatibilidade dos endpoints e produtos existentes deve ser preservada por regressão documental, dbt e API nas sprints posteriores.

## Documentos da Sprint 26

- `docs/sprints/fase5/baseline_hardgate_fase4.md`: inventário congelado do baseline `v3.0.0`.
- `docs/sprints/fase5/matriz_lacunas_produto.md`: mapa de lacunas comerciais e técnicas por domínio.
- `docs/sprints/fase5/padrao_nomes_fase5.md`: vocabulário obrigatório para tabelas e modelos novos.
- `docs/sprints/fase5/governanca_minima_fase5.md`: schemas, roles, contratos mínimos e regras de publicação.

## Sequência da Fase 5

| Sprint | Escopo | Status após Sprint 26 |
|--------|--------|-----------------------|
| Sprint 26 | Baseline real `v3.0.0`, inventário e governança mínima | Documental |
| Sprint 27 | Qualidade documental e modelos `dq_*` | Backlog |
| Sprint 28 | Enriquecimento CNPJ Serpro/cache | Backlog |
| Sprint 29 | MDM público de operadora, estabelecimento e prestador | Backlog |
| Sprint 30 | Ingestão privada tenant e MDM contrato/subfatura | Backlog |
| Sprint 31 | Produtos premium em SQL direto e superfície `api_premium_*` | Backlog |
| Sprint 32 | Endpoints `/v1/premium/*`, smoke e hardgate da Fase 5 | Backlog |
| Sprint 33 | Governança documental formal final e release `v3.8.0-gov` | Backlog |

## Contrato Arquitetural Premium

| Superfície | Papel | Consumidor | Regra |
|------------|-------|------------|-------|
| `consumo_ans` | Produto SQL direto legado | Clientes atuais | Mantido intacto a partir do baseline `v3.0.0`. |
| `healthintel_cliente_reader` | Role comum | Clientes legados | Pode ler `consumo_ans`; não pode receber grants em schemas premium ou internos da Fase 5. |
| `consumo_premium_ans` | Produto SQL direto premium | Clientes premium | Recebe apenas modelos `consumo_premium_*` aprovados na Sprint 31. |
| `healthintel_premium_reader` | Role premium | Clientes premium | Pode ler `consumo_premium_ans` conforme contrato comercial premium. |
| `api_ans.api_premium_*` | Camada de serviço premium | FastAPI | Única superfície de leitura permitida para endpoints premium. |

Regra bloqueante: a FastAPI nunca lê `consumo_premium_ans` diretamente. Rotas premium devem consultar exclusivamente `api_ans.api_premium_*`, preservando o padrão arquitetural já usado nas Fases 1 a 4.

## Camadas Novas Planejadas

| Camada | Schema/documento | Primeira sprint de implementação | Observação |
|--------|------------------|----------------------------------|------------|
| Qualidade documental | `quality_ans` | Sprint 27 | Modelos `dq_*` e tabelas `*_validado`. |
| Enriquecimento CNPJ | `enrichment` | Sprint 28 | Cache/auditoria Serpro, sem scraping. |
| MDM público | `mdm` | Sprint 29 | Golden records públicos e crosswalks. |
| Entrada privada tenant | `bruto_cliente`, `stg_cliente` | Sprint 30 | Contrato/subfatura privados por tenant. |
| MDM privado | `mdm_privado` | Sprint 30 | Dados privados isolados por tenant. |
| SQL direto premium | `consumo_premium_ans` | Sprint 31 | Produto premium para clientes SQL. |
| Serviço API premium | `api_ans.api_premium_*` | Sprint 31/32 | Superfície exclusiva da FastAPI premium. |

## Princípio de Execução

A Sprint 26 não cria código, SQL, dbt, API ou infraestrutura. Ela cria a documentação mínima para que as Sprints 27 a 33 sejam executadas sem ambiguidade e sem risco de regressão contra `v3.0.0`.
