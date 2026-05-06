# Matriz de Planos

| Plano | Escopo comercial | Rate limit por hora | SLA latência p95 | SLA disponibilidade | Observação |
| --- | --- | --- | --- | --- | --- |
| `piloto` | API Core com CNES agregado | 100 | 500 ms | 99,0% | Entrada controlada |
| `essencial` | API Core com CNES agregado | 1.000 | 200 ms | 99,0% | Consumo analítico padrão |
| `plus` | API Core + rede avançada e dados adicionais | 5.000 | 200 ms | 99,5% | Inclui cobertura adicional |
| `enterprise` | API Core + módulos avançados | 20.000 | 150 ms | 99,9% | Integração corporativa |
| `enterprise_tecnico` | API Core + acesso técnico contratado | ilimitado | 150 ms | 99,9% | Acesso técnico completo |
| `analitico` | API Core + dados ampliados | 5.000 | 200 ms | 99,5% | Nome comercial legado |
| `tecnico` | API Core + acesso técnico contratado | 5.000 | 200 ms | 99,5% | Alias comercial legado |

## Leitura

- API Core é a oferta principal de consumo do produto e inclui CNES agregado por município e UF.
- Rede avançada, dados adicionais e módulos avançados entram apenas por contrato.
- Acesso técnico contratado deve ser tratado como exceção comercial, não como fluxo público.
