# Dívida Técnica — `make smoke-tiss` / `seed_demo_rede.py`

**Detectada em:** Sprint 37 (2026-04-28)
**Prioridade:** baixa (não bloqueia operação nem ingestão real)
**Status:** resolvida na finalização da Sprint 37

---

## Sintoma

```
make smoke-tiss
# TypeError: 'str' object cannot be interpreted as an integer
# File: scripts/seed_demo_rede.py
# Coluna: bruto_ans.rede_prestador_municipio.competencia
```

O script `scripts/seed_demo_rede.py` passa um valor `str` (ex.: `"202504"`) para a coluna `competencia` de `bruto_ans.rede_prestador_municipio`, que está declarada como `integer` (ou espera conversão explícita via `int()`).

Smoke `make smoke-tiss` falha **antes de qualquer asserção do TISS** porque o fixture de dados de rede é carregado na suite e lança `TypeError` durante setup.

---

## Causa raiz

`seed_demo_rede.py` não converte `competencia` para `int` antes do INSERT. A tabela `bruto_ans.rede_prestador_municipio` provavelmente declara a coluna como `integer` (ou o driver psycopg2/asyncpg rejeita a string). Nenhum arquivo alterado pela Sprint 37 ou 36 toca `seed_demo_rede.py` — defeito pré-existente.

---

## Impacto

- `make smoke-tiss` não pode ser executado em ambiente sem dados de rede pré-carregados.
- **Não afeta ingestão real** (seed scripts são apenas para ambiente local de desenvolvimento).
- **Não afeta `make smoke` (piloto), `make smoke-cnes`, `make smoke-sib`, `make smoke-cadop`**.
- **Não afeta `pytest ingestao/tests/` nem `pytest api/tests/`** (suite de testes unitários e de integração não usa `seed_demo_rede.py`).

---

## Correção proposta

Em `scripts/seed_demo_rede.py`, linha onde `competencia` é atribuída, adicionar conversão:

```python
# antes
"competencia": "202504",
# depois
"competencia": int("202504"),
```

Ou, se o campo vier de variável externa:

```python
row["competencia"] = int(row["competencia"])
```

Verificar também `bruto_ans.rede_prestador_municipio` DDL para confirmar tipo da coluna (`integer` vs `text`).

---

## Aceite

Smoke `make smoke-tiss` executando sem TypeError no fixture de rede.

## Resolução — 2026-04-28

- `scripts/seed_demo_rede.py`: `competencia` dos registros Bronze convertida para `int`.
- `scripts/seed_demo_rede.py`: carga demo dividida em lotes com `hash_arquivo` distinto por linha para respeitar índices únicos existentes por competência/hash.
- `scripts/seed_demo_tiss.py`: mesma padronização de hash por linha para TISS/DIOPS demo.
- `scripts/smoke_tiss.py`: `DBT_LOG_PATH` e `DBT_TARGET_PATH` movidos para `/tmp` e execução ajustada para `dbt seed` + `dbt run`, evitando data tests não relacionados ao smoke.
- Evidência: `make smoke-tiss` retornou 3 checks com 0 falhas e HTTP 200 para `/v1/tiss/123456/procedimentos`, `/v1/tiss/123456/sinistralidade` e `/v1/rede/gap/3550308`.

---

**Owner:** Engenharia de dados HealthIntel.
