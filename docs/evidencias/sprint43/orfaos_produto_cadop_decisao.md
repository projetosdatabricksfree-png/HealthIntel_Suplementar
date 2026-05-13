# Decisão Sprint 43 — Órfãos `registro_ans` em produto vs CADOP

## Contexto

Auditoria Sprint 42 reportou **57.074 órfãos** `registro_ans` em
`stg_ans.stg_produto_caracteristica` que não correspondem a nenhum
`registro_ans` em `stg_ans.stg_cadop`. A Sprint 43 abriu F7 para diagnosticar
a causa e decidir entre **bug de normalização** vs **histórico legítimo**.

## Diagnóstico

```sql
with orfaos as (
  select distinct pc.registro_ans
  from stg_ans.stg_produto_caracteristica pc
  where pc.registro_ans is not null
    and not exists (
      select 1 from stg_ans.stg_cadop c where c.registro_ans = pc.registro_ans
    )
)
select count(*) from orfaos;
```

| Métrica | Valor |
|---|---:|
| `produto.total_registros` | 163.661 |
| `produto.distinct(registro_ans)` | 2.935 |
| `cadop.total_registros` | 1.107 |
| `cadop.distinct(registro_ans)` | 1.107 |
| **Órfãos distintos (registro_ans)** | **2.014** |
| **Órfãos em linhas** | **~57.074** |
| Órfãos contidos em `stg_operadora_cancelada` | 0 (tabela vazia) |
| Bronze `bruto_ans.cadop` distintos | 1.107 |

## Conclusão (decisão binária)

**Histórico legítimo, não bug.**

Razões:
1. **A fonte ANS oficial `Relatorio_cadop.csv` publica apenas operadoras ATIVAS.**
   O bronze refletindo 1.107 distintos é exatamente o que a fonte traz; não há
   bug de parser, casting, ou normalização (`normalizar_registro_ans` já está
   aplicado corretamente — todos os IDs têm 6 chars).
2. O produto/plano agrega histórico — produtos comercializados por operadoras
   que hoje podem estar canceladas, em liquidação extrajudicial, alienadas,
   incorporadas, etc.
3. A diferença distintos `2.935 produto - 1.107 cadop = 1.828`, próxima dos
   2.014 órfãos. Indica que ~1.800-2.000 operadoras históricas geraram produtos
   no passado e hoje não constam no CADOP atual.
4. `stg_operadora_cancelada` está vazio — a fonte ANS de operadoras canceladas
   (PDF/planilha trimestral separada) ainda não foi ingerida.

## Plano de correção definitiva (Sprint 44)

1. **Ingerir fonte ANS de operadoras canceladas** (DAG nova ou ajuste em
   `dag_ingest_cadop`). Fontes possíveis:
   - https://www.gov.br/ans/pt-br/assuntos/operadoras/operadoras-em-direcao-fiscal-e-liquidacao-extrajudicial
   - https://www.gov.br/ans/pt-br/assuntos/operadoras/operadoras-com-cancelamento-compulsorio
2. **Criar `nucleo_ans.dim_operadora_historica`** como union de:
   - CADOP ativo (`stg_cadop`)
   - Operadoras canceladas (`stg_operadora_cancelada`)
   - Operadoras "fantasma" descobertas via produto (com flag `origem='produto_historico'`)
3. **Redirecionar FK de produto** para `dim_operadora_historica` ao invés de
   apenas CADOP ativo.

## Decisão para a Sprint 43

- Aceitar o histórico legítimo.
- Transformar o teste dbt `relationships(registro_ans) -> stg_cadop` em
  **warning** (severity: warn) com mensagem explícita "histórico legítimo
  pendente Sprint 44" em `_schema.yml`.
- Registrar `dim_operadora_historica` como tarefa explícita em
  `docs/sprints/fase10/backlog_pos_sprint43.md`.

## Evidência

```
$ docker compose ... psql ... -c "<query>"
total_registros_produto|163661
produto_distintos|2935
total_registros_cadop|1107
cadop_distintos|1107
orfaos_distintos|2014
amostra_orfao_max_registro|424269
amostra_orfao_min_registro|000027
stg_operadora_cancelada|0
```

Script reproduzível: `scripts/auditoria/auditar_orfaos_produto_cadop.sql`.
