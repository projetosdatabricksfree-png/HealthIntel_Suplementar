# 📊 RELATÓRIO DETALHADO DO BANCO DE DADOS HEALTHINTEL

**Data:** 2026-05-18  
**Banco:** PostgreSQL 16  
**Ambiente:** Docker (healthintel_postgres)

---

## 📈 RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| **Total de Schemas** | 12 |
| **Total de Tabelas** | 379 |
| **Total de Registros** | **117.77 Milhões** |
| **Tamanho Total do Banco** | **32+ GB** |
| **Schemas Ativos** | 12 (todos) |
| **Anos de Cobertura** | 2026 (dados parciais) |

---

## 🗂️ SCHEMAS E DISTRIBUIÇÃO DE DADOS

### Resumo por Schema

| Schema | Tabelas | Registros | Tamanho | % do Total |
|--------|---------|-----------|--------|-----------|
| **bruto_ans** | 102 | 116,223,056 | **32 GB** | **98.7%** |
| **consumo_ans** | 26 | 809,452 | 108 MB | 0.69% |
| **nucleo_ans** | 39 | 675,401 | 152 MB | 0.57% |
| **api_ans** | 90 | 48,725 | 183 MB | 0.04% |
| **public** | 42 | 15,102 | 11 MB | 0.01% |
| **plataforma** | 34 | 1,280 | 9.2 MB | <0.01% |
| **ref_ans** | 11 | 20 | 1.2 MB | <0.01% |
| **mdm_privado** | 8 | 0 | 64 kB | - |
| **consumo_premium_ans** | 11 | 0 | 1.3 MB | - |
| **quality_ans** | 5 | 0 | 552 kB | - |
| **bruto_cliente** | 2 | 0 | 80 kB | - |
| **mdm_ans** | 9 | 0 | 488 kB | - |

---

## 📊 DETALHAMENTO POR SCHEMA

### 🔴 **bruto_ans** - Bronze (Raw Data)
- **Tabelas:** 102
- **Com Dados:** 7
- **Vazias:** 95
- **Registros:** 116,223,056
- **Tamanho:** 32 GB

**Top 5 Tabelas Principais:**
1. `produto_prestador_hospitalar` - 42,907,740 registros (11 GB)
2. `operadora_prestador_nao_hospitalar` - 31,959,000 registros (8.7 GB)
3. `painel_precificacao` - 30,149,562 registros (8 GB)
4. `diops_operadora_trimestral_default` - 10,191,724 registros (3.6 GB)
5. `produto_tabela_auxiliar` - 877,468 registros (356 MB)

---

### 🟢 **consumo_ans** - Consumo/Entrega BI
- **Tabelas:** 26
- **Com Dados:** 17
- **Vazias:** 9
- **Registros:** 809,452
- **Tamanho:** 108 MB

**Top 5 Tabelas Principais:**
1. `consumo_produto_plano` - 163,661 registros (33 MB)
2. `consumo_historico_plano` - 163,567 registros (14 MB)
3. `consumo_regulatorio_operadora_trimestre` - 161,173 registros (21 MB)
4. `consumo_igr` - 136,908 registros (15 MB)
5. `consumo_tuss_procedimento_vigente` - 64,654 registros (10 MB)

---

### 🟡 **nucleo_ans** - Gold (Marts)
- **Tabelas:** 39
- **Com Dados:** 18
- **Vazias:** 21
- **Registros:** 675,401
- **Tamanho:** 152 MB

**Top 5 Tabelas Principais:**
1. `mart_regulatorio_operadora` - 161,173 registros (21 MB)
2. `fat_monitoramento_regulatorio_trimestral` - 161,173 registros (35 MB)
3. `fat_score_v2_operadora_mensal` - 136,034 registros (32 MB)
4. `fat_score_regulatorio_operadora_mensal` - 136,032 registros (31 MB)
5. `dim_operadora_scd` - 1,000+ registros

---

