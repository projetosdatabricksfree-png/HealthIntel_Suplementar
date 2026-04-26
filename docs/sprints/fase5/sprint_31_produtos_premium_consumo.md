# Sprint 31 — Produtos Premium Validados para Consumo

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.6.0-premium`
**Objetivo:** criar novos data products comerciais sem substituir os atuais.
**Fim esperado:** produto premium disponível para consumo SQL direto e para API premium, com dados curados, validados e qualidade explícita.
**Critério de saída:** modelos `consumo_premium_*` materializados em `consumo_premium_ans`; modelos `api_premium_*` materializados em `api_ans`; role `healthintel_premium_reader` com acesso ao schema premium; todos com `mdm_status`, `quality_score_*` e referência aos master IDs; nenhum modelo `consumo_*` existente alterado.

## Regra-mãe

- [ ] `consumo_operadora_360` permanece intacta.
- [ ] Nenhum dos 8 modelos atuais de `consumo_ans` é alterado.
- [ ] Nenhum modelo TISS/CNES existente é alterado.
- [ ] Modelos premium de entrega SQL vivem em `healthintel_dbt/models/consumo_premium/` e no schema `consumo_premium_ans`.
- [ ] Modelos premium de API vivem em `healthintel_dbt/models/api/premium/` e no schema `api_ans`, com prefixo `api_premium_*`.
- [ ] Endpoints premium da Sprint 32 consomem apenas `api_ans.api_premium_*`, nunca `consumo_premium_ans.consumo_premium_*` diretamente.
- [ ] `healthintel_cliente_reader` não recebe grant em `consumo_premium_ans`; clientes premium usam `healthintel_premium_reader`.

## Histórias

### HIS-11.0 — Resolver dívida técnica TUSS/ROL antes do produto TISS/TUSS

- [ ] Verificar a existência física dos seeds `healthintel_dbt/seeds/ref_tuss.csv` e `healthintel_dbt/seeds/ref_rol_procedimento.csv` antes de executar `dbt seed`.
- [ ] Corrigir a divergência atual em que `_seeds.yml` referencia `ref_tuss` e `ref_rol_procedimento`, mas os arquivos CSV podem não existir no recorte do repositório.
- [ ] Definir explicitamente se TUSS será seed sintético de desenvolvimento, ingestão oficial ou tabela versionada própria.
- [ ] Criar validação pré-dbt seed que falha de forma explícita quando o arquivo esperado não existe, exceto em modo CI sintético documentado.
- [ ] Registrar a decisão em `docs/produto/tiss_tuss_premium.md` antes de publicar qualquer modelo `consumo_premium_tiss_*`.

### HIS-11.1 — Criar consumo premium de operadora

- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_operadora_360_validado.sql`.
- [ ] Usar `consumo_operadora_360` como fonte (LEFT JOIN, leitura apenas).
- [ ] Adicionar `operadora_master_id`.
- [ ] Adicionar `cnpj_digito_valido` (vindo de `dq_operadora_documento`).
- [ ] Adicionar `cnpj_receita_status` (vindo de `int_cnpj_receita_validado`).
- [ ] Adicionar `mdm_status`.
- [ ] Adicionar `quality_score_documental` (0–100).
- [ ] Adicionar `quality_score_mdm` (0–100).
- [ ] Não alterar `consumo_operadora_360`.
- [ ] Tag dbt `consumo_premium`.

### HIS-11.2 — Criar consumo premium CNES

- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_cnes_estabelecimento_validado.sql`.
- [ ] Usar `stg_cnes_estabelecimento` e fatos CNES existentes como fonte.
- [ ] Adicionar `estabelecimento_master_id`.
- [ ] Adicionar `prestador_master_id`.
- [ ] Adicionar `cnpj_digito_valido`.
- [ ] Adicionar `cnpj_receita_status`.
- [ ] Adicionar `municipio_valido` (validado contra `ref_municipio_ibge`).
- [ ] Adicionar `cnes_formato_valido`.
- [ ] Adicionar `quality_score_cnes`.
- [ ] Não alterar os fatos CNES já existentes.

### HIS-11.3 — Criar consumo premium TISS/TUSS

Contexto: o Padrão TISS é obrigatório para troca eletrônica de dados na saúde suplementar e mantém o componente TUSS como representação de conceitos. TISS sem dimensão TUSS versionada perde valor comercial.

- [ ] Criar `healthintel_dbt/models/staging/stg_tuss_terminologia.sql`.
- [ ] Criar `healthintel_dbt/models/marts/dimensao/dim_tuss_terminologia.sql`.
- [ ] Criar `healthintel_dbt/models/marts/dimensao/dim_tuss_procedimento.sql`.
- [ ] Criar `healthintel_dbt/models/consumo_premium/xref_tiss_tuss_procedimento.sql`.
- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_tiss_procedimento_tuss_validado.sql`.
- [ ] Usar `stg_tiss_procedimento`, `int_tiss_operadora_trimestre`, `fat_tiss_procedimento_operadora` e `mart_tiss_procedimento` como fontes.
- [ ] Adicionar `versao_tuss`.
- [ ] Adicionar `codigo_tuss`.
- [ ] Adicionar `descricao_tuss`.
- [ ] Adicionar `vigencia_inicio`.
- [ ] Adicionar `vigencia_fim`.
- [ ] Adicionar `is_tuss_vigente` (bit).
- [ ] Adicionar `tiss_tuss_match_status` (MATCHED | UNMATCHED | DEPRECATED | AMBIGUOUS).
- [ ] Não alterar os modelos TISS já existentes.

