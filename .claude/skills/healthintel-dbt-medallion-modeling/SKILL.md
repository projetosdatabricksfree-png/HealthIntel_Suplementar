---
name: healthintel-dbt-medallion-modeling
description: Modelagem dbt e arquitetura medalhão — separação de schemas, nomenclatura e regras de exposição.
---

# HealthIntel — dbt e Arquitetura Medalhão

## Quando usar esta skill

- Ao criar/alterar modelos em `healthintel_dbt/models/`.
- Ao definir schema, materialização, post-hooks, tags ou contratos de modelo dbt.
- Ao avaliar de onde a API ou o cliente SQL deve ler.
- Ao revisar nomenclatura de modelos, dimensões, fatos e marts.

## Regras obrigatórias

1. Topologia de schemas (medalhão):
   - `bruto_ans` — **camada bruta/Bronze interna**.
   - `stg_ans` e `int_ans` — **Prata interna** (staging em view; intermediários ephemeral).
   - `nucleo_ans` — **Ouro interno** (dim_*, fat_*, mart_* BI).
   - `api_ans` — **única superfície autorizada para a API** (projeções denormalizadas, indexáveis).
   - `consumo_ans` — **SQL Standard / BI** via role `healthintel_cliente_reader`.
   - `consumo_premium_ans` — **SQL Premium** via role `healthintel_premium_reader`.
2. **A API nunca lê diretamente `bruto_ans`, `stg_ans`, `int_ans` ou `nucleo_ans`.** Sempre via `api_ans`.
3. **Cliente SQL nunca acessa schemas internos.** Apenas `consumo_ans` ou `consumo_premium_ans` conforme contrato.
4. Nomenclatura previsível e obrigatória:
   - `stg_*` em `models/staging/` (view, 1:1 com a fonte, normalização e cast).
   - `int_*` em `models/intermediate/` (ephemeral; join, derivação, preparação).
   - `dim_*` em `models/marts/dimensao/` (table, schema `nucleo_ans`).
   - `fat_*` em `models/marts/fato/` (table/incremental, schema `nucleo_ans`; marts BI `mart_*` também aqui).
   - `api_*` em `models/api/` (com `post_hook: criar_indices(...)`); subdiretórios `bronze/` e `prata/` quando aplicável.
   - `consumo_*` em `models/consumo/` com `tag: consumo`, materializado como `table`, schema `consumo_ans`.
   - `consumo_premium_*` em `models/consumo/` (ou subpasta dedicada) com tag/escopo premium e schema `consumo_premium_ans`.
5. Toda **tabela de consumo** (api_ans, consumo_ans, consumo_premium_ans) precisa de:
   - **contrato** (colunas, tipos, descrição),
   - **teste** (dbt generic test e/ou singular),
   - **documentação** (YAML correspondente).
6. Modelos incrementais reprocessam as últimas 3–4 competências (ANS republica correções). `unique_key` deve ser confiável.
7. Identificadores normalizados: `registro_ans` sempre 6 dígitos via macro `normalizar_registro_ans()`; competência via `competencia_para_data()`.
8. Particionamento: RANGE por competência (mensal) ou trimestre. Sem LIST/HASH.
9. Surrogate keys: fatos referenciam `operadora_id` (FK em `snap_operadora`, SCD2). Não usar `registro_ans` cru como FK.

## Anti-padrões

- Criar endpoint FastAPI lendo `nucleo_ans.*` ou `stg_ans.*` direto.
- Materializar staging como `table` (deve ser `view`).
- Criar `consumo_*` sem teste e sem YAML.
- Usar nomes que não seguem o prefixo (`stg_`, `int_`, `dim_`, `fat_`, `api_`, `consumo_`, `consumo_premium_`).
- Esconder lógica de negócio dentro de view de staging (staging é cast/normalização, não regra).
- Criar mart Ouro em `api_ans` (Ouro mora em `nucleo_ans`; `api_ans` é projeção da Ouro).
- Misturar dados de `consumo_ans` e `consumo_premium_ans` na mesma tabela (a separação é o contrato comercial).
- Apagar/renomear coluna em `api_ans`/`consumo_*` sem ciclo de versionamento e aviso ao consumidor.

## Checklist antes de concluir

- [ ] Modelo está no schema correto para sua camada?
- [ ] Nomenclatura segue o prefixo (`stg_/int_/dim_/fat_/api_/consumo_/consumo_premium_`)?
- [ ] Materialização correta (view para staging, ephemeral para int, table/incremental para marts/api/consumo)?
- [ ] Modelo de API tem `post_hook: criar_indices(...)`?
- [ ] Modelo de consumo tem contrato + teste + YAML?
- [ ] Nenhum endpoint API foi apontado para schema interno?
- [ ] Nenhum acesso de cliente foi apontado para schema interno?
- [ ] Incremental tem `unique_key` confiável e reprocessa janela coerente de competências?
- [ ] `registro_ans` foi normalizado (6 dígitos) onde aparece?

## Exemplo de prompt de uso

> “Vou criar um mart de sinistralidade trimestral por operadora e expor para clientes Premium.
> Aplique a skill `healthintel-dbt-medallion-modeling` e me oriente:
> (1) onde fica o `fat_*` em `nucleo_ans`,
> (2) qual `api_*` em `api_ans` projeta isso para FastAPI,
> (3) qual `consumo_premium_*` em `consumo_premium_ans` é exposto via `healthintel_premium_reader`,
> (4) que testes/contrato mínimos preciso adicionar.”
