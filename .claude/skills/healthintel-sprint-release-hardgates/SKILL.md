---
name: healthintel-sprint-release-hardgates
description: Disciplina de sprints, releases, baseline, tags e hardgates — proteção contra reabertura indevida e marcação prematura de conclusão.
---

# HealthIntel — Sprints, Releases, Baseline e Hardgates

## Quando usar esta skill

- Ao planejar, abrir, atualizar ou fechar uma sprint em `docs/sprints/fase{N}/`.
- Ao marcar tarefas como `[x]` em qualquer documento de sprint, story, baseline ou roadmap.
- Ao mexer em arquivos de baseline, hardgate, release notes ou tags (`baseline_*.md`, `hardgate_*.md`, `release_*.md`).
- Ao avaliar se uma fase pode ser declarada concluída.

## Regras obrigatórias

1. **Sprint antiga concluída não deve ser reaberta** sem justificativa explícita registrada (motivo, escopo do reabrir, impacto em baseline e tag).
2. **Novas fases são aditivas.** Fase 5 não “refaz” Fase 4; Fase 4 está taggeada como v3.0.0 e isso não pode ser sobrescrito.
3. `[x]` só é permitido quando a tarefa está **implementada, testada e validada** — com evidência objetiva (commit/SHA, arquivo, teste passando, comando executado).
4. Antes de fechar sprint, validar:
   - tag (ex.: `v1.0.0`, `v2.0.0`, `v3.0.0`),
   - SHA do commit de fechamento,
   - diff resumido,
   - hardgates definidos para aquela sprint/fase.
5. Toda modificação em sprint deve listar:
   - arquivos alterados,
   - pendências remanescentes,
   - comandos executados (lint, test, dbt build, smoke, etc.).
6. **Baseline aprovado não deve ser quebrado.** Se for tecnicamente necessário quebrar, abrir nota explícita (não silenciosa) e propor ao usuário antes de aplicar.
7. Sprint em roadmap (Fase 5 hoje) **não pode ser apresentada como concluída** — mesmo que o código pareça pronto.

## Anti-padrões

- Marcar `[x]` em tarefa só porque “parece feito” ou “provavelmente está feito”.
- Reabrir sprint antiga para “arrumar uma coisinha” sem registrar motivo, escopo e impacto.
- Editar `baseline_*.md` ou release notes sem associar a tag/SHA correspondente.
- Misturar entrega de sprint nova com correções silenciosas de sprint antiga taggeada.
- Apagar/renomear pendências para fingir que sprint terminou limpa.
- Declarar fase concluída sem hardgates verificados.

## Checklist antes de concluir

- [ ] Toda tarefa marcada `[x]` tem evidência (commit, arquivo, teste, comando)?
- [ ] Foi feita distinção entre “implementado”, “testado” e “validado em ambiente”?
- [ ] Tag e SHA estão registrados quando aplicável?
- [ ] Hardgates da sprint foram explicitamente verificados?
- [ ] Baseline anterior não foi alterado de forma silenciosa?
- [ ] Pendências foram listadas no documento da sprint, não escondidas?
- [ ] Nenhuma sprint do roadmap (Fase 5) foi marcada como concluída sem entrega real?

## Exemplo de prompt de uso

> “Vou atualizar `docs/sprints/fase5/sprint_26.md` e marcar 4 itens como `[x]`.
> Aplique a skill `healthintel-sprint-release-hardgates`, verifique se há evidência objetiva (commit, teste, arquivo) para cada item, valide hardgates pendentes e me diga quais itens **não** podem ser marcados ainda.”
