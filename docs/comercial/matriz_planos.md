# Matriz de Planos

| Plano | Camadas | Rate limit por hora | SLA latência p95 | SLA disponibilidade | Observação |
| --- | --- | --- | --- | --- | --- |
| `piloto` | `ouro` | 100 | 500 ms | 99,0% | Entrada controlada |
| `essencial` | `ouro` | 1.000 | 200 ms | 99,0% | Consumo analítico padrão |
| `plus` | `ouro`, `prata` | 5.000 | 200 ms | 99,5% | Inclui dados padronizados |
| `enterprise` | `ouro`, `prata`, `bronze` | 20.000 | 150 ms | 99,9% | Integração corporativa |
| `enterprise_tecnico` | `ouro`, `prata`, `bronze` | ilimitado | 150 ms | 99,9% | Acesso técnico completo |
| `analitico` | `ouro`, `prata` | 5.000 | 200 ms | 99,5% | Nome comercial para Prata |
| `tecnico` | `ouro`, `prata` | 5.000 | 200 ms | 99,5% | Alias comercial legado |

## Leitura

- `bronze` é cobrada com custo maior no rate limit porque expõe dado técnico de baixo nível.
- `prata` é intermediária e inclui qualidade e quarentena.
- `ouro` é a camada principal de consumo do produto.

