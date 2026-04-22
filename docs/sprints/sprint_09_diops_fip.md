# Sprint 09 — DIOPS e FIP

**Status:** Planejada
**Objetivo:** iniciar a fase financeira com ingestao e padronizacao das bases economico-financeiras.
**Criterio de saida:** fatos financeiros basicos ficam disponíveis para analise de operadora.

## Historias

### HIS-09.1 — Ingerir DIOPS

- [ ] Mapear formato vigente do DIOPS.
- [ ] Criar layout registry financeiro.
- [ ] Carregar DIOPS em `bruto_ans`.

### HIS-09.2 — Ingerir FIP

- [ ] Mapear arquivos e periodicidade do FIP.
- [ ] Criar carga bronze para FIP.
- [ ] Criar staging financeiro para FIP.

### HIS-09.3 — Harmonizar fatos financeiros

- [ ] Criar intermediate financeiro canonico.
- [ ] Relacionar fatos financeiros a operadora e competencia.
- [ ] Registrar versionamento de publicacao financeira.

### HIS-09.4 — Validar a fundacao financeira

- [ ] Criar testes dbt de consistencia financeira.
- [ ] Criar smoke tests de ingestao financeira.
- [ ] Validar reprocessamento historico financeiro.
