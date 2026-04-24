# consumo_beneficiarios_municipio_mes

| Campo | Valor |
|---|---|
| Proposito | Beneficiarios mensais por municipio e operadora. |
| Caso de uso | Analise territorial de carteira. |
| Grao | `registro_ans`, `cd_municipio`, `competencia`. |
| Chaves primarias | `registro_ans`, `cd_municipio`, `competencia`. |
| Chaves de negocio | `registro_ans`, `cd_municipio`. |
| Metricas disponiveis | `qt_beneficiarios`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| cd_municipio | text | Codigo IBGE | `fat_beneficiario_localidade` | n/a |

```sql
select * from consumo_ans.consumo_beneficiarios_municipio_mes where cd_municipio = '3550308';
```
