# consumo_score_operadora_mes

| Campo | Valor |
|---|---|
| Proposito | Score mensal por operadora. |
| Caso de uso | Ranking externo e comparacao de operadoras. |
| Grao | `registro_ans`, `competencia`. |
| Chaves primarias | `registro_ans`, `competencia`. |
| Chaves de negocio | `registro_ans`. |
| Metricas disponiveis | `score_total`, `faixa_score`, componentes do score. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| score_total | numeric | Score final | `mart_score_operadora` | 0-100 |

```sql
select * from consumo_ans.consumo_score_operadora_mes where score_total >= 80;
```
