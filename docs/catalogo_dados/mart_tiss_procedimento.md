# mart_tiss_procedimento

| Campo | Valor |
|---|---|
| Proposito | Utilizacao e custo TISS por procedimento. |
| Caso de uso | Analise assistencial e sinistralidade por grupo. |
| Grao | Uma linha por `registro_ans`, `cd_procedimento_tuss`, `trimestre`. |
| Chaves primarias | `registro_ans`, `cd_procedimento_tuss`, `trimestre`. |
| Chaves de negocio | `registro_ans`, `cd_procedimento_tuss`. |
| Metricas | `qt_procedimentos`, `vl_total`, `custo_medio_procedimento`, `sinistralidade_pct`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| cd_procedimento_tuss | text | Grupo/procedimento TISS | `fat_tiss_procedimento_operadora` | n/a |
| vl_total | numeric | Valor total | `fat_tiss_procedimento_operadora` | BRL |

```sql
select * from nucleo_ans.mart_tiss_procedimento where trimestre = '2025T1';
```
