# Sprint 41 — Delta ANS 100%: Somente o que ainda falta

> Projeto: HealthIntel Suplementar  
> Objetivo: implementar apenas os datasets/modelos que ainda não aparecem claramente no projeto atual, sem mexer no que já existe.  
> Escopo: lacunas para cobertura 100% do repositório público ANS + disponibilização final das novas tabelas ouro/API/consumo.

---

## 0. Premissas obrigatórias

- [x] Não recriar `plataforma.fonte_dado_ans`.
- [x] Não recriar `plataforma.arquivo_fonte_ans`.
- [x] Não recriar `bruto_ans.ans_arquivo_generico`.
- [x] Não recriar `bruto_ans.ans_linha_generica`.
- [x] Não recriar MongoDB como registry de layouts.
- [x] Não recriar pipeline bronze existente.
- [x] Não alterar CADOP ativo existente.
- [x] Não alterar SIB existente.
- [x] Não alterar CNES existente.
- [x] Não alterar DIOPS/FIP existente.
- [x] Não alterar IDSS/IGR/NIP existente.
- [x] Não alterar Portabilidade existente.
- [x] Não alterar Prudencial existente.
- [x] Não alterar Regime Especial existente.
- [x] Não alterar RN623 existente.
- [x] Não alterar Taxa de Resolutividade existente.
- [x] Não alterar TISS procedimento existente.
- [x] Não alterar TUSS staging/dimensão existente sem necessidade.
- [x] Não alterar VDA existente.
- [x] Não alterar API atual já publicada.

---

## 1. Base de comparação

### Já existe no projeto atual

O repositório já mostra modelos staging para:

```text
stg_cadop
stg_cnes_estabelecimento
stg_diops
stg_fip
stg_glosa
stg_idss
stg_igr
stg_nip
stg_portabilidade
stg_prudencial
stg_rede_assistencial
stg_regime_especial
stg_rn623_lista
stg_sib_municipio
stg_sib_operadora
stg_taxa_resolutividade
stg_tiss_procedimento
stg_tuss_terminologia
stg_vda
```

Também já existem APIs como:

```text
api_cnes_municipio
api_cnes_rede_gap
api_financeiro_operadora_mensal
api_market_share_mensal
api_operadora
api_oportunidade_municipio_mensal
api_portabilidade_operadora_mensal
api_ranking_composto_mensal
api_ranking_crescimento
api_ranking_oportunidade
api_ranking_score
api_rede_assistencial
api_regime_especial_operadora
api_regulatorio_operadora_trimestral
api_rn623_lista_trimestral
api_score_operadora_mensal
api_score_regulatorio_operadora_mensal
api_score_v2_operadora_mensal
api_score_v3_operadora_mensal
api_sinistralidade_procedimento
api_tiss_operadora_trimestral
api_vazio_assistencial
```

### Repositório oficial ANS usado para lacunas

Base principal:

```text
https://dadosabertos.ans.gov.br/FTP/PDA/
```

---

## 2. Fora do escopo desta sprint

Esta sprint não deve alterar as famílias que já existem no projeto.

- [ ] Não refatorar CADOP ativo.
- [ ] Não refatorar SIB.
- [ ] Não refatorar CNES.
- [ ] Não refatorar DIOPS/FIP.
- [ ] Não refatorar IDSS/IGR/NIP.
- [ ] Não refatorar Portabilidade.
- [ ] Não refatorar Prudencial.
- [ ] Não refatorar Regime Especial.
- [ ] Não refatorar RN623.
- [ ] Não refatorar Taxa Resolutividade.
- [ ] Não refatorar TISS procedimento já existente.
- [ ] Não refatorar APIs atuais.
- [ ] Não alterar bronze genérico, exceto se for estritamente necessário para registrar novos `dataset_codigo`.

---

# 3. Datasets que ainda faltam implementar

## 3.1 Planos e produtos

### 3.1.1 Características de produtos de saúde suplementar

Caminho:

```text
/FTP/PDA/caracteristicas_produtos_saude_suplementar-008/
```

Tabelas novas:

- [x] `bruto_ans.produto_caracteristica`
- [x] `bruto_ans.produto_tabela_auxiliar`
- [x] `stg_ans.stg_produto_caracteristica`
- [x] `stg_ans.stg_produto_tabela_auxiliar`
- [ ] `nucleo_ans.dim_produto_plano`
- [x] `api_ans.api_produto_plano`
- [x] `consumo_ans.consumo_produto_plano`
- [ ] `consumo_premium_ans.produto_plano_completo`

### 3.1.2 Histórico de planos

Caminho:

```text
/FTP/PDA/historico_planos_saude/
```

Tabelas novas:

- [x] `bruto_ans.historico_plano`
- [x] `stg_ans.stg_historico_plano`
- [ ] `nucleo_ans.dim_historico_plano`
- [x] `api_ans.api_historico_plano`
- [ ] `consumo_ans.consumo_historico_plano`

### 3.1.3 Serviços opcionais dos planos

Caminho:

```text
/FTP/PDA/servicos_opcionais_planos_saude/
```

Tabelas novas:

- [x] `bruto_ans.plano_servico_opcional`
- [x] `stg_ans.stg_plano_servico_opcional`
- [ ] `nucleo_ans.dim_plano_servico_opcional`
- [ ] `api_ans.api_plano_servico_opcional`
- [ ] `consumo_ans.consumo_plano_servico_opcional`

### 3.1.4 Quadros auxiliares de corresponsabilidade

Caminho:

```text
/FTP/PDA/quadros_auxiliares_de_corresponsabilidade/
```

Tabelas novas:

- [x] `bruto_ans.quadro_auxiliar_corresponsabilidade`
- [x] `stg_ans.stg_quadro_auxiliar_corresponsabilidade`
- [ ] `nucleo_ans.dim_quadro_auxiliar_corresponsabilidade`
- [ ] `api_ans.api_quadro_auxiliar_corresponsabilidade`

---

## 3.2 TUSS — o que falta

O projeto já possui `stg_tuss_terminologia`, mas ainda falta fechar TUSS como produto oficial e auditável.

Caminho:

```text
/FTP/PDA/terminologia_unificada_saude_suplementar_TUSS/
```

Arquivos oficiais:

```text
Dicionario_de_dados.ods
TUSS.zip
```

Tabelas novas/ajustes pontuais:

- [x] `bruto_ans.tuss_terminologia_oficial`
- [x] `api_ans.api_tuss_procedimento_vigente`
- [ ] `consumo_ans.consumo_tuss_procedimento_vigente`
- [ ] `consumo_premium_ans.tuss_procedimento_vigente`

Tasks TUSS:

