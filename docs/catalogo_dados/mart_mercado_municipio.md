# mart_mercado_municipio

| Campo | Valor |
|---|---|
| Proposito | Mercado territorial por municipio. |
| Caso de uso | Avaliar concentracao, oportunidade e presenca de operadoras. |
| Grao | Uma linha por `cd_municipio`, `competencia`. |
| Chaves primarias | `cd_municipio`, `competencia`. |
| Chaves de negocio | `cd_municipio`. |
| Metricas | `qt_beneficiarios_total`, `qt_operadoras_ativas`, `hhi`, `score_oportunidade`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| cd_municipio | text | Codigo IBGE | `fat_market_share_mensal` | n/a |
| competencia | integer | Competencia mensal | `fat_market_share_mensal` | YYYYMM |
| hhi | numeric | Concentracao de mercado | `fat_market_share_mensal` | indice |

```sql
select * from nucleo_ans.mart_mercado_municipio where uf = 'SP';
```
