# mart_operadora_360

| Campo | Valor |
|---|---|
| Proposito | Visao mensal consolidada da operadora. |
| Caso de uso | Perfil 360, score, crescimento e componentes principais. |
| Grao | Uma linha por `registro_ans`, `competencia`. |
| Chaves primarias | `registro_ans`, `competencia`. |
| Chaves de negocio | `registro_ans`. |
| Metricas | `qt_beneficiarios`, `score_total`, componentes do score. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| registro_ans | text | Registro ANS | `fat_beneficiario_operadora` | n/a |
| competencia | integer | Competencia mensal | `fat_beneficiario_operadora` | YYYYMM |
| qt_beneficiarios | integer | Beneficiarios ativos | `fat_beneficiario_operadora` | beneficiarios |
| score_total | numeric | Score v3 final | `fat_score_v3_operadora_mensal` | 0-100 |

```sql
select * from nucleo_ans.mart_operadora_360 where competencia = 202501;
```
