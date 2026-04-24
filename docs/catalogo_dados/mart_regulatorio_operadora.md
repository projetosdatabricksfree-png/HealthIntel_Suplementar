# mart_regulatorio_operadora

| Campo | Valor |
|---|---|
| Proposito | Situacao regulatoria trimestral da operadora. |
| Caso de uso | Monitoramento de risco regulatorio. |
| Grao | Uma linha por `registro_ans`, `trimestre`. |
| Chaves primarias | `registro_ans`, `trimestre`. |
| Chaves de negocio | `registro_ans`. |
| Metricas | `qtd_reclamacoes`, `indice_reclamacao`, `demandas_nip`, `taxa_resolutividade`. |

| Coluna | Tipo | Descricao | Origem | Unidade |
|---|---|---|---|---|
| registro_ans | text | Registro ANS | `fat_monitoramento_regulatorio_trimestral` | n/a |
| trimestre | text | Trimestre | `fat_monitoramento_regulatorio_trimestral` | YYYYTn |
| nivel_alerta | text | Faixa de risco | derivado | categoria |

```sql
select * from nucleo_ans.mart_regulatorio_operadora where trimestre = '2025T1';
```