- [x] Criar parser oficial para `TUSS.zip`.
- [x] Registrar/validar layout TUSS no Mongo existente.
- [x] Carregar TUSS oficial em `bruto_ans.tuss_terminologia_oficial`.
- [x] Garantir versionamento por `versao_tuss`.
- [x] Garantir `vigencia_inicio`.
- [x] Garantir `vigencia_fim`.
- [x] Garantir `is_tuss_vigente`.
- [x] Garantir chave técnica por `codigo_tuss + versao_tuss`.
- [x] Criar API própria `api_tuss_procedimento_vigente`.
- [ ] Criar consumo SQL `consumo_tuss_procedimento_vigente`.
- [ ] Criar premium SQL `tuss_procedimento_vigente`.
- [ ] Proibir crosswalk sintético em produção.
- [ ] Criar teste dbt para `codigo_tuss` não nulo.
- [ ] Criar teste dbt para duplicidade por `codigo_tuss + versao_tuss`.
- [ ] Criar teste dbt para vigência inválida.
- [ ] Criar smoke de busca por código TUSS.
- [ ] Criar smoke de busca por descrição de procedimento.

Não fazer:

- [ ] Não substituir a TUSS por CBHPM.
- [ ] Não publicar CBHPM como dado aberto.
- [ ] Não usar tabela sintética como base comercial.

---

## 3.3 TISS — subfamílias oficiais que faltam

O projeto já possui `stg_tiss_procedimento` e `api_tiss_operadora_trimestral`. O delta é separar e disponibilizar as subfamílias oficiais do diretório TISS.

Caminho:

```text
/FTP/PDA/TISS/
```

Subpastas oficiais:

```text
/FTP/PDA/TISS/AMBULATORIAL/
/FTP/PDA/TISS/HOSPITALAR/
/FTP/PDA/TISS/DADOS_DE_PLANOS/
/FTP/PDA/TISS/DICIONARIO/
```

Tabelas novas:

- [x] `bruto_ans.tiss_ambulatorial`
- [x] `bruto_ans.tiss_hospitalar`
- [x] `bruto_ans.tiss_dados_plano`
- [x] `stg_ans.stg_tiss_ambulatorial`
- [x] `stg_ans.stg_tiss_hospitalar`
- [x] `stg_ans.stg_tiss_dados_plano`
- [ ] `nucleo_ans.fat_tiss_ambulatorial`
- [ ] `nucleo_ans.fat_tiss_hospitalar`
- [ ] `nucleo_ans.fat_tiss_plano`
- [x] `api_ans.api_tiss_ambulatorial_operadora_mes`
- [x] `api_ans.api_tiss_hospitalar_operadora_mes`
- [x] `api_ans.api_tiss_plano_mes`
- [ ] `consumo_ans.consumo_tiss_utilizacao_operadora_mes`
- [ ] `consumo_premium_ans.tiss_evento_procedimento_mes`

Retenção obrigatória:

- [ ] TISS no Postgres: últimos 24 meses nas tabelas API/consumo.
- [ ] Histórico completo: R2/landing.
- [ ] TISS bruto pesado não deve ser exposto para cliente.

---

## 3.4 SIP

Caminho:

```text
/FTP/PDA/SIP/
```

Tabelas novas:

- [x] `bruto_ans.sip_mapa_assistencial`
- [x] `stg_ans.stg_sip_mapa_assistencial`
- [ ] `nucleo_ans.fat_sip_assistencial`
- [x] `api_ans.api_sip_assistencial_operadora`
- [ ] `consumo_ans.consumo_sip_assistencial_operadora`
- [ ] `consumo_premium_ans.sip_assistencial_operadora`

Tasks:

- [ ] Registrar layout SIP no Mongo.
- [ ] Criar parser dos arquivos `sip_mapa_assistencial`.
- [ ] Criar staging tipado.
- [ ] Criar ouro agregado por operadora/período/tipo assistencial.
- [ ] Criar API e consumo.
- [ ] Criar teste de volume mínimo.
- [ ] Criar teste de período não nulo.
- [ ] Criar teste de relacionamento com operadora.

---

## 3.5 Ressarcimento ao SUS

### 3.5.1 Beneficiários identificados SUS/ABI

Caminho:

```text
/FTP/PDA/beneficiarios_identificados_sus_abi/
```

Tabelas novas:

- [x] `bruto_ans.ressarcimento_beneficiario_abi`
- [x] `stg_ans.stg_ressarcimento_beneficiario_abi`
- [ ] `nucleo_ans.fat_ressarcimento_beneficiario_abi`
- [x] `api_ans.api_ressarcimento_beneficiario_abi`

### 3.5.2 Dados de ressarcimento SUS por operadora/plano

Caminho:

```text
/FTP/PDA/dados_ressarcimento_SUS_operadora_planos_saude/
```

Tabelas novas:

- [x] `bruto_ans.ressarcimento_sus_operadora_plano`
- [x] `stg_ans.stg_ressarcimento_sus_operadora_plano`
- [ ] `nucleo_ans.fat_ressarcimento_sus_operadora_plano`
- [x] `api_ans.api_ressarcimento_sus_operadora_plano`
- [ ] `consumo_ans.consumo_ressarcimento_sus_operadora`

### 3.5.3 HC Ressarcimento SUS

Caminho:

```text
/FTP/PDA/hc_ressarcimento_sus/
```

Tabelas novas:

- [x] `bruto_ans.ressarcimento_hc`
- [x] `stg_ans.stg_ressarcimento_hc`
- [x] `api_ans.api_ressarcimento_hc_operadora`

### 3.5.4 Cobrança e arrecadação

Caminho:

```text
/FTP/PDA/ressarcimento_ao_SUS_cobranca_arrecadacao/
```

Tabelas novas:

- [x] `bruto_ans.ressarcimento_cobranca_arrecadacao`
- [x] `stg_ans.stg_ressarcimento_cobranca_arrecadacao`
- [x] `api_ans.api_ressarcimento_cobranca_arrecadacao`

### 3.5.5 Índice de efetivo pagamento

Caminho:

```text
/FTP/PDA/ressarcimento_ao_SUS_indice_efetivo_pagamento/
```

Tabelas novas:

- [x] `bruto_ans.ressarcimento_indice_pagamento`
- [x] `stg_ans.stg_ressarcimento_indice_pagamento`
- [x] `api_ans.api_ressarcimento_indice_pagamento`

---

## 3.6 Precificação, NTRP e reajustes

### 3.6.1 Área de comercialização NTRP

Caminho:

```text
/FTP/PDA/area_comercializacao_planos_ntrp/
```

Tabelas novas:

- [x] `bruto_ans.ntrp_area_comercializacao`
- [x] `stg_ans.stg_ntrp_area_comercializacao`
- [x] `api_ans.api_ntrp_area_comercializacao`

### 3.6.2 Painel de precificação

Caminho:

```text
/FTP/PDA/painel_precificacao-053/
```

Tabelas novas:

- [x] `bruto_ans.painel_precificacao`
- [x] `stg_ans.stg_painel_precificacao`
- [ ] `nucleo_ans.fat_painel_precificacao`
- [x] `api_ans.api_painel_precificacao`

