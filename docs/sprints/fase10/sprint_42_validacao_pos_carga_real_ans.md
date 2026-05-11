# Sprint 42 — Validação Pós-Carga Real ANS na VPS

> Projeto: HealthIntel Suplementar  
> Objetivo: validar a carga real pós-deploy da Sprint 41 na VPS, monitorando DAGs, status de arquivos ANS, contagens de tabelas finais, retenção TISS/RPC, TUSS oficial, grants e evidências auditáveis.  
> Escopo: validação operacional dos dados reais carregados nas camadas `api_ans` e `consumo_ans`, sem alterar arquitetura, billing, autenticação, middleware ou deploy.

---

## 0. Premissas obrigatórias

- [ ] Não alterar lógica de produção.
- [ ] Não alterar `deploy.yml`.
- [ ] Não alterar `ci.yml`.
- [ ] Não alterar billing.
- [ ] Não alterar autenticação.
- [ ] Não alterar middleware.
- [ ] Não recriar tabelas.
- [ ] Não truncar tabelas.
- [ ] Não apagar dados.
- [ ] Não rodar carga destrutiva.
- [ ] Não mascarar falhas.
- [ ] Não marcar validação como concluída sem evidência.
- [ ] Registrar toda consulta executada em arquivo de evidência.
- [ ] Registrar diagnóstico explícito para DAG, tabela ou endpoint com falha.
- [ ] Validar somente o que foi deployado e carregado.
- [ ] Preservar a arquitetura atual: `api_ans` para API, `consumo_ans` para SQL Standard e `consumo_premium_ans` para SQL Premium.
- [ ] Não expor `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans` ou `plataforma` para cliente final.

---

## 1. Contexto da sprint

A Sprint 41 foi fechada operacionalmente com:

- [x] Datasets delta ANS implementados.
- [x] Modelos `api_ans` publicados.
- [x] Modelos `consumo_ans` publicados.
- [x] Grants aplicados.
- [x] CI verde.
- [x] Deploy VPS executado.
- [x] `dbt build --select tag:delta_ans_100` com `PASS=162 ERROR=0`.
- [x] `pytest ingestao/tests/` com 101 passed.
- [x] `pytest api/tests/` com 114 passed.
- [x] Smokes SQL estruturais executados.
- [x] Evidências da Sprint 41 criadas.

Esta Sprint 42 não implementa novos datasets.  
Ela valida a **carga real na VPS** e transforma a entrega estrutural em entrega demonstrável com dados reais.

---

## 2. Infraestrutura alvo

### Ambiente local

```text
/home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar
```

### Ambiente VPS

```text
Host: 5.189.160.27
Usuário: root
Projeto: /opt/healthintel
SSH key: ~/.ssh/healthintel_vps
```

### Comando base SSH

```bash
ssh -i ~/.ssh/healthintel_vps root@5.189.160.27
```

### Diretório de evidências

```text
docs/evidencias/ans_100_delta/
```

---

## 3. Fora do escopo

Esta sprint não deve implementar novas features.

- [ ] Não criar nova arquitetura.
- [ ] Não alterar regra comercial.
- [ ] Não alterar planos comerciais.
- [ ] Não implementar billing por créditos.
- [ ] Não implementar catálogo comercial automático.
- [ ] Não criar novos endpoints FastAPI, exceto se já houver tarefa formal separada.
- [ ] Não criar novas tabelas `nucleo_ans`.
- [ ] Não criar novas tabelas `consumo_premium_ans`.
- [ ] Não implementar documentais classificados como `não_comercial`.
- [ ] Não refatorar DAGs existentes, salvo correção mínima e comprovada de bug operacional.
- [ ] Não alterar modelos dbt já aprovados, salvo correção mínima comprovada por falha real.
- [ ] Não alterar scripts de deploy.
- [ ] Não alterar CI/CD.

---

# 4. Histórias da sprint

## História 1 — Validar ambiente da VPS pós-deploy

Como mantenedor do HealthIntel,  
quero validar que a VPS está saudável após o deploy,  
para garantir que a carga real será executada sobre ambiente íntegro.

### Tasks

