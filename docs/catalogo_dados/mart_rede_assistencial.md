# mart_rede_assistencial

| Campo | Valor |
|---|---|
| Proposito | Presenca de rede por operadora e municipio. |
| Caso de uso | Avaliar cobertura, densidade e gaps CNES. |
| Grao | Uma linha por `registro_ans`, `cd_municipio`, `competencia`. |
| Chaves primarias | `registro_ans`, `cd_municipio`, `competencia`. |
| Chaves de negocio | `registro_ans`, `cd_municipio`. |
| Metricas | `qt_prestadores`, `densidade_por_10k`, `gap_leitos_cnes`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| registro_ans | text | Registro ANS | `fat_cobertura_rede_municipio` | n/a |
| cd_municipio | text | Codigo IBGE | `fat_cobertura_rede_municipio` | n/a |
| qt_prestadores | integer | Prestadores declarados | `fat_cobertura_rede_municipio` | prestadores |

```sql
select * from nucleo_ans.mart_rede_assistencial where cd_municipio = '3550308';
```