### 3.6.3 Percentuais de reajuste

Caminho:

```text
/FTP/PDA/percentuais_de_reajuste_de_agrupamento-055/
```

Tabelas novas:

- [x] `bruto_ans.percentual_reajuste_agrupamento`
- [x] `stg_ans.stg_percentual_reajuste_agrupamento`
- [x] `api_ans.api_reajuste_agrupamento`

### 3.6.4 Nota técnica NTRP / VCM / faixa etária

Caminho:

```text
/FTP/PDA/nota_tecnica_ntrp_vcm_faixa_etaria/
```

Tabelas novas:

- [x] `bruto_ans.ntrp_vcm_faixa_etaria`
- [x] `stg_ans.stg_ntrp_vcm_faixa_etaria`
- [x] `api_ans.api_ntrp_vcm_faixa_etaria`

### 3.6.5 Valor comercial médio por município

Caminho:

```text
/FTP/PDA/valor_comercial_medio_por_municipio_NTRP-054/
```

Tabelas novas:

- [x] `bruto_ans.valor_comercial_medio_municipio`
- [x] `stg_ans.stg_valor_comercial_medio_municipio`
- [ ] `nucleo_ans.fat_valor_comercial_medio_municipio`
- [x] `api_ans.api_valor_comercial_medio_municipio`

### 3.6.6 Faixa de preço

Caminho:

```text
/FTP/PDA/faixa_de_preco/
```

Tabelas novas:

- [x] `bruto_ans.faixa_preco`
- [x] `stg_ans.stg_faixa_preco`
- [x] `api_ans.api_faixa_preco`

### Consumo consolidado

- [x] `consumo_ans.consumo_precificacao_plano`
- [ ] `consumo_premium_ans.precificacao_plano`

---

## 3.7 Operadoras complementares

### 3.7.1 Operadoras canceladas

Caminho:

```text
/FTP/PDA/operadoras_de_plano_de_saude_canceladas/
```

Tabelas novas:

- [x] `bruto_ans.operadora_cancelada`
- [x] `stg_ans.stg_operadora_cancelada`
- [ ] `nucleo_ans.dim_operadora_cancelada`
- [x] `api_ans.api_operadora_cancelada`

### 3.7.2 Operadoras acreditadas

Caminho:

```text
/FTP/PDA/operadoras_acreditadas/
```

Tabelas novas:

- [x] `bruto_ans.operadora_acreditada`
- [x] `stg_ans.stg_operadora_acreditada`
- [x] `api_ans.api_operadora_acreditada`

---

## 3.8 Rede e prestadores complementares

### 3.8.1 Prestadores acreditados

Caminho:

```text
/FTP/PDA/prestadores_acreditados/
```

Tabelas novas:

- [x] `bruto_ans.prestador_acreditado`
- [x] `stg_ans.stg_prestador_acreditado`
- [x] `api_ans.api_prestador_acreditado`

### 3.8.2 Produtos e prestadores hospitalares

Caminho:

```text
/FTP/PDA/produtos_e_prestadores_hospitalares/
```

Tabelas novas:

- [x] `bruto_ans.produto_prestador_hospitalar`
- [x] `stg_ans.stg_produto_prestador_hospitalar`
- [ ] `nucleo_ans.fat_produto_prestador_hospitalar`
- [x] `api_ans.api_produto_prestador_hospitalar`

### 3.8.3 Operadoras e prestadores não hospitalares

Caminho:

```text
/FTP/PDA/operadoras_e_prestadores_nao_hospitalares/
```

Tabelas novas:

- [x] `bruto_ans.operadora_prestador_nao_hospitalar`
- [x] `stg_ans.stg_operadora_prestador_nao_hospitalar`
- [x] `api_ans.api_operadora_prestador_nao_hospitalar`

### 3.8.4 Solicitações de alteração de rede hospitalar

Caminho:

```text
/FTP/PDA/solicitacoes_alteracao_rede_hospitalar-046/
```

Tabelas novas:

- [x] `bruto_ans.solicitacao_alteracao_rede_hospitalar`
- [x] `stg_ans.stg_solicitacao_alteracao_rede_hospitalar`
- [ ] `nucleo_ans.fat_alteracao_rede_hospitalar`
- [x] `api_ans.api_alteracao_rede_hospitalar`
- [ ] `consumo_premium_ans.alteracao_rede_hospitalar`

---

## 3.9 Regulatórios complementares

### 3.9.1 Penalidades aplicadas

Caminho:

```text
/FTP/PDA/penalidades_aplicadas_a_operadoras/
```

Tabelas novas:

- [x] `bruto_ans.penalidade_operadora`
- [x] `stg_ans.stg_penalidade_operadora`
- [ ] `nucleo_ans.fat_penalidade_operadora`
- [x] `api_ans.api_penalidade_operadora`
- [ ] `consumo_premium_ans.penalidade_operadora`

### 3.9.2 Monitoramento de garantia de atendimento

Caminho:

```text
/FTP/PDA/monitoramento_garantia_atendimento/
```

Tabelas novas:

- [x] `bruto_ans.monitoramento_garantia_atendimento`
- [x] `stg_ans.stg_monitoramento_garantia_atendimento`
- [x] `api_ans.api_garantia_atendimento`

### 3.9.3 PEONA SUS

Caminho:

```text
/FTP/PDA/peona_sus/
```

Tabelas novas:

- [x] `bruto_ans.peona_sus`
- [x] `stg_ans.stg_peona_sus`
- [x] `api_ans.api_peona_sus`

### 3.9.4 PROMOPREV

Caminho:

```text
/FTP/PDA/promoprev-052/
```

Tabelas novas:

- [x] `bruto_ans.promoprev`
- [x] `stg_ans.stg_promoprev`
- [x] `api_ans.api_promoprev`

### 3.9.5 RPC

Caminho:

```text
/FTP/PDA/RPC/
```

Tabelas novas:

- [x] `bruto_ans.rpc`
- [x] `stg_ans.stg_rpc`
- [ ] `nucleo_ans.fat_rpc`
- [x] `api_ans.api_rpc_operadora_mes`
- [ ] `consumo_premium_ans.rpc_operadora_mes`

Retenção:

- [x] RPC no Postgres: últimos 24 meses nas tabelas API/consumo.
- [ ] Histórico completo: R2/landing.

### 3.9.6 IAP

Caminho:

```text
/FTP/PDA/IAP/
```

Tabelas novas:

- [x] `bruto_ans.iap`
- [x] `stg_ans.stg_iap`
- [x] `api_ans.api_iap`

### 3.9.7 PFA

Caminho:

```text
/FTP/PDA/PFA/
```

Tabelas novas:

- [x] `bruto_ans.pfa`
- [x] `stg_ans.stg_pfa`
- [x] `api_ans.api_pfa`

