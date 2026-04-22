# Sprint 11 — Rede Assistencial

**Status:** Planejada
**Objetivo:** iniciar a camada de inteligencia de cobertura e rede assistencial.
**Criterio de saida:** dados de rede assistencial ficam harmonizados por geografia e operadora.

## Historias

### HIS-11.1 — Ingerir rede assistencial

- [ ] Mapear painel e fontes de rede assistencial.
- [ ] Criar contratos de coleta e versionamento.
- [ ] Carregar dados de rede em bronze.

### HIS-11.2 — Harmonizar cobertura geografica

- [ ] Criar staging de rede por municipio e UF.
- [ ] Relacionar rede a operadora e segmento.
- [ ] Criar dimensoes geograficas de apoio.

### HIS-11.3 — Publicar fatos de rede

- [ ] Criar mart de cobertura assistencial.
- [ ] Criar mart de densidade de rede.
- [ ] Expor dataset versionado para API.

### HIS-11.4 — Validar qualidade de rede

- [ ] Criar testes de integridade geografica.
- [ ] Validar consistencia temporal das publicacoes.
- [ ] Criar alertas de atraso ou quebra de fonte.
