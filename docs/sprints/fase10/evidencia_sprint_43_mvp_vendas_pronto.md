# Evidencia Sprint 43 - MVP Vendas

Data: 2026-05-13 22:38 Europe/Berlin

## Estado Comercial

| Dominio | api_rows | consumo_rows | DAG / processamento | dbt | Status comercial |
| --- | ---: | ---: | --- | --- | --- |
| Operadoras/CADOP | 1.107 | 757 em `consumo_operadora_360` | `dag_ingest_cadop` success; `dag_mestre_mensal` success | OK | VENDAVEL |
| Produto/Plano | 163.661 | 163.661 | `dag_ingest_produto_plano` success | OK | VENDAVEL |
| TUSS oficial | 64.654 | 64.654 | `dag_ingest_tuss_oficial` success | OK | VENDAVEL |
| SIB Beneficiarios | 803 prata operadora; 59.892 bronze municipio | 757 operadora / 646 municipio | `dag_ingest_sib` success acionada pelo mestre | OK | VENDAVEL_COM_RESSALVA |
| IDSS | 13.072 | 0 | `dag_anual_idss` success nesta rodada | OK | VENDAVEL |
| IGR | 136.908 | 0 | `dag_ingest_igr` success nesta rodada | OK | VENDAVEL |
| NIP | 53.637 | 0 | `dag_ingest_nip` success nesta rodada | OK | VENDAVEL |
| Regulatorio consolidado | 125.287 | 0 | Recalculado por IGR/NIP | OK | VENDAVEL |
| Financeiro DIOPS/FIP | 1.019 em `api_prata_diops`; `api_financeiro_operadora_mensal` 0 | 1.013 | `dag_ingest_diops` success; dbt financeiro build success | OK | VENDAVEL_COM_RESSALVA |
| Glosa | `api_prata_glosa` pendente de refresh especifico | 0 | `dag_ingest_glosa` success anterior | Parcial | VENDAVEL_COM_RESSALVA |
| Prudencial | Bronze 11.216 | 0 | `dag_ingest_prudencial` success anterior | Parcial | VENDAVEL_COM_RESSALVA |
| Regime Especial | Bronze 118 | 0 | `dag_ingest_regime_especial` success anterior | Parcial | VENDAVEL_COM_RESSALVA |
| Taxa Resolutividade | Bronze 63.366 | 0 | `dag_ingest_taxa_resolutividade` success anterior | Parcial | VENDAVEL_COM_RESSALVA |
| CNES/Rede assistencial | `api_cnes_municipio` 0; `api_rede_assistencial` 0 | 0 | CNES fonte DATASUS fora do pipeline ANS; rede prestadores em processamento | Pendente | EM_VALIDACAO |
| Rede prestadores complementar | 0 API; 9.912.834 bronze em `produto_prestador_hospitalar` no momento da evidencia | 0 | `dag_ingest_rede_prestadores` running | Pendente | EM_PROCESSAMENTO |
| TISS | 0 | 0 | Fonte SP/REM 2025 nao encontrada | Pendente | EM_VALIDACAO |
| SIP | 0 API; bronze `sip_mapa_assistencial` ja existente | 0 | `dag_ingest_sip_delta` success anterior | Pendente | EM_VALIDACAO |
| NTRP | 0 APIs principais | 0 | Falha anterior por 137/encoding; streaming corrigido mas nao reprocessado nesta janela | Pendente | EM_VALIDACAO |

## Correcoes Nesta Rodada

- Corrigido `scripts/materializar_regulatorio_generico.py` removendo comentarios `# noqa` de SQL enviado ao Postgres.
- Corrigido `dag_mestre_mensal` para nao depender de `postgres_default`, usando `SessionLocal`.
- Corrigido `dag_dbt_freshness` para executar freshness no recorte de fontes reais carregadas do MVP.
- Corrigido streaming em `ingestao_delta_ans.py` para nao ler CSV inteiro ao detectar encoding.
- Ativado streaming para `painel_precificacao`, `produto_prestador_hospitalar` e `operadora_prestador_nao_hospitalar`.
- Serializada `dag_ingest_rede_prestadores` para evitar cargas pesadas paralelas.
- Tornado idempotente o registro de `arquivo_fonte_ans` quando hash duplicado ja existe.

## Validacoes

- `dag_anual_idss`: success; `api_prata_idss` 13.072.
- `dag_ingest_igr`: success; `api_prata_igr` 136.908.
- `dag_ingest_nip`: success; `api_prata_nip` 53.637.
- `dag_mestre_mensal`: success.
- `dag_dbt_freshness`: success.
- dbt financeiro: build success, PASS=19, ERROR=0.
- dbt parse/compile do recorte MVP: success.
- API `/saude`: OK.

## Decisao

- MVP VENDAVEL: NAO, enquanto CNES/Rede segue sem serving final e a DAG de rede prestadores ainda esta running.
- PODE INICIAR VENDAS COM ESCOPO CONTROLADO: SIM, se o escopo excluir CNES/Rede detalhada, TISS, SIP e NTRP e usar apenas Operadoras, Produto/Plano, TUSS, SIB basico, Regulatorio e DIOPS.
- CORE API COMPLETA: NAO.