### 3.9.8 Programa de qualificação institucional

Caminho:

```text
/FTP/PDA/programa_de_qualificacao_institucional/
```

Tabelas novas:

- [x] `bruto_ans.programa_qualificacao_institucional`
- [x] `stg_ans.stg_programa_qualificacao_institucional`
- [x] `api_ans.api_programa_qualificacao_institucional`

---

## 3.10 Beneficiários e cobertura complementares

### 3.10.1 Beneficiários por região geográfica

Caminho:

```text
/FTP/PDA/dados_de_beneficiarios_por_regiao_geografica/
```

Tabelas novas:

- [x] `bruto_ans.beneficiario_regiao_geografica`
- [x] `stg_ans.stg_beneficiario_regiao_geografica`
- [x] `api_ans.api_beneficiario_regiao_geografica`

### 3.10.2 Informações consolidadas de beneficiários

Caminho:

```text
/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/
```

Tabelas novas:

- [x] `bruto_ans.beneficiario_informacao_consolidada`
- [x] `stg_ans.stg_beneficiario_informacao_consolidada`
- [x] `api_ans.api_beneficiario_informacao_consolidada`

### 3.10.3 Taxa de cobertura de planos de saúde

Caminho:

```text
/FTP/PDA/taxa_de_cobertura_de_planos_de_saude-047/
```

Tabelas novas:

- [x] `bruto_ans.taxa_cobertura_plano`
- [x] `stg_ans.stg_taxa_cobertura_plano`
- [x] `api_ans.api_taxa_cobertura_plano`

---

## 3.11 Cadernos e bases documentais

Essas bases entram para cobertura 100%, mas não precisam virar produto principal de API no primeiro momento.

### 3.11.1 Caderno SS

Caminho:

```text
/FTP/PDA/Caderno_SS/
```

Tabelas novas:

- [ ] `bruto_ans.caderno_ss`
- [ ] `stg_ans.stg_caderno_ss`
- [ ] `api_ans.api_caderno_ss_indicador`

### 3.11.2 Caderno de Informação

Caminho:

```text
/FTP/PDA/caderno_de_informacao/
```

Tabelas novas:

- [ ] `bruto_ans.caderno_informacao`
- [ ] `stg_ans.stg_caderno_informacao`
- [ ] `api_ans.api_caderno_informacao_indicador`

### 3.11.3 Glossário de saúde suplementar

Caminho:

```text
/FTP/PDA/glossario_saude_suplementar/
```

Tabelas novas:

- [ ] `bruto_ans.glossario_saude_suplementar`
- [ ] `stg_ans.stg_glossario_saude_suplementar`
- [ ] `api_ans.api_glossario_saude_suplementar`

### 3.11.4 Agenda de autoridades

Caminho:

```text
/FTP/PDA/agenda_de_autoridades/
```

Decisão:

- [ ] Catalogar e arquivar.
- [ ] Carregar em bronze genérico se parseável.
- [ ] Não criar ouro comercial, salvo se houver estrutura tabular útil.

### 3.11.5 Plano anual de atividades

Caminho:

```text
/FTP/PDA/plano_anual_de_atividades/
```

Decisão:

- [ ] Catalogar e arquivar.
- [ ] Carregar em bronze genérico se parseável.
- [ ] Não criar ouro comercial, salvo se houver estrutura tabular útil.

---

# 4. Histórias da sprint

## História 1 — Implementar somente datasets faltantes

Como mantenedor do HealthIntel,  
quero implementar apenas os datasets ANS que ainda não existem no projeto,  
para atingir cobertura 100% sem mexer no que já está funcionando.

### Tasks

- [ ] Criar arquivo `docs/sprints/fase_ans_100/sprint_41_delta_ans_100.md`.
- [ ] Criar matriz `dataset_codigo`, `familia`, `caminho_ans`, `status_atual`, `acao`.
- [ ] Marcar datasets já existentes como `fora_escopo`.
- [ ] Marcar datasets faltantes como `implementar`.
- [ ] Para cada dataset faltante, registrar layout no Mongo existente.
- [ ] Para cada dataset faltante, criar bronze tipado somente se for dataset comercial/tabular.
- [ ] Para dataset documental, usar bronze genérico e decisão formal de não publicar API comercial.
- [ ] Não alterar `DATASET_CONFIG` de datasets existentes, exceto para acrescentar novos códigos.
- [ ] Não alterar modelos dbt já existentes, exceto quando for necessário apenas criar relacionamento com tabelas novas.

### Critérios de aceite

- [ ] Nenhum modelo existente é removido.
- [ ] Nenhuma tabela existente é renomeada.
- [ ] Nenhum schema existente é reestruturado.
- [ ] Apenas novos datasets entram na sprint.
- [ ] O relatório final separa `novo`, `fora_escopo` e `não_comercial`.

---

## História 2 — Produtos e planos como nova dimensão comercial

### Tasks

- [x] Implementar `produto_caracteristica`.
- [x] Implementar `produto_tabela_auxiliar`.
- [x] Implementar `historico_plano`.
- [x] Implementar `plano_servico_opcional`.
- [x] Implementar `quadro_auxiliar_corresponsabilidade`.
- [ ] Criar relacionamento com `api_operadora` existente.
- [x] Criar `api_produto_plano`.
- [x] Criar `consumo_produto_plano`.
- [ ] Criar `produto_plano_completo` premium.

### Hard gates

- [ ] `registro_ans` não nulo.
- [ ] Código do plano/produto não nulo quando existir.
- [ ] Chave natural sem duplicidade na versão vigente.
- [ ] Relacionamento com operadora validado.
- [ ] API retorna produtos por operadora.
- [ ] API retorna histórico por plano/produto.

---

## História 3 — TUSS oficial como produto

### Tasks

- [x] Criar carga oficial de `TUSS.zip`.
- [x] Criar `bruto_ans.tuss_terminologia_oficial`.
- [x] Publicar `api_ans.api_tuss_procedimento_vigente`.
- [ ] Publicar `consumo_ans.consumo_tuss_procedimento_vigente`.
- [ ] Publicar `consumo_premium_ans.tuss_procedimento_vigente`.
- [ ] Bloquear crosswalk sintético em produção.

### Hard gates

- [x] `TUSS.zip` carregado.
- [x] `Dicionario_de_dados.ods` registrado no Mongo.
- [ ] `codigo_tuss` não nulo.
- [ ] `descricao` não nula.
- [x] `is_tuss_vigente` calculado.
- [ ] Sem duplicidade por código/versão.
- [ ] Smoke de busca por código.
- [ ] Smoke de busca por texto.
- [ ] Nenhum modelo premium usa TUSS sintética.

---

## História 4 — TISS oficial por subfamília

### Tasks