- [ ] Acessar a VPS via SSH.
- [ ] Validar containers com `docker compose ps`.
- [ ] Validar Postgres.
- [ ] Validar Mongo.
- [ ] Validar Redis.
- [ ] Validar API.
- [ ] Validar Airflow, se usado na carga.
- [ ] Validar Nginx/Caddy, se aplicável.
- [ ] Executar health check público da API.
- [ ] Executar readiness check da API, respeitando autenticação se houver.
- [ ] Registrar saída em evidência.

### Comandos

```bash
ssh -i ~/.ssh/healthintel_vps root@5.189.160.27 'cd /opt/healthintel && docker compose ps'
```

```bash
curl -i https://api.healthintel.com.br/saude
curl -i https://api.healthintel.com.br/ready
curl -i https://app.healthintel.com.br
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_ambiente.md
```

### Critérios de aceite

- [ ] Postgres está `Up` ou `healthy`.
- [ ] Mongo está `Up` ou `healthy`.
- [ ] Redis está `Up` ou `healthy`.
- [ ] API está `Up` ou `healthy`.
- [ ] Airflow está operacional quando aplicável.
- [ ] `/saude` responde HTTP 200.
- [ ] `/ready` responde conforme regra de autenticação esperada.
- [ ] Evidência salva.

---

## História 2 — Rodar e monitorar DAGs Delta ANS

Como mantenedor do HealthIntel,  
quero monitorar os DAGs delta ANS na VPS,  
para confirmar que as cargas reais foram executadas ou diagnosticar falhas.

### DAGs esperados

- [ ] `dag_ingest_produto_plano`
- [ ] `dag_ingest_tuss_oficial`
- [ ] `dag_ingest_tiss_subfamilias`
- [ ] `dag_ingest_sip_delta`
- [ ] `dag_ingest_ressarcimento_sus`
- [ ] `dag_ingest_precificacao_ntrp`
- [ ] `dag_ingest_rede_prestadores`
- [ ] `dag_ingest_regulatorios_complementares`
- [ ] `dag_ingest_beneficiarios_cobertura`

### Tasks

- [ ] Listar DAGs delta disponíveis no Airflow.
- [ ] Verificar última execução de cada DAG.
- [ ] Verificar estado dos DAGs.
- [ ] Verificar tasks com falha.
- [ ] Rodar manualmente somente DAGs idempotentes e seguros.
- [ ] Registrar logs relevantes.
- [ ] Classificar cada DAG como `OK`, `alerta` ou `falha`.
- [ ] Registrar evidência.

### Comandos

```bash
ssh -i ~/.ssh/healthintel_vps root@5.189.160.27 'cd /opt/healthintel && docker compose exec -T airflow-scheduler airflow dags list | grep -E "produto|tuss|tiss|sip|ressarcimento|precificacao|rede|regulatorios|beneficiarios|delta" || true'
```

```bash
ssh -i ~/.ssh/healthintel_vps root@5.189.160.27 'cd /opt/healthintel && docker compose exec -T airflow-scheduler airflow dags list-runs -d dag_ingest_tuss_oficial --limit 5'
```

Somente se o DAG for idempotente:

```bash
ssh -i ~/.ssh/healthintel_vps root@5.189.160.27 'cd /opt/healthintel && docker compose exec -T airflow-scheduler airflow dags trigger dag_ingest_tuss_oficial'
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_dags.md
```

### Critérios de aceite

- [ ] DAGs existentes foram listados.
- [ ] Última execução registrada.
- [ ] Falhas foram diagnosticadas.
- [ ] DAGs críticos foram classificados.
- [ ] Logs relevantes salvos.
- [ ] Evidência salva.

---

## História 3 — Validar `plataforma.arquivo_fonte_ans`

Como mantenedor do HealthIntel,  
quero verificar o status dos arquivos fonte ANS,  
para confirmar se os arquivos foram baixados, carregados, ignorados por duplicidade ou ficaram com erro.

### Tasks

- [ ] Listar status por família.
- [ ] Listar status geral.
- [ ] Validar famílias delta ANS.
- [ ] Identificar arquivos com erro.
- [ ] Identificar arquivos pendentes.
- [ ] Identificar arquivos sem parser.
- [ ] Registrar status final.

