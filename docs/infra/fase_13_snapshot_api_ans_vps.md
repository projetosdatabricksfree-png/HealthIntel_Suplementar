# Fase 13 - Evidencia de Snapshot `api_ans` na VPS

## 1. Objetivo

Registrar a execucao da publicacao do snapshot do schema `api_ans` na VPS de homologacao, com foco em restaurar payload funcional da API Core sem alterar edge publica, sem rodar carga pesada e sem tocar em outros schemas.

## 2. Contexto

Estado anterior confirmado:

- HTTPS/Caddy homologado;
- `https://api.healthintel.com.br/saude` e `/prontidao` em `200`;
- `api_ans` incompleto na VPS;
- `api_ans.api_operadora` vazio na VPS;
- `/v1/operadoras` respondendo `200` com `dados: []`;
- `/v1/rankings/operadora/score` falhando por ausencia de `api_ans.api_ranking_score`;
- `/v1/mercado/municipio` falhando por ausencia de `api_ans.api_market_share_mensal`.

## 3. Estado antes

### VPS

- total de tabelas em `api_ans`: `1`
- `api_ans.api_operadora`: `0` linhas

### Local

- schema `api_ans` materializado
- `api_ans.api_operadora`: `2` linhas
- classificacao dos dados: `DEMO_TECNICA_COM_PAYLOAD`

## 4. Snapshot exportado

Preencher apos execucao:

- arquivo:
- tamanho:
- timestamp:
- origem:
- schema exportado:

## 5. Manifesto

Preencher apos execucao:

- caminho do manifesto:
- classificacao dos dados:
- veredito do manifesto:
- total de tabelas listadas:

## 6. Backup VPS

Preencher apos execucao:

- arquivo de backup:
- horario:
- local:

## 7. Importacao

Preencher apos execucao:

- comando utilizado:
- status:
- houve erro?: sim/nao
- observacoes:

## 8. Contagens antes e depois

### Antes

- total de tabelas em `api_ans`:
- `api_ans.api_operadora`:

### Depois

- total de tabelas em `api_ans`:
- `api_ans.api_operadora`:

## 9. Resultado dos endpoints

Registrar:

- `GET /v1/operadoras`
- `GET /v1/rankings/operadora/score`
- `GET /v1/mercado/municipio`
- classificacao de cada um:
  - `OK_COM_DADOS`
  - `OK_VAZIO`
  - `ERRO_TABELA`
  - `ERRO_BACKEND`
  - `ERRO_AUTH`

## 10. Resultado do Live Tester

Registrar:

- endpoint testado:
- URL chamada:
- payload retornado:
- houve dados?: sim/nao

## 11. Classificacao dos dados

Regra:

- se a origem vier de `seed_demo_*`, classificar como `demo tecnica`;
- so classificar como `demo comercial controlada` quando a origem for serving real da ANS.

Status esperado desta execucao:

- `demo tecnica com payload`

## 12. Rollback

Comando de rollback:

```bash
cat backups/api_ans/<backup_escolhido>.sql | docker exec -i healthintel_postgres psql \
  -U healthintel \
  -d healthintel

docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "analyze;"
```

Registrar se o rollback foi necessario.

## 13. Pendencias

Preencher apos execucao:

- 

## 14. Veredito

Usar uma das saidas:

- `pronto para demo tecnica com payload`
- `pronto para demo comercial controlada`
- `nao aprovado`

Default atual antes da importacao:

- `nao aprovado para demo comercial controlada`
