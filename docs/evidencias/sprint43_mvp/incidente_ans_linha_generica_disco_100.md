# Incidente: `bruto_ans.ans_linha_generica` ocupando disco da VPS

## Data/hora

- Registro: 2026-05-14T13:21:14+02:00
- Ambiente: VPS HealthIntel em `/opt/healthintel`

## Disco antes

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       387G  387G   56M 100% /
```

## Maiores tabelas antes

| Tabela | Tamanho |
|---|---:|
| `bruto_ans.ans_linha_generica` | 322 GB |
| `bruto_ans.produto_prestador_hospitalar` | 11 GB |
| `bruto_ans.operadora_prestador_nao_hospitalar` | 8719 MB |
| `bruto_ans.produto_tabela_auxiliar` | 356 MB |
| `bruto_ans.diops_operadora_trimestral_default` | 328 MB |

## Causa provável

`bruto_ans.ans_linha_generica` foi usada como fallback generico para carga bruta
massiva. A tabela chegou a 322 GB, 93,76% do banco, com aproximadamente
325.965.871 linhas por `max(id)`.

A auditoria posterior mostrou erros `DiskFullError` em arquivos SIB tentando
executar `insert into bruto_ans.ans_linha_generica`, especialmente:

- `sib_inativo_SP.zip` (2980 MB)
- `sib_inativo_RJ.zip` (936 MB)
- `sib_inativo_RS.zip` (316 MB)
- `sib_inativo_SC.zip` (196 MB)

Tambem havia cargas pesadas recentes em `dag_ingest_rede_prestadores`,
especialmente:

- `ingerir_produto_prestador_hospitalar`
- `ingerir_operadora_prestador_nao_hospitalar`

Essas cargas de rede geraram tabelas bronze proprias grandes, enquanto a causa
critica de disco cheio foi o fallback generico sem limite forte aceitando
datasets massivos como SIB.

## Ação de mitigação

- Airflow pausado via `airflow dags pause --treat-dag-id-as-regex -y '.*'`.
- Sessoes ativas no Postgres verificadas; nao havia escrita ativa em
  `bruto_ans.ans_linha_generica`.
- Dependencia direta verificada; apenas a view staging
  `stg_ans.stg_ans_linha_generica` depende diretamente da tabela.
- `TRUNCATE TABLE bruto_ans.ans_linha_generica` executado.

## Truncate executado

SIM.

## Disco depois

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       387G   65G  323G  17% /
```

Depois do truncate:

- Banco `healthintel`: 21 GB
- `bruto_ans.ans_linha_generica`: 32 kB

## Proteção implementada

- Bloqueio de uso de `bruto_ans.ans_linha_generica` para datasets/familias de
  rede, prestador, CNES, TISS, DIOPS, FIP, NTRP, SIP e SIB.
- Allowlist explicita para uso generico pequeno.
- Limite maximo de 100 MB por arquivo para carga generica.
- Limite maximo de 1.000.000 linhas por arquivo para carga generica.
- Tentativas bloqueadas registradas em `plataforma.tentativa_carga_ans` como
  `LAYOUT_NAO_MAPEADO` ou `ERRO_VALIDACAO`.
- Script de auditoria criado em
  `scripts/auditoria/auditar_bronze_generico_explosivo.sql`.

## Testes executados

- `pytest ingestao/tests`: 133 passed, 1 warning, executado com
  `POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_USER=healthintel
  POSTGRES_PASSWORD=healthintel POSTGRES_DB=healthintel`.
- `ruff check .`: nao executado com sucesso porque `ruff` nao esta instalado
  na `.venv`, no container `api` nem no container `airflow-scheduler`.
- Script `scripts/auditoria/auditar_bronze_generico_explosivo.sql` executado
  com sucesso; resultado principal: `bruto_ans.ans_linha_generica` 32 kB,
  0 linhas estimadas, recomendacao `OK`.

## Estado de retomada

- DAGs permanecem pausadas.
- Nao retomar `rede_prestadores` ate confirmar bronze proprio e monitoramento
  de `ans_linha_generica`.