- [x] Implementar `TISS/AMBULATORIAL`.
- [x] Implementar `TISS/HOSPITALAR`.
- [x] Implementar `TISS/DADOS_DE_PLANOS`.
- [ ] Registrar dicionários de `TISS/DICIONARIO` no Mongo.
- [x] Publicar APIs separadas.
- [x] Manter TISS API/consumo em janela de 24 meses.

### Hard gates

- [x] Ambulatorial carregado.
- [x] Hospitalar carregado.
- [x] Dados de planos carregado.
- [x] Retenção de 24 meses aplicada.
- [ ] API exige filtros para consultas grandes.
- [ ] Sem exposição de bruto pesado.

---

## História 5 — SIP

### Tasks

- [x] Implementar SIP Mapa Assistencial.
- [ ] Criar fato assistencial.
- [x] Criar API.
- [ ] Criar consumo.
- [ ] Relacionar com operadora.

### Hard gates

- [ ] Período não nulo.
- [ ] Operadora não nula quando aplicável.
- [ ] Volume mínimo carregado.
- [ ] API responde por operadora/período.

---

## História 6 — Ressarcimento ao SUS

### Tasks

- [x] Implementar ABI.
- [x] Implementar dados por operadora/plano.
- [x] Implementar HC.
- [x] Implementar cobrança/arrecadação.
- [x] Implementar índice de efetivo pagamento.
- [ ] Criar consumo consolidado.

### Hard gates

- [x] Carga por família concluída.
- [x] Valores numéricos tipados como `decimal(18,2)` quando financeiros.
- [ ] Datas tipadas.
- [ ] Chaves de operadora/plano validadas quando existirem.
- [ ] API responde por operadora.

---

## História 7 — Precificação, NTRP e reajustes

### Tasks

- [x] Implementar área de comercialização.
- [x] Implementar painel de precificação.
- [x] Implementar percentuais de reajuste.
- [x] Implementar NTRP/VCM/faixa etária.
- [x] Implementar valor comercial médio por município.
- [x] Implementar faixa de preço.
- [x] Criar consumo de precificação.

### Hard gates

- [x] Valores financeiros tipados.
- [ ] Competência/período não nulo.
- [x] Município/UF normalizados quando existirem.
- [ ] Produto/plano relacionado quando possível.
- [ ] API com filtros obrigatórios.

---

## História 8 — Rede, prestadores e acreditação complementares

### Tasks

- [x] Implementar operadoras canceladas.
- [x] Implementar operadoras acreditadas.
- [x] Implementar prestadores acreditados.
- [x] Implementar produtos/prestadores hospitalares.
- [x] Implementar operadoras/prestadores não hospitalares.
- [x] Implementar solicitações de alteração de rede hospitalar.

### Hard gates

- [ ] Operadora relacionada quando aplicável.
- [ ] CNES relacionado quando aplicável.
- [ ] Município/UF normalizados.
- [ ] API não expõe granularidade sensível desnecessária.
- [ ] Tabelas pesadas possuem filtros obrigatórios.

---

## História 9 — Regulatórios complementares

### Tasks

- [x] Implementar penalidades.
- [x] Implementar garantia de atendimento.
- [x] Implementar PEONA SUS.
- [x] Implementar PROMOPREV.
- [x] Implementar RPC.
- [x] Implementar IAP.
- [x] Implementar PFA.
- [x] Implementar programa de qualificação institucional.

### Hard gates

- [ ] Período/competência tipado.
- [ ] Operadora relacionada quando aplicável.
- [x] RPC limitado a 24 meses nas tabelas de API/consumo.
- [ ] Histórico completo preservado fora do Postgres quente.
- [ ] API documentada.

---

## História 10 — Beneficiários/cobertura complementares

### Tasks

- [x] Implementar beneficiários por região geográfica.
- [x] Implementar informações consolidadas de beneficiários.
- [x] Implementar taxa de cobertura de planos.
- [x] Criar APIs específicas.
- [x] Não alterar SIB existente.

### Hard gates

- [ ] Competência no formato `YYYYMM`.
- [x] Município/UF normalizados quando existirem.
- [x] Indicadores numéricos tipados.
- [x] Sem conflito com SIB existente.

---

## História 11 — Documentais e glossário

### Tasks

- [ ] Implementar Caderno SS se tabular.
- [ ] Implementar Caderno de Informação se tabular.
- [ ] Implementar glossário.
- [ ] Catalogar agenda de autoridades.
- [ ] Catalogar plano anual de atividades.
- [ ] Registrar decisão `não_comercial` quando não houver tabela útil.

### Hard gates

- [ ] Dataset documental tem status final.
- [ ] Dicionários ficam registrados.
- [ ] Sem criação de API inútil.
- [ ] Sem carga pesada sem valor de produto.

---

# 5. Novos arquivos esperados

## Infra/Postgres

- [x] `infra/postgres/init/041_delta_ans_produtos_planos.sql`
- [x] `infra/postgres/init/042_delta_ans_tuss_oficial.sql`
- [x] `infra/postgres/init/043_delta_ans_tiss_subfamilias.sql`
- [x] `infra/postgres/init/044_delta_ans_sip.sql`
- [x] `infra/postgres/init/045_delta_ans_ressarcimento_sus.sql`
- [x] `infra/postgres/init/046_delta_ans_precificacao_ntrp.sql`
- [x] `infra/postgres/init/047_delta_ans_rede_prestadores.sql`
- [x] `infra/postgres/init/048_delta_ans_regulatorios_complementares.sql`
- [x] `infra/postgres/init/049_delta_ans_beneficiarios_cobertura.sql`

## Ingestão

- [x] `ingestao/app/ingestao_delta_ans.py` (consolidado com todos os parsers)
- [x] `scripts/bootstrap_layout_registry_produtos_planos.py`
- [x] `scripts/bootstrap_layout_registry_tuss_oficial.py`
- [x] `scripts/bootstrap_layout_registry_tiss_subfamilias.py`
- [x] `scripts/bootstrap_layout_registry_sip_delta.py`
- [x] `scripts/bootstrap_layout_registry_ressarcimento_sus.py`
- [x] `scripts/bootstrap_layout_registry_precificacao_ntrp.py`
- [x] `scripts/bootstrap_layout_registry_rede_prestadores.py`
- [x] `scripts/bootstrap_layout_registry_regulatorios_complementares.py`
- [x] `scripts/bootstrap_layout_registry_beneficiarios_cobertura.py`

## dbt staging

