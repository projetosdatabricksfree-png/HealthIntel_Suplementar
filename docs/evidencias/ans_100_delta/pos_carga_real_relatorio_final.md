# Relatório Final — Validação Pós-Carga Real ANS (Sprint 42)

**Data/hora:** 2026-05-11T22:07:46Z  
**Commit:** e665fbf  
**VPS:** 5.189.160.27  
**Executado por:** Sprint 42 — validar_pos_carga_real_sprint_42.sh  

---

## 1. Status dos Containers

| Serviço | Status |
|---|---|
| healthintel_postgres | Up 3 days (healthy) |
| healthintel_mongo | Up 3 days (healthy) |
| healthintel_redis | Up 3 days (healthy) |
| healthintel_airflow_scheduler | Up 3 days (healthy) |
| healthintel_airflow_webserver | Up 3 days (healthy) |
| healthintel_api | Up 3 days |
| healthintel_nginx | Up 3 days |
| healthintel_frontend | Up 29 minutes |
| healthintel_grafana | Up 8 hours |

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_ambiente.md`

**Conclusão:** ✅ Ambiente VPS íntegro — todos os serviços Up.

---

## 2. API Health Check

| Endpoint | Resultado |
|---|---|
| `/saude` (interno VPS) | HTTP 200 `{"status":"ok"}` |
| `/prontidao` (interno VPS) | HTTP 401 (protegido por auth — correto) |
| `app.healthintel.com.br` (externo) | HTTP 200 |

**Observação:** `/saude` externo via `api.healthintel.com.br` retorna 400 "Invalid host header" — comportamento do Caddy com IP não autorizado. Interno funciona corretamente.

**Conclusão:** ✅ API operacional.

---

## 3. Status dos DAGs Delta ANS

| DAG | Carregado | Ativo | Execuções |
|---|---|---|---|
| dag_ingest_produto_plano | ✅ | True | ❌ Nenhuma |
| dag_ingest_tuss_oficial | ✅ | True | ❌ Nenhuma |
| dag_ingest_tiss_subfamilias | ✅ | True | ❌ Nenhuma |
| dag_ingest_sip_delta | ✅ | True | ❌ Nenhuma |
| dag_ingest_ressarcimento_sus | ✅ | True | ❌ Nenhuma |
| dag_ingest_precificacao_ntrp | ✅ | True | ❌ Nenhuma |
| dag_ingest_rede_prestadores | ✅ | True | ❌ Nenhuma |
| dag_ingest_regulatorios_complementares | ✅ | True | ❌ Nenhuma |
| dag_ingest_beneficiarios_cobertura | ✅ | True | ❌ Nenhuma |

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_dags.md`

**Conclusão:** ⚠️ DAGs carregados mas nunca executados. Carga real não realizada.

---

## 4. Status de `plataforma.arquivo_fonte_ans`

```
status | total_arquivos
-------+----------------
(0 rows)
```

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_status_arquivos.md`

**Conclusão:** ❌ Tabela vazia. Nenhum arquivo ANS foi baixado nem processado na VPS.

---

## 5. Contagens `api_ans` — Tabelas Delta

**Total de tabelas em api_ans:** 60 (pré-Sprint 41)  
**Tabelas delta existentes:** 0 / 20

Todas as 20 tabelas da Sprint 41 estão ausentes — erro "relation does not exist" para `api_produto_plano`, `api_tuss_procedimento_vigente` e demais.

**Root cause:** `dbt build --select tag:delta_ans_100` não foi executado na VPS após o deploy.

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_api_ans_counts.md`

**Conclusão:** ❌ Tabelas delta api_ans ausentes.

---

## 6. Contagens `consumo_ans` — Tabelas Delta

**Total de tabelas em consumo_ans:** 8 (pré-Sprint 41)  
**Tabelas delta existentes:** 0 / 11

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_consumo_ans_counts.md`

**Conclusão:** ❌ Tabelas delta consumo_ans ausentes.

---

## 7. Validação TISS/RPC — Janela 24 Meses

**Status:** Não validável — tabelas ausentes.

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_tiss_rpc_24_meses.md`

**Conclusão:** ⏳ Pendente de ingestão + dbt build na VPS.

---

## 8. Validação TUSS Oficial

**Status:** Não validável — `api_tuss_procedimento_vigente` ausente.

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_tuss_oficial_busca.md`

**Conclusão:** ⏳ Pendente de `dag_ingest_tuss_oficial` + dbt build.

---

## 9. Grants Finais

| Role | Schema | Privilégios |
|---|---|---|
| healthintel | api_ans | 420 |
| healthintel | consumo_ans | 56 |
| healthintel | consumo_premium_ans | 77 |
| healthintel_cliente_reader | consumo_ans | 8 |
| healthintel_premium_reader | consumo_premium_ans | 11 |

**Grants indevidos em bruto_ans / stg_ans / int_ans / nucleo_ans:** 0 rows ✅

**Evidência:** `docs/evidencias/ans_100_delta/pos_carga_real_grants.md`

**Conclusão:** ✅ Grants corretos — acesso comercial liberado, acesso interno protegido.

---

## 10. Falhas Encontradas

| Item | Falha | Diagnóstico |
|---|---|---|
| plataforma.arquivo_fonte_ans | Vazia | Nenhum DAG de ingestão executado na VPS |
| api_ans — 20 tabelas delta | Ausentes | dbt build não executado na VPS |
| consumo_ans — 11 tabelas delta | Ausentes | dbt build não executado na VPS |
| TISS/RPC 24 meses | Não validado | Tabelas ausentes |
| TUSS oficial | Não validado | Tabela ausente |

---

## 11. Pendências Pós-Carga Real

Para completar a Sprint 42, é necessário:

1. **Executar os 9 DAGs delta** na VPS:
   ```bash
   ssh -i ~/.ssh/healthintel_vps root@5.189.160.27 \
     'cd /opt/healthintel && docker compose -f infra/docker-compose.yml exec -T airflow-scheduler \
      airflow dags trigger dag_ingest_tuss_oficial'
   ```
   Repetir para cada DAG.

2. **Aguardar conclusão das ingestões** — monitorar `plataforma.arquivo_fonte_ans` e `plataforma.job`.

3. **Executar dbt build** na VPS:
   ```bash
   ssh -i ~/.ssh/healthintel_vps root@5.189.160.27 \
     'cd /opt/healthintel && docker compose -f infra/docker-compose.yml exec -T api \
      bash -c "cd /app && dbt build --select tag:delta_ans_100 --target prod"'
   ```

4. **Re-executar** `bash scripts/validar_pos_carga_real_sprint_42.sh` após as ingestões.

5. **Atualizar** este relatório com os dados reais.

---

## 12. Decisão Final

**Classificação:** ❌ Não OK para demonstração comercial com dados reais

**Justificativa:**
- O ambiente VPS está íntegro e a API está operacional.
- Os grants estão corretos — nenhum acesso indevido.
- Os 9 DAGs delta estão carregados no Airflow.
- **Porém:** Nenhum DAG foi executado → nenhuma ingestão real → nenhuma tabela delta criada.
- As 20 tabelas `api_ans` e 11 tabelas `consumo_ans` da Sprint 41 não existem na VPS.
- TISS, RPC e TUSS não podem ser validados sem as tabelas.

**Próximo estado esperado:** OK com ressalvas — após ingestão + dbt build, o produto estará disponível para demonstração, com a ressalva de que endpoints FastAPI para os novos datasets ainda não existem (escopo de sprint posterior, conforme §11.4 da Sprint 41).

---

*Gerado por: Sprint 42 — scripts/validar_pos_carga_real_sprint_42.sh*
