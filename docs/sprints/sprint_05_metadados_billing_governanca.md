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
