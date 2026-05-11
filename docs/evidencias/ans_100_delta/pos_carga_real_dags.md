# Evidência — DAGs Delta ANS

**Timestamp:** 2026-05-11T22:07:46Z  
**Commit:** e665fbf  

## Diagnóstico — runs históricos (validação manual)

```
dag_ingest_tuss_oficial     → "No data found" — nenhuma execução registrada
Todos os 9 DAGs delta       → carregados (is_active=True), NENHUM foi executado
plataforma.arquivo_fonte_ans → 0 rows — nenhuma ingestão real ocorreu na VPS
```

**Classificação por DAG:**

| DAG | Status |
|---|---|
| dag_ingest_produto_plano | alerta — carregado, nunca executado |
| dag_ingest_tuss_oficial | alerta — carregado, nunca executado |
| dag_ingest_tiss_subfamilias | alerta — carregado, nunca executado |
| dag_ingest_sip_delta | alerta — carregado, nunca executado |
| dag_ingest_ressarcimento_sus | alerta — carregado, nunca executado |
| dag_ingest_precificacao_ntrp | alerta — carregado, nunca executado |
| dag_ingest_rede_prestadores | alerta — carregado, nunca executado |
| dag_ingest_regulatorios_complementares | alerta — carregado, nunca executado |
| dag_ingest_beneficiarios_cobertura | alerta — carregado, nunca executado |

**Diagnóstico:** O deploy da Sprint 41 enviou os arquivos DAG para `/opt/airflow/dags/` mas não disparou nenhuma execução. A carga real ANS ainda não foi realizada na VPS. Pendência: trigger manual de cada DAG ou aguardar agendamento.


## Lista DAGs delta
```
dag_ingest_beneficiarios_cobertura     | /opt/airflow/dags/dag_ingest_beneficiarios_cobertura.py     | airflow | True     
dag_ingest_depara_sip_tuss             | /opt/airflow/dags/dag_ingest_depara_sip_tuss.py             | airflow | True     
dag_ingest_precificacao_ntrp           | /opt/airflow/dags/dag_ingest_precificacao_ntrp.py           | airflow | True     
dag_ingest_produto_plano               | /opt/airflow/dags/dag_ingest_produto_plano.py               | airflow | True     
dag_ingest_rede_assistencial           | /opt/airflow/dags/dag_ingest_rede_assistencial.py           | airflow | True     
dag_ingest_rede_prestadores            | /opt/airflow/dags/dag_ingest_rede_prestadores.py            | airflow | True     
dag_ingest_regulatorios_complementares | /opt/airflow/dags/dag_ingest_regulatorios_complementares.py | airflow | True     
dag_ingest_ressarcimento_sus           | /opt/airflow/dags/dag_ingest_ressarcimento_sus.py           | airflow | True     
dag_ingest_sip_delta                   | /opt/airflow/dags/dag_ingest_sip_delta.py                   | airflow | True     
dag_ingest_tiss                        | /opt/airflow/dags/dag_ingest_tiss.py                        | airflow | True     
dag_ingest_tiss_subfamilias            | /opt/airflow/dags/dag_ingest_tiss_subfamilias.py            | airflow | True     
dag_ingest_tuss                        | /opt/airflow/dags/dag_ingest_tuss.py                        | airflow | True     
dag_ingest_tuss_oficial                | /opt/airflow/dags/dag_ingest_tuss_oficial.py                | airflow | True     
```

## Últimas execuções: dag_ingest_produto_plano
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_produto_plano
```

## Últimas execuções: dag_ingest_tuss_oficial
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_tuss_oficial
```

## Últimas execuções: dag_ingest_tiss_subfamilias
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_tiss_subfamilias
```

## Últimas execuções: dag_ingest_sip_delta
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_sip_delta
```

## Últimas execuções: dag_ingest_ressarcimento_sus
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_ressarcimento_sus
```

## Últimas execuções: dag_ingest_precificacao_ntrp
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_precificacao_ntrp
```

## Últimas execuções: dag_ingest_rede_prestadores
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_rede_prestadores
```

## Últimas execuções: dag_ingest_regulatorios_complementares
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit

airflow command error: unrecognized arguments: --limit 5, see help above.
AVISO: falha ao consultar dag_ingest_regulatorios_complementares
```

## Últimas execuções: dag_ingest_beneficiarios_cobertura
```

airflow command error: unrecognized arguments: --limit 5, see help above.
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config         View configuration
      connections    Manage connections
      dags           Manage DAGs
      db             Database operations
      jobs           Manage jobs
      pools          Manage pools
      providers      Display providers
      roles          Manage roles
      tasks          Manage tasks
      users          Manage users
      variables      Manage variables

    Commands:
      cheat-sheet    Display cheat sheet
      dag-processor  Start a standalone Dag Processor instance
      info           Show information about current Airflow and environment
      kerberos       Start a kerberos ticket renewer
      plugins        Dump information about loaded plugins
      rotate-fernet-key
                     Rotate encrypted connection credentials and variables
      scheduler      Start a scheduler instance
      standalone     Run an all-in-one copy of Airflow
      sync-perm      Update permissions for existing roles and optionally DAGs
      triggerer      Start a triggerer instance
      version        Show the version
      webserver      Start a Airflow webserver instance

Options:
  -h, --help         show this help message and exit
AVISO: falha ao consultar dag_ingest_beneficiarios_cobertura
```

