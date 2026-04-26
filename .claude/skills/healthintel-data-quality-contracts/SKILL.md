---
name: healthintel-data-quality-contracts
description: Qualidade de dados, contratos de tabela, testes dbt e validações regulatórias mínimas para o produto DaaS.
---

# HealthIntel — Qualidade de Dados e Contratos

## Quando usar esta skill

- Ao criar/alterar tabela em `api_ans`, `consumo_ans`, `consumo_premium_ans` ou marts de `nucleo_ans`.
- Ao escrever/atualizar YAML de documentação dbt (`_*.yml`).
- Ao criar testes em `healthintel_dbt/tests/` (genéricos ou singulares `assert_*.sql`).
- Ao tratar dados ausentes, inválidos, fora de domínio ou em quarentena.

## Regras obrigatórias

1. **Toda tabela exposta** (api_ans, consumo_ans, consumo_premium_ans) precisa de **testes mínimos**:
   - chave única (`unique` ou combinação via teste singular),
   - `not_null` em colunas-chave (ex.: `competencia`, `operadora_id`/`registro_ans`),
   - `relationships` para FKs (ex.: `operadora_id` → `dim_operadora_atual.operadora_id`),
   - `accepted_values` em colunas categóricas conhecidas (modalidade, UF, status, rating).
2. **Toda coluna importante** precisa de descrição **técnica** (origem, tipo, regra de cálculo) **e de negócio** (o que significa para o cliente). Sem isso, não publica.
3. Validações regulatórias quando aplicável:
   - **Registro ANS**: 6 dígitos com leading zeros (macro `normalizar_registro_ans`).
   - **CNPJ**: 14 dígitos, validação de dígito verificador.
   - **CPF**: 11 dígitos, validação de dígito verificador (apenas se houver caso de uso real — evitar PII desnecessária).
   - **CNES**: 7 dígitos.
   - **Competência**: formato YYYYMM, mês válido (01–12).
4. **Separar quatro situações** — nunca colapsar em um único `NULL` opaco:
   - **erro técnico** (falha de pipeline, sem dado por incidente),
   - **dado ausente** (fonte não publicou para aquela competência),
   - **dado inválido** (não passou na validação semântica → quarentena),
   - **dado não aplicável** (a regra de negócio diz que aquela coluna não se aplica àquele registro).
5. Criar/atualizar **YAML de documentação** sempre que criar ou alterar modelo. Sem YAML coerente, o modelo não está “pronto”.
6. **Não publicar tabela de consumo sem contrato mínimo**: schema declarado, descrições, testes, materialização, refresh policy.
7. Usar a infraestrutura existente: hash bronze, taxa de aprovação por dataset (`taxa_aprovacao_dataset`), envelope `qualidade.taxa_aprovacao` na Prata, quarentena semântica.
8. Quando um teste falhar, o caminho é **investigar a fonte e isolar o registro** (quarentena, ajuste de regra documentado), nunca relaxar o teste para o pipeline “passar”.

## Anti-padrões

- Adicionar coluna em tabela de consumo e não documentar no YAML.
- Marcar `not_null` que “quebra com frequência” como warning silencioso para o pipeline rodar.
- Tratar registro inválido como `NULL` em coluna no consumo, sem rastro em quarentena.
- Reutilizar `relationships` apontando para dimensão que não existe ou que ainda é staging.
- Confundir “linha não veio” com “valor é zero” em métricas (zera silenciosamente uma operadora real).
- Publicar `consumo_*` sem teste, “porque é só uma vista”.
- Validar CNPJ/CPF sem necessidade real (evitar manipular PII fora do propósito).
- Aceitar “está no Excel do parceiro” como contrato — contrato é YAML + teste no repositório.

## Checklist antes de concluir

- [ ] Tabela tem chave única declarada e testada?
- [ ] Colunas-chave têm `not_null`?
- [ ] FKs estão cobertas por `relationships`?
- [ ] Colunas categóricas têm `accepted_values` quando aplicável?
- [ ] YAML descreve cada coluna em termos técnicos **e** de negócio?
- [ ] Identificadores regulatórios estão normalizados/validados?
- [ ] Os quatro estados (erro técnico / ausente / inválido / não aplicável) estão tratados de forma distinta?
- [ ] Quarentena registra motivo, regra violada e lote?
- [ ] Nenhum teste foi rebaixado/silenciado para “passar o build”?

## Exemplo de prompt de uso

> “Vou expor `consumo_ans.consumo_score_operadora_mensal`.
> Aplique a skill `healthintel-data-quality-contracts` e me liste:
> (1) chave única e granularidade,
> (2) testes dbt mínimos (`unique`, `not_null`, `relationships`, `accepted_values`),
> (3) campos que precisam de descrição técnica e de negócio,
> (4) como tratar competências sem publicação ANS vs. operadora sem dado vs. dado em quarentena.”
