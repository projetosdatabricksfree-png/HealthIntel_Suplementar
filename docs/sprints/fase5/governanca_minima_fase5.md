# Governança Mínima — Fase 5

Este documento define a governança obrigatória antes da implementação das Sprints 27 a 32. Ele documenta a configuração futura esperada, mas não altera `healthintel_dbt/dbt_project.yml`, SQL, API ou infraestrutura na Sprint 26.

## Schemas Oficiais da Fase 5

| Schema | Responsabilidade | Primeira sprint de uso | Publicação |
|--------|------------------|------------------------|------------|
| `quality_ans` | Qualidade documental, scores, regras `dq_*` e tabelas `*_validado` técnicas | Sprint 27 | Interna/API premium apenas após derivação em `api_ans.api_premium_*` quando aplicável |
| `mdm` | MDM público, golden records, crosswalks e exceptions | Sprint 29 | Interna/API premium apenas via `api_ans.api_premium_*` |
| `bruto_cliente` | Entrada privada bruta por tenant para contrato/subfatura | Sprint 30 | Interna, sem grants para cliente legado |
| `stg_cliente` | Staging privada por tenant com cast, limpeza, layout e quarentena | Sprint 30 | Interna, sem grants para cliente legado |
| `mdm_privado` | MDM privado por tenant para contrato/subfatura | Sprint 30 | Interna/premium, com isolamento por tenant |
| `consumo_premium_ans` | Entrega SQL direta premium | Sprint 31 | Cliente premium via `healthintel_premium_reader` |
| `api_ans.api_premium_*` | Modelos de serviço premium | Sprint 31/32 | FastAPI premium |

## Roles Oficiais

| Role | Uso | Grants permitidos |
|------|-----|-------------------|
| `healthintel_cliente_reader` | Cliente legado | Leitura em `consumo_ans` conforme contrato atual. Sem grants em `consumo_premium_ans`, `quality_ans`, `enrichment`, `mdm`, `bruto_cliente`, `stg_cliente` ou `mdm_privado`. |
| `healthintel_premium_reader` | Cliente premium SQL direto | Leitura em `consumo_premium_ans` após hardgate da Sprint 31. |

## Regra de Grants e Revokes

- Grants premium devem ser explícitos e nunca herdados de `healthintel_cliente_reader`.
- `healthintel_cliente_reader` deve receber revokes explícitos em schemas premium e internos da Fase 5.
- `healthintel_premium_reader` não autoriza leitura direta em `api_ans`, `quality_ans`, `enrichment`, `mdm`, `bruto_cliente`, `stg_cliente` ou `mdm_privado` sem decisão formal posterior.
- A FastAPI usa a superfície `api_ans`; endpoints premium devem consultar apenas `api_ans.api_premium_*`.
- `consumo_premium_ans` é produto SQL direto premium, não camada de serviço da API.

## Configuração Futura do dbt_project.yml

A configuração abaixo é obrigatória para implementação futura, mas deve ser aplicada somente na sprint que alterar dbt:

```yaml
models:
  healthintel_dbt:
    staging:
      cliente:
        +schema: stg_cliente
        +materialized: view
        +tags: ["stg_cliente", "mdm_privado"]
    quality:
      +schema: quality_ans
      +materialized: table
      +tags: ["quality"]
    mdm:
      +schema: mdm
      +materialized: table
      +tags: ["mdm"]
    mdm_privado:
      +schema: mdm_privado
      +materialized: table
      +tags: ["mdm_privado"]
    consumo_premium:
      +schema: consumo_premium_ans
      +materialized: table
      +tags: ["consumo_premium"]
    api:
      premium:
        +schema: api_ans
        +materialized: table
        +tags: ["api", "premium"]
```

## Contrato Mínimo de Tabela

Toda tabela nova da Fase 5 deve documentar:

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| Nome físico | Sim | Nome completo com schema e tabela. |
| Responsabilidade | Sim | O que a tabela resolve e o que explicitamente não resolve. |
| Granularidade | Sim | Unidade única da linha. |
| Upstream | Sim | Fontes e modelos usados. |
| Downstream | Sim | Produtos, APIs ou tabelas derivadas. |
| Owner técnico | Sim | Responsável por manutenção técnica. |
| Owner de negócio | Sim | Responsável por regra de negócio e aceite funcional. |
| Classificação LGPD | Sim | Pública, interna, pessoal, sensível ou privada tenant. |
| Regra de publicação | Sim | Condição para expor em SQL direto ou API. |
| Regra de teste | Sim | Testes dbt/API/documentais mínimos. |
| Regra de rollback | Sim | Como remover a publicação sem afetar baseline. |

