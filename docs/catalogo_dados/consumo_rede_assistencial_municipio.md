# consumo_rede_assistencial_municipio

| Campo | Valor |
|---|---|
| Proposito | Rede assistencial por municipio. |
| Caso de uso | Analise de cobertura e gaps. |
| Grao | `registro_ans`, `cd_municipio`, `competencia`. |
| Chaves primarias | `registro_ans`, `cd_municipio`, `competencia`. |
| Chaves de negocio | `registro_ans`, `cd_municipio`. |
| Metricas disponiveis | `qt_prestadores`, `gap_leitos_cnes`, `classificacao_vazio`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| qt_prestadores | integer | Prestadores | `mart_rede_assistencial` | prestadores |

```sql
select * from consumo_ans.consumo_rede_assistencial_municipio where competencia = 202501;
```