- [x] `healthintel_dbt/models/staging/stg_produto_caracteristica.sql`
- [x] `healthintel_dbt/models/staging/stg_produto_tabela_auxiliar.sql`
- [x] `healthintel_dbt/models/staging/stg_historico_plano.sql`
- [x] `healthintel_dbt/models/staging/stg_plano_servico_opcional.sql`
- [x] `healthintel_dbt/models/staging/stg_quadro_auxiliar_corresponsabilidade.sql`
- [x] `healthintel_dbt/models/staging/stg_tiss_ambulatorial.sql`
- [x] `healthintel_dbt/models/staging/stg_tiss_hospitalar.sql`
- [x] `healthintel_dbt/models/staging/stg_tiss_dados_plano.sql`
- [x] `healthintel_dbt/models/staging/stg_sip_mapa_assistencial.sql`
- [x] `healthintel_dbt/models/staging/stg_ressarcimento_beneficiario_abi.sql`
- [x] `healthintel_dbt/models/staging/stg_ressarcimento_sus_operadora_plano.sql`
- [x] `healthintel_dbt/models/staging/stg_ressarcimento_hc.sql`
- [x] `healthintel_dbt/models/staging/stg_ressarcimento_cobranca_arrecadacao.sql`
- [x] `healthintel_dbt/models/staging/stg_ressarcimento_indice_pagamento.sql`
- [x] `healthintel_dbt/models/staging/stg_ntrp_area_comercializacao.sql`
- [x] `healthintel_dbt/models/staging/stg_painel_precificacao.sql`
- [x] `healthintel_dbt/models/staging/stg_percentual_reajuste_agrupamento.sql`
- [x] `healthintel_dbt/models/staging/stg_ntrp_vcm_faixa_etaria.sql`
- [x] `healthintel_dbt/models/staging/stg_valor_comercial_medio_municipio.sql`
- [x] `healthintel_dbt/models/staging/stg_faixa_preco.sql`
- [x] `healthintel_dbt/models/staging/stg_operadora_cancelada.sql`
- [x] `healthintel_dbt/models/staging/stg_operadora_acreditada.sql`
- [x] `healthintel_dbt/models/staging/stg_prestador_acreditado.sql`
- [x] `healthintel_dbt/models/staging/stg_produto_prestador_hospitalar.sql`
- [x] `healthintel_dbt/models/staging/stg_operadora_prestador_nao_hospitalar.sql`
- [x] `healthintel_dbt/models/staging/stg_solicitacao_alteracao_rede_hospitalar.sql`
- [x] `healthintel_dbt/models/staging/stg_penalidade_operadora.sql`
- [x] `healthintel_dbt/models/staging/stg_monitoramento_garantia_atendimento.sql`
- [x] `healthintel_dbt/models/staging/stg_peona_sus.sql`
- [x] `healthintel_dbt/models/staging/stg_promoprev.sql`
- [x] `healthintel_dbt/models/staging/stg_rpc.sql`
- [x] `healthintel_dbt/models/staging/stg_iap.sql`
- [x] `healthintel_dbt/models/staging/stg_pfa.sql`
- [x] `healthintel_dbt/models/staging/stg_programa_qualificacao_institucional.sql`
- [x] `healthintel_dbt/models/staging/stg_beneficiario_regiao_geografica.sql`
- [x] `healthintel_dbt/models/staging/stg_beneficiario_informacao_consolidada.sql`
- [x] `healthintel_dbt/models/staging/stg_taxa_cobertura_plano.sql`

## dbt API

- [x] `healthintel_dbt/models/api/api_produto_plano.sql`
- [x] `healthintel_dbt/models/api/api_historico_plano.sql`
- [x] `healthintel_dbt/models/api/api_tuss_procedimento_vigente.sql`
- [x] `healthintel_dbt/models/api/api_tiss_ambulatorial_operadora_mes.sql`
- [x] `healthintel_dbt/models/api/api_tiss_hospitalar_operadora_mes.sql`
- [x] `healthintel_dbt/models/api/api_tiss_plano_mes.sql`
- [x] `healthintel_dbt/models/api/api_sip_assistencial_operadora.sql`
- [x] `healthintel_dbt/models/api/api_ressarcimento_beneficiario_abi.sql`
- [x] `healthintel_dbt/models/api/api_ressarcimento_sus_operadora_plano.sql`
- [x] `healthintel_dbt/models/api/api_ressarcimento_hc.sql`
- [x] `healthintel_dbt/models/api/api_ressarcimento_cobranca_arrecadacao.sql`
- [x] `healthintel_dbt/models/api/api_ressarcimento_indice_pagamento.sql`
- [x] `healthintel_dbt/models/api/api_ntrp_area_comercializacao.sql`
- [x] `healthintel_dbt/models/api/api_painel_precificacao.sql`
- [x] `healthintel_dbt/models/api/api_reajuste_agrupamento.sql`
- [x] `healthintel_dbt/models/api/api_ntrp_vcm_faixa_etaria.sql`
- [x] `healthintel_dbt/models/api/api_valor_comercial_medio_municipio.sql`
- [x] `healthintel_dbt/models/api/api_faixa_preco.sql`
- [x] `healthintel_dbt/models/api/api_operadora_cancelada.sql`
- [x] `healthintel_dbt/models/api/api_operadora_acreditada.sql`
- [x] `healthintel_dbt/models/api/api_prestador_acreditado.sql`
- [x] `healthintel_dbt/models/api/api_produto_prestador_hospitalar.sql`
- [x] `healthintel_dbt/models/api/api_operadora_prestador_nao_hospitalar.sql`
- [x] `healthintel_dbt/models/api/api_alteracao_rede_hospitalar.sql`
- [x] `healthintel_dbt/models/api/api_penalidade_operadora.sql`
- [x] `healthintel_dbt/models/api/api_garantia_atendimento.sql`
- [x] `healthintel_dbt/models/api/api_peona_sus.sql`
- [x] `healthintel_dbt/models/api/api_promoprev.sql`
- [x] `healthintel_dbt/models/api/api_rpc_operadora_mes.sql`
- [x] `healthintel_dbt/models/api/api_iap.sql`
- [x] `healthintel_dbt/models/api/api_pfa.sql`
- [x] `healthintel_dbt/models/api/api_programa_qualificacao_institucional.sql`
- [x] `healthintel_dbt/models/api/api_beneficiario_regiao_geografica.sql`
- [x] `healthintel_dbt/models/api/api_beneficiario_informacao_consolidada.sql`
- [x] `healthintel_dbt/models/api/api_taxa_cobertura_plano.sql`

## DAGs Airflow

- [x] `ingestao/dags/dag_ingest_produto_plano.py`
- [x] `ingestao/dags/dag_ingest_tuss_oficial.py`
- [x] `ingestao/dags/dag_ingest_tiss_subfamilias.py`
- [x] `ingestao/dags/dag_ingest_sip_delta.py`
- [x] `ingestao/dags/dag_ingest_ressarcimento_sus.py`
- [x] `ingestao/dags/dag_ingest_precificacao_ntrp.py`
- [x] `ingestao/dags/dag_ingest_rede_prestadores.py`
- [x] `ingestao/dags/dag_ingest_regulatorios_complementares.py`
- [x] `ingestao/dags/dag_ingest_beneficiarios_cobertura.py`

## dbt Consumo

