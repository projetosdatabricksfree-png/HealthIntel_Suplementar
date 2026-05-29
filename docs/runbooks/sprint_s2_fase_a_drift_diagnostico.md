# Sprint S2 Fase A — Diagnóstico de drift de layout

Documentação do estado encontrado em `2026-05-27` ao iniciar o backfill da Fase A do plano `precisamos-analisar-a-quantidade-warm-newt`. Sprint S2 está **bloqueado por decisão de produto** — alterações de layout exigem revisão de contratos de API e hardgate.

## Reajustes — `percentual_reajuste_agrupamento`

| Onde | Layout |
|---|---|
| **Código** (`ingestao/app/carregar_postgres.py:602`) | competencia · registro_ans · tipo_contratacao · agrupamento · percentual_reajuste · data_aplicacao |
| **Publicado pela ANS** (`/FTP/PDA/percentuais_de_reajuste_de_agrupamento-055/pda-055-Percentuais_de_Reajuste_de_Agrupamento.csv`, last-mod 2025-05-15) | REGISTRO_OPERADORA · CICLO · TP_AGRUPAMENTO · PCT_UNICO · PCT_AMBULATORIAL · PCT_INT_SEM_OBSTET · PCT_INT_COM_OBSTET · QT_CONTRATOS · QT_BENEF · RAZAO_SOCIAL |
| **Mongo `layout`** (status: `rascunho`) | sem `campos` definidos |

**Diferenças semânticas:**
- ANS agora **decompõe percentual por tipo de atendimento** (único / ambulatorial / int. com / sem obstetrícia) em vez de uma única coluna `percentual_reajuste`.
- Granularidade temporal mudou: `CICLO` (ano) substituiu `competencia` + `data_aplicacao`.
- Volumetria por contratos e beneficiários agora vem no mesmo arquivo (era separado).

## VDA — `vda_operadora_mensal`

| Onde | Layout |
|---|---|
| **Código** (`carregar_postgres.py:283`) | competencia · registro_ans · valor_devido · valor_pago · saldo_devedor · situacao_cobranca · data_vencimento · fonte_publicacao |
| **DAG** (`dag_ingest_vda.py`) | apenas registra `layout_nao_mapeado` (stub) |
| **Publicado pela ANS** em `beneficiarios_vinculos_tipo_contratacao_vda/Beneficiarios_operadora_e_carteira.csv` | CD_OPERADORA · GR_MODALIDADE · COBERTURA · VIGENCIA_PLANO · GR_CONTRATACAO · TIPO_FINANCIAMENTO · MES · ID_CMPT · NR_BENEF |

**O dataset mudou de natureza.** O VDA original (Valor a Devolver — componente financeiro) parece ter sido descontinuado ou reorganizado. O caminho `vda` na ANS hoje publica **vínculos de beneficiários por tipo de contratação** — outra coisa. Servir este dataset como "VDA / Garantias" no site é incorreto.

## Garantias — `monitoramento_garantia_atendimento`

| Onde | Layout |
|---|---|
| **Código** (`carregar_postgres.py:754`) | competencia · registro_ans · tipo_garantia · qt_ocorrencias · qt_resolvidas · qt_pendentes · prazo_medio_resolucao |
| **Publicado pela ANS** (`/monitoramento_garantia_atendimento/monit_garantia_atendimento.csv`) | COMPETENCIA · DT_INICIO_COMPETENCIA · DT_FIM_COMPETENCIA · REGISTRO_OPERADORA · NM_OPERADORA · POSICAO |

**Diferenças:**
- ANS hoje publica **uma única classificação `POSICAO`** (FAIXA 1, 2, ...) em vez das 4 métricas decompostas.
- Granularidade temporal: trimestral textual (`"4º Trim./2015"`) — exige parser.

## Implicação para Sprint S2

Cada dataset exige:

1. **Decisão de produto** — manter a promessa do dataset ou reposicionar a oferta:
   - VDA: reavaliar se faz sentido oferecer dado que mudou de natureza.
   - Reajustes: estrutura nova é mais rica (4 tipos de percentual) — bom de manter mas API e Coverage precisam refletir o novo formato.
   - Garantias: classificação simplificada — ainda útil, mas com menos detalhe que o anunciado.

2. **Hardgate** (CLAUDE.md regra de baseline Fase 5/9): qualquer alteração em `bruto_ans.*`, `stg_*`, `api_*` desses datasets é mudança aditiva ou exige hardgate. Como as tabelas estão vazias em produção, o risco operacional é mínimo, mas o contrato precisa ser revisto formalmente.

3. **Trabalho técnico** por dataset (≥1 PR/sprint cada):
   - Atualizar `carregar_postgres.py` (mapping)
   - DDL em `infra/postgres/init/0XX_*.sql` para recriar `bruto_ans.*` com novo schema
   - Atualizar layout no MongoDB (`layout` + `layout_versao`)
   - Refazer modelos dbt `stg_* → int_* → api_*` (quebra de baseline)
   - Atualizar endpoints e schemas Pydantic
   - Tests de integration + smoke

## Próximos passos sugeridos

- Levar este diagnóstico à decisão de produto antes de implementar.
- Enquanto isso: Coverage.tsx já move os 3 datasets para "Backfill em andamento" (✅ feito em S1).
- Avançar para **Sprint S3** (SIB 2024 backfill, NIP, FIP) e **Sprint S4** (hardgate freshness + Coverage dinâmico), que **não exigem** alteração de baseline.

## Comandos para reproduzir os snapshots de layout ANS

```bash
curl -sS https://dadosabertos.ans.gov.br/FTP/PDA/percentuais_de_reajuste_de_agrupamento-055/pda-055-Percentuais_de_Reajuste_de_Agrupamento.csv | head -2
curl -sS https://dadosabertos.ans.gov.br/FTP/PDA/monitoramento_garantia_atendimento/monit_garantia_atendimento.csv | head -2
curl -sS https://dadosabertos.ans.gov.br/FTP/PDA/beneficiarios_vinculos_tipo_contratacao_vda/Beneficiarios_operadora_e_carteira.csv | head -2
```
