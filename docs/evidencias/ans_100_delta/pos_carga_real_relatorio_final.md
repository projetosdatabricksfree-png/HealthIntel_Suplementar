# Relatorio Final - Validacao Pos-Carga Real ANS (Sprint 42)

**Data/hora:** 2026-05-13T11:28:52Z

**Commit VPS validado:** 072c13c

**VPS:** 5.189.160.27

**Execucao:** `scripts/validar_pos_carga_real_sprint_42.sh` + `dbt build --select tag:delta_ans_100`

---

## 1. Ambiente e deploy

- VPS em `/opt/healthintel` no commit `072c13c`.
- Containers principais `Up`; Postgres, Mongo, Redis, Airflow e API operacionais.
- CI GitHub verde para os commits:
  - `25e2bc5` / run `25794261398`
  - `67cc020` / run `25794831236`
  - `d98f304` / run `25795263440`
  - `072c13c` / run `25795744668`
- Deploy GitHub verde para `072c13c` / run `25795970097`.

Evidencia: `docs/evidencias/ans_100_delta/pos_carga_real_ambiente.md`.

---

## 2. Ingestao real executada

Runs mais recentes com sucesso:

- `dag_ingest_tuss_oficial`: `manual__2026-05-13T10:54:35+00:00`
- `dag_ingest_sip_delta`: `manual__2026-05-13T10:54:52+00:00`
- `dag_ingest_produto_plano`: `manual__2026-05-13T11:24:27+00:00`

Correcoes feitas durante a validacao:

- Discovery de diretorios oficiais ANS antes de baixar arquivos.
- Registro auditavel em `plataforma.arquivo_fonte_ans`.
- Carga direta/normalizada para fontes reais que nao batiam com aliases antigos.
- Idempotencia na auditoria apos falha parcial.
- Seletor dbt da DAG de produtos restrito a produtos/planos.

Evidencia: `docs/evidencias/ans_100_delta/pos_carga_real_dags.md`.

---

## 3. Auditoria de arquivos

Status final em `plataforma.arquivo_fonte_ans`:

```text
carregado  | 7
erro_carga | 3
```

Os 3 `erro_carga` sao tentativas historicas do arquivo `produto_tabela_auxiliar`
antes da correcao de truncamento/idempotencia. A tentativa corrigida ficou
`carregado`.

Evidencia: `docs/evidencias/ans_100_delta/pos_carga_real_status_arquivos.md`.

---

## 4. Contagens finais

Principais tabelas com dados reais:

```text
bruto_ans.produto_caracteristica          163969
bruto_ans.produto_tabela_auxiliar         877472
bruto_ans.tuss_terminologia_oficial       129402
bruto_ans.sip_mapa_assistencial             5903
api_ans.api_produto_plano                 163661
api_ans.api_historico_plano               163567
api_ans.api_quadro_auxiliar_corresponsabilidade 1032
api_ans.api_tuss_procedimento_vigente      64654
consumo_ans.consumo_produto_plano         163661
consumo_ans.consumo_historico_plano       163567
consumo_ans.consumo_tuss_procedimento_vigente 64654
```

SIP carregou bruto real, mas `api_sip_assistencial_operadora` e
`consumo_sip_assistencial_operadora` ficaram com 0 linhas porque o arquivo SIP
oficial carregado nao traz `registro_ans`, que e chave obrigatoria nos modelos
atuais.

Evidencias:

- `docs/evidencias/ans_100_delta/pos_carga_real_api_ans_counts.md`
- `docs/evidencias/ans_100_delta/pos_carga_real_consumo_ans_counts.md`

---

## 5. dbt e qualidade

Comando executado na VPS:

```bash
docker compose -f infra/docker-compose.yml run --rm dbt build --select tag:delta_ans_100
```

Resultado:

```text
PASS=161 WARN=1 ERROR=0 SKIP=0 TOTAL=162
```

Warning mantido:

- `relationships_stg_produto_caracteristica_registro_ans__registro_ans__ref_stg_cadop_`
- 57.074 registros de produtos nao encontraram correspondencia em `stg_cadop`.

Esse warning nao bloqueia o build, mas impede classificar a carga como "OK sem
ressalvas".

---

## 6. Pendencias reais

- TISS subfamilias ainda nao tem carga real validada; tabelas API/consumo TISS
  ficaram com 0 linhas.
- `DADOS_DE_PLANOS` oficial da ANS publica `PLANOS.zip` direto na pasta, sem
  ano/UF, e o arquivo nao traz `registro_ans`; isso exige ajuste de contrato
  antes de declarar cobertura TISS completa.
- SIP bruto foi carregado, mas a camada API/consumo atual filtra por
  `registro_ans`; sem enriquecimento ou contrato alternativo, a camada final
  fica vazia.
- Permanecem 3 linhas historicas `erro_carga` na auditoria, preservadas como
  evidencia de tentativas falhas antes da correcao.

---

## 7. Decisao final

**Classificacao:** OK com ressalvas.

Justificativa:

- Ambiente, CI e deploy estao verdes.
- `dag_ingest_tuss_oficial`, `dag_ingest_produto_plano` e
  `dag_ingest_sip_delta` executaram com sucesso.
- `dbt build --select tag:delta_ans_100` passou na VPS.
- Produtos/planos e TUSS oficial estao com dados reais em `api_ans` e
  `consumo_ans`.
- TISS subfamilias e SIP final ainda precisam de ajuste de contrato/fonte para
  nao declarar cobertura nacional/completa sem evidencia.

---

*Gerado por validacao operacional Codex em 2026-05-13.*
