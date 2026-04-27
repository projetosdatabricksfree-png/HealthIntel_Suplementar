# Template de Documentação de Relacionamento

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar relacionamentos entre tabelas.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `origem` | Tabela origem | `api_ans.api_premium_contrato_validado` |
| `destino` | Tabela destino | `mdm_privado.mdm_contrato_master` |
| `tipo` | `fk_fisica`, `fk_logica`, `xref` | `fk_logica` |
| `colunas` | Colunas de join | `contrato_master_id` |
| `cardinalidade` | `1:1`, `1:N`, `N:M` | `1:1` |
| `obrigatorio` | `sim` ou `nao` | `sim` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `deprecated` | `ativo` |