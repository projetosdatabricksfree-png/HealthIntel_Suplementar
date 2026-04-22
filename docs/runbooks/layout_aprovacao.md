# Runbook — Cadastro e aprovação de layout

## Pré-requisitos

- API pública e `mongo_layout_service` ativos;
- `X-API-Key` administrativa;
- `LAYOUT_SERVICE_TOKEN` configurado entre API e layout service.

## Passos

1. Cadastrar layout:

```bash
curl -X POST http://localhost:8080/admin/layouts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hi_local_admin_2026_api_key" \
  -d '{
    "dataset_codigo": "cadop",
    "nome": "Cadastro de Operadoras CSV",
    "descricao": "Layout base para CADOP",
    "tabela_raw_destino": "bruto_ans.cadop",
    "formato_esperado": "csv",
    "delimitador": ";"
  }'
```

2. Criar versão:

```bash
curl -X POST http://localhost:8080/admin/layouts/layout_cadop_csv/versoes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hi_local_admin_2026_api_key" \
  -d '{
    "versao": "v1",
    "colunas": [
      {"nome_canonico": "registro_ans", "tipo": "string", "obrigatorio": true},
      {"nome_canonico": "competencia", "tipo": "integer", "obrigatorio": true}
    ]
  }'
```

3. Criar alias:

```bash
curl -X POST http://localhost:8080/admin/layouts/layout_cadop_csv/aliases \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hi_local_admin_2026_api_key" \
  -d '{
    "nome_fisico": "competência",
    "destino_raw": "competencia",
    "obrigatorio": true,
    "layout_versao_id": "layout_cadop_csv:v1",
    "regra_transformacao": "identity"
  }'
```

4. Aprovar versão:

```bash
curl -X POST http://localhost:8080/admin/layouts/layout_cadop_csv/aprovar \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hi_local_admin_2026_api_key" \
  -d '{
    "status": "ativo",
    "layout_versao_id": "layout_cadop_csv:v1",
    "motivo": "Aprovado para carga controlada"
  }'
```

## Validações

- `GET /admin/layouts` deve listar o layout como `ativo`;
- `POST /admin/layouts/validar-arquivo` deve retornar `compativel=true` para arquivo aderente;
- `evento_layout` precisa registrar criação, aprovação e eventual depreciação.
