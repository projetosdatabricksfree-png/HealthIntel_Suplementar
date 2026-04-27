# Padrões de Índices, Chaves e Constraints

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir padrões para índices, chaves naturais, surrogate keys, constraints, funções e triggers na plataforma HealthIntel Suplementar.

---

## Padrão de Chave Natural

1. Toda tabela publicada deve ter chave natural documentada.
2. Chave natural é a combinação de colunas que identifica unicamente o registro no negócio.
3. Exemplos:
   - `registro_ans + competencia` para operadora mensal
   - `cnes + competencia` para estabelecimento
   - `codigo_tuss + versao_tuss` para procedimento TUSS
   - `tenant_id + numero_contrato_normalizado` para contrato privado

---

## Padrão de Surrogate Key

1. Surrogate keys usam hash MD5 ou UUID.
2. Nomenclatura: `<entidade>_master_id` para masters MDM.
3. Exemplos:
   - `operadora_master_id varchar(32)` — MD5 de `registro_ans`
   - `contrato_master_id varchar(32)` — MD5 de `tenant_id + numero_contrato_normalizado`
4. Surrogate key nunca é exposta como campo de negócio sem documentação.
5. Surrogate key é obrigatória em tabelas premium.

---

## Primary Key

1. Toda tabela materializada deve ter primary key.
2. Nomenclatura: `pk_<tabela>`.
3. Composta quando necessário: `pk_mdm_operadora_master` em `(operadora_master_id, competencia)`.
4. Primary key nunca usa coluna volátil (ex: `_carregado_em`).

---

## Foreign Key

1. Foreign key física é opcional — preferir relacionamento lógico via dbt.
2. Quando física, nomenclatura: `fk_<origem>_<destino>`.
3. FK física não deve bloquear ingestão — usar `on delete set null` ou evitar em staging.
4. Relacionamento lógico documentado em `_schema.yml` ou `schema.yml` do dbt.

---

## Unique Constraints

1. Nomenclatura: `uk_<tabela>_<colunas>`.
2. Usar em chaves naturais publicadas.
3. Exemplo: `uk_operadora_master_registro_ans_competencia`.

---

## Check Constraints

1. Nomenclatura: `ck_<tabela>_<regra>`.
2. Usar para regra barata e inviolável:
   - Faixa de score: `ck_quality_dataset_score_0_100`
   - Competência válida: `ck_competencia_200001_209912`
   - Status enumerado: `ck_mdm_status_ativo_inativo_pendente`
3. **Nunca** usar para regra analítica instável.
4. **Nunca** bloquear ingestão bruta sem necessidade.

---

## Índices

1. Todo índice deve ter justificativa documentada.
2. Nomenclatura: `ix_<tabela>_<colunas>`.
3. Nomenclatura índice único: `ux_<tabela>_<colunas>`.
4. Criar índice para:
   - Colunas usadas em `where` com alta seletividade.
   - Colunas de join com tabelas grandes.
   - Colunas de ordenação em API.
   - Colunas de competência/trimestre.
5. Justificar explicitamente índices em staging (evitar overhead de ingestão).

---

## Preferência: dbt Tests sobre Constraints Físicas

1. Para validações analíticas, preferir dbt tests sobre constraints:
   - `unique` / `not_null` para chaves
   - `accepted_values` para domínios
   - `relationships` para integridade referencial
   - Testes singulares para regras complexas
2. dbt tests podem ser configurados com `severity: warn` ou `severity: error`.
3. dbt tests não bloqueiam ingestão, mas sinalizam qualidade.

---

## Funções PostgreSQL

1. Usar apenas para regra pequena, determinística e reusável.
2. Exemplos aprovados:
   - `normalizar_cnpj(cnpj text) → varchar(14)`
   - `validar_cnpj_completo(cnpj text) → boolean`
   - `competencia_para_data(competencia int) → date`
3. **Proibido**: função que faça chamada HTTP, acesso a API externa ou requisição de rede.
4. **Proibido**: provider externo (Serpro, Receita, BrasilAPI) sem ADR.
5. Toda função deve ter contrato documentado: entrada, saída, efeitos colaterais.

---

## Triggers

1. Usar apenas para auditoria ou regra operacional inevitável.
2. Exemplos aceitáveis:
   - `_carregado_em` preenchido automaticamente.
   - Log de alteração em tabela de configuração.
3. **Proibido**: trigger para agregação pesada.
4. **Proibido**: trigger para transformação analítica complexa.
5. Triggers não substituem dbt tests.
6. Triggers não substituem MDM.
7. Todo trigger deve ter justificativa documentada.

---

## Relacionamentos Especiais

### Relacionamento MDM
- Master tables públicas (`mdm_ans`) usam `operadora_master_id` como surrogate key.
- Tabelas downstream referenciam `operadora_master_id` como FK lógica.
- Crosswalk (`xref_*`) mapeia múltiplas origens para o mesmo master.

### Relacionamento Premium
- Tabelas `api_premium_*` contêm `operadora_master_id` das tabelas MDM.
- Linhagem documentada no campo `upstream` do catálogo de tabelas.

### Relacionamento Privado por Tenant
- Tabelas em `mdm_privado` e `consumo_premium_ans` exigem `tenant_id`.
- FK lógica inclui `tenant_id` quando cruza schemas.
- RLS garante isolamento no PostgreSQL.