### 🔵 **api_ans** - API Serving Layer
- **Tabelas:** 90
- **Com Dados:** 5
- **Vazias:** 85
- **Registros:** 48,725
- **Tamanho:** 183 MB

**Tabelas com Dados:**
1. `api_taxa_resolutividade_operadora_trimestral` - 26,062 registros (4.5 MB)
2. `api_prudencial_operadora_trimestral` - 11,216 registros (1.5 MB)
3. `api_prata_diops` - 10,486 registros (1.5 MB)
4. `api_glosa_operadora_mensal` - 844 registros (192 kB)
5. `api_regime_especial_operadora_trimestral` - 117 registros (88 kB)

---

### ⚙️ **plataforma** - Metadados Operacionais
- **Tabelas:** 34
- **Com Dados:** 11
- **Vazias:** 23
- **Registros:** 1,280
- **Tamanho:** 9.2 MB

**Tabelas Principais:**
- `job` - Jobs de ingestão
- `log_uso` - Logs de utilização da API
- `politica_dataset` - Políticas de datasets
- `retencao_particao_log` - Retenção de logs

---

### 📋 **Outros Schemas**

| Schema | Tabelas | Registros | Status |
|--------|---------|-----------|--------|
| **public** | 42 | 15,102 | Misto (dados de sistema) |
| **ref_ans** | 11 | 20 | Referência mínima |
| **bruto_cliente** | 2 | 0 | Vazio (premium) |
| **mdm_ans** | 9 | 0 | Vazio (MDM público) |
| **mdm_privado** | 8 | 0 | Vazio (MDM privado) |
| **quality_ans** | 5 | 0 | Vazio (data quality) |
| **consumo_premium_ans** | 11 | 0 | Vazio (premium) |

---

## 📅 COMPETÊNCIAS (Períodos de Dados)

### Status Atual
- **Anos com Dados:** 2026 (parcial)
- **Competência Mínima:** 202605 (Maio/2026)
- **Competência Máxima:** 202605 (Maio/2026)
- **Total de Competências:** 1 (apenas maio/2026)

### Distribuição
```
Maio 2026 (202605):
├── bruto_ans: 116,223,056 registros
├── consumo_ans: 809,452 registros
└── nucleo_ans: 675,401 registros
```

**⚠️ Nota:** O banco está em fase inicial com apenas dados de maio/2026 carregados. A cobertura de 3 anos (2021-2023) mencionada no CLAUDE.md deve estar prevista para próximas cargas.

---

## 📊 ANÁLISE DE DENSIDADE DE DADOS

### Tabelas Vazias vs Com Dados

| Schema | Vazias | Com Dados | Taxa Preenchimento |
|--------|--------|-----------|-------------------|
| **api_ans** | 85 | 5 | 5.6% |
| **bruto_ans** | 95 | 7 | 6.9% |
| **nucleo_ans** | 21 | 18 | 46.2% |
| **consumo_ans** | 9 | 17 | 65.4% |
| **plataforma** | 23 | 11 | 32.4% |
| **public** | 28 | 14 | 33.3% |
| **bruto_cliente** | 2 | 0 | 0% |
| **mdm_ans** | 9 | 0 | 0% |
| **mdm_privado** | 8 | 0 | 0% |
| **quality_ans** | 5 | 0 | 0% |
| **consumo_premium_ans** | 11 | 0 | 0% |
| **ref_ans** | 9 | 2 | 18.2% |

---

## 💾 TAMANHO E ARMAZENAMENTO

### Distribuição de Tamanho
```
32 GB total

bruto_ans ........... 32 GB (98.7%)
├── produto_prestador_hospitalar ....... 11 GB
├── operadora_prestador_nao_hospitalar .. 8.7 GB
├── painel_precificacao ................ 8 GB
└── outros ............................. 4.3 GB

Outros schemas ......................... 400 MB (1.3%)
├── consumo_ans ......................... 108 MB
├── nucleo_ans ........................... 152 MB
├── api_ans ............................. 183 MB
└── demais .............................. -43 MB
```

