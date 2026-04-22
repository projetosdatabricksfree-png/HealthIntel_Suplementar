# Sprint 05 — Metadados, Billing e Governanca

**Status:** Concluida
**Objetivo:** consolidar metadados operacionais, catalogo de datasets e base de billing.
**Criterio de saida:** uso, versoes e entidades comerciais ficam rastreaveis de ponta a ponta.

## Historias

### HIS-05.1 — Modelar a camada comercial

- [x] Criar `plataforma.cliente`.
- [x] Criar `plataforma.plano`.
- [x] Criar `plataforma.chave_api`.

### HIS-05.2 — Registrar uso e consumo

- [x] Criar `plataforma.log_uso`.
- [x] Persistir consumo por request autenticado.
- [x] Associar consumo ao plano contratado.

### HIS-05.3 — Controlar versao de dataset e jobs

- [x] Criar `plataforma.versao_dataset`.
- [x] Criar `plataforma.job`.
- [x] Emitir metadados de pipeline para consulta.

### HIS-05.4 — Expor catalogo operacional

- [x] Implementar endpoint de catalogo de datasets.
- [x] Implementar endpoint de versao publicada.
- [x] Implementar endpoint de status de pipeline.

### HIS-05.5 — Estruturar billing base

- [x] Definir regra de faturamento por consumo.
- [x] Fechar estrategia de upgrade de plano.
- [x] Criar trilha minima de auditoria para cobranca.

## Entregas implementadas

- [x] Criar `plataforma.ciclo_faturamento`.
- [x] Criar `plataforma.fatura_consumo`.
- [x] Criar `plataforma.historico_plano`.
- [x] Criar `plataforma.auditoria_cobranca`.
- [x] Implementar `POST /admin/billing/fechar-ciclo`.
- [x] Implementar `GET /admin/billing/resumo`.
- [x] Implementar `POST /admin/billing/upgrade`.
- [x] Implementar script operacional `scripts/fechar_ciclo_billing.py`.
- [x] Registrar `job` operacional de fechamento de billing.

### HIS-05.6 — Contratos de meta endpoints e padronizacao de erros

- [ ] Implementar endpoint `GET /v1/meta/pipeline` retornando status dos jobs recentes de `plataforma.job` com campos `dag_id`, `status`, `iniciado_em`, `finalizado_em`, `dataset` (PRD secao 9.3 Grupo Meta).
- [ ] Padronizar respostas de erro 401, 403 e 429 com corpo JSON `{codigo, mensagem, detalhe}` em todos os middlewares — garantir que `autenticacao.py` e `rate_limit.py` retornam este envelope (PRD secao 9.3 Respostas de Erro).
- [ ] Garantir que `plataforma.versao_dataset` registra campo `hash_sha256` para cada dataset com hash do arquivo de origem, permitindo auditoria de integridade.
