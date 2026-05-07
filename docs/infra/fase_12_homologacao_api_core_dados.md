# Fase 12 - Homologacao da API Core com dados reais

## 1. objetivo

Validar se a camada de serving `api_ans` sustenta payload comercial minimo para a demo controlada do HealthIntel Core ANS via `https://api.healthintel.com.br`, sem rodar carga pesada, sem TISS, sem CNES completo e sem mascarar ausencia de dados.

## 2. ambiente

- Local: `/home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar`
- VPS de homologacao: `5.189.160.27`
- Frontend: `https://app.healthintel.com.br`
- API: `https://api.healthintel.com.br`
- Estado de borda: HTTPS/Caddy homologado, `8080/tcp` fechado publicamente e API mantida em `127.0.0.1:8080` na VPS

## 3. impacto arquitetural

Nenhuma alteracao foi aplicada em pipeline, dbt, Airflow, schema de dados, regras de negocio ou contratos de endpoint. Esta fase adiciona apenas validacao operacional e documentacao da camada de servico.

O diagnostico confirma que a API consulta apenas `api_ans`. Portanto:

- resposta `200` com `dados: []` indica camada de serving publicada, mas sem conteudo;
- resposta `500` com `UndefinedTable` indica schema de serving incompleto na VPS;
- o problema atual e de materializacao/publicacao da camada `api_ans`, nao da camada HTTP/TLS.

## 4. contagem das tabelas `api_ans`

### VPS

- tamanho total do banco: `10 MB`
- total de tabelas em `api_ans`: `1`
- tabela existente: `api_operadora`
- linhas em `api_ans.api_operadora`: `0`

### Local

- tamanho total do banco: `1719 MB`
- total de tabelas em `api_ans`: `60`
- linhas em `api_ans.api_operadora`: `2`
- observacao: apesar do schema local estar materializado, a maioria das tabelas observadas via `pg_stat_user_tables` ainda aparece sem linhas estimadas relevantes para demo comercial

## 5. endpoints testados

### Publicos

- `GET /saude`
- `GET /prontidao`

### Core autenticados

- `GET /v1/meta/endpoints`
- `GET /v1/operadoras?pagina=1&por_pagina=10`
- `GET /v1/rankings/operadora/score?pagina=1&por_pagina=10`
- `GET /v1/mercado/municipio?pagina=1&por_pagina=10`

## 6. status por endpoint

| Endpoint | Status | Classificacao | Evidencia |
| --- | --- | --- | --- |
| `/saude` | `200` | `OK_COM_DADOS` | responde status da API |
| `/prontidao` | `200` | `OK_COM_DADOS` | responde dependencias |
| `/v1/meta/endpoints` | `200` | `OK_COM_DADOS` | catalogo de contratos publicado |
| `/v1/operadoras` | `200` | `OK_VAZIO` | payload com `dados: []` na VPS |
| `/v1/rankings/operadora/score` | `500` | `ERRO_TABELA` | `UndefinedTableError` para `api_ans.api_ranking_score` |
| `/v1/mercado/municipio` | `500` | `ERRO_TABELA` | `UndefinedTableError` para `api_ans.api_market_share_mensal` |

## 7. payload minimo esperado

A homologacao comercial minima so passa se `/v1/operadoras` retornar `200` com pelo menos um registro real contendo:

- `registro_ans`
- `nome` ou `razao_social`
- `modalidade`, se disponivel
- `uf_sede`, se disponivel
- `competencia_referencia`, se disponivel

## 8. resultado real

### VPS

`/v1/operadoras` respondeu:

```json
{
  "dados": [],
  "meta": {
    "competencia_referencia": "atual",
    "versao_dataset": "sib_operadora_v1",
    "total": 0,
    "pagina": 1,
    "por_pagina": 10,
    "cache": "miss"
  }
}
```

Isso fecha o status como `PENDENTE_DADOS_SERVING`.

### Local

O ambiente local possui `2` linhas em `api_ans.api_operadora`, o que mostra que existe um caminho minimo de publicacao local, mas a VPS ainda nao recebeu nem esse snapshot controlado.

## 9. pendencias

1. Publicar dados reais em `api_ans.api_operadora` na VPS.
2. Publicar as tabelas Core referenciadas por ranking e mercado na VPS:
   - `api_ans.api_ranking_score`
   - `api_ans.api_market_share_mensal`
3. Validar consistencia entre `plataforma.versao_dataset` e o conteudo materializado em `api_ans`.
4. Reexecutar o check comercial somente apos a publicacao da camada serving.

## 10. decisao

### Veredito atual

- pronto para demo tecnica: `sim`
- pronto para demo comercial controlada: `nao`

Motivo: `/v1/operadoras` ainda nao retorna nenhum registro real na VPS.

## 11. proximo passo tecnico

O caminho mais seguro e arquiteturalmente consistente e:

1. materializar localmente a camada `api_ans` minima do Core;
2. validar localmente os endpoints `/v1/operadoras`, `/v1/rankings/operadora/score` e `/v1/mercado/municipio`;
3. exportar snapshot controlado apenas das tabelas de serving necessarias;
4. importar o snapshot na VPS;
5. reexecutar `scripts/vps/check_api_core_comercial.sh`.

## 12. comandos de referencia usados no diagnostico

```bash
docker exec -i healthintel_postgres psql -P pager=off -U healthintel -d healthintel -c "
select count(*) as total_tabelas
from information_schema.tables
where table_schema = 'api_ans';
"

docker exec -i healthintel_postgres psql -P pager=off -U healthintel -d healthintel -c "
select count(*) as linhas
from api_ans.api_operadora;
"

curl -i "https://api.healthintel.com.br/v1/operadoras?pagina=1&por_pagina=10" \
  -H "X-API-Key: <chave_hml_dev>"
```
