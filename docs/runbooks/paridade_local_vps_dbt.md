# Paridade Local x VPS dbt/PostgreSQL

## Diagnostico

Use este runbook quando o dbt roda em um ambiente, mas falha na VPS por objeto ausente, seed faltante, coluna defasada ou permissao divergente.

Causas provaveis:

- `dbt seed` nao foi executado na VPS ou falhou antes de materializar `ref_ans`.
- Um model dbt existe no manifest, mas ainda nao foi materializado no banco da VPS.
- Um model incremental recebeu coluna nova e o banco manteve a estrutura antiga.
- Scripts `infra/postgres/init/*.sql` foram interpretados como migrations reaplicaveis.
- Local e VPS estao em commits diferentes.

Regras de seguranca:

- Nao dropar schemas ou banco.
- Nao recriar volume Docker.
- Nao rodar `--full-refresh` global.
- Nao alterar models antes de diagnosticar.
- Nao criar mocks para esconder falha real.

## Init SQL nao e migration reaplicavel

Os arquivos em `infra/postgres/init/*.sql` sao bootstrap do PostgreSQL para volume novo. Eles rodam no inicio do container apenas quando o volume esta vazio.

Nao assuma que alterar um arquivo em `infra/postgres/init/` corrige uma VPS ja existente. Para corrigir VPS com dados, use um dos caminhos seguros:

- `dbt seed` para seeds de referencia.
- `dbt build --select <modelo>` para materializar objeto dbt especifico.
- `dbt build --select <modelo> --full-refresh` apenas para incremental pontual e justificado.
- SQL operacional idempotente revisado, quando o objeto nao for gerenciado por dbt.

## Comparar commit local e VPS

