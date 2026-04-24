# Contratos Por Camada

Este documento resume os contratos formais da arquitetura medallion do HealthIntel Suplementar. A API pública consulta apenas `api_ans`; as demais camadas existem para governar ingestão, padronização e modelagem.

| Camada | Schema | Objetivo | Transformações permitidas | Validações | Saída esperada | Exposição API | Risco principal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bronze | `bruto_ans` | Espelho técnico fiel da fonte | Hash, lote, auditoria, particionamento, controle de idempotência | Estruturais, hash de arquivo, hash de linha, contagem de registros | Tabela auditável por lote e competência | Bronze API apenas para `enterprise_tecnico` | Dado corrompido ou lote duplicado |
| Prata entrada | `stg_ans` | Dado padronizado e tipado | Cast, limpeza, normalização, parsing, quarentena | Tipagem, domínio, regex, chaves e datas válidas | Views padronizadas por dataset | Prata API para `analitico` e acima | Domínio incorreto silencioso |
| Prata saída | `int_ans` | Dado enriquecido para negócio | Joins, dedup, janelas, flags e composição de métricas | Consistência analítica e integridade referencial | Modelos intermediários prontos para ouro | Prata API enriquecida | Explosão de join ou duplicidade |
| Ouro analítico | `nucleo_ans` | Verdade analítica e regras de negócio | Modelagem dimensional, scores, rankings, snapshots | Unicidade, faixa de score, chaves e relações | Fatos e dimensões confiáveis | Não exposto diretamente | Divergência metodológica |
| Ouro serviço | `api_ans` | Produto estável e indexado para consumo | Desnormalização, paginação, índices e envelope de contrato | Schema estável, latência e compatibilidade retroativa | Tabelas e views otimizadas para API | API principal do produto | Latência e drift de contrato |

## Regras Operacionais

- Bronze é reprocessável e idempotente por `hash_arquivo`.
- Prata sempre expõe qualidade e quarentena de forma explícita.
- Ouro analítico não deve ser consultado diretamente pela API.
- Ouro serviço é a única camada lida pelos endpoints analíticos e comerciais.
- Mudança de layout físico pertence ao motor de ingestão, não ao dbt.