- [x] `healthintel_dbt/models/consumo/consumo_precificacao_plano.sql`
- [x] `healthintel_dbt/models/consumo/consumo_rede_acreditacao.sql`
- [x] `healthintel_dbt/models/consumo/consumo_regulatorio_complementar_operadora.sql`
- [x] `healthintel_dbt/models/consumo/consumo_beneficiarios_cobertura_municipio.sql`

## Grants

- [x] `infra/postgres/init/050_delta_ans_grants.sql`

## YAML Documentação

- [x] `healthintel_dbt/models/staging/_stg_produtos_planos.yml`
- [x] `healthintel_dbt/models/staging/_stg_ressarcimento_sus.yml`
- [x] `healthintel_dbt/models/staging/_stg_precificacao_ntrp.yml`
- [x] `healthintel_dbt/models/staging/_stg_rede_prestadores.yml`
- [x] `healthintel_dbt/models/staging/_stg_regulatorios_complementares.yml`
- [x] `healthintel_dbt/models/staging/_stg_beneficiarios_cobertura.yml`

## Documentação

- [ ] `docs/sprints/fase_ans_100/sprint_41_delta_ans_100.md`
- [ ] `docs/catalogo_datasets_ans_faltantes.md`
- [ ] `docs/catalogo_tuss_oficial.md`
- [ ] `docs/catalogo_tabelas_api_delta_ans.md`
- [ ] `docs/runbooks/deploy_delta_ans_100_producao.md`
- [ ] `docs/evidencias/ans_100_delta/README.md`

---

# 6. Testes obrigatórios

## Python

- [ ] Testar parser de produtos/planos.
- [ ] Testar parser de TUSS oficial.
- [ ] Testar parser de TISS ambulatorial.
- [ ] Testar parser de TISS hospitalar.
- [ ] Testar parser de TISS dados de planos.
- [ ] Testar parser de SIP.
- [ ] Testar parser de ressarcimento SUS.
- [ ] Testar parser de NTRP/precificação.
- [ ] Testar parser de rede/prestadores.
- [ ] Testar parser de regulatórios complementares.
- [ ] Testar parser de beneficiários/cobertura.
- [ ] Testar arquivo grande sem carregar tudo em memória.
- [ ] Testar encoding `latin1`, `utf-8`, `utf-8-sig`.
- [ ] Testar delimitador `;`, `,`, `|`, `tab`.

## dbt

- [ ] `not_null` nas chaves principais.
- [ ] `unique` em dimensões vigentes.
- [ ] `relationships` com `api_operadora`/`dim_operadora` quando aplicável.
- [ ] `accepted_values` para UF.
- [ ] Teste de `competencia` no formato `YYYYMM`.
- [ ] Teste de `registro_ans` com 6 caracteres.
- [ ] Teste de vigência TUSS.
- [ ] Teste de retenção 24 meses para TISS.
- [ ] Teste de retenção 24 meses para RPC.
- [ ] Teste de volume mínimo por dataset.
- [ ] Teste de documentação YAML para todo modelo novo.

---

# 7. Hard gates finais

## Ambiente

- [ ] `docker compose ps`
- [ ] Postgres saudável.
- [ ] Mongo saudável.
- [ ] Redis saudável.
- [ ] API saudável.
- [ ] Airflow saudável, se usado na carga.
- [ ] Nenhum secret versionado.
- [ ] Nenhuma porta interna exposta indevidamente.

## Qualidade Python

- [x] `ruff check api ingestao scripts testes` (passou)
- [ ] `pytest ingestao/tests/ -v`
- [ ] `pytest api/tests/ -v`

## Qualidade dbt

- [ ] `dbt debug`
- [ ] `dbt deps`
- [ ] `dbt parse`
- [ ] `dbt compile`
- [ ] `dbt build --select tag:delta_ans_100`
- [ ] `dbt test --select tag:delta_ans_100`
- [ ] `dbt docs generate`

## Smokes SQL

### Produtos

```sql
select count(*) from api_ans.api_produto_plano;
select count(*) from api_ans.api_historico_plano;
```

### TUSS

```sql
select count(*) from api_ans.api_tuss_procedimento_vigente;

select codigo_tuss, count(*)
from api_ans.api_tuss_procedimento_vigente
group by codigo_tuss
having count(*) > 1;
```

### TISS

```sql
select min(competencia), max(competencia)
from api_ans.api_tiss_ambulatorial_operadora_mes;

select min(competencia), max(competencia)
from api_ans.api_tiss_hospitalar_operadora_mes;
```

### SIP

```sql
select count(*)
from api_ans.api_sip_assistencial_operadora;
```

### Ressarcimento SUS

```sql
select count(*)
from api_ans.api_ressarcimento_sus_operadora_plano;
```

### Precificação

```sql
select count(*)
from api_ans.api_painel_precificacao;

select count(*)
from api_ans.api_valor_comercial_medio_municipio;
```

### Rede/prestadores

```sql
select count(*)
from api_ans.api_prestador_acreditado;

select count(*)
from api_ans.api_alteracao_rede_hospitalar;
```

### Regulatórios complementares

```sql
select count(*)
from api_ans.api_penalidade_operadora;

select count(*)
from api_ans.api_rpc_operadora_mes;
```

### Grants

```sql
select grantee, table_schema, count(*)
from information_schema.role_table_grants
where table_schema in ('api_ans', 'consumo_ans', 'consumo_premium_ans')
group by grantee, table_schema
order by grantee, table_schema;
```

## Smokes API

- [ ] `GET /health`
- [ ] `GET /ready`
- [ ] `GET /api/produtos-planos?registro_ans=...`
- [ ] `GET /api/tuss/procedimentos?codigo_tuss=...`
- [ ] `GET /api/tiss/ambulatorial?competencia=...&registro_ans=...`
- [ ] `GET /api/tiss/hospitalar?competencia=...&registro_ans=...`
- [ ] `GET /api/sip?registro_ans=...`
- [ ] `GET /api/ressarcimento-sus?registro_ans=...`
- [ ] `GET /api/precificacao?uf=...`
- [ ] `GET /api/rede/prestadores-acreditados?uf=...`
- [ ] `GET /api/regulatorio/penalidades?registro_ans=...`

---

# 8. Critérios de fechamento

A sprint só pode ser marcada como fechada quando:

- [x] Todos os datasets faltantes prioritários foram implementados ou formalmente marcados como `não_comercial`.
- [x] TUSS oficial foi carregada a partir de `TUSS.zip`.
- [ ] TUSS sintética/crosswalk sintético não é usado em produção.
- [x] TISS oficial foi separada em ambulatorial/hospitalar/dados de planos.
- [x] Produtos/planos estão publicados em API/consumo.
- [x] Ressarcimento SUS está publicado em API/consumo.
- [x] Precificação/NTRP está publicada em API/consumo.
- [x] Regulatórios complementares estão publicados.
- [x] Grants aplicados.
- [ ] dbt build/test passou.
- [ ] Smokes SQL passaram.
- [ ] Smokes API passaram.
- [ ] Evidências foram salvas em `docs/evidencias/ans_100_delta/`.
- [ ] Release notes foram criadas.

