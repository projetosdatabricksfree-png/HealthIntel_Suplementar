# Sprint 02 — Layout Registry e Bronze

**Status:** Concluida
**Objetivo:** operacionalizar o registry de layout em `MongoDB` e preparar a ingestao deterministica para bronze.
**Criterio de saida:** layouts, versoes, aliases e validacoes estruturais ficam persistidos com rastreabilidade.

## Historias

### HIS-02.1 — Persistir o cadastro de datasets e layouts

- [x] Criar repositorio Mongo real em `mongo_layout_service/app/repositories/layout_repository.py`.
- [x] Criar colecoes `fonte_dataset`, `layout`, `layout_versao`, `layout_alias`, `layout_execucao` e `evento_layout`.
- [x] Criar indices para busca operacional e unicidade de layout.

### HIS-02.2 — Implementar o servico administrativo de layout

- [x] Implementar `mongo_layout_service/app/services/layout_service.py` com CRUD de layout, versao e alias.
- [x] Implementar rotas administrativas em `mongo_layout_service/app/routers/layout.py`.
- [x] Integrar a API publica administrativa com proxy HTTP em `api/app/services/layout_admin.py`.

### HIS-02.3 — Selecionar layout por regra deterministica

- [x] Implementar assinatura estrutural baseada em colunas detectadas.
- [x] Implementar validacao sem heuristica semantica.
- [x] Implementar resolucao de aliases manuais por layout e versao.

### HIS-02.4 — Registrar execucao e incompatibilidade estrutural

- [x] Persistir execucoes de validacao em `layout_execucao`.
- [x] Expor consulta de layouts incompativeis.
- [x] Persistir quarentena operacional em tabelas relacionais de `plataforma`.

### HIS-02.5 — Integrar a ingestao bronze ao registry

- [x] Conectar `ingestao/app/identificar_layout.py` ao servico real de layout.
- [x] Conectar `ingestao/app/aplicar_alias.py` ao layout resolvido por versao.
- [x] Implementar carga efetiva de `CADOP` em `bruto_ans`.
- [x] Implementar carga efetiva de `SIB por operadora` em `bruto_ans`.
- [x] Implementar carga efetiva de `SIB por municipio` em `bruto_ans`.
