# consumo_beneficiarios_operadora_mes

| Campo | Valor |
|---|---|
| Proposito | Beneficiarios mensais por operadora. |
| Caso de uso | Serie temporal de carteira. |
| Grao | `registro_ans`, `competencia`. |
| Chaves primarias | `registro_ans`, `competencia`. |
| Chaves de negocio | `registro_ans`. |
| Metricas disponiveis | `qt_beneficiarios`, `variacao_12m_pct`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| qt_beneficiarios | integer | Beneficiarios ativos | `fat_beneficiario_operadora` | beneficiarios |

```sql
select * from consumo_ans.consumo_beneficiarios_operadora_mes where registro_ans = '123456';
```
