# SLO e SLA Operacionais

## SLOs da plataforma

| Indicador | Meta |
| --- | --- |
| Disponibilidade API pública | `>= 99,5%` mensal |
| p95 `GET /v1/operadoras` com cache aquecido | `<= 200 ms` |
| p95 `GET /v1/operadoras/{registro_ans}/score` com cache aquecido | `<= 220 ms` |
| Freshness `cadop` | atraso máximo de `24h` |
| Freshness `sib_operadora` | atraso máximo de `72h` após publicação ANS |
| Freshness `sib_municipio` | atraso máximo de `72h` após publicação ANS |
| Taxa de erro 5xx na API | `< 1%` por janela de 15 min |
| Falha de parse por lote | `< 2%` de linhas por lote |

## SLA externo por plano

| Plano | SLA suporte | Rate limit base |
| --- | --- | --- |
| Starter | horário comercial, resposta em `2 dias úteis` | `60 rpm` |
| Growth | horário comercial, resposta em `1 dia útil` | `180 rpm` |
| Pro | prioridade média, resposta em `8h úteis` | `600 rpm` |
| Enterprise | prioridade alta, resposta em `4h úteis` | customizável |

## Regras

- atraso da ANS é comunicado em `GET /v1/meta/pipeline` e no catálogo operacional;
- mudança de layout sem cadastro aprovado bloqueia ingestão e envia o arquivo para quarentena;
- queda de dependência crítica derruba `/prontidao` para `503`;
- revisão dos SLOs ocorre a cada mudança de capacidade ou de plano.
