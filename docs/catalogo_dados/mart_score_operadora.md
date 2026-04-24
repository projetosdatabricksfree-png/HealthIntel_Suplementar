# mart_score_operadora

| Campo | Valor |
|---|---|
| Proposito | Score mensal da operadora e componentes. |
| Caso de uso | Ranking, comparacao e priorizacao comercial. |
| Grao | Uma linha por `registro_ans`, `competencia`. |
| Chaves primarias | `registro_ans`, `competencia`. |
| Chaves de negocio | `registro_ans`. |
| Metricas | `score_total`, `componente_core`, `componente_regulatorio`, `componente_financeiro`, `componente_rede`, `componente_estrutural`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| score_total | numeric | Score final | `fat_score_v3_operadora_mensal` | 0-100 |
| faixa_score | text | Faixa interpretavel | derivado | categoria |

```sql
select registro_ans, score_total from nucleo_ans.mart_score_operadora order by score_total desc;
```