---

# 9. Prompt completo para implementação

```text
Você está trabalhando no projeto HealthIntel Suplementar.

Objetivo:
Implementar a Sprint 41 — Delta ANS 100%, criando somente os datasets e tabelas que ainda não existem no projeto atual.

Regra principal:
NÃO mexer no que já existe e funciona.
NÃO recriar catálogo.
NÃO recriar bronze genérico.
NÃO recriar Mongo Layout Registry.
NÃO refatorar modelos existentes.
NÃO renomear tabelas existentes.
NÃO remover APIs existentes.

Apenas adicionar as lacunas.

Estruturas existentes que devem ser preservadas:
- plataforma.fonte_dado_ans
- plataforma.arquivo_fonte_ans
- bruto_ans.ans_arquivo_generico
- bruto_ans.ans_linha_generica
- MongoDB Layout Registry
- integração /layout/validar-arquivo
- pipeline bronze existente
- modelos staging existentes
- modelos API existentes

Datasets que já existem e não devem ser alterados:
- CADOP ativo
- CNES
- DIOPS
- FIP
- Glosa
- IDSS
- IGR
- NIP
- Portabilidade
- Prudencial
- Rede Assistencial existente
- Regime Especial
- RN623
- SIB município
- SIB operadora
- Taxa de Resolutividade
- TISS procedimento existente
- TUSS staging existente, salvo promoção oficial para API
- VDA
- APIs atuais já publicadas

Implementar somente os seguintes deltas:

1. Produtos e planos
- /FTP/PDA/caracteristicas_produtos_saude_suplementar-008/
- /FTP/PDA/historico_planos_saude/
- /FTP/PDA/servicos_opcionais_planos_saude/
- /FTP/PDA/quadros_auxiliares_de_corresponsabilidade/

2. TUSS oficial
- /FTP/PDA/terminologia_unificada_saude_suplementar_TUSS/
- Dicionario_de_dados.ods
- TUSS.zip
- TUSS oficial deve virar API/consumo e não pode depender de crosswalk sintético em produção.

3. TISS oficial por subfamília
- /FTP/PDA/TISS/AMBULATORIAL/
- /FTP/PDA/TISS/HOSPITALAR/
- /FTP/PDA/TISS/DADOS_DE_PLANOS/
- /FTP/PDA/TISS/DICIONARIO/

4. SIP
- /FTP/PDA/SIP/

5. Ressarcimento SUS
- /FTP/PDA/beneficiarios_identificados_sus_abi/
- /FTP/PDA/dados_ressarcimento_SUS_operadora_planos_saude/
- /FTP/PDA/hc_ressarcimento_sus/
- /FTP/PDA/ressarcimento_ao_SUS_cobranca_arrecadacao/
- /FTP/PDA/ressarcimento_ao_SUS_indice_efetivo_pagamento/

6. Precificação, NTRP e reajustes
- /FTP/PDA/area_comercializacao_planos_ntrp/
- /FTP/PDA/painel_precificacao-053/
- /FTP/PDA/percentuais_de_reajuste_de_agrupamento-055/
- /FTP/PDA/nota_tecnica_ntrp_vcm_faixa_etaria/
- /FTP/PDA/valor_comercial_medio_por_municipio_NTRP-054/
- /FTP/PDA/faixa_de_preco/

7. Operadoras, rede e prestadores complementares
- /FTP/PDA/operadoras_de_plano_de_saude_canceladas/
- /FTP/PDA/operadoras_acreditadas/
- /FTP/PDA/prestadores_acreditados/
- /FTP/PDA/produtos_e_prestadores_hospitalares/
- /FTP/PDA/operadoras_e_prestadores_nao_hospitalares/
- /FTP/PDA/solicitacoes_alteracao_rede_hospitalar-046/

8. Regulatórios complementares
- /FTP/PDA/penalidades_aplicadas_a_operadoras/
- /FTP/PDA/monitoramento_garantia_atendimento/
- /FTP/PDA/peona_sus/
- /FTP/PDA/promoprev-052/
- /FTP/PDA/RPC/
- /FTP/PDA/IAP/
- /FTP/PDA/PFA/
- /FTP/PDA/programa_de_qualificacao_institucional/

9. Beneficiários/cobertura complementares
- /FTP/PDA/dados_de_beneficiarios_por_regiao_geografica/
- /FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/
- /FTP/PDA/taxa_de_cobertura_de_planos_de_saude-047/

10. Documentais
- /FTP/PDA/Caderno_SS/
- /FTP/PDA/caderno_de_informacao/
- /FTP/PDA/glossario_saude_suplementar/
- /FTP/PDA/agenda_de_autoridades/
- /FTP/PDA/plano_anual_de_atividades/

Regras:
- Se tabular: bronze + staging + API somente quando houver valor.
- Se documental: catalogar, arquivar, bronze genérico se parseável, marcar como não_comercial.
- API deve consultar somente api_ans.
- Cliente SQL comum deve acessar somente consumo_ans.
- Cliente SQL premium deve acessar somente consumo_premium_ans.
- TISS e RPC devem respeitar janela de 24 meses no Postgres para API/consumo.

Hard gates:
- ruff check api ingestao scripts testes
- pytest ingestao/tests/ -v
- pytest api/tests/ -v
- dbt debug
- dbt deps
- dbt parse
- dbt compile
- dbt build --select tag:delta_ans_100
- dbt test --select tag:delta_ans_100
- dbt docs generate
- smoke SQL
- smoke API
- grants em api_ans, consumo_ans, consumo_premium_ans
- evidências em docs/evidencias/ans_100_delta/

Não finalizar se:
- TUSS oficial não veio de TUSS.zip
- crosswalk sintético estiver em produção
- API consultar schema interno
- tabela nova não tiver YAML
- tabela nova não tiver teste mínimo
- tabela nova não tiver grant
- TISS/RPC ignorarem retenção de 24 meses
- algum dataset faltante prioritário não tiver status final
```

---

# 10. Resultado esperado

Ao final da sprint, o projeto terá apenas adições, sem quebrar o que já existe:

- [ ] Novos datasets ANS cobertos.
- [ ] TUSS oficial publicada.
- [ ] TISS oficial por subfamília publicada.
- [ ] Produtos/planos publicados.
- [ ] SIP publicado.
- [ ] Ressarcimento SUS publicado.
- [ ] Precificação/NTRP publicado.
- [ ] Rede/prestadores complementares publicados.
- [ ] Regulatórios complementares publicados.
- [ ] Beneficiários/cobertura complementares publicados.
- [ ] Documentais classificados.
- [ ] APIs novas documentadas.
- [ ] Consumo SQL novo liberado.
- [ ] Grants aplicados.
- [ ] Hard gates concluídos.
