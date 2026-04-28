# Particionamento anual PostgreSQL por `competencia YYYYMM`

## Objetivo

A Sprint 35 implementa particionamento anual PostgreSQL para as tabelas SIB
`bruto_ans.sib_beneficiario_operadora` e `bruto_ans.sib_beneficiario_municipio`.
A coluna `competencia` continua sendo `integer` no formato `YYYYMM`; a mudança é
exclusivamente física, no limite das partições.

## Por que anual e não mensal

O padrão anual reduz a quantidade de objetos no catálogo, simplifica retenção e
mantém pruning eficiente para consultas por ano ou por intervalo de competência.
Partições mensais para SIB são anti-padrão nesta fase porque aumentam custo
operacional sem alterar o contrato lógico de dados.

Exemplo correto:

```sql
FOR VALUES FROM (202601) TO (202701)
```

No particionamento `RANGE` do PostgreSQL, o limite inferior é inclusivo e o
limite superior é exclusivo. Portanto, a partição acima recebe competências de
`202601` até `202612`.

## Janela hot

Com `p_anos_carga = 2` em 2026:

- `ano_inicial = 2025`
- `ano_final = 2026`
- `ano_preparado = 2027`
- `competencia_minima = 202501`
- `competencia_maxima_exclusiva = 202701`

Isso significa que a janela hot carrega 2025 e 2026, enquanto a partição de
2027 é criada vazia para preparar a virada operacional.

Na virada de ano para 2027:

- a janela hot passa a carregar 2026 e 2027;
- a partição de 2028 passa a ser preparada;
- a remoção ou destacamento de 2025 só pode ocorrer após backup válido e
  validação de retenção.

## Funções criadas

`infra/postgres/init/030_fase7_particionamento_anual.sql` cria as funções:

- `plataforma.calcular_janela_carga_anual(p_anos_carga, p_data_referencia)`:
  calcula ano vigente, janela hot e competência mínima/máxima exclusiva.
- `plataforma.criar_particao_anual_competencia(p_schema, p_tabela, p_ano)`:
  cria ou reaproveita uma partição anual `<tabela>_<ano>`.
- `plataforma.preparar_particoes_janela_atual(p_schema, p_tabela, p_anos_carga)`:
  cria/reaproveita as partições de `ano_inicial` até `ano_preparado`.
- `plataforma.alertar_default_particao()`: registra quando uma linha cai em
  partição `_default`.

## Auditoria

A tabela `plataforma.retencao_particao_log` registra ações de particionamento:

- `criada`
- `reaproveitada`
- `destacada`
- `removida`
- `default_recebeu_linha`

O índice `ix_retencao_particao_log_lookup` apoia consultas por schema, tabela e
execução recente.

## Trigger da default

As partições `bruto_ans.sib_beneficiario_operadora_default` e
`bruto_ans.sib_beneficiario_municipio_default` recebem trigger `after insert`.
Quando uma linha cai na default, o evento é registrado em
`plataforma.retencao_particao_log` com `acao = 'default_recebeu_linha'`.

Esse alerta indica competência fora da janela preparada e deve ser tratado como
incidente operacional, exceto em carga histórica controlada.

## Validação de pruning

Comando obrigatório:

```sql
EXPLAIN (ANALYZE, VERBOSE, BUFFERS)
SELECT count(*)
FROM bruto_ans.sib_beneficiario_operadora
WHERE competencia BETWEEN 202601 AND 202612;
```

Critério:

- deve aparecer apenas `bruto_ans.sib_beneficiario_operadora_2026`;
- não deve aparecer `bruto_ans.sib_beneficiario_operadora_2025`;
- não deve aparecer `bruto_ans.sib_beneficiario_operadora_2027`;
- não deve aparecer `bruto_ans.sib_beneficiario_operadora_default`.

## Anti-padrões

- Usar `LIST` ou `HASH` partitioning para `competencia`.
- Criar partições mensais SIB, como `_2026_01` ou `_2026_02`.
- Alterar `competencia` para `date`, `text` ou outro formato.
- Hardcodar ano em código Python ou SQL de automação.
- Dropar partições ou dados sem backup válido e dry-run.

## Rollback

O rollback seguro exige:

1. pausar ingestão SIB;
2. validar backup/dump disponível;
3. reverter a DAG legado se a automação anual precisar ser suspensa;
4. restaurar por backup/dump se houver corrupção ou attach inválido;
5. executar `dbt parse`, testes de ingestão e smoke SIB antes de reativar.

Nesta sprint não há `DETACH`, `ATTACH` destrutivo nem drop de dados por padrão.
Se a partição `_default` contiver linhas dentro da janela planejada, o bootstrap
aborta e exige migração manual com backup e dry-run.

## Backup emergencial

`pg_dump` é aceito apenas como medida temporária até a Sprint 39. A solução
oficial futura de backup e PITR é `pgBackRest`.

## Observações do ambiente local

- A tag `v3.8.0-gov` não está presente neste clone; a validação de baseline deve
  usar diff explícito dos paths protegidos.
- O arquivo `ingestao/dags/dag_criar_particao_mensal.py` mantém nome legado por
  compatibilidade, mas não cria mais partições mensais para SIB.
