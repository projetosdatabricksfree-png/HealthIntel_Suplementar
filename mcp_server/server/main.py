import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import ExecuteStatementRequest

# Carrega ambiente local (.env) se disponível
load_dotenv()

# Inicializa o servidor MCP
mcp = FastMCP("Databricks HealthIntel Server")

# Inicializa o cliente Databricks
# Para Databricks Apps, ele usará a identidade do app automaticamente
try:
    db = WorkspaceClient()
except Exception as e:
    print(f"Erro ao inicializar WorkspaceClient: {e}")
    db = None

@mcp.tool()
def list_catalogs() -> list[str]:
    """Lista todos os catálogos disponíveis no Unity Catalog."""
    if not db:
        return ["Erro: Cliente Databricks não inicializado."]
    
    catalogs = db.catalogs.list()
    return [c.name for c in catalogs]

@mcp.tool()
def list_schemas(catalog_name: str) -> list[str]:
    """Lista todos os esquemas (databases) dentro de um catálogo específico."""
    if not db:
        return ["Erro: Cliente Databricks não inicializado."]
    
    schemas = db.schemas.list(catalog_name=catalog_name)
    return [s.name for s in schemas]

@mcp.tool()
def list_tables(catalog_name: str, schema_name: str) -> list[str]:
    """Lista todas as tabelas dentro de um esquema específico."""
    if not db:
        return ["Erro: Cliente Databricks não inicializado."]
    
    tables = db.tables.list(catalog_name=catalog_name, schema_name=schema_name)
    return [t.name for t in tables]

@mcp.tool()
def query_sql(sql_query: str, warehouse_id: str = None) -> str:
    """
    Executa uma consulta SQL no Databricks SQL Warehouse.
    
    Args:
        sql_query: A query SQL a ser executada.
        warehouse_id: O ID do SQL Warehouse (opcional, tenta ler do ambiente se não fornecido).
    """
    if not db:
        return "Erro: Cliente Databricks não inicializado."
    
    # Tenta obter o Warehouse ID do ambiente se não fornecido
    # No .env usamos DATABRICKS_HTTP_PATH que contém o ID no final
    # Ou o usuário pode configurar DATABRICKS_WAREHOUSE_ID directamente
    wid = warehouse_id or os.getenv("DATABRICKS_WAREHOUSE_ID")
    
    if not wid and os.getenv("DATABRICKS_HTTP_PATH"):
        # Extrai o ID do caminho HTTP (ex: /sql/1.0/warehouses/XXXX)
        path = os.getenv("DATABRICKS_HTTP_PATH")
        wid = path.split("/")[-1]

    if not wid:
        return "Erro: Warehouse ID não encontrado no ambiente nem fornecido como argumento."

    try:
        response = db.statement_execution.execute_statement(
            warehouse_id=wid,
            statement=sql_query
        )
        
        # Converte o resultado simplificado para string/JSON
        # Nota: Idealmente o LLM interpreta o objeto, mas retornamos string para o MCP básico
        return str(response.result.data_array) if response.result else "Query executada com sucesso (sem retorno de dados)."
    except Exception as e:
        return f"Erro ao executar query: {str(e)}"

def main():
    """Ponto de entrada do servidor."""
    # O FastMCP lida com o transporte HTTP/SSE automaticamente
    mcp.run()

if __name__ == "__main__":
    main()
