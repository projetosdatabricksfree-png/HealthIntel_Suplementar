# Padrão de Nomes — Fase 5

Este documento define nomes permitidos para novos artefatos da Fase 5. O padrão é obrigatório para evitar colisão com o baseline `v3.0.0` e manter separação entre produtos legados, premium SQL direto e superfície da FastAPI.

## Regras Gerais

- Usar `snake_case`, singular e pt_BR.
- Não renomear modelos existentes do baseline `v3.0.0`.
- Não criar nomes que pareçam substituir `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*` ou `consumo_*` existentes.
- Todo nome novo deve indicar camada, responsabilidade e tipo de entrega.
- A FastAPI premium deve ler apenas `api_ans.api_premium_*`.

## Prefixos e Sufixos Obrigatórios

| Padrão | Uso | Schema esperado | Exemplo válido |
|--------|-----|-----------------|----------------|
| `dq_*` | Resultado de qualidade documental ou regra de data quality | `quality_ans` | `dq_operadora_documento` |
| `*_validado` | Tabela com validação técnica aplicada | `quality_ans`, `consumo_premium_ans` ou `api_ans` conforme superfície | `cnes_estabelecimento_validado` |
| `*_enriquecido` | Tabela com dado externo controlado/cacheado | `enrichment` | `operadora_cnpj_enriquecido` |
| `mdm_*_master` | Golden record de entidade master | `mdm` ou `mdm_privado` | `mdm_operadora_master` |
| `xref_*_origem` | Crosswalk entre identificadores de origem e entidade master | `mdm` ou `mdm_privado` | `xref_operadora_origem` |
| `*_exception` | Divergência, inconsistência ou conflito de resolução MDM | `mdm`, `mdm_privado` ou `quality_ans` | `mdm_operadora_exception` |
| `consumo_premium_*` | Produto SQL direto premium | `consumo_premium_ans` | `consumo_premium_operadora_360_validado` |
| `api_premium_*` | Modelo de serviço premium consumido pela FastAPI | `api_ans` | `api_premium_operadora_360_validado` |
| `stg_cliente_*` | Staging privada por tenant | `stg_cliente` | `stg_cliente_contrato` |
| `mdm_privado.*` | MDM privado com isolamento por tenant | `mdm_privado` | `mdm_privado.mdm_contrato_master` |

## Exemplos Válidos

| Nome | Motivo |
|------|--------|
| `dq_cnpj_operadora` | Prefixo de qualidade, domínio explícito e sem colisão com baseline. |
| `operadora_cnpj_enriquecido` | Enriquecimento externo controlado para operadora. |
| `mdm_operadora_master` | Golden record público de operadora. |
| `xref_estabelecimento_origem` | Crosswalk de estabelecimento para fontes públicas. |
| `mdm_estabelecimento_exception` | Tabela de divergências do MDM público. |
| `consumo_premium_contrato_validado` | Entrega SQL premium em schema premium. |
| `api_premium_contrato_validado` | Modelo de serviço para rota premium da FastAPI. |
| `stg_cliente_subfatura` | Staging privada por tenant antes do MDM privado. |
| `mdm_privado.mdm_subfatura_master` | Master data privado no schema correto. |

## Exemplos Proibidos

| Nome proibido | Motivo |
|---------------|--------|
| `consumo_operadora_360_v2` | Parece substituir produto legado em `consumo_ans`. Use `consumo_premium_operadora_360_validado`. |
| `api_operadora_premium` | Mistura padrão legado `api_*` com premium. Use `api_premium_operadora_360_validado`. |
| `stg_contrato` | Sugere staging pública ou genérica. Use `stg_cliente_contrato`. |
| `int_operadora_mdm` | Cria MDM dentro da camada intermediate. Use `mdm_operadora_master`. |
| `fat_contrato` | Contrato privado não pertence ao mart público do baseline. Use `mdm_privado.mdm_contrato_master` ou produto premium explícito. |
| `operadora_gold` | Sufixo genérico e sem contrato de camada. Use `mdm_operadora_master` ou `consumo_premium_operadora_360_validado`. |
| `tabela_premium` | Nome sem domínio, sem camada e sem responsabilidade. |
| `api_premium_from_consumo_premium` | Nome expõe implementação indevida e sugere leitura direta proibida. |

## Separação Legado, Premium e API

- `consumo_ans` e `healthintel_cliente_reader` ficam reservados a clientes legados.
- `consumo_premium_ans` e `healthintel_premium_reader` ficam reservados a clientes premium.
- `consumo_premium_*` é entrega SQL direta premium.
- `api_premium_*` é a única superfície permitida para FastAPI premium.
- A FastAPI nunca consulta `consumo_premium_ans` diretamente.

## Colisão com Baseline

Antes de criar qualquer modelo da Fase 5, validar documentalmente contra a tag `v3.0.0`:

```bash
git ls-tree -r --name-only v3.0.0 -- healthintel_dbt/models
```

Nenhum nome novo pode repetir o nome lógico de modelo existente nem criar variação que pareça alterar a semântica aprovada das Fases 1 a 4.
