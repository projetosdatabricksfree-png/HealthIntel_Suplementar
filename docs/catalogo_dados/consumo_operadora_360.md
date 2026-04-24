# consumo_operadora_360

| Campo | Valor |
|---|---|
| Proposito | Entrega cliente da visao 360 da operadora. |
| Caso de uso | Analise externa em SQL, Python, Metabase ou Power BI. |
| Grao | `registro_ans`, `competencia`. |
| Chaves primarias | `registro_ans`, `competencia`. |
| Chaves de negocio | `registro_ans`. |
| Metricas disponiveis | Beneficiarios, score e componentes. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| registro_ans | text | Registro ANS | `mart_operadora_360` | n/a |
| competencia | integer | Competencia | `mart_operadora_360` | YYYYMM |
| score_total | numeric | Score final | `mart_operadora_360` | 0-100 |

```sql
select * from consumo_ans.consumo_operadora_360 where competencia = 202501;
```
