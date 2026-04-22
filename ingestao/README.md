# Ingestao

Area destinada aos DAGs Airflow, scripts de download, validacao estrutural e carga da camada `bruto_ans`.

O objetivo do scaffold e preservar a separacao entre:

- descoberta do arquivo e hash;
- resolucao de layout no MongoDB;
- traducao origem -> destino RAW;
- carga idempotente no PostgreSQL;
- registro operacional em `plataforma`.
