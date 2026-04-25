# Sprint 26 — Baseline, Congelamento e Mapa de Expansão

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.1.0-baseline`
**Objetivo:** congelar tudo o que já passou no hardgate da Fase 4 e mapear, com precisão, o que será adicionado na Fase 5.
**Fim esperado:** documento de expansão com tudo que será novo, sem tocar no legado aprovado.
**Critério de saída:** `docs/fase5/baseline_hardgate_fase4.md`, `docs/fase5/matriz_lacunas_produto.md` e `docs/fase5/padrao_nomes_fase5.md` publicados; lista completa de modelos congelados; padrão de nomes documentado e referenciado pelas Sprints 27–32.

## Regra-mãe da Fase 5 (vale para esta sprint e todas as seguintes)

- [ ] Não alterar a lógica aprovada das Fases 1 a 4.
- [ ] Não renomear tabelas existentes.
- [ ] Não substituir `stg_*`, `int_*`, `fat_*`, `api_*` ou `consumo_*` já aprovadas.
- [ ] Criar apenas tabelas novas, com sufixos: `_validado`, `_qualificado`, `_mdm`, `_golden`, `_exception`, `_premium`.
- [ ] Usar os modelos existentes como fonte.
- [ ] Publicar novos produtos de consumo apenas depois de passarem em testes próprios.
- [ ] Manter os endpoints atuais funcionando sem mudança de contrato.
- [ ] Criar endpoints novos para dados validados/enriquecidos.

## Histórias

### HIS-06.1 — Congelar a base aprovada

- [ ] Criar `docs/fase5/baseline_hardgate_fase4.md`.
- [ ] Registrar que os modelos atuais de `staging`, `intermediate`, `marts`, `api` e `consumo` são baseline aprovado e imutáveis na Fase 5.
- [ ] Listar todos os modelos existentes da camada `consumo_ans` (8 modelos da Sprint 24).
- [ ] Listar todos os modelos existentes da camada `api_ans` (Bronze, Prata e Gold) que ainda podem virar consumo premium.
- [ ] Listar os fatos/marts existentes (`fat_*`, `mart_*`) que serão usados como fonte para novos produtos premium.
- [ ] Registrar regra: nenhum modelo existente pode ser reescrito, renomeado ou alterado em sua semântica na Fase 5.
- [ ] Registrar regra: toda melhoria deve entrar como modelo novo, com nome distinto.
- [x] Anexar referência cruzada para a tag git `v3.0.0` como ponto de congelamento.

### HIS-06.2 — Criar matriz de lacunas comerciais

- [ ] Criar `docs/fase5/matriz_lacunas_produto.md`.
- [ ] Marcar o que já está pronto para consumo (consumo_ans atual).
- [ ] Marcar o que está apenas em staging.
- [ ] Marcar o que está em fato/mart, mas ainda não é exposto a clientes.
- [ ] Marcar o que está em API, mas ainda não está em consumo.
- [ ] Marcar o que exige validação de documento (CPF, CNPJ, CNES, registro_ans).
- [ ] Marcar o que exige MDM (operadora, prestador, estabelecimento, contrato, subfatura).
- [ ] Marcar o que exige contrato/subfatura (módulo privado por tenant).
- [ ] Marcar o que exige enriquecimento externo (Receita/Serpro, TUSS).
- [ ] Cruzar cada lacuna com a Sprint que vai resolvê-la (27, 28, 29, 30, 31 ou 32).

### HIS-06.3 — Definir padrão de nomes para novas tabelas

- [ ] Criar `docs/fase5/padrao_nomes_fase5.md`.
- [ ] Documentar padrão `*_validado` para tabelas com validação técnica.
- [ ] Documentar padrão `*_enriquecido` para tabelas com dados externos.
- [ ] Documentar padrão `*_mdm` para tabelas com golden record.
- [ ] Documentar padrão `*_exception` para inconsistências.
- [ ] Documentar padrão `consumo_premium_*` para produtos comerciais novos.
- [ ] Documentar padrão `dq_*` para Data Quality.
- [ ] Documentar padrão `xref_*` para tabelas de relacionamento/crosswalk.
- [ ] Documentar padrão `mdm_*` para entidades master.
- [ ] Garantir que nenhum dos padrões colide com nomes já existentes em `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans`, `api_ans` ou `consumo_ans`.

## Entregas esperadas

- [ ] `docs/fase5/baseline_hardgate_fase4.md`
- [ ] `docs/fase5/matriz_lacunas_produto.md`
- [ ] `docs/fase5/padrao_nomes_fase5.md`
- [ ] `docs/fase5/README.md` introduzindo a Fase 5 e listando as Sprints 26–32 + 33

## Validação esperada (hard gates)

- [x] Baseline aprovado lista 100% dos modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*` existentes na tag `v3.0.0`.
- [ ] Matriz de lacunas vincula cada lacuna a uma sprint da Fase 5.
- [ ] Padrão de nomes não colide com nomes já existentes (verificação documental).
- [ ] Nenhum arquivo SQL, YAML, Python ou de configuração fora de `docs/fase5/` é alterado nesta sprint.

## Resultado Esperado

Sprint 26 entrega o ponto-zero da Fase 5: o time tem um inventário formal do que já está congelado, um mapa do que precisa ser adicionado e um vocabulário (sufixos `_validado`, `_mdm`, `_premium`, etc.) que será usado uniformemente nas Sprints 27 a 32. Nenhum modelo da Fase 1–4 sofre alteração; a Fase 5 nasce 100% aditiva.
