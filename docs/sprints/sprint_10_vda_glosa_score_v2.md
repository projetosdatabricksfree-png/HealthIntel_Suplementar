# Sprint 10 — VDA, Glosa e Score v2

**Status:** Planejada
**Objetivo:** ampliar a camada financeira com VDA, glosa e score composto de segunda geracao.
**Criterio de saida:** produto passa a oferecer inteligencia financeira mais profunda por operadora.

## Historias

### HIS-10.1 — Ingerir VDA

- [ ] Mapear origem oficial e formato operacional de VDA.
- [ ] Criar carga bronze de VDA.
- [ ] Criar staging e mart de VDA.

### HIS-10.2 — Ingerir glosa

- [ ] Mapear dataset e granularidade de glosa.
- [ ] Criar parsing e carga em bronze.
- [ ] Criar fato consolidado de glosa.

### HIS-10.3 — Calcular score v2

- [ ] Unificar score core, regulatorio e financeiro.
- [ ] Definir pesos versionados do score v2.
- [ ] Publicar fato mensal do score v2.

### HIS-10.4 — Atualizar a API

- [ ] Criar endpoints financeiros e score v2.
- [ ] Atualizar contratos de resposta e metadados.
- [ ] Executar regressao sobre endpoints existentes.