### SQL — status por família

```sql
select
    familia,
    status,
    count(*) as total_arquivos
from plataforma.arquivo_fonte_ans
group by familia, status
order by familia, status;
```

### SQL — status geral

```sql
select
    status,
    count(*) as total_arquivos
from plataforma.arquivo_fonte_ans
group by status
order by status;
```

### SQL — famílias delta ANS

```sql
select
    familia,
    count(*) filter (where status in ('carregado', 'bronze_generico', 'arquivado_r2')) as sucesso,
    count(*) filter (where status like 'erro%') as erro,
    count(*) filter (where status in ('baixado_sem_parser', 'pendente')) as pendente,
    count(*) as total
from plataforma.arquivo_fonte_ans
where familia in (
    'produtos_planos',
    'tuss',
    'tiss',
    'sip',
    'ressarcimento_sus',
    'precificacao_ntrp',
    'rede_prestadores',
    'regulatorios_complementares',
    'beneficiarios_cobertura'
)
group by familia
order by familia;
```

### SQL — descobrir nomes reais de família

```sql
select distinct familia
from plataforma.arquivo_fonte_ans
order by familia;
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_status_arquivos.md
```

### Critérios de aceite

- [ ] Status por família registrado.
- [ ] Status geral registrado.
- [ ] Famílias delta avaliadas.
- [ ] Erros documentados.
- [ ] Pendências documentadas.
- [ ] Evidência salva.

---

## História 4 — Conferir contagem das tabelas `api_ans` novas

Como mantenedor do HealthIntel,  
quero validar a existência e volume das tabelas finais `api_ans`,  
para confirmar que a camada de serviço está disponível após a carga real.

### Tabelas `api_ans` prioritárias

- [ ] `api_ans.api_produto_plano`
- [ ] `api_ans.api_historico_plano`
- [ ] `api_ans.api_plano_servico_opcional`
- [ ] `api_ans.api_quadro_auxiliar_corresponsabilidade`
- [ ] `api_ans.api_tuss_procedimento_vigente`
- [ ] `api_ans.api_tiss_ambulatorial_operadora_mes`
- [ ] `api_ans.api_tiss_hospitalar_operadora_mes`
- [ ] `api_ans.api_tiss_plano_mes`
- [ ] `api_ans.api_sip_assistencial_operadora`
- [ ] `api_ans.api_ressarcimento_beneficiario_abi`
- [ ] `api_ans.api_ressarcimento_sus_operadora_plano`
- [ ] `api_ans.api_ressarcimento_hc`
- [ ] `api_ans.api_ressarcimento_cobranca_arrecadacao`
- [ ] `api_ans.api_ressarcimento_indice_pagamento`
- [ ] `api_ans.api_painel_precificacao`
- [ ] `api_ans.api_valor_comercial_medio_municipio`
- [ ] `api_ans.api_prestador_acreditado`
- [ ] `api_ans.api_alteracao_rede_hospitalar`
- [ ] `api_ans.api_penalidade_operadora`
- [ ] `api_ans.api_rpc_operadora_mes`

### SQL

