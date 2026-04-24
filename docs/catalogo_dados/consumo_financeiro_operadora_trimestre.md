# consumo_financeiro_operadora_trimestre

| Campo | Valor |
|---|---|
| Proposito | Financeiro trimestral por operadora. |
| Caso de uso | Analise de resultado, receita e sinistralidade. |
| Grao | `registro_ans`, `trimestre`. |
| Chaves primarias | `registro_ans`, `trimestre`. |
| Chaves de negocio | `registro_ans`. |
| Metricas disponiveis | `receita_total`, `sinistralidade_pct`, `resultado_operacional`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| receita_total | numeric | Receita total | `fat_financeiro_operadora_trimestral` | BRL |

```sql
select * from consumo_ans.consumo_financeiro_operadora_trimestre where trimestre = '2025T1';
```
