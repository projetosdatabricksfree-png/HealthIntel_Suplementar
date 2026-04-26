---
name: healthintel-ans-ingestion-bronze
description: Ingestão de dados ANS (públicos/regulatórios) e disciplina da camada bruta/bronze — preservação de origem, lote e rastreabilidade.
---

# HealthIntel — Ingestão ANS e Camada Bronze

## Quando usar esta skill

- Ao criar/alterar DAGs em `ingestao/dags/dag_ingest_*.py` ou `dag_mestre_mensal.py`/`dag_anual_idss.py`.
- Ao definir/alterar tabelas em `bruto_ans` ou layouts no `mongo_layout_service`.
- Ao trabalhar em `scripts/elt_*.py` (`make elt-discover|extract|load|all|status`).
- Ao tratar reingestão, reprocessamento, quarentena bruta ou versionamento de layout.

## Regras obrigatórias

1. As fontes ANS (CADOP, SIB, IGR, NIP, RN623, IDSS, TISS, CNES, DIOPS, FIP etc.) são **públicas**, mas o valor do produto está em **engenharia, curadoria, contrato e exposição controlada**. Tratar a ingestão como insumo, não como produto final.
2. **Bronze (`bruto_ans`)** preserva origem fiel:
   - dataset, fonte, URL/origem, data de carga, competência (YYYYMM) ou trimestre,
   - identificador de lote (`lote_ingestao` em `plataforma`),
   - hash/checksum quando aplicável,
   - metadados que permitam reconstruir a carga.
3. **Não expor `bruto_ans` diretamente ao cliente.** É camada interna. Endpoints `/v1/bronze` existentes são governados, autenticados, com plano `enterprise_tecnico` e `verificar_camada('bronze')`.
4. **Eventual produto derivado de dados brutos deve sair via `api_ans`** — nunca o cliente comercial puxando direto da bronze.
5. Ingestão deve ser **idempotente** quando aplicável (mesmo arquivo + mesmo lote = mesmo estado final). Reingestão controlada por competência/lote.
6. Registrar sempre: origem, data de carga, competência, hash/checksum (quando o dataset suportar), status do job em `plataforma.job`.
7. **Não quebrar layouts anteriores sem versionamento.** Mudança de layout passa por:
   - registro de nova versão no `mongo_layout_service`,
   - aprovação de layout (ver runbook),
   - compatibilidade ou migração explícita downstream.
8. Arquivos que falham validação semântica vão para `bruto_ans.*_quarentena` com motivo da rejeição, regra violada e lote — **nunca silenciosamente para a tabela servida**.
9. Toda DAG nova precisa de entrada em `healthintel_dbt/models/staging/_sources.yml` com `freshness` (warn após N dias).

## Anti-padrões

- Misturar transformação de negócio dentro da ingestão (ingestão é Bronze, não Prata).
- Sobrescrever `bruto_ans` sem preservar lote/competência anteriores.
- Aceitar arquivo com layout incompatível “porque o cliente está esperando”.
- Carregar dados sem registrar `plataforma.job` / lote / freshness.
- Expor diretamente `bruto_ans` em consulta SQL para cliente comercial.
- Reprocessar competência sem isolar lote (perde rastreabilidade).
- Tratar quarentena como erro — quarentena é **proteção**, parte do contrato do produto.

## Checklist antes de concluir

- [ ] DAG/script registra dataset, lote, competência, data de carga e (se aplicável) hash?
- [ ] `plataforma.job` é atualizado com status (`sucesso`/`falha`) e timestamps?
- [ ] Layout foi validado contra o `mongo_layout_service` antes do load?
- [ ] Nova versão de layout foi versionada (não sobrescrita)?
- [ ] Registros inválidos vão para `*_quarentena` com motivo claro?
- [ ] Entrada em `_sources.yml` com `freshness` foi adicionada/atualizada?
- [ ] A ingestão é idempotente (rerun da mesma competência/lote produz o mesmo estado)?
- [ ] Nenhuma rota direta de cliente para `bruto_ans` foi introduzida?

## Exemplo de prompt de uso

> “Vou adicionar a ingestão real do dataset DIOPS competência 202604.
> Aplique a skill `healthintel-ans-ingestion-bronze` e me oriente:
> (1) o que precisa estar em `_sources.yml`, (2) como registrar o lote em `plataforma`,
> (3) como tratar registros que não batem com o layout no `mongo_layout_service`,
> (4) garantir que nenhum cliente comercial enxergue `bruto_ans.diops_*` direto.”