### HIS-11.4 — Criar consumo premium contrato/subfatura

- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_contrato_validado.sql`.
- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_subfatura_validada.sql`.
- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_contrato_subfatura_operadora.sql`.
- [ ] Criar `healthintel_dbt/models/consumo_premium/consumo_premium_contrato_inconsistencia.sql`.
- [ ] Expor `contrato_master_id`.
- [ ] Expor `subfatura_master_id`.
- [ ] Expor `operadora_master_id`.
- [ ] Expor `mdm_status`.
- [ ] Expor `quality_score_contrato`.
- [ ] Expor `quality_score_subfatura`.
- [ ] Filtrar exceções bloqueantes (não publicar em premium).

### HIS-11.5 — Criar modelos de serviço `api_premium_*`

- [ ] Criar pasta `healthintel_dbt/models/api/premium/`.
- [ ] Criar `api_premium_operadora_360_validado.sql` lendo o produto premium de operadora aprovado.
- [ ] Criar `api_premium_cnes_estabelecimento_validado.sql` lendo o produto premium CNES aprovado.
- [ ] Criar `api_premium_tiss_procedimento_tuss_validado.sql` lendo o produto premium TISS/TUSS aprovado.
- [ ] Criar `api_premium_tuss_procedimento.sql` para a rota dedicada de procedimentos TUSS.
- [ ] Criar `api_premium_mdm_operadora.sql` lendo `mdm_operadora_master` sem expor campos internos indevidos.
- [ ] Criar `api_premium_mdm_prestador.sql` lendo `mdm_prestador_master` sem expor campos internos indevidos.
- [ ] Criar `api_premium_contrato_validado.sql`, `api_premium_subfatura_validada.sql` e `api_premium_quality_dataset.sql` para rotas premium da Sprint 32.
- [ ] Garantir tags `["api", "premium"]` em todos os modelos `api_premium_*`.

## Entregas esperadas

- [ ] 7 modelos `consumo_premium_*` em `consumo_premium_ans` (`operadora_360_validado`, `cnes_estabelecimento_validado`, `tiss_procedimento_tuss_validado`, `contrato_validado`, `subfatura_validada`, `contrato_subfatura_operadora`, `contrato_inconsistencia`)
- [ ] Modelos `api_premium_*` em `api_ans` para uso exclusivo da FastAPI premium
- [ ] Role `healthintel_premium_reader` e schema `consumo_premium_ans` em `infra/postgres/init/027_fase5_premium_roles.sql`
- [ ] Dimensão TUSS (`stg_tuss_terminologia`, `dim_tuss_terminologia`, `dim_tuss_procedimento`, `xref_tiss_tuss_procedimento`)
- [ ] Tag dbt `consumo_premium`
- [ ] Tag dbt `premium` nos modelos `api_premium_*`
- [ ] `_consumo_premium.yml` com testes genéricos (`unique`, `not_null`, `accepted_values`)

## Validação esperada (hard gates)

- [ ] `dbt build --select tag:consumo_premium tag:premium` zero erros.
- [ ] `dbt test --select tag:consumo_premium tag:premium` zero falhas.
- [ ] `consumo_operadora_360.sql` e os 8 modelos atuais de `consumo_ans` byte-idênticos à tag `v3.0.0`.
- [ ] Modelos TISS existentes inalterados.
- [ ] Seeds ou tabelas TUSS/ROL existem fisicamente ou a decisão de fonte sintética/oficial está documentada e validada antes do build.
- [ ] `quality_score_*` ∈ [0, 100] em 100% das linhas.
- [ ] Nenhuma linha em `consumo_premium_*` com CNPJ tecnicamente inválido (validação cruzada com `dq_*`).
- [ ] Nenhuma linha de contrato/subfatura premium com exceção `is_blocking = 1`.
- [ ] `healthintel_cliente_reader` não tem `USAGE` nem `SELECT` em `consumo_premium_ans`.
- [ ] FastAPI premium aponta somente para `api_ans.api_premium_*`.

## Resultado Esperado

Sprint 31 entrega os primeiros data products comerciais validados e enriquecidos da Fase 5. Cada linha publicada tem score de qualidade explícito, master IDs e rastreabilidade até a fonte oficial (Serpro para CNPJ). Os modelos atuais permanecem intactos — clientes legados continuam consumindo o `consumo_ans` original, clientes premium passam a ter acesso SQL direto ao `consumo_premium_ans` e a FastAPI passa a ter modelos próprios `api_ans.api_premium_*`.