```sql
select 'api_produto_plano' as tabela, count(*) as linhas from api_ans.api_produto_plano
union all
select 'api_historico_plano', count(*) from api_ans.api_historico_plano
union all
select 'api_plano_servico_opcional', count(*) from api_ans.api_plano_servico_opcional
union all
select 'api_quadro_auxiliar_corresponsabilidade', count(*) from api_ans.api_quadro_auxiliar_corresponsabilidade
union all
select 'api_tuss_procedimento_vigente', count(*) from api_ans.api_tuss_procedimento_vigente
union all
select 'api_tiss_ambulatorial_operadora_mes', count(*) from api_ans.api_tiss_ambulatorial_operadora_mes
union all
select 'api_tiss_hospitalar_operadora_mes', count(*) from api_ans.api_tiss_hospitalar_operadora_mes
union all
select 'api_tiss_plano_mes', count(*) from api_ans.api_tiss_plano_mes
union all
select 'api_sip_assistencial_operadora', count(*) from api_ans.api_sip_assistencial_operadora
union all
select 'api_ressarcimento_beneficiario_abi', count(*) from api_ans.api_ressarcimento_beneficiario_abi
union all
select 'api_ressarcimento_sus_operadora_plano', count(*) from api_ans.api_ressarcimento_sus_operadora_plano
union all
select 'api_ressarcimento_hc', count(*) from api_ans.api_ressarcimento_hc
union all
select 'api_ressarcimento_cobranca_arrecadacao', count(*) from api_ans.api_ressarcimento_cobranca_arrecadacao
union all
select 'api_ressarcimento_indice_pagamento', count(*) from api_ans.api_ressarcimento_indice_pagamento
union all
select 'api_painel_precificacao', count(*) from api_ans.api_painel_precificacao
union all
select 'api_valor_comercial_medio_municipio', count(*) from api_ans.api_valor_comercial_medio_municipio
union all
select 'api_prestador_acreditado', count(*) from api_ans.api_prestador_acreditado
union all
select 'api_alteracao_rede_hospitalar', count(*) from api_ans.api_alteracao_rede_hospitalar
union all
select 'api_penalidade_operadora', count(*) from api_ans.api_penalidade_operadora
union all
select 'api_rpc_operadora_mes', count(*) from api_ans.api_rpc_operadora_mes
order by tabela;
```

### Interpretação

- [ ] Tabela não existe: falha estrutural.
- [ ] Tabela existe e está vazia: pendente de carga real.
- [ ] Tabela existe e tem linhas: OK.
- [ ] Tabela com erro de permissão: falha de grant ou conexão.

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_api_ans_counts.md
```

---

## História 5 — Conferir contagem das tabelas `consumo_ans` novas

Como mantenedor do HealthIntel,  
quero validar as tabelas `consumo_ans` entregues para SQL Standard,  
para confirmar que a camada de consumo está disponível após carga real.

### Tabelas `consumo_ans` prioritárias

- [ ] `consumo_ans.consumo_produto_plano`
- [ ] `consumo_ans.consumo_historico_plano`
- [ ] `consumo_ans.consumo_plano_servico_opcional`
- [ ] `consumo_ans.consumo_tuss_procedimento_vigente`
- [ ] `consumo_ans.consumo_tiss_utilizacao_operadora_mes`
- [ ] `consumo_ans.consumo_sip_assistencial_operadora`
- [ ] `consumo_ans.consumo_ressarcimento_sus_operadora`
- [ ] `consumo_ans.consumo_precificacao_plano`
- [ ] `consumo_ans.consumo_rede_acreditacao`
- [ ] `consumo_ans.consumo_regulatorio_complementar_operadora`
- [ ] `consumo_ans.consumo_beneficiarios_cobertura_municipio`

### SQL

```sql
select 'consumo_produto_plano' as tabela, count(*) as linhas from consumo_ans.consumo_produto_plano
union all
select 'consumo_historico_plano', count(*) from consumo_ans.consumo_historico_plano
union all
select 'consumo_plano_servico_opcional', count(*) from consumo_ans.consumo_plano_servico_opcional
union all
select 'consumo_tuss_procedimento_vigente', count(*) from consumo_ans.consumo_tuss_procedimento_vigente
union all
select 'consumo_tiss_utilizacao_operadora_mes', count(*) from consumo_ans.consumo_tiss_utilizacao_operadora_mes
union all
select 'consumo_sip_assistencial_operadora', count(*) from consumo_ans.consumo_sip_assistencial_operadora
union all
select 'consumo_ressarcimento_sus_operadora', count(*) from consumo_ans.consumo_ressarcimento_sus_operadora
union all
select 'consumo_precificacao_plano', count(*) from consumo_ans.consumo_precificacao_plano
union all
select 'consumo_rede_acreditacao', count(*) from consumo_ans.consumo_rede_acreditacao
union all
select 'consumo_regulatorio_complementar_operadora', count(*) from consumo_ans.consumo_regulatorio_complementar_operadora
union all
select 'consumo_beneficiarios_cobertura_municipio', count(*) from consumo_ans.consumo_beneficiarios_cobertura_municipio
order by tabela;
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_consumo_ans_counts.md
```

### Critérios de aceite

- [ ] Tabelas existem.
- [ ] Contagens registradas.
- [ ] Tabelas vazias justificadas como pendentes de carga real.
- [ ] Falhas estruturais diagnosticadas.
- [ ] Evidência salva.

---

## História 6 — Validar TISS/RPC com janela de 24 meses

Como mantenedor do HealthIntel,  
quero validar que TISS e RPC respeitam a janela quente de 24 meses,  
para evitar explosão de volume no Postgres e preservar a política operacional da Sprint 41.

### Tasks

- [ ] Validar `api_tiss_ambulatorial_operadora_mes`.
- [ ] Validar `api_tiss_hospitalar_operadora_mes`.
- [ ] Validar `api_tiss_plano_mes`.
- [ ] Validar `api_rpc_operadora_mes`.
- [ ] Validar `consumo_tiss_utilizacao_operadora_mes`.
- [ ] Confirmar `competencia_min`.
- [ ] Confirmar `competencia_max`.
- [ ] Confirmar quantidade de competências distintas.
- [ ] Confirmar que `qtd_competencias <= 24`, quando houver dados.
- [ ] Confirmar formato `YYYYMM`.

### SQL — API

```sql
select
    'api_tiss_ambulatorial_operadora_mes' as tabela,
    min(competencia) as competencia_min,
    max(competencia) as competencia_max,
    count(distinct competencia) as qtd_competencias,
    count(*) as linhas
