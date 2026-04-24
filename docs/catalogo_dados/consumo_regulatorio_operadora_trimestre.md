# consumo_regulatorio_operadora_trimestre

| Campo | Valor |
|---|---|
| Proposito | Regulatorio trimestral por operadora. |
| Caso de uso | Monitoramento externo de risco. |
| Grao | `registro_ans`, `trimestre`. |
| Chaves primarias | `registro_ans`, `trimestre`. |
| Chaves de negocio | `registro_ans`. |
| Metricas disponiveis | `nivel_alerta`, `indice_reclamacao`, `qtd_processos_ativos`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| nivel_alerta | text | Nivel de alerta | `mart_regulatorio_operadora` | categoria |

```sql
select * from consumo_ans.consumo_regulatorio_operadora_trimestre where nivel_alerta = 'alto';
```