Local:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
```

VPS:

```bash
cd /opt/healthintel
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
```

Se os commits divergirem, registre isso no incidente. Gere o baseline local a partir do commit que representa o estado esperado para a VPS.

## Validar target dbt

Local:

```bash
export ENV_NAME=local
export DATABASE_URL='postgresql://healthintel:healthintel@localhost:5432/healthintel'
make dbt-debug
make dbt-parse
```

VPS:

```bash
cd /opt/healthintel
export ENV_NAME=vps
export DATABASE_URL='postgresql://healthintel:***@localhost:5432/healthintel'
make dbt-debug
make dbt-parse
```

Se usar target especifico:

```bash
export DBT_TARGET=prod
make dbt-debug
make dbt-parse
```

## Exportar catalogo local

```bash
export ENV_NAME=local
export DATABASE_URL='postgresql://healthintel:healthintel@localhost:5432/healthintel'
make audit-schema-export
```

Arquivos principais:

- `tmp/auditoria/catalogo_schema_latest.csv`
- `tmp/auditoria/catalogo_objetos_latest.csv`
- `tmp/auditoria/catalogo_grants_latest.csv`
- `tmp/auditoria/catalogo_constraints_latest.csv`
- `tmp/auditoria/catalogo_indexes_latest.csv`

Copie esses arquivos para a VPS em um diretorio de baseline, por exemplo:

```bash
mkdir -p tmp/auditoria/baseline_local
```

## Exportar catalogo VPS

Na VPS:

```bash
cd /opt/healthintel
export ENV_NAME=vps
export DATABASE_URL='postgresql://healthintel:***@localhost:5432/healthintel'
make audit-schema-export
```

## Rodar auditoria com baseline local

Na VPS:

```bash
cd /opt/healthintel
export ENV_NAME=vps
export DATABASE_URL='postgresql://healthintel:***@localhost:5432/healthintel'
export BASELINE_DIR='tmp/auditoria/baseline_local'
make audit-schema-parity
```

Modo bloqueante:

```bash
make audit-schema-parity-strict
```

`STRICT=0` gera relatorio sem falhar. `STRICT=1` retorna erro se faltar schema, seed obrigatoria, objeto dbt esperado ou grant minimo obrigatorio.

Relatorios:

- `tmp/auditoria/relatorio_paridade_latest.md`
- `tmp/auditoria/manifest_dbt_latest.json`

## Interpretar objeto ausente

No relatorio, veja `Objetos dbt faltantes`.

Se o objeto for seed em `ref_ans`, rode `dbt seed` antes de qualquer mart.

Se for model table/view, valide dependencias upstream e rode build pontual:

```bash
cd healthintel_dbt
DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt build --select nome_do_modelo
```

Se o objeto estiver em schema fora do escopo principal, o relatorio marca `WARN`. Isso indica que o manifest dbt espera materializacao em schema adicional, como `mdm_ans`, `quality_ans`, `mdm_privado` ou `stg_cliente`.

## Interpretar coluna ausente ou divergente

Na secao `Diferencas contra baseline local`:

- `missing_column`: a coluna existe no baseline local e falta na VPS.
- `data_type_mismatch`: tipo logico diverge.
- `udt_name_mismatch`: tipo fisico PostgreSQL diverge.
- `is_nullable_mismatch`: nulidade diverge.
- `column_default_mismatch`: default diverge.
- `ordinal_position_mismatch`: apenas `WARN`; a ordem da coluna mudou, mas isso normalmente nao quebra consultas nomeadas.

Para model incremental com coluna nova, primeiro confirme o model e o volume. Depois use `--full-refresh` pontual:

```bash
cd healthintel_dbt
DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt build --select nome_do_modelo --full-refresh
```

Nao use `--full-refresh` global em tabelas grandes. Se o model for grande, registre janela, impacto e rollback antes.

## Interpretar grant ausente

Na secao `Grants e permissoes`:

- `healthintel_cliente_reader` deve ter acesso minimo em `consumo_ans`, se a role existir.
- `healthintel_premium_reader` deve ter acesso minimo em `consumo_premium_ans`, se a role existir.
- Roles ausentes sao reportadas, mas a auditoria nao cria roles.
- `ref_ans` e `api_ans` sao reportados de forma observacional quando roles de leitura existentes aparecerem no projeto/banco.

Corrija grants com SQL operacional idempotente revisado. Nao amplie permissao em schema interno sem decisao explicita.

## Rodar seeds obrigatorias

Seeds obrigatorias para mart:

- `ref_ans.ref_modalidade`
- `ref_ans.ref_indicador_financeiro`

Validar via auditoria:

```bash
make audit-schema-parity-strict
```

Corrigir seed ausente:

```bash
make dbt-seed
make audit-schema-parity-strict
```

A auditoria exige que as tabelas existam e que `count(*) > 0`.

## Quando usar full-refresh pontual

Use apenas quando:

- O model e incremental.
- A divergencia e estrutural, como coluna nova ausente.
- O reprocessamento do model especifico cabe na janela operacional.
- As dependencias upstream ja estao consistentes.

Comando:

```bash
cd healthintel_dbt
DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt build --select nome_do_modelo --full-refresh
```

## Quando nao usar full-refresh

Nao use quando:

- A seed obrigatoria esta ausente.
- O problema e falta de grant.
- O problema e target dbt errado.
- O problema e commit local/VPS divergente.
- O model e grande e nao ha janela aprovada.
- A causa ainda nao foi identificada.

## Reexecutar mart com seguranca

Somente depois de `ref_ans.ref_modalidade` e `ref_ans.ref_indicador_financeiro` existirem e terem linhas:

```bash
make audit-schema-parity-strict
make dbt-build-mart
```

O comando `make dbt-build-mart` executa:

```bash
dbt build --select +tag:mart
```

## Checklist final

- [ ] Local e VPS estao no commit esperado ou a divergencia esta documentada.
- [ ] `make dbt-debug` passa no ambiente alvo.
- [ ] `make dbt-parse` passa no ambiente alvo.
- [ ] Catalogo local foi exportado do commit esperado.
- [ ] Catalogo VPS foi exportado.
- [ ] `make audit-schema-parity-strict` nao aponta schemas obrigatorios ausentes.
- [ ] `ref_ans.ref_modalidade` existe e tem `count(*) > 0`.
- [ ] `ref_ans.ref_indicador_financeiro` existe e tem `count(*) > 0`.
- [ ] Objetos dbt faltantes foram corrigidos ou justificados.
- [ ] Divergencias de coluna foram corrigidas ou tratadas com full-refresh pontual aprovado.
- [ ] Grants minimos foram corrigidos ou justificados.
- [ ] `dbt build --select +tag:mart` foi executado somente apos seeds obrigatorias estarem validas.