from api_ans.api_tiss_ambulatorial_operadora_mes
union all
select
    'api_tiss_hospitalar_operadora_mes',
    min(competencia),
    max(competencia),
    count(distinct competencia),
    count(*)
from api_ans.api_tiss_hospitalar_operadora_mes
union all
select
    'api_tiss_plano_mes',
    min(competencia),
    max(competencia),
    count(distinct competencia),
    count(*)
from api_ans.api_tiss_plano_mes
union all
select
    'api_rpc_operadora_mes',
    min(competencia),
    max(competencia),
    count(distinct competencia),
    count(*)
from api_ans.api_rpc_operadora_mes;
```

### SQL — consumo

```sql
select
    'consumo_tiss_utilizacao_operadora_mes' as tabela,
    min(competencia) as competencia_min,
    max(competencia) as competencia_max,
    count(distinct competencia) as qtd_competencias,
    count(*) as linhas
from consumo_ans.consumo_tiss_utilizacao_operadora_mes;
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_tiss_rpc_24_meses.md
```

### Critérios de aceite

- [ ] TISS API respeita 24 meses.
- [ ] RPC API respeita 24 meses.
- [ ] TISS consumo respeita 24 meses.
- [ ] Competência está em formato `YYYYMM`.
- [ ] Evidência salva.

---

## História 7 — Validar TUSS oficial com busca por código e descrição

Como mantenedor do HealthIntel,  
quero validar a TUSS oficial carregada a partir do `TUSS.zip`,  
para garantir que a tabela de referência de procedimentos está apta para consulta.

### Tasks

- [ ] Contar TUSS vigente.
- [ ] Verificar duplicidade por `codigo_tuss + versao_tuss`.
- [ ] Buscar registros por código.
- [ ] Buscar registros por descrição.
- [ ] Validar `vigencia_inicio`.
- [ ] Validar `vigencia_fim`.
- [ ] Validar `is_tuss_vigente`.
- [ ] Validar tabela de consumo.
- [ ] Registrar evidência.

### SQL — contagem

```sql
select
    count(*) as total_tuss_vigente
from api_ans.api_tuss_procedimento_vigente;
```

### SQL — duplicidade

```sql
select
    codigo_tuss,
    versao_tuss,
    count(*) as total
from api_ans.api_tuss_procedimento_vigente
group by codigo_tuss, versao_tuss
having count(*) > 1
order by total desc
limit 20;
```

### SQL — busca por código

```sql
select
    codigo_tuss,
    descricao,
    versao_tuss,
    vigencia_inicio,
    vigencia_fim,
    is_tuss_vigente
