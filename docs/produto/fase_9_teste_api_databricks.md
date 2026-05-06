# Fase 9 - Teste da API no Databricks

## Regra Central

Databricks cloud nao acessa `http://localhost:8080` da maquina local. Para testar notebooks no Databricks, a API precisa estar publicada ou tunelada.

Opcoes validas:

- VPS com URL publica e HTTPS.
- Cloudflare Tunnel.
- ngrok.
- VPN.
- Rede privada com rota para a API.

Sequencia recomendada:

1. Homologar localmente o frontend e a API.
2. Subir API/frontend para VPS ou tunel seguro.
3. Validar saude, prontidao, CORS e API key.
4. Testar no Databricks usando secret scope.

## Notebook de Teste

```python
import requests
import pandas as pd

BASE_URL = "https://sua-api-publica-ou-tunel"
API_KEY = dbutils.secrets.get("healthintel", "api_key")

headers = {"X-API-Key": API_KEY}

checks = [
    ("/saude", False),
    ("/prontidao", False),
    ("/v1/meta/endpoints", True),
    ("/v1/operadoras", True),
    ("/v1/rankings/operadora/score", True),
    ("/v1/mercado/municipio", True),
]

for endpoint, auth in checks:
    resp = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=headers if auth else {},
        params={"pagina": 1, "por_pagina": 20} if endpoint.startswith("/v1") else {},
        timeout=30,
    )
    print(endpoint, resp.status_code)
    print(resp.text[:1000])
    resp.raise_for_status()

resp = requests.get(
    f"{BASE_URL}/v1/operadoras",
    headers=headers,
    params={"pagina": 1, "por_pagina": 20},
    timeout=30,
)

dados = resp.json()
df = pd.json_normalize(dados.get("dados", dados))
display(df)
```

## Exemplo PySpark

```python
json_data = dados.get("dados", dados)
spark_df = spark.createDataFrame(pd.json_normalize(json_data))
display(spark_df)
```

## Pendencias Antes do Teste Externo

- URL publica ou tunel seguro.
- HTTPS valido.
- API key real ou chave de piloto cadastrada.
- CORS ajustado para a origem do frontend, quando aplicavel.
- Secrets no Databricks Secret Scope, nunca hardcoded em notebook.
