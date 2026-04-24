# consumo_oportunidade_municipio

| Campo | Valor |
|---|---|
| Proposito | Oportunidade territorial por municipio. |
| Caso de uso | Priorizacao comercial e territorial. |
| Grao | `cd_municipio`, `competencia`. |
| Chaves primarias | `cd_municipio`, `competencia`. |
| Chaves de negocio | `cd_municipio`. |
| Metricas disponiveis | `score_oportunidade`, `hhi`, `qt_operadoras_ativas`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| score_oportunidade | numeric | Score de oportunidade | `mart_mercado_municipio` | 0-100 |

```sql
select * from consumo_ans.consumo_oportunidade_municipio order by score_oportunidade desc;
```