from api_ans.api_tuss_procedimento_vigente
where codigo_tuss is not null
limit 20;
```

### SQL — busca por descrição

```sql
select
    codigo_tuss,
    descricao,
    versao_tuss,
    is_tuss_vigente
from api_ans.api_tuss_procedimento_vigente
where lower(descricao) like '%consulta%'
limit 20;
```

### SQL — consumo

```sql
select
    count(*) as total_tuss_consumo
from consumo_ans.consumo_tuss_procedimento_vigente;
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_tuss_oficial_busca.md
```

### Critérios de aceite

- [ ] TUSS oficial possui registros quando carga real foi executada.
- [ ] Duplicidades foram avaliadas.
- [ ] Busca por código retorna registros quando houver dados.
- [ ] Busca por descrição retorna registros quando houver dados.
- [ ] Consumo TUSS foi validado.
- [ ] Evidência salva.

---

## História 8 — Validar grants finais

Como mantenedor do HealthIntel,  
quero validar os grants das camadas finais,  
para garantir que clientes não acessem camadas internas e que as camadas comerciais estejam liberadas corretamente.

### Tasks

- [ ] Validar grants em `api_ans`.
- [ ] Validar grants em `consumo_ans`.
- [ ] Validar grants em `consumo_premium_ans`.
- [ ] Confirmar `healthintel_cliente_reader` em `consumo_ans`, quando aplicável.
- [ ] Confirmar `healthintel_premium_reader` em `consumo_premium_ans`, quando aplicável.
- [ ] Confirmar ausência de grants indevidos em `bruto_ans`.
- [ ] Confirmar ausência de grants indevidos em `stg_ans`.
- [ ] Confirmar ausência de grants indevidos em `int_ans`.
- [ ] Confirmar ausência de grants indevidos em `nucleo_ans`.
- [ ] Salvar evidência.

### SQL — grants finais

```sql
select
    grantee,
    table_schema,
    count(*) as total_privilegios
from information_schema.role_table_grants
where table_schema in ('api_ans', 'consumo_ans', 'consumo_premium_ans')
group by grantee, table_schema
order by grantee, table_schema;
```

### SQL — grants indevidos em camadas internas

```sql
select
    grantee,
    table_schema,
    count(*) as total_privilegios
from information_schema.role_table_grants
where table_schema in ('bruto_ans', 'stg_ans', 'int_ans', 'nucleo_ans')
  and grantee in ('healthintel_cliente_reader', 'healthintel_premium_reader')