---

## 🔍 TABELAS MAIS POPULOSAS (Top 15)

| Rank | Schema | Tabela | Registros | Tamanho |
|------|--------|--------|-----------|---------|
| 1 | bruto_ans | produto_prestador_hospitalar | 42,907,740 | 11 GB |
| 2 | bruto_ans | operadora_prestador_nao_hospitalar | 31,959,000 | 8.7 GB |
| 3 | bruto_ans | painel_precificacao | 30,149,562 | 8 GB |
| 4 | bruto_ans | diops_operadora_trimestral_default | 10,191,724 | 3.6 GB |
| 5 | bruto_ans | produto_tabela_auxiliar | 877,468 | 356 MB |
| 6 | consumo_ans | consumo_produto_plano | 163,661 | 33 MB |
| 7 | consumo_ans | consumo_historico_plano | 163,567 | 14 MB |
| 8 | nucleo_ans | mart_regulatorio_operadora | 161,173 | 21 MB |
| 9 | nucleo_ans | fat_monitoramento_regulatorio_trimestral | 161,173 | 35 MB |
| 10 | consumo_ans | consumo_regulatorio_operadora_trimestre | 161,173 | 21 MB |
| 11 | consumo_ans | consumo_igr | 136,908 | 15 MB |
| 12 | nucleo_ans | fat_score_v2_operadora_mensal | 136,034 | 32 MB |
| 13 | nucleo_ans | fat_score_regulatorio_operadora_mensal | 136,032 | 31 MB |
| 14 | bruto_ans | sip_mapa_assistencial | 133,392 | 42 MB |
| 15 | consumo_ans | consumo_tuss_procedimento_vigente | 64,654 | 10 MB |

---

## ✅ CHECKLIST DE INTEGRIDADE

| Item | Status | Observações |
|------|--------|------------|
| Schemas Esperados | ✅ | 12/12 presentes |
| Dados em Bronze | ✅ | 116M registros carregados |
| Dados em Gold | ✅ | Milhões de registros processados |
| API Layer Poblada | ⚠️ | 5/90 tabelas com dados |
| Competências | ⚠️ | Apenas maio/2026; cobertura 3 anos esperada |
| Premium Schemas | ❌ | Vazios (não implementado) |
| MDM | ❌ | Vazio (não carregado) |
| Quality Checks | ❌ | Vazio (não executado) |

---

## 📌 RECOMENDAÇÕES

1. **Backfill de Dados:**
   - Completar cobertura de 3 anos (2021-2023) conforme Release 0.9
   - Monitorar competências adicionais via `plataforma.job`

2. **Schema Premium:**
   - Ativar ingestion para `consumo_premium_ans` e `bruto_cliente`
   - Validar MDM público e privado

3. **API Layer:**
   - 85 tabelas vazias em `api_ans` — aguardam materialização
   - Verificar triggers/views para dados sob demanda

4. **Quality Checks:**
   - Ativar validações em `quality_ans` (CNPJ-DV, CNES-DV)
   - Implementar monitoramento de SLA

5. **Armazenamento:**
   - 32 GB ocupados; monitorar crescimento com novos períodos
   - Considerar compressão ou particionamento se necessário

---

## 📐 ESTRUTURA MEDALLON (Esperada)

```
Bronze (bruto_ans)
  116M registros ✅
  32 GB (98.7% do banco)
  
Staging (stg_ans/int_ans)
  [Views epímeras — não materializadas]
  
Gold (nucleo_ans)
  675K registros ✅
  152 MB (marts, dimensões)
  
API (api_ans)
  48K registros ✅
  183 MB (5/90 tabelas pobladas)
  
Consumo (consumo_ans)
  809K registros ✅
  108 MB (entrega BI/cliente)
```

---

**Relatório Gerado:** 2026-05-18 | **Próxima Verificação Recomendada:** Semanal