## Contrato Mínimo de Coluna

Toda coluna nova deve documentar:

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| Nome | Sim | `snake_case`, singular e pt_BR. |
| Tipo esperado | Sim | Tipo dbt/PostgreSQL esperado. |
| Descrição | Sim | Semântica funcional. |
| Obrigatoriedade | Sim | `not_null`, opcional ou derivada. |
| Fonte | Sim | Origem direta ou regra de derivação. |
| Regra de qualidade | Sim | Teste, domínio aceito ou regra de consistência. |
| Classificação LGPD | Sim | Classificação por coluna quando aplicável. |
| Máscara/hash | Condicional | Obrigatório para dado privado/pessoal quando aplicável. |

## Classificação LGPD

| Classe | Regra |
|--------|-------|
| Pública ANS/DATASUS | Dado público de fonte oficial; pode compor produto após curadoria. |
| Interna operacional | Dado técnico de pipeline, score, cache ou auditoria; não é exposto diretamente a cliente. |
| Pessoal | Dado que identifica pessoa natural; não entra em produto público. |
| Sensível | Dado de saúde/pessoa natural; exige justificativa, minimização, auditoria e controles específicos. |
| Privada tenant | Dado enviado por cliente; exige `tenant_id` desde a origem, isolamento e regra de acesso explícita. |

CPF fica fora do produto público. Qualquer uso futuro de CPF só pode ocorrer em fluxo privado/tenant, com hash, máscara, auditoria, justificativa de negócio e aprovação LGPD.

## Regras de Publicação

- Produto legado continua em `consumo_ans`.
- Produto SQL premium deve ser publicado apenas em `consumo_premium_ans`.
- Produto API premium deve ser publicado apenas como `api_ans.api_premium_*`.
- Camadas `quality_ans`, `enrichment`, `mdm`, `bruto_cliente`, `stg_cliente` e `mdm_privado` não são superfícies diretas da FastAPI.
- Toda publicação precisa de documentação, teste, owner técnico, owner de negócio e validação de não regressão contra `v3.0.0`.

## Regras de Teste

- Modelos `dq_*`: testar chave de negócio, score/faixa, nulos críticos e divergências esperadas.
- Modelos `*_validado`: testar unicidade, documentos normalizados e status de validação.
- Modelos `*_enriquecido`: testar fonte de validação, data de consulta/cache e ausência de scraping.
- Modelos `mdm_*_master`: testar unicidade de master key, sobrevivência de atributos e crosswalk.
- Modelos `*_exception`: testar presença de motivo, severidade, fonte e data de detecção.
- Modelos `consumo_premium_*`: testar contrato comercial, granularidade e role premium.
- Modelos `api_premium_*`: testar compatibilidade de resposta e leitura exclusiva pela FastAPI.

## Regras de Rollback

- Rollback da Fase 5 não pode remover nem alterar objetos do baseline `v3.0.0`.
- Novas publicações premium devem poder ser despublicadas por revogação de grants/rotas premium sem impacto em `consumo_ans` ou endpoints existentes.
- Tabelas novas devem ser recriáveis de forma idempotente a partir de upstreams documentados.
- Dados privados devem ter rollback por tenant e preservar trilha de auditoria.

## Regra de Não Regressão contra v3.0.0

- Antes de cada hardgate da Fase 5, comparar alterações contra a tag `v3.0.0`.
- Não alterar modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*` ou `consumo_*` existentes no baseline.
- Não alterar contrato de endpoints existentes.
- Não ampliar grants de `healthintel_cliente_reader` para schemas premium ou internos.
- Não permitir leitura direta de `consumo_premium_ans` pela FastAPI.

## Bootstrap PostgreSQL Futuro

A Fase 5 deve seguir o padrão atual do projeto em `infra/postgres/init/`. A Sprint 26 apenas reserva documentalmente os scripts:

- `infra/postgres/init/026_fase5_quality_enrichment_mdm.sql`
- `infra/postgres/init/027_fase5_premium_roles.sql`
- `infra/postgres/init/028_fase5_mdm_privado_rls.sql`

Nenhum desses arquivos deve ser criado na Sprint 26. A criação física pertence às sprints de implementação correspondentes.
