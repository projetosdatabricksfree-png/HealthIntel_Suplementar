# Sprint 26 — Baseline, Congelamento e Mapa de Expansão

**Status:** Concluída documentalmente
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.1.0-baseline`
**Objetivo:** congelar tudo o que já passou no hardgate da Fase 4 e mapear, com precisão, o que será adicionado na Fase 5.
**Fim esperado:** documento de expansão com tudo que será novo, sem tocar no legado aprovado.
**Critério de saída:** `docs/sprints/fase5/baseline_hardgate_fase4.md`, `docs/sprints/fase5/matriz_lacunas_produto.md`, `docs/sprints/fase5/padrao_nomes_fase5.md` e `docs/sprints/fase5/governanca_minima_fase5.md` publicados; lista completa de modelos congelados; padrão de nomes, schemas, roles premium e configuração dbt documentados e referenciados pelas Sprints 27–32.

## Regra-mãe da Fase 5 (vale para esta sprint e todas as seguintes)

- [x] Não alterar a lógica aprovada das Fases 1 a 4.
- [x] Não renomear tabelas existentes.
- [x] Não substituir `stg_*`, `int_*`, `fat_*`, `api_*` ou `consumo_*` já aprovadas.
- [x] Criar apenas tabelas novas, com sufixos: `_validado`, `_qualificado`, `_mdm`, `_golden`, `_exception`, `_premium`.
- [x] Usar os modelos existentes como fonte.
- [ ] Publicar novos produtos de consumo apenas depois de passarem em testes próprios.
- [x] Manter os endpoints atuais funcionando sem mudança de contrato.
- [ ] Criar endpoints novos para dados validados/enriquecidos.
- [x] Garantir que a FastAPI continue consultando apenas `api_ans`; endpoints premium devem ler `api_ans.api_premium_*`, nunca `consumo_premium_ans` diretamente.

## Histórias

### HIS-06.1 — Congelar a base aprovada

- [x] Criar `docs/sprints/fase5/baseline_hardgate_fase4.md`.
- [x] Registrar que os modelos atuais de `staging`, `intermediate`, `marts`, `api` e `consumo` são baseline aprovado e imutáveis na Fase 5.
- [x] Listar todos os modelos `consumo_*` existentes no baseline `v3.0.0` do repositório.
- [x] Listar todos os modelos existentes da camada `api_ans` (Bronze, Prata e Gold) que ainda podem virar consumo premium.
- [x] Listar os fatos/marts existentes (`fat_*`, `mart_*`) que serão usados como fonte para novos produtos premium.
- [x] Registrar regra: nenhum modelo existente pode ser reescrito, renomeado ou alterado em sua semântica na Fase 5.
- [x] Registrar regra: toda melhoria deve entrar como modelo novo, com nome distinto.
- [x] Anexar referência cruzada para a tag git `v3.0.0` como ponto de congelamento.

### HIS-06.2 — Criar matriz de lacunas comerciais

- [x] Criar `docs/sprints/fase5/matriz_lacunas_produto.md`.
- [x] Marcar o que já está pronto para consumo (consumo_ans atual).
- [x] Marcar o que está apenas em staging.
- [x] Marcar o que está em fato/mart, mas ainda não é exposto a clientes.
- [x] Marcar o que está em API, mas ainda não está em consumo.
- [x] Marcar o que exige validação de documento (CPF, CNPJ, CNES, registro_ans).
- [x] Marcar o que exige MDM (operadora, prestador, estabelecimento, contrato, subfatura).
- [x] Marcar o que exige contrato/subfatura (módulo privado por tenant).
- [x] Marcar o que exige enriquecimento externo (Serpro para CNPJ, TUSS).
- [x] Cruzar cada lacuna com a Sprint que vai resolvê-la (27, 28, 29, 30, 31 ou 32).

### HIS-06.3 — Definir padrão de nomes para novas tabelas

- [x] Criar `docs/sprints/fase5/padrao_nomes_fase5.md`.
- [x] Documentar padrão `*_validado` para tabelas com validação técnica.
- [x] Documentar padrão `*_enriquecido` para tabelas com dados externos.
- [x] Documentar padrão `*_mdm` para tabelas com golden record.
- [x] Documentar padrão `*_exception` para inconsistências.
- [x] Documentar padrão `consumo_premium_*` para produtos comerciais novos no schema `consumo_premium_ans`.
- [x] Documentar padrão `api_premium_*` para modelos de serviço premium no schema `api_ans`.
- [x] Documentar padrão `dq_*` para Data Quality.
- [x] Documentar padrão `xref_*` para tabelas de relacionamento/crosswalk.
- [x] Documentar padrão `mdm_*` para entidades master.
- [x] Garantir que nenhum dos padrões colide com nomes já existentes em `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans`, `api_ans` ou `consumo_ans`.
- [x] Documentar que `consumo_ans` e `healthintel_cliente_reader` ficam reservados a clientes legados.
- [x] Documentar que `consumo_premium_ans` e `healthintel_premium_reader` ficam reservados a clientes premium.
- [x] Documentar que modelos `api_premium_*` são a única superfície permitida para FastAPI premium.

### HIS-06.4 — Definir governança mínima e configuração física da Fase 5

- [x] Criar `docs/sprints/fase5/governanca_minima_fase5.md`.
- [x] Definir padrões mínimos de schema, nomenclatura, template de tabela, template de coluna, classificação LGPD e owner técnico/de negócio antes da criação de qualquer modelo da Fase 5.
- [x] Definir que novas tabelas devem ter contrato mínimo: responsabilidade, granularidade, upstream, downstream, owner, sensibilidade LGPD, regra de publicação e validação.
- [x] Definir a configuração obrigatória do `healthintel_dbt/dbt_project.yml` para novos diretórios:

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
    enrichment:
      +schema: enrichment
      +materialized: table
      +tags: ["enrichment"]
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

- [x] Definir que a Fase 5 seguirá o padrão atual de bootstrap PostgreSQL em `infra/postgres/init/`, sem criar um diretório paralelo de migrations enquanto não houver sistema oficial para isso.
- [x] Reservar os scripts `infra/postgres/init/026_fase5_quality_enrichment_mdm.sql`, `infra/postgres/init/027_fase5_premium_roles.sql` e `infra/postgres/init/028_fase5_mdm_privado_rls.sql`.
- [x] Definir que `027_fase5_premium_roles.sql` cria `consumo_premium_ans`, `healthintel_premium_reader`, grants premium e revokes explícitos para `healthintel_cliente_reader`.

## Entregas esperadas

- [x] `docs/sprints/fase5/baseline_hardgate_fase4.md`
- [x] `docs/sprints/fase5/matriz_lacunas_produto.md`
- [x] `docs/sprints/fase5/padrao_nomes_fase5.md`
- [x] `docs/sprints/fase5/governanca_minima_fase5.md`
- [x] `docs/sprints/fase5/README.md` introduzindo a Fase 5 e listando as Sprints 26–32 + 33

## Validação esperada (hard gates)

- [x] Baseline aprovado lista 100% dos modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*` existentes na tag `v3.0.0`.
- [x] Matriz de lacunas vincula cada lacuna a uma sprint da Fase 5.
- [x] Padrão de nomes não colide com nomes já existentes (verificação documental).
- [x] Governança mínima da Sprint 26 define schemas, roles, padrões de tabela/coluna, classificação LGPD e owners antes da execução das Sprints 27–32.
- [x] Nenhum arquivo SQL, YAML, Python ou de configuração fora de `docs/sprints/fase5/` é alterado nesta sprint.

## Resultado Esperado

Sprint 26 entrega o ponto-zero da Fase 5: o time tem um inventário formal do que já está congelado, um mapa do que precisa ser adicionado, um vocabulário (sufixos `_validado`, `_mdm`, `_premium`, etc.) e a governança mínima que será usada uniformemente nas Sprints 27 a 32. Nenhum modelo da Fase 1–4 sofre alteração; a Fase 5 nasce 100% aditiva.