group by grantee, table_schema
order by grantee, table_schema;
```

### Resultado esperado

```text
zero linhas ou nenhum privilégio indevido em camadas internas
```

### Evidência

```text
docs/evidencias/ans_100_delta/pos_carga_real_grants.md
```

### Critérios de aceite

- [ ] Grants comerciais registrados.
- [ ] Ausência de acesso indevido validada.
- [ ] Evidência salva.

---

## História 9 — Consolidar relatório final pós-carga real

Como mantenedor do HealthIntel,  
quero consolidar a validação pós-carga real em um relatório final,  
para decidir se o produto está pronto para demonstração comercial com dados reais.

### Arquivo esperado

```text
docs/evidencias/ans_100_delta/pos_carga_real_relatorio_final.md
```

### Conteúdo obrigatório

- [ ] Data/hora da validação.
- [ ] Commit atual.
- [ ] Status dos containers.
- [ ] Status dos DAGs delta ANS.
- [ ] Status de `plataforma.arquivo_fonte_ans`.
- [ ] Contagem das tabelas `api_ans` novas.
- [ ] Contagem das tabelas `consumo_ans` novas.
- [ ] Validação TISS/RPC 24 meses.
- [ ] Validação TUSS oficial.
- [ ] Validação de grants.
- [ ] Falhas encontradas.
- [ ] Pendências pós-carga real.
- [ ] Decisão final:
  - [ ] OK para demonstração comercial.
  - [ ] OK com ressalvas.
  - [ ] Não OK.

### Critérios de aceite

- [ ] Relatório final criado.
- [ ] Todos os arquivos de evidência referenciados.
- [ ] Falhas não mascaradas.
- [ ] Decisão final explícita.
- [ ] Evidência salva.

---

## História 10 — Atualizar checklist da Sprint 41

Como mantenedor do HealthIntel,  
quero atualizar o checklist da Sprint 41 com base na carga real,  
para fechar corretamente os itens que dependiam de dados reais.

### Arquivo

```text
docs/sprints/fase10/sprint_41_delta_ans_100_faltantes.md
```

### Marcar `[x]` somente se houver evidência real

- [ ] Smoke de busca por código TUSS.
- [ ] Smoke de busca por texto TUSS.
- [ ] Sem duplicidade por código/versão.
- [ ] TISS 24 meses validado.
- [ ] RPC 24 meses validado.
- [ ] API responde por operadora/período, quando endpoint existir.
- [ ] Volume mínimo carregado, quando houver dados reais.
- [ ] Grants finais validados.
- [ ] Monitoramento pós-carga real concluído.

### Não marcar como `[x]`

- [ ] Itens sem dados carregados.
- [ ] Endpoints FastAPI inexistentes.
- [ ] Modelos premium não implementados.
- [ ] Modelos `nucleo_ans` não implementados.
- [ ] Documentais classificados como `não_comercial`.

### Critérios de aceite

- [ ] Checklist atualizado.
- [ ] Nenhum item marcado sem evidência.
- [ ] Pendências documentadas.
- [ ] Evidências referenciadas.

---

# 5. Arquivos esperados

## Evidências

- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_ambiente.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_dags.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_status_arquivos.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_api_ans_counts.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_consumo_ans_counts.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_tiss_rpc_24_meses.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_tuss_oficial_busca.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_grants.md`
- [ ] `docs/evidencias/ans_100_delta/pos_carga_real_relatorio_final.md`

## Scripts

- [ ] `scripts/smoke_delta_ans_100_api.sh`
- [ ] `scripts/smoke_delta_ans_100_sql.sql`
- [ ] `scripts/validar_pos_carga_real_sprint_42.sh`

## Documentação

- [ ] `docs/sprints/fase10/sprint_42_validacao_pos_carga_real_ans.md`
- [ ] Atualização de `docs/sprints/fase10/sprint_41_delta_ans_100_faltantes.md`

---

# 6. Hard gates

## Ambiente

- [ ] `docker compose ps` na VPS.
- [ ] Postgres saudável.
- [ ] Mongo saudável.
- [ ] Redis saudável.
- [ ] API saudável.
- [ ] Airflow saudável, quando aplicável.
- [ ] `/saude` HTTP 200.
- [ ] `/ready` validado conforme regra esperada.

## DAGs

- [ ] DAGs delta ANS listados.
- [ ] Últimas execuções registradas.
- [ ] Falhas diagnosticadas.
- [ ] Logs relevantes salvos.
- [ ] DAGs críticos classificados.

## Banco

- [ ] `plataforma.arquivo_fonte_ans` validada.
- [ ] Contagens `api_ans` registradas.
- [ ] Contagens `consumo_ans` registradas.
- [ ] TISS 24 meses validado.
- [ ] RPC 24 meses validado.
- [ ] TUSS oficial validada.
- [ ] Grants finais validados.
- [ ] Ausência de grants indevidos validada.

## Documentação

- [ ] Evidências criadas.
- [ ] Relatório final criado.
- [ ] Checklist Sprint 41 atualizado.
- [ ] CI verde.
- [ ] Deploy verde.

---

# 7. Critérios de fechamento

A Sprint 42 só pode ser marcada como fechada quando:

- [ ] Ambiente VPS validado.
- [ ] DAGs delta ANS monitorados.
- [ ] `plataforma.arquivo_fonte_ans` validada.
- [ ] Contagens `api_ans` registradas.
- [ ] Contagens `consumo_ans` registradas.
- [ ] TISS/RPC 24 meses validado.
- [ ] TUSS oficial validada por código e descrição.
- [ ] Grants finais validados.
- [ ] Relatório final pós-carga real criado.
- [ ] Checklist da Sprint 41 atualizado com evidência real.
- [ ] Evidências salvas em `docs/evidencias/ans_100_delta/`.
- [ ] CI passou.
- [ ] Deploy passou.

