# Alertas mínimos — homologação e piloto assistido

## Objetivo

Definir o conjunto mínimo de alertas para operar o HealthIntel Suplementar em
homologação VPS e em piloto pago assistido. Este documento não substitui uma
stack completa de métricas; ele define o piso operacional para detectar falhas
que bloqueiam API, ingestão, dbt, backup e proteção comercial.

## Canais e responsabilidade

- Dono primário: operação/SRE.
- Dono técnico por dado: engenharia de dados.
- Canal mínimo: e-mail ou webhook operacional do provedor escolhido.
- Severidade `critico`: exige ação imediata antes de continuar venda ou carga.
- Severidade `aviso`: exige correção planejada antes do próximo ciclo.

## Alertas críticos

| Alerta | Condição | Evidência mínima | Ação |
| --- | --- | --- | --- |
| API indisponível | `/saude` ou `/prontidao` fora de `200` por 5 min | `make smoke` ou log Nginx/API | Reiniciar serviço e verificar Postgres, Redis e MongoDB. |
| Smoke comercial falhando | `make smoke` com qualquer endpoint `500` ou `401/403` inesperado | saída do `scripts/smoke_piloto.py` | Bloquear demonstração e corrigir serving/dbt/chaves. |
| dbt quebrado | `make dbt-build` ou `make dbt-test` com erro | log dbt em `/tmp/healthintel_dbt_logs` | Não publicar dados novos; corrigir modelo/fonte. |
| Freshness vencido | dataset crítico sem atualização dentro do SLO documentado | `plataforma.job` ou tabela de auditoria de carga | Validar ingestão, lote e fonte ANS. |
| Backup inválido | `make smoke-pgbackrest` falha em VPS | `plataforma.backup_execucao` e `pgbackrest info` | Bloquear cliente pagante até restore/backup estar válido. |
| Rate limit indisponível fechado | API retorna `RATE_LIMIT_INDISPONIVEL` em hml/prod | logs da API | Recuperar Redis antes de liberar tráfego comercial. |

## Alertas de aviso

| Alerta | Condição | Evidência mínima | Ação |
| --- | --- | --- | --- |
| CNPJ inválido em camada premium | teste dbt `assert_cnpj_digito_invalido_em_modelos` com warning | saída do `make dbt-test` | Priorizar correção de qualidade antes de proposta enterprise. |
| SQL lint com dívida aberta | `make sql-lint` falha por regras de estilo existentes | saída do SQLFluff | Planejar correção incremental por domínio de modelos. |
| Consumo próximo do limite | cliente atinge 80% do limite do plano | `plataforma.uso_api` ou billing | Acionar upsell ou ajuste de plano. |
| DAG sem execução recente | DAG crítica sem execução no período esperado | UI/log Airflow | Verificar scheduler, conexões e credenciais. |

## Evidência mínima por go/no-go

Antes de homologação VPS:

```bash
make compose-config-hml
make dbt-build
make dbt-test
make smoke
make smoke-pgbackrest
```

Antes de piloto pago:

```bash
make smoke
make dbt-test
bash scripts/run_load_test.sh
```

## Observações

- Em ambiente `hml` e `prod`, `API_RATE_LIMIT_FAIL_OPEN=false` deve ser usado.
- Backup sem `repo2` e restore/PITR testado continua sendo risco operacional.
- Alertas devem ser registrados como evidência de operação, não apenas como
  checklist documental.
