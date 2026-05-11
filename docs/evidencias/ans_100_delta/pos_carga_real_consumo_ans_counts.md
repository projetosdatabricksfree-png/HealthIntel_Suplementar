# Evidência — Contagens consumo_ans

**Timestamp:** 2026-05-11T22:07:46Z  
**Commit:** e665fbf  

## Contagens consumo_ans (11 tabelas)
```
ERROR:  relation "consumo_ans.consumo_produto_plano" does not exist
ERRO: query falhou — nenhuma das 11 tabelas delta existe na VPS
```

## Diagnóstico — tabelas delta ausentes (validação manual)

```sql
-- Executado: select count(*) from information_schema.tables where table_schema = 'consumo_ans';
-- Resultado: 8 tabelas pré-Sprint 41
-- Resultado: 0 tabelas delta (consumo_produto_plano, consumo_tuss_procedimento_vigente, etc.)
```

**Root cause:** Mesma causa das tabelas api_ans — `dbt build --select tag:delta_ans_100` não executado na VPS.

| Tabela | Existe na VPS |
|---|---|
| consumo_produto_plano | ❌ ausente |
| consumo_historico_plano | ❌ ausente |
| consumo_plano_servico_opcional | ❌ ausente |
| consumo_tuss_procedimento_vigente | ❌ ausente |
| consumo_tiss_utilizacao_operadora_mes | ❌ ausente |
| consumo_sip_assistencial_operadora | ❌ ausente |
| consumo_ressarcimento_sus_operadora | ❌ ausente |
| consumo_precificacao_plano | ❌ ausente |
| consumo_rede_acreditacao | ❌ ausente |
| consumo_regulatorio_complementar_operadora | ❌ ausente |
| consumo_beneficiarios_cobertura_municipio | ❌ ausente |