---

# 8. Não finalizar se

- [ ] Postgres estiver indisponível.
- [ ] API estiver indisponível.
- [ ] Airflow estiver indisponível quando necessário para carga.
- [ ] DAG delta crítico falhar sem diagnóstico.
- [ ] Tabela `api_ans` nova estiver ausente.
- [ ] Tabela `consumo_ans` nova estiver ausente.
- [ ] TUSS oficial estiver vazia sem justificativa.
- [ ] TISS exceder 24 meses nas tabelas API/consumo.
- [ ] RPC exceder 24 meses nas tabelas API/consumo.
- [ ] Cliente tiver grant indevido em `bruto_ans`, `stg_ans`, `int_ans` ou `nucleo_ans`.
- [ ] Evidências não forem salvas.
- [ ] Checklist for marcado sem evidência.
- [ ] Falhas forem omitidas.

---

# 9. Comandos de commit

```bash
git status
git add docs/evidencias/ans_100_delta docs/sprints/fase10/sprint_41_delta_ans_100_faltantes.md docs/sprints/fase10/sprint_42_validacao_pos_carga_real_ans.md scripts/smoke_delta_ans_100_api.sh scripts/smoke_delta_ans_100_sql.sql scripts/validar_pos_carga_real_sprint_42.sh
git commit -m "docs: criar sprint 42 de validacao pos-carga real ans"
git push origin main
```

Acompanhar:

```bash
gh run list --limit 5
gh run list --workflow=ci.yml --limit 3
gh run list --workflow=deploy.yml --limit 3
```

---

# 10. Resultado esperado

Ao final da Sprint 42:

- [ ] O ambiente da VPS estará validado.
- [ ] Os DAGs delta ANS estarão monitorados.
- [ ] O status dos arquivos fonte ANS estará auditado.
- [ ] As tabelas `api_ans` novas terão contagem registrada.
- [ ] As tabelas `consumo_ans` novas terão contagem registrada.
- [ ] TISS/RPC estarão validados com janela de 24 meses.
- [ ] TUSS oficial estará validada por código e descrição.
- [ ] Grants finais estarão validados.
- [ ] O relatório final pós-carga real estará salvo.
- [ ] A Sprint 41 estará atualizada com base em evidência real.
- [ ] O produto estará classificado como:
  - [ ] OK para demonstração comercial.
  - [ ] OK com ressalvas.
  - [ ] Não OK.

---

# 11. Prompt operacional para execução

```text
Você está trabalhando no projeto HealthIntel Suplementar.

Objetivo:
Executar a Sprint 42 — Validação Pós-Carga Real ANS na VPS.

Escopo:
Validar DAGs delta ANS, plataforma.arquivo_fonte_ans, contagens api_ans, contagens consumo_ans, retenção TISS/RPC 24 meses, TUSS oficial por código/descrição, grants finais e evidências pós-carga real.

Regras:
- Não alterar lógica de produção.
- Não alterar deploy.yml.
- Não alterar ci.yml.
- Não alterar billing.
- Não alterar autenticação.
- Não alterar middleware.
- Não recriar tabelas.
- Não truncar tabelas.
- Não apagar dados.
- Não rodar carga destrutiva.
- Não mascarar falhas.
- Não marcar validação como OK sem evidência.
- Toda consulta executada deve ser registrada.

Executar as histórias da sprint na ordem:
1. Validar ambiente VPS.
2. Rodar/monitorar DAGs delta ANS.
3. Conferir plataforma.arquivo_fonte_ans.
4. Conferir contagem das tabelas api_ans novas.
5. Conferir contagem das tabelas consumo_ans novas.
6. Validar TISS/RPC com janela de 24 meses.
7. Validar TUSS oficial com busca por código e descrição.
8. Validar grants finais.
9. Consolidar relatório final.
10. Atualizar checklist da Sprint 41.
11. Commitar e acompanhar CI/deploy.

Critérios:
- Evidências salvas em docs/evidencias/ans_100_delta/.
- Relatório final criado.
- Checklist atualizado sem mascarar pendências.
- CI verde.
- Deploy verde.
```
