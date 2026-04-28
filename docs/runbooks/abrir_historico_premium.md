# Runbook — Abrir Histórico Premium

## Pré-requisitos

- Cliente ativo em `plataforma.cliente`.
- Dataset ativo em `plataforma.politica_dataset`.
- Dataset com `classe_dataset='grande_temporal'` ou `historico_sob_demanda=true`.
- Faixa de competência aprovada comercialmente.
- Backup/restore operacional disponível para o ambiente.

## Criar Solicitação

```sql
insert into plataforma.solicitacao_historico (
    cliente_id,
    dataset_codigo,
    competencia_inicio,
    competencia_fim,
    motivo
) values (
    '<cliente_uuid>',
    'sib_operadora',
    202401,
    202412,
    'Pedido comercial aprovado para histórico premium'
);
```

## Aprovar no MVP

```sql
update plataforma.solicitacao_historico
   set status = 'aprovada',
       aprovado_em = now()
 where id = <solicitacao_id>
   and status = 'pendente';

update plataforma.cliente_dataset_acesso
   set ativo = false
 where cliente_id = '<cliente_uuid>'::uuid
   and dataset_codigo = 'sib_operadora'
   and ativo is true;

insert into plataforma.cliente_dataset_acesso (
    cliente_id,
    dataset_codigo,
    plano,
    acesso_historico,
    competencia_inicio,
    competencia_fim,
    ativo
) values (
    '<cliente_uuid>'::uuid,
    'sib_operadora',
    'historico_sob_demanda',
    true,
    202401,
    202412,
    true
);
```

## Executar Backfill

Em Airflow, aguardar a próxima execução da `dag_historico_sob_demanda` ou disparar manualmente.

Em smoke/local sem dados reais:

```bash
HISTORICO_SOB_DEMANDA_DRY_RUN=true make smoke-historico-sob-demanda
```

## Validar

```sql
select status, erro
from plataforma.solicitacao_historico
where id = <solicitacao_id>;

select *
from plataforma.cliente_dataset_acesso
where cliente_id = '<cliente_uuid>'::uuid
  and dataset_codigo = 'sib_operadora'
  and ativo is true;

select to_regclass('bruto_ans.sib_beneficiario_operadora_2024');
```

## Bloquear ou Encerrar Acesso

```sql
update plataforma.cliente_dataset_acesso
   set ativo = false
 where cliente_id = '<cliente_uuid>'::uuid
   and dataset_codigo = 'sib_operadora'
   and ativo is true;
```

## Rollback

- Marcar entitlement como `ativo=false`.
- Cancelar solicitações pendentes/aprovadas quando aplicável.
- Manter dados já materializados; sem entitlement ativo, eles não ficam acessíveis ao cliente.
- Se necessário, restaurar dados por backup/dump conforme runbooks de backup da Fase 7.
