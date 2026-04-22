# Databricks HealthIntel MCP Server

Este é um servidor Model Context Protocol (MCP) personalizado, projetado para rodar como um **Databricks App**. Ele permite que agentes de IA interajam diretamente com seu Unity Catalog e SQL Warehouses.

## Ferramentas Disponíveis

- `list_catalogs`: Lista todos os catálogos.
- `list_schemas(catalog_name)`: Lista bancos de dados.
- `list_tables(catalog_name, schema_name)`: Lista tabelas.
- `query_sql(sql_query)`: Executa consultas SQL em um SQL Warehouse.

## Como fazer o Deploy

1. Certifique-se de que você tem o Databricks CLI instalado e autenticado.
2. No diretório raiz deste servidor (`mcp_server`), execute:

```bash
databricks apps deploy mcp-health-intel --source-code-path .
```

## Como Usar Localmente (Desenvolvimento)

Para testar o servidor localmente:

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Rode o servidor em modo dev:
   ```bash
   mcp dev server/main.py
   ```

## Configuração

O servidor lê automaticamente as credenciais do ambiente ou do contexto do Databricks App. Para desenvolvimento local, ele utiliza o arquivo `.env` na raiz do projeto.